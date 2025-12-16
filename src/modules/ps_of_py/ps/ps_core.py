"""This is a python script for photoshop"""

import os
import time

from loguru import logger
from photoshop import Session
from photoshop.api import Application

from .ps_layer_factory import LayerFactory
from .ps_utils import ExportOptionsFactory

logger.add("./logs/Photoshop.log", rotation="1 MB")


class Photoshop:
    """Photoshop操作类"""

    def __init__(
        self,
        psd_name: str,
        psd_dir_path: str = "psd",
        export_folder: str = "default_export_folder",
        file_format: str = "png",
        suffix: str = "",
        colse_ps: bool = False,
    ):
        """
        初始化Photoshop类

        :param psd_name: psd文件名
        :param psd_dir_path: psd文件路径,默认工作目录下的psd文件夹
        :param export_folder: 导出文件夹名,是在默认工作目录下创建
        :param file_format: 导出文件格式，默认为png
        :param colse_ps: 是否在core结束时关闭photoshop
        """
        self.psd_name = psd_name
        self.psd_dir_path = psd_dir_path
        self.export_folder = self._create_export_folder(export_folder)
        self.file_format = file_format.lower()
        self.suffix = suffix
        self.colse_ps = colse_ps
        logger.info(
            f"初始化Photoshop类成功,{
                (
                    self.psd_name,
                    self.psd_dir_path,
                    self.export_folder,
                    self.file_format,
                    self.suffix,
                    self.colse_ps,
                )
            }"
        )

    def __enter__(self):
        """初始化Photoshop会话"""
        self.app = Application()

        return self._init_ps_session()

    def __exit__(self, exc_type, exc_val, exc_tb):
        """关闭Photoshop会话"""
        self.layer_factory.restore_all_layers_to_initial()
        if self.colse_ps:
            self.doc.close()

    def _init_ps_session(self):
        """初始化Photoshop会话"""
        try:
            self.psd_file_path = self._get_psd_file_path()
            with Session(file_path=self.psd_file_path, action="open") as ps_session:
                self.ps_session = ps_session
                self.doc = ps_session.active_document

                # 使用工厂创建导出选项
                self.saveoptions = ExportOptionsFactory.create_export_options(
                    self.file_format
                )

            self.layer_factory = LayerFactory(ps_session)

            self.run_time_record: dict = {}  # 运行时间记录
        except Exception as e:
            logger.error(f"初始化Photoshop会话失败: {e}")
            raise Exception(f"初始化Photoshop会话失败: {e}")

    def _get_psd_file_path(self) -> str | None:
        """
        获取PSD文件路径

        :return: PSD文件完整路径
        """
        try:
            # 如果传入的是绝对路径
            if not os.path.isabs(self.psd_dir_path):
                base_path = os.path.join(os.getcwd(), self.psd_dir_path)
            else:
                base_path = self.psd_dir_path
            file_path = os.path.join(base_path, f"{self.psd_name}")
            if os.path.isfile(file_path):
                return file_path
            raise FileNotFoundError(f"找不到PSD文件: {self.psd_name}")

        except Exception as e:
            logger.error(f"获取PSD文件路径失败: {e}")
            raise FileNotFoundError(f"找不到PSD文件: {self.psd_name}")

    def _create_export_folder_1(self, export_folder: str) -> str:
        """
        创建导出文件夹

        :param export_folder: 导出文件夹名
        :return: 导出文件夹完整路径
        """
        try:
            full_path = os.path.join(os.getcwd(), export_folder)
            if not os.path.exists(full_path):
                os.makedirs(full_path)
                logger.warning(f"创建文件夹 {full_path} 成功")
            return full_path

        except Exception as e:
            raise FileNotFoundError(f"创建文件夹 {full_path} 失败: {e}")

    def _create_export_folder(self, export_folder: str | None) -> str:
        """返回导出文件夹路径"""
        try:
            if not export_folder or export_folder.strip() == "":
                export_folder = "default_export_folder"

            full_path = os.path.join(os.getcwd(), export_folder)

            if not os.path.exists(full_path):
                os.makedirs(full_path)
                logger.info(f"创建文件夹 {full_path} 成功")

            return full_path

        except Exception as e:
            logger.error(f"创建文件夹 {export_folder} 失败: {e}")
            return ""

    def get_psd_info(self) -> dict:
        """返回当前psd文件信息"""
        with self:
            return {
                "name": self.ps_session.active_document.name,
                "psd_file_path": self.psd_file_path,
                "psd_size": f"width: {self.doc.width:.0f}, height: {self.doc.height:.0f}",
                "all_layer": self.layer_factory.get_all_layers(),
            }

    def ps_saveas(self, export_name: str):
        """保存文件到指定路径"""

        export_name_list = export_name.split("|")
        export_path = "/".join(export_name_list)
        try:
            if len(export_name_list) > 1:
                os.makedirs(
                    self.export_folder + "/" + export_name_list[0], exist_ok=True
                )
                logger.debug(
                    f"创建文件夹 {self.export_folder + '/' + export_name_list[0]} 成功"
                )
        except Exception as e:
            logger.error(f"创建文件夹 {self.export_folder} 失败: {e}")
        try:
            path = f"{self.export_folder}/{export_path}{self.suffix}.{self.file_format}"
            self.doc.saveAs(
                path,
                self.saveoptions,
                asCopy=True,
            )
            logger.info(f"导出{path}成功")
        except Exception as e:
            logger.error(f"导出{path}失败")
            raise Exception(f"保存文件到指定路径失败: {e}")

    def core(self, export_name: str, input_data: dict):
        """
        核心处理函数

        :param export_name: 导出文件名
        :param input_data: 输入数据，包含需要修改的图层属性
        """
        start_time = time.time()

        # 1.查找已经修改但接下来不需要修改的图层，需要恢复的图层
        current_all_initialized = set(self.layer_factory.current_state.keys())
        for layer_to_restore in current_all_initialized - input_data.keys():
            initial_state = self.layer_factory.initial_state.get(layer_to_restore, {})
            if not initial_state:
                continue
            logger.info(f"正在恢复图层 {layer_to_restore} 到初始状态")
            self.layer_factory.change_layer_state(layer_to_restore, initial_state)

            del self.layer_factory.initial_state[layer_to_restore]

        # 2. 执行任务之前看是否修改的属性需要记录修改前状态
        for layer_name, change_state in input_data.items():
            if layer_name not in self.layer_factory.initial_state:
                logger.debug(f"图层 {layer_name} 需要记录初始状态")
                if "visible" in change_state.keys():
                    logger.debug(f"图层 {layer_name} 的初始状态已保存")
                    self.layer_factory.save_initial_layer_state(
                        layer_name, change_state
                    )
                elif "textItem" in change_state.keys():
                    if any(
                        change_state["textItem"].get(key) for key in ["size", "color"]
                    ):
                        self.layer_factory.save_initial_layer_state(
                            layer_name, change_state
                        )

            current_state = self.layer_factory.current_state.get(layer_name, {})
            if current_state == {}:
                logger.warning(f"图层 {layer_name} 的初始属性不存在")

            # 增加对move属性的检查
            if "move" in current_state:
                current_move = current_state["move"]
                new_move = change_state.get("move", None)
                # 如果之前修改过位置或旋转，但这次不需要修改
                if current_move is not None and new_move is None:
                    logger.info(f"图层 {layer_name} 需要先恢复位置到初始状态")
                    self.layer_factory.change_layer_state(
                        layer_name,
                        self.layer_factory.initial_state.get(layer_name, {}),
                    )

            # 增加对textItem属性的检查
            if "textItem" in current_state and "textItem" in change_state:
                current_text_item = current_state["textItem"]
                new_text_item = change_state["textItem"]

                # 如果之前修改过字体   大小颜色,删除线，但这次不需要修改
                text_properties = ["size", "color", "strikeThru"]
                needs_restore = any(
                    current_text_item.get(prop) is not None
                    and prop not in new_text_item
                    for prop in text_properties
                )
                if needs_restore:
                    logger.info(f"图层 {layer_name} 需要先恢复字体大小和颜色到初始状态")
                    self.layer_factory.restore_text_item_to_initial(layer_name)
                    logger.info(f"图层 {layer_name} 需要先恢复字体大小和颜色到初始状态")
                    self.layer_factory.restore_text_item_to_initial(layer_name)

            # 3. 判断是否需要真正修改
            if current_state != change_state:
                logger.info(
                    f"图层 {layer_name} 状态不一致需要修改\n修改前: {current_state}\n修改后: {change_state}"
                )
                # 4. 执行修改
                self.layer_factory.change_layer_state(layer_name, change_state)
            else:
                logger.info(f"图层 {layer_name} 状态一致，无需修改")

        # 5. 导出文件
        self.ps_saveas(export_name)

        # 6. 记录运行时间
        self.run_time_record[export_name] = round(time.time() - start_time, 2)
