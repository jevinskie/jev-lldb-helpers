import argparse

import lldb


class UnsignedExpressionAction(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        if len(values) == 1:
            try:
                expr_unsigned = int(values[0], 0)
                if expr_unsigned < 0:
                    parser.lldb_result.SetError(f"{values[0]} is negative")
                    parser.lldb_result.SetStatus(lldb.eReturnStatusFailed)
                    setattr(namespace, self.dest, None)
                    return
                setattr(namespace, self.dest, expr_unsigned)
                return
            except ValueError:
                pass
        target = parser.lldb_debugger.GetSelectedTarget()
        expr_val = target.EvaluateExpression(" ".join(values))
        expr_unsigned = expr_val.GetValueAsUnsigned()
        setattr(namespace, self.dest, expr_unsigned)
