import subprocess
import click


def force_reinstall_self():
    cmd = "poetry build && pip3 install dist/sen_script-0.1.1-py3-none-any.whl --force-reinstall"
    subprocess.run(cmd, shell=True)


def ssh_cmd(host, cmd):
    cmd = f"ssh {host} '{cmd}'"
    print("running ssh command:", cmd)
    try:
        subprocess.check_output(cmd, shell=True)
    except subprocess.CalledProcessError as e:
        print(e.output)


@click.command()
@click.argument("host")
def update_self_at_remote(host):
    cmd = "poetry build"
    subprocess.run(cmd, shell=True)

    whl_name = "sen_script-0.1.1-py3-none-any.whl"
    whl_path = f"dist/{whl_name}"

    cmd = f"scp {whl_path} {host}:{whl_name}"
    subprocess.run(cmd, shell=True)

    cmd = f"pip3 install {whl_name} --break-system-packages --force-reinstall --no-warn-script-location"
    ssh_cmd(host, cmd)

    cmd = f"rm {whl_name}"
    ssh_cmd(host, cmd)
