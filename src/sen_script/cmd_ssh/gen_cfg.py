import click
import os
from sen_script.cmd_ssh import parse_single_or_list
from sen_script.cmd_ssh import read_hosts


def gen_cfg_block(host, ip, port, user):
    host = f"Host {host}"
    host_ip = f"    HostName {ip}"
    user = f"    User {user}"
    port = f"    Port {port}"
    return f"{host}\n{host_ip}\n{user}\n{port}"


@click.command()
@click.option(
    "--host",
    "-H",
    type=str,
    help="single host name, or list like 'remote-host-[20-31]'",
    required=True,
)
@click.option(
    "--ip",
    type=str,
    help="single ip address, or list like '192.168.1.[20-31]'",
    required=True,
)
@click.option("--port", "-p", type=int, default=22, show_default=True)
@click.option("--user", "-u", type=str, default="root", show_default=True)
def gen_cfg(host, ip, port, user):
    """
    generate ssh configuations and add it to ~/.ssh/config
    """
    print(f"host: {host}, ip: {ip}, port: {port}, user:{user}")

    config_path = os.path.expanduser("~/.ssh/config")
    exist_hosts = read_hosts(config_path)

    hosts = parse_single_or_list(host)
    ips = parse_single_or_list(ip)
    cfgs = []
    for h, i in zip(hosts, ips):
        if h not in exist_hosts:
            cfgs.append(gen_cfg_block(h, i, port, user))
        else:
            print(f"host {h} already exist")

    if not cfgs:
        print(f"no new host added")
        return

    cfgs = "\n".join(cfgs)
    print("generate ssh config")
    print(cfgs)
    with open(config_path, "a") as f:
        print(f"writing ssh config to {config_path}")
        f.write("\n" + cfgs)
