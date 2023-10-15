import argparse
import shlex

import lldb

from unsigned_expr_action import UnsignedExpressionAction


def __lldb_init_module(debugger, internal_dict):
    debugger.HandleCommand("command script add -f lldb_unslide.unslide unslide")


def offset_in_module(tgt, mod, addr):
    low_faddr = 0x1_0000_0000_0000_0000
    low_laddr = low_faddr
    contained = False
    for sec in mod.sections:
        faddr = sec.addr.GetFileAddress()
        laddr = sec.addr.GetLoadAddress(tgt)
        if laddr <= addr <= laddr + sec.GetByteSize():
            contained = True
        if faddr == 0:
            continue
        low_faddr = min(faddr, low_faddr)
        low_laddr = min(laddr, low_laddr)
    if contained:
        return low_faddr, addr - low_laddr
    return None, None


def copy_to_clipboard(val: str, result):
    try:
        import pyperclip

        pyperclip.copy(val)
    except ImportError:
        result.AppendWarning(
            "pyperclip is not installed! Install with `xcrun pip3 install -U pyperclip`"
        )


def get_argparse_parser(debugger, result):
    class CustomHelpFormatter(argparse.RawDescriptionHelpFormatter):
        def _format_args(self, action, default_metavar):
            if action.dest == "address":
                return self._metavar_formatter(action, None)(1)[0]
            else:
                return super(CustomHelpFormatter, self)._format_args(action, default_metavar)

    parser = argparse.ArgumentParser(
        prog="unslide",
        description="""\
unslide address(es)

Example:

(lldb) unslide 0x1005b7d10
0x00000001005b7d10 => libfoo.dylib:0x3bd10 0x000000010003bd10\t\t/Users/jevin/code/libfoo.dylib\
""",
        formatter_class=CustomHelpFormatter,
    )
    parser.lldb_debugger = debugger
    parser.lldb_result = result
    parser.add_argument(
        "-c", "--copy", action="store_true", help="Copy unslid address to clipboard"
    )
    parser.add_argument(
        "address",
        metavar="<ADDRESS EXPRESSION>",
        nargs="+",
        action=UnsignedExpressionAction,
        help="Address expression to start dumping from. Can be decimal, hex, octal, binary or a complex expression.",
    )
    return parser


def unslide(debugger, command, result, internal_dict):
    parser = get_argparse_parser(debugger, result)
    args = parser.parse_args(shlex.split(command))
    if not result.Succeeded():
        return

    target = debugger.GetSelectedTarget()
    for mod in target.modules:
        low_faddr, offset = offset_in_module(target, mod, args.address)
        if low_faddr is not None:
            faddr = low_faddr + offset
            result.AppendMessage(
                f"{args.address:#018x} => {mod.file.GetFilename()}:{offset:#x} {faddr:#018x}\t\t{mod.file.GetDirectory()}/{mod.file.GetFilename()}\n"
            )
            if args.copy:
                copy_to_clipboard(f"{faddr:#018x}", result)
            result.SetStatus(lldb.eReturnStatusSuccessFinishResult)
            break
    else:
        result.SetError(f"{args.address:#018x} can't be resolved\n")
        result.SetStatus(lldb.eReturnStatusFailed)
