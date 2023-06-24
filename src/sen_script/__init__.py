import click
import os

HOME = os.path.expanduser("~")
CONTEXT_SETTINGS = dict(help_option_names=["-h", "--help"])


@click.group(context_settings=CONTEXT_SETTINGS)
def cli_root():
    """main command line tool"""
    pass


@click.group()
def ssh():
    pass


cli_root.add_command(ssh)

from sen_script.cmd_ssh import gen_cfg
from sen_script.cmd_ssh import copy_id


ssh.add_command(gen_cfg.gen_cfg)
ssh.add_command(copy_id.copy_id)


if __name__ == "__main__":
    cli_root()
