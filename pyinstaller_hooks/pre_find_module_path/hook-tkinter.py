"""Keep the stdlib tkinter modules discoverable in this frozen build.

PyInstaller's default pre-find hook skips them when Tcl cannot initialize
during build-time probing. The build script bundles Tcl/Tk data and DLLs.
"""
import os
import sys


def pre_find_module_path(hook_api):
    hook_api.search_dirs = [os.path.join(sys.prefix, "Lib")]
