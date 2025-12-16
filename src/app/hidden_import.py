import tkinter
from tkinter import filedialog

import photoshop
import PIL
import xlwings
from loguru import logger

# logger.add("logs/app.log", format="{time} {level} {message}")


def load_hidden_import():
    logger.info("load_hidden_import")

    import_dict = {
        tkinter.__name__: tkinter.TkVersion,
        filedialog.__name__: "8.6",
        xlwings.__name__: xlwings.__version__,
        photoshop.__name__: "0.24.1",
        PIL.__name__: PIL.__version__,
    }

    for name, version in import_dict.items():
        logger.info(f"{name}: {version}")
    return import_dict
