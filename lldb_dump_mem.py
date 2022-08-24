# import commands
import optparse
import shlex

import lldb


def __lldb_init_module(debugger, internal_dict):
    debugger.HandleCommand("command script add -f lldb_dump_mem.dump_mem dump_mem")
    # print('dump_mem command added')


def create_dump_mem_options():
    usage = "usage: %prog [options]"
    description = """Dump <size> bytes of memory from <address> to <file>"""
    parser = optparse.OptionParser(description=description, prog="dump_mem", usage=usage)
    parser.add_option("-a", "--address", type="int", dest="address", help="Address to dump.")
    parser.add_option("-s", "--size", type="int", dest="size", help="Size of dump.")
    parser.add_option("-f", "--file", type="string", dest="path", help="File to dump into.")

    return parser


def dump_mem(debugger, command, result, internal_dict):
    print("dump_mem run")
    command_args = shlex.split(command)
    parser = create_dump_mem_options()

    try:
        (options, args) = parser.parse_args(command_args)

    except:
        # if you don't handle exceptions, passing an incorrect argument to the OptionParser will cause LLDB to exit
        result.SetError("option parsing failed")
        return
    print(options)

    error_ref = lldb.SBError()
    process = debugger.GetSelectedTarget().GetProcess()
    memory = process.ReadMemory(options.address, options.size, error_ref)
    if error_ref.Success():
        with open(options.path, "wb") as dumpf:
            dumpf.write(memory)
    else:
        result.AppendString(str(error_ref))

    return
