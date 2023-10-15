import argparse
import shlex

import lldb

from unsigned_expr_action import UnsignedExpressionAction


def __lldb_init_module(debugger, internal_dict):
    debugger.HandleCommand("command script add -f lldb_dump_mem.dump_mem dump_mem")


def get_argparse_parser(debugger, result):
    class CustomHelpFormatter(argparse.HelpFormatter):
        def _format_args(self, action, default_metavar):
            if action.dest == "address":
                return self._metavar_formatter(action, None)(1)[0]
            else:
                return super(CustomHelpFormatter, self)._format_args(action, default_metavar)

    parser = argparse.ArgumentParser(
        description="Dump <SIZE EXPRESSION> bytes of memory from <ADDRESS EXPRESSION> to <FILE>",
        prog="dump_mem",
        formatter_class=CustomHelpFormatter,
    )
    parser.lldb_debugger = debugger
    parser.lldb_result = result
    parser.add_argument(
        "address",
        metavar="<ADDRESS EXPRESSION>",
        nargs="+",
        action=UnsignedExpressionAction,
        help="Address expression to start dumping from. Can be decimal, hex, octal, binary or a complex expression.",
    )
    parser.add_argument(
        "-s",
        "--size",
        metavar="<SIZE EXPRESSION>",
        action=UnsignedExpressionAction,
        type=lambda s: shlex.split(s),
        required=True,
        help="Size of dump expression. Can be decimal, hex, octal, binary or a *quoted* complex expression.",
    )
    parser.add_argument("-f", "--file", required=True, help="File to dump into.")
    return parser


def dump_mem(debugger, command, result, internal_dict):
    parser = get_argparse_parser(debugger, result)
    args = parser.parse_args(shlex.split(command))
    if not result.Succeeded():
        return

    error_ref = lldb.SBError()
    process = debugger.GetSelectedTarget().GetProcess()
    memory = process.ReadMemory(args.address, args.size, error_ref)
    if error_ref.Success():
        try:
            with open(args.file, "wb") as dumpf:
                dumpf.write(memory)
                result.AppendMessage(f"Dumped {args.size:#0x} bytes from {args.address:#018x}")
                result.SetStatus(lldb.eReturnStatusSuccessFinishResult)
        except Exception as e:
            result.SetError(
                f"Failed writing memory dump of {args.size:#0x} bytes from address {args.address:#018x} to '{args.file}'.\nGot exception:\n{e}"
            )
            result.SetStatus(lldb.eReturnStatusFailed)
    else:
        result.SetError(error_ref)
        result.SetStatus(lldb.eReturnStatusFailed)
