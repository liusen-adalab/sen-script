import click
import pexpect
import subprocess

from sen_script import HOME
from sen_script.cmd_ssh import parse_single_or_list


def read_hosts(config_path) -> list[str]:
    with open(config_path) as config_path:
        host_lines = list(
            filter(lambda l: "host " in l.lower(), config_path.readlines())
        )
        return list(map(lambda l: l.strip().split()[-1], host_lines))


def start_user_agent():
    cmd = "ssh-agent"
    subprocess.run(cmd, shell=True, check=True, capture_output=True)


identity_passphrase = None


def type_key_passphrase(p: pexpect.spawn, identity: str):
    print("typing passphrase for", identity)
    require_password = "Enter passphrase for.+"
    end = pexpect.EOF
    expects = [require_password, end]

    global identity_passphrase

    if identity_passphrase is not None:
        print(f"trying cached passphrase: {identity_passphrase}")
        p.sendline(identity_passphrase)

        idx = p.expect(expects, timeout=10)
        if end == expects[idx]:
            return

    password = None
    while True:
        password = click.prompt(f"{identity}'s password", hide_input=True, type=str)
        print(f"sending {identity} password: {password}")
        p.sendline(password)

        idx = p.expect(expects, timeout=5)

        if end == expects[idx]:
            identity_passphrase = password
            return


def type_remote_passphrase(p: pexpect.spawn, host):
    global cached_remote_passphrase

    require_remote_pwd = "password.+"
    deny = "Permission denied.+"
    end = pexpect.EOF
    expects = [require_remote_pwd, deny, end]

    if cached_remote_passphrase is not None:
        print(f"trying cached passphrase: {cached_remote_passphrase}")
        p.sendline(cached_remote_passphrase)

        idx = p.expect(expects, timeout=10)
        if end == expects[idx]:
            return

    password = None
    while True:
        password = click.prompt(f"{host}'s password", hide_input=True, type=str)
        print(f"sending {host} password")
        p.sendline(password)

        idx = p.expect(expects, timeout=10)
        if end == expects[idx]:
            cached_remote_passphrase = password
            return
        elif deny == expects[idx]:
            print(f"permission denied for {host}")
            return


def add_to_ssh_agent(identity: str):
    cmd = f"ssh-add {identity}"
    print("adding key to ssh-agent:", cmd)
    p = pexpect.spawn(cmd)

    require_password = "Enter passphrase for.+"
    end = pexpect.EOF
    expects = [require_password, end]

    idx = p.expect(expects, timeout=3)
    if require_password == expects[idx]:
        type_key_passphrase(p, identity)
    elif end == expects[idx]:
        pass

    print(f"{identity} added to ssh-agent")


cached_remote_passphrase = None


def copy_id_to_host(host: str, identity: str):
    cmd = f"ssh-copy-id -i {identity} {host}"
    print("executing:", cmd)
    p = pexpect.spawn(cmd)

    already_copied = "All keys were skipped.*"
    remote_not_known = "Are you sure you want to continue connecting.+"
    require_remote_pwd = "password:.*"
    require_key_pwd = "Enter passphrase for.+"
    no_route = "No route to host.*"
    could_not_resolve = "Could not resolve hostname.+"

    eof = pexpect.EOF
    expects = [
        already_copied,
        require_remote_pwd,
        remote_not_known,
        require_key_pwd,
        no_route,
        could_not_resolve,
        eof,
    ]

    idx = p.expect(expects, timeout=10)

    if already_copied == expects[idx]:
        print(f"{identity} already copied to {host}, skipping")
    elif remote_not_known == expects[idx]:
        p.sendline("yes")
        idx = p.expect(expects, timeout=10)
        if eof == expects[idx]:
            return
        type_remote_passphrase(p, host)
    elif require_remote_pwd == expects[idx]:
        type_remote_passphrase(p, host)
    elif require_key_pwd == expects[idx]:
        type_key_passphrase(p, identity)
    elif eof == expects[idx]:
        print(f"{identity} already copied to {host}, skipping")
    elif no_route == expects[idx]:
        print(f"no route to {host}, skipping")
    elif could_not_resolve == expects[idx]:
        print(f"could not resolve {host}, skipping")


@click.command()
@click.option(
    "-i",
    "identity",
    type=click.Path(exists=True),
    default=f"{HOME}/.ssh/id_rsa",
    show_default=True,
    help="identify file path",
)
@click.option(
    "-c",
    "--cfg-file",
    "config_file",
    type=click.Path(exists=True, resolve_path=True),
    default=f"{HOME}/.ssh/config",
    show_default=True,
    help="config file",
)
@click.option(
    "--host",
    "-H",
    "hosts",
    type=str,
    help="single or list like 'remote-host-[20-31]' hosts to copy identity",
)
def copy_id(config_file, identity, hosts):
    """
    copy local ssh identity to all host in ~/.ssh/config
    """
    print(f"copying {identity} to {config_file}")
    start_user_agent()
    if hosts is None:
        hosts = read_hosts(config_file)
    else:
        hosts = parse_single_or_list(hosts)

    for h in hosts:
        copy_id_to_host(h, identity)

    add_to_ssh_agent(identity)


if __name__ == "__main__":
    copy_id()
