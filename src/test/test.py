import xlwings as xw


def get_active():
    return xw.books.active.name


def get_range():
    return xw.books.active.api.Application.Selection.Value
