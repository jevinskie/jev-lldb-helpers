import os
import sys

# print("HELLO", file=sys.stderr)
# print(f"orig sys.path: {sys.path}", file=sys.stderr)

new_sys_path = []

for p in sys.path:
    if len(p) == 0:
        continue
    if "Python.framework/Versions/2." in p:
        continue
    if not os.path.exists(p):
        continue
    new_sys_path.append(p)


new_voltron_path = os.path.expanduser("~/.lldb/voltron")
if os.path.exists(new_voltron_path):
    new_sys_path.insert(1, new_voltron_path)


ver_major = sys.version_info.major
ver_minor = sys.version_info.minor

new_lib_py_site = os.path.join(
    sys.platlibdir, f"python{ver_major}.{ver_minor}", "site-packages"
)

new_py_sysroot = os.path.expanduser("~/.lldb/py-sysroot")
new_py_sysroot_site = os.path.join(new_py_sysroot, new_lib_py_site)
if os.path.exists(new_py_sysroot_site):
    new_sys_path.insert(1, new_py_sysroot_site)


# print(f"new_sys_path: {new_sys_path}", file=sys.stderr)

sys.path = new_sys_path

# print(f"new sys.path: {sys.path}", file=sys.stderr)
