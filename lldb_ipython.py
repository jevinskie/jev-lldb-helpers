import argparse
import sys

import IPython
from traitlets.config import Config


def __lldb_init_module(debugger, internal_dict):
    debugger.HandleCommand("command script add -f lldb_ipython.ipython ipython")


def get_argparse_parser():
    parser = argparse.ArgumentParser(description="IPython in LLDB", prog="ipython")
    return parser


def ipython(debugger, command, result, internal_dict):
    # parser = get_argparse_parser()
    # args = parser.parse_args(shlex.split(command))

    # rinspect(internal_dict, all=True)
    # rprint(internal_dict.keys())
    # rprint(internal_dict['lldb'].__dict__)
    # rprint(internal_dict['lldb'].__dir__())

    # print('ipython really running now')

    c = Config()
    # FIXME: these don't work
    c.InteractiveShellApp.exec_lines = [
        "print('begin exec_lines')",
        "lldb.target = lldb.debugger.GetSelectedTarget()",
        "lldb.process = lldb.target.GetProcess()",
        "lldb.thread = lldb.process.GetSelectedThread()",
        "lldb.frame = lldb.thread.GetSelectedFrame()",
        "print('end exec_lines')",
    ]
    c.InteractiveShell.colors = "Neutral" if sys.stdout.isatty() else "NoColor"
    c.InteractiveShell.confirm_exit = False
    c.TerminalIPythonApp.display_banner = False
    IPython.embed(config=c)
    # IPython.start_ipython(user_ns=internal_dict, config=c)
