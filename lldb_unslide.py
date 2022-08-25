import argparse
import shlex

import lldb

# (lldb) unslide 0x1005b7d10
# 0x00000001005b7d10 => libfoo.dylib:0x3bd10 0x000000010003bd10		/Users/jevin/code/libfoo.dylib


def __lldb_init_module(debugger, internal_dict):
    debugger.HandleCommand("command script add -f lldb_unslide.unslide unslide")


def Address(n: str):
    return int(n, 0)


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


def unslide(debugger, command, result, internal_dict):
    parser = argparse.ArgumentParser(prog="unslide", description="unslide addresses")
    parser.add_argument("-v", "--verbose", action="store_true", help="verbose mode")
    parser.add_argument("addr", type=Address, nargs="+", help="address to unslide")

    args = parser.parse_args(shlex.split(command))

    tgt = debugger.GetSelectedTarget()

    for addr in args.addr:
        for mod in tgt.modules:
            low_faddr, offset = offset_in_module(tgt, mod, addr)
            if low_faddr is not None:
                faddr = low_faddr + offset
                result.AppendMessage(
                    f"{addr:#018x} => {mod.file.GetFilename()}:{offset:#x} {faddr:#018x}\t\t{mod.file.GetDirectory()}/{mod.file.GetFilename()}\n"
                )
                break
        else:
            result.AppendMessage(f"{addr:#018x} can't be resolved\n")

    return
