import sys

if sys.version_info.major >= 3:

    # import commands
    import optparse
    import shlex

    import IPython
    import lldb
    from traitlets.config import Config

    # from rich import print as rprint
    # from rich import inspect as rinspect

    def __lldb_init_module(debugger, internal_dict):
        debugger.HandleCommand("command script add -f lldb_ipython.ipython ipython")
        # print('dump_mem command added')

    def create_ipython_options():
        usage = "usage: %prog [options]"
        description = """IPython woohoo"""
        parser = optparse.OptionParser(description=description, prog="ipython", usage=usage)
        # parser.add_option('-a', '--address', type='int', dest='address', help='Address to dump.')
        # parser.add_option('-s', '--size', type='int', dest='size', help='Size of dump.')
        # parser.add_option('-f', '--file', type='string', dest='path', help='File to dump into.')

        return parser

    def ipython(debugger, command, result, internal_dict):
        # print('ipython run')
        command_args = shlex.split(command)
        parser = create_ipython_options()

        try:
            (options, args) = parser.parse_args(command_args)

        except:
            # if you don't handle exceptions, passing an incorrect argument to the OptionParser will cause LLDB to exit
            result.SetError("option parsing failed")
            return
        # print(options)

        # rinspect(internal_dict, all=True)
        # rprint(lldb.thread)
        # rprint(internal_dict['lldb'].thread)
        # rprint(internal_dict['thread'])

        # print('ipython really running now')

        c = Config()
        c.InteractiveShellApp.exec_lines = [
            "lldb.target = lldb.debugger.GetSelectedTarget()",
            "lldb.process = lldb.target.GetProcess()",
            "lldb.thread = lldb.process.GetSelectedThread()",
            "lldb.frame = lldb.thread.GetSelectedFrame()",
        ]
        # c.InteractiveShell.colors = 'LightBG'
        c.InteractiveShell.colors = "NoColor"
        c.InteractiveShell.confirm_exit = False
        c.TerminalIPythonApp.display_banner = False
        # IPython.terminal.embed.embed(config=c)
        IPython.start_ipython(user_ns=internal_dict, config=c)

        return
