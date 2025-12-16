import tkinter
from tkinter import filedialog

import xlwings
from loguru import logger

# logger.add("logs/app.log", format="{time} {level} {message}")


def load_hidden_import():
    logger.info("load_hidden_import")
    logger.info(f"xlwings -> {xlwings.__version__}")
    logger.info(f"tkinter -> {tkinter.TkVersion}")
    logger.info(f"filedialog -> {filedialog.__name__}")
    import_dict = {
        "xlwings": xlwings.__version__,
        "tkinter": tkinter.TkVersion,
    }
    return import_dict
