"""Ensure CustomTkinter theme assets are available under sys._MEIPASS at startup."""

import os
import shutil
import sys


def _ensure_customtkinter_assets() -> None:
    if not getattr(sys, 'frozen', False):
        return

    meipass = getattr(sys, '_MEIPASS', '')
    if not meipass:
        return

    expected_theme = os.path.join(meipass, 'customtkinter', 'assets', 'themes', 'blue.json')
    if os.path.isfile(expected_theme):
        return

    exe_dir = os.path.dirname(os.path.abspath(sys.executable))
    search_roots = [
        exe_dir,
        os.path.join(exe_dir, '_internal'),
    ]

    for root in search_roots:
        src = os.path.join(root, 'customtkinter')
        src_theme = os.path.join(src, 'assets', 'themes', 'blue.json')
        if not os.path.isfile(src_theme):
            continue

        dst = os.path.join(meipass, 'customtkinter')
        if os.path.isdir(dst):
            shutil.rmtree(dst)
        shutil.copytree(src, dst)
        return


_ensure_customtkinter_assets()
