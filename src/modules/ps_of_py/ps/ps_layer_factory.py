"""图层工厂"""

import time

from loguru import logger
from photoshop import Session
from photoshop.api._artlayer import ArtLayer
from photoshop.api._layerSet import LayerSet

from .ps_utils import ColorFactory

logger.add("./logs/LayerFactory.log", rotation="1 MB")


class LayerFactory:
    """工厂类：创建和管理图层状态"""

    def __init__(self, ps_session: Session):
        self.ps_session = ps_session

        self.layer_dict = {}  # 图层列表
        self.initial_state = {}  # 初始状态
        self.current_state = {}  # 当前状态

        self.run_time_record: dict = {}  # 运行时间记录

    def get_all_layers(self) -> list[LayerSet | ArtLayer]:
        """获取所有图层
        :return: 图层信息
        """
        layers = []
        layers.append(
            {"TOP": [layer.name for layer in self.ps_session.active_document.artLayers]}
        )

        # 构建图层集及其子图层的详细信息
        for layer_set in self.ps_session.active_document.layerSets:
            layers_in_set = [layer.name for layer in layer_set.artLayers] + [
                layer.name for layer in layer_set.layerSets
            ]
            layers.append(f"{layer_set.name}: {layers_in_set}")

        return layers

    def get_layer_by_layername(self, layername: str) -> list[LayerSet | ArtLayer]:
        """根据层名获取图层

        :return layer_list: 图层名称
        """

        if layername in self.layer_dict:
            # 如果层名在图层列表中，则直接返回
            return self.layer_dict[layername]

        layer_path = layername.split("/")
        final_name = layer_path[-1]
        copy_name = f"{final_name} 拷贝"
        change_layer_list = []

        # 根路径
        root_path = self.ps_session.active_document
        # 循环找到最后一个节点
        for layer_item in layer_path[:-1]:
            try:
                current_layer = root_path.layerSets.getByName(layer_item)
            except Exception:
                logger.error(f"未找到图层集 '{layer_item}' 在路径 {layer_path}")
                break
        else:
            layerSets_list = [layerSet.name for layerSet in current_layer.layerSets]
            artLayers_list = [artLayer.name for artLayer in current_layer.artLayers]
            # 优先查找图层集
            if final_name in layerSets_list:
                target_layer = current_layer.layerSets.getByName(final_name)
                change_layer_list.append(target_layer)
                if copy_name in layerSets_list:
                    target_layer = current_layer.layerSets.getByName(copy_name)
                    change_layer_list.append(target_layer)
            # 再查找图层
            elif final_name in artLayers_list:
                target_layer = current_layer.artLayers.getByName(final_name)
                change_layer_list.append(target_layer)
                if copy_name in artLayers_list:
                    target_layer = current_layer.artLayers.getByName(copy_name)
                    change_layer_list.append(target_layer)

            else:
                logger.error(f"未找到图层 '{final_name}' 在路径 {layer_path}")

        self.layer_dict[layername] = change_layer_list
        return change_layer_list

    def change_layer_state(self, layer_name: str, change_state: dict):
        """修改图层状态
        :param layer_name: 图层名称
        :param layerinfo: 图层信息
        """
        layer_list = self.get_layer_by_layername(layer_name)
        for layer in layer_list:
            # 修改图层状态
            self._change_layer_state(layer, change_state)
            # 保存当前状态
            self.current_state[layer_name] = change_state

    def save_initial_layer_state(self, layername: str, layerinfo: dict):
        """保存图层状态

        :param layer_name: 图层名称
        :param layerinfo: 图层信息
        """
        if layername not in self.initial_state:
            target_layers = self.get_layer_by_layername(layername)
            for target_layer in target_layers:
                # 使用工厂创建初始状态
                state = self._create_layer_state(target_layer, layerinfo)

                # 同时保存初始状态和当前状态
                self.initial_state[layername] = state.copy()
                self.current_state[layername] = state.copy()

                logger.info(f"保存初始状态成功: {layername=}, {state=}")

    def restore_text_item_to_initial(self, layer_name: str):
        """将指定图层的文本属性恢复到初始状态

        :param layer_name: 图层名称
        """
        initial_state = self.initial_state.get(layer_name, {})
        if "textItem" in initial_state:
            self.change_layer_state(layer_name, initial_state)
            logger.info(f"图层 {layer_name} 的文本属性已恢复到初始状态")

    def restore_all_layers_to_initial(self):
        """恢复所有图层的状态为初始状态"""
        for layer_name, layer_info in self.initial_state.items():
            self.change_layer_state(layer_name, layer_info)

    def _create_layer_state(self, layer: LayerSet | ArtLayer, layer_info: dict) -> dict:
        """
        记录图层状态信息

        :param layer: 图层对象
        :param layer_info: 图层信息
        :return: 初始状态字典
        """
        state = {}
        if "visible" in layer_info:
            state["visible"] = layer.visible
        if "move" in layer_info:
            state["move"] = (layer.bounds[0], layer.bounds[1])  # type: ignore #
        if "textItem" in layer_info:
            state["textItem"] = {}
            text_item = layer.textItem
            state["textItem"]["contents"] = text_item.contents
            state["textItem"]["size"] = text_item.size
            state["textItem"]["font"] = text_item.font
            state["textItem"]["strikeThru"] = text_item.strikeThru.value
            font_color = text_item.color.rgb
            # 将RGB颜色转换为十六进制
            state["textItem"]["color"] = ColorFactory.rgb_to_hex(
                font_color.red, font_color.green, font_color.blue
            )
        return state

    def _change_layer_state(self, layer: LayerSet | ArtLayer, change_state: dict):
        """
        修改图层状态

        :param layer_key: 图层名称
        :param change_state: 初始状态
        :return: 修改结果
        """
        start_time = time.time()

        # if "visible" in change_state and (layer is LayerSet or layer is ArtLayer):
        if "visible" in change_state:
            layer.visible = change_state["visible"]
        else:
            logger.debug("这里没有被触发")
        # 修改旋转角度
        if "move" in change_state:
            x = layer.bounds[0]  # type: ignore
            y = layer.bounds[1]  # type: ignore
            layer.translate(change_state["move"][0] - x, change_state["move"][1] - y)
        # 修改旋转角度
        if "rotate" in change_state:
            layer.rotate(change_state["rotate"])
        # 如果是文本图层，修改文本属性
        if "textItem" in change_state:
            text_item_state = change_state["textItem"]
            for key, attr_name in text_item_state.items():
                # 如果是颜色，则将十六进制颜色转换为RGB颜色
                if key == "color":
                    attr_name = ColorFactory.hex_to_rgb(attr_name)
                # 如果是内容，则转换为字符串
                if key == "contents":
                    attr_name = str(attr_name)
                setattr(layer.textItem, key, attr_name)

        self.run_time_record[layer.name + str(change_state)] = round(
            time.time() - start_time, 2
        )
