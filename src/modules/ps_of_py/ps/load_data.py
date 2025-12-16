"""本模块包含用于加载和预处理数据的函数"""

from itertools import zip_longest
from typing import Any, Dict, List

import xlwings as xw


class LoadData:
    """该类用于加载和预处理数据"""

    def __init__(self, sheet_name: str = None, table_name: str | int = 0):
        """
        初始化LoadData类
        :param sheet_name: 工作表名称
        :param table_name: 表格名称或索引
        """
        try:
            if sheet_name:
                self.sheet = xw.books.active.sheets[sheet_name]
            else:
                self.sheet = xw.sheets.active
            # 读取表格
            self.table = self.sheet.tables[table_name]
            # 读取表格的表头
            self.table_header = self.table.header_row_range.value
            # 读取表格中的数据
            self.table_values = self.table.data_body_range.value
            # 读取当前选择的单元格
            self.selected_ranges: str | list[str] = (
                self.sheet.api.Application.Selection.Value
            )
            # 读取表格中写入的导出配置信息
            self.settings = self.read_settings()
        except OSError as e:
            print(f"无法读取您的表格,请检查您的excel文件\n{e}")

    def read_settings(self) -> dict:
        """读取导出配置信息"""
        try:
            if self.sheet.range("colse_ps").value == "是":
                colse_ps = True
            else:
                colse_ps = False
        except Exception:
            colse_ps = True

        try:
            settings: dict = {
                "psd_name": self.sheet.range("psd_name").value,
                "psd_dir_path": self.sheet.range("psd_file_path").value,
                "export_folder": self.sheet.range("export_folder").value,
                "file_format": self.sheet.range("file_format").value,
                "suffix": self.sheet.range("suffix").value,
                "colse_ps": colse_ps,
            }
        except ValueError as e:
            print(f"无法读取到表格中的配置信息,将使用默认配置\n{e}")
            settings: dict = {
                "psd_name": None,
                "psd_file_path": None,
                "export_folder": "默认名称",
                "file_format": "png",
                "suffix": "",
                "colse_ps": False,
            }
        return settings

    def read_range(self) -> List[Dict[str, Any]]:
        """读取表格数据并返回列表"""
        result_list = []

        for row in self.table_values:
            row_dict = {
                k: v for k, v in zip_longest(self.table_header, row, fillvalue=None)
            }
            result_list.append(row_dict)
        return result_list

    def filter_data(
        self, input_data: List[Dict[str, Any]]
    ) -> Dict[str, Dict[str, Any]]:
        """过滤数据，构造图层修改指令"""
        result_dict = {}
        for row_dict in input_data:
            # 创建一个所有图层的字典
            layer_dict = {
                "其他信息": {},
                "修改信息": {},
            }
            for header in row_dict.keys():
                if row_dict[header] is not None:
                    # 创建单个图层的字典
                    layer_info = {}
                    # 匹配标题属性
                    header_parts = header.split("|")
                    match header_parts:
                        # 匹配修改文本图层属性
                        case ["文本", *layer_list]:
                            layer_info["图层路径"] = layer_list

                            layer_info["textItem"] = {}
                            cell_value_parts = str(row_dict[header]).split("|")
                            match cell_value_parts:
                                case [
                                    str(text),
                                    str(font_size),
                                    str(font_color),
                                    str(strikeThru),
                                ]:
                                    layer_info["textItem"]["contents"] = text
                                    if font_size != "":
                                        layer_info["textItem"]["size"] = int(font_size)
                                    if font_color != "":
                                        layer_info["textItem"]["color"] = font_color
                                    if strikeThru != "":
                                        layer_info["textItem"]["strikeThru"] = int(
                                            strikeThru
                                        )
                                case [str(text), str(font_size), str(font_color)]:
                                    layer_info["textItem"]["contents"] = text
                                    layer_info["textItem"]["size"] = int(font_size)
                                    layer_info["textItem"]["color"] = font_color
                                case [str(text), str(font_size)]:
                                    layer_info["textItem"]["contents"] = text
                                    layer_info["textItem"]["size"] = int(font_size)
                                case _:
                                    layer_info["textItem"]["contents"] = row_dict[
                                        header
                                    ]

                        # 匹配表头中修改可显性图层属性
                        case ["可显性", *layer_list]:
                            if layer_list[0] == "":
                                layer_info["图层路径"] = []
                            # 这里如果两个图层组需要操作两次的话, 就会在表格中重复, excel 会自动多一个复制处理
                            elif layer_list[-1] in [str(i) for i in range(1, 11)]:
                                layer_info["图层路径"] = layer_list[:-1]
                            elif layer_list[-1] == "":
                                layer_info["图层路径"] = layer_list[0:1]
                            else:
                                layer_info["图层路径"] = layer_list
                            # 匹配单元格内容
                            cell_value_parts = row_dict[header].split("|")
                            match cell_value_parts:
                                # 如果是T或F, 则直接设置visible属性
                                case [str(layer_name), "T"]:
                                    layer_info["图层路径"].append(layer_name)
                                    layer_info["visible"] = True
                                case [str(layer_name), "F"]:
                                    layer_info["图层路径"].append(layer_name)
                                    layer_info["visible"] = False
                                # 如果没有, 默认为True
                                case _:
                                    layer_info["图层路径"].append(row_dict[header])
                                    layer_info["visible"] = True

                        # 匹配其他信息
                        case _:
                            layer_dict["其他信息"][header] = row_dict[header]
                            pass

                            # layer_info["其他信息"] = []
                            # layer_info["其他信息"].append(row_dict[header])

                    if layer_info:
                        full_path = "/".join(layer_info["图层路径"])
                        del layer_info["图层路径"]
                        layer_dict["修改信息"][full_path] = layer_info
            result_dict[row_dict["导出文件名"]] = layer_dict
        return result_dict

    def selected_skus(self) -> List[Dict[str, Any]]:
        """返回选中的SKUs"""
        processed_data = self.filter_data(self.read_range())
        result: List[Dict[str, Any]] = []
        # 如果没有选择SKU, 则返回空列表
        if self.selected_ranges:
            if isinstance(self.selected_ranges, tuple):
                sku_list = [i[0] for i in self.selected_ranges if i is not None]
            else:
                sku_list = [self.selected_ranges]
            for filename, content in processed_data.items():
                if filename in sku_list:
                    result.append(
                        {
                            "任务名": str(filename).replace(".0", ""),
                            "其他信息": content["其他信息"],
                            "修改信息": content["修改信息"],
                        }
                    )
        return result


if __name__ == "__main__":
    ld = LoadData()
    ans = ld.selected_skus()
    print(ans)
