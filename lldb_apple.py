import argparse
import shlex

import lldb


def __lldb_init_module(debugger, internal_dict):
    debugger.HandleCommand("command script add -f lldb_apple.dyld_verbose dyld-verbose")


# macOS 14.3.1 23D60 dyld
dyld_print_vars = [
    "DYLD_PRINT_SEGMENTS",
    "DYLD_PRINT_LIBRARIES",
    "DYLD_PRINT_BINDINGS",
    "DYLD_PRINT_INITIALIZERS",
    "DYLD_PRINT_APIS",
    "DYLD_PRINT_NOTIFICATIONS",
    "DYLD_PRINT_INTERPOSING",
    "DYLD_PRINT_LOADERS",
    "DYLD_PRINT_SEARCHING",
    # "DYLD_PRINT_ENV",
    # "DYLD_PRINT_TO_STDERR",
    # "DYLD_PRINT_TO_FILE",
]


def dyld_verbose(debugger, command, result, internal_dict):
    parser = argparse.ArgumentParser(
        description="enable dyld verbose logging via env var", prog="dyld-verbose"
    )
    parser.parse_args(shlex.split(command))

    for v in dyld_print_vars:
        debugger.HandleCommand(f"env {v}=1")
    result.AppendMessage("Set DYLD_PRINT env vars")
    result.SetStatus(lldb.eReturnStatusSuccessFinishResult)
