"""收集可选第三方模块的版本号，给侧边栏 Modules_Info 弹窗展示。

注意：本文件名叫 hidden_import 是历史遗留 —— 它并不向 PyInstaller 提供
hidden-import 提示，纯粹是给 UI 展示用。任意一个模块缺失或 import 失败都不
应阻止应用启动。
"""

from typing import Any, Callable


def _try_load(loader: Callable[[], tuple[str, Any]]) -> tuple[str, Any] | None:
    try:
        return loader()
    except Exception:
        return None


def _tkinter() -> tuple[str, Any]:
    import tkinter

    return tkinter.__name__, tkinter.TkVersion


def _filedialog() -> tuple[str, Any]:
    import tkinter
    from tkinter import filedialog

    return filedialog.__name__, tkinter.TkVersion


def _xlwings() -> tuple[str, Any]:
    import xlwings

    return xlwings.__name__, xlwings.__version__


def _photoshop() -> tuple[str, Any]:
    import photoshop

    return photoshop.__name__, getattr(photoshop, "__version__", "unknown")


def _pillow() -> tuple[str, Any]:
    import PIL

    return PIL.__name__, PIL.__version__


def _tinydb() -> tuple[str, Any]:
    import tinydb

    return tinydb.__name__, tinydb.__version__


def _openpyxl() -> tuple[str, Any]:
    import openpyxl

    return openpyxl.__name__, openpyxl.__version__


def _qrcode() -> tuple[str, Any]:
    """qrcode 包未导出 __version__，从 importlib.metadata 取。"""
    from importlib.metadata import version

    import qrcode  # noqa: F401  确认可导入

    return "qrcode", version("qrcode")


def _pywin32() -> tuple[str, Any]:
    """pywin32 没有 __version__；从 importlib.metadata 取分发包版本号。"""
    from importlib.metadata import version

    import win32print  # noqa: F401  确认本机的 pywin32 已正确安装

    return "pywin32", version("pywin32")


def load_hidden_import() -> dict[str, Any]:
    """逐个尝试加载，跳过 ImportError 等失败项。"""
    loaders = [
        _tkinter,
        _filedialog,
        _xlwings,
        _photoshop,
        _pillow,
        _tinydb,
        _openpyxl,
        _qrcode,
        _pywin32,
    ]
    result: dict[str, Any] = {}
    for loader in loaders:
        entry = _try_load(loader)
        if entry is not None:
            name, version = entry
            result[name] = version
    return result
