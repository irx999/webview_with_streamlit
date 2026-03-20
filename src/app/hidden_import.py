import tkinter
from tkinter import filedialog

import photoshop
import PIL
import xlwings


def load_hidden_import():
    """加载隐藏的导入"""

    import_dict = {
        tkinter.__name__: tkinter.TkVersion,
        filedialog.__name__: tkinter.TkVersion,
        xlwings.__name__: xlwings.__version__,
        photoshop.__name__: "0.24.1",
        PIL.__name__: PIL.__version__,
    }

    return import_dict
