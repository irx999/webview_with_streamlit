"""Export options factory for creating different format export options"""

from typing import Any

from photoshop.api import (
    BMPSaveOptions,
    EPSSaveOptions,
    GIFSaveOptions,
    JPEGSaveOptions,
    PDFSaveOptions,
    PhotoshopSaveOptions,
    PNGSaveOptions,
    SolidColor,
    TargaSaveOptions,
    TiffSaveOptions,
)


class ExportOptionsFactory:
    """Factory class for creating export options based on file format"""

    @staticmethod
    def create_export_options(file_format: str) -> Any:
        """
        Create export options based on file format

        Args:
            file_format (str): The desired file format

        Returns:
            Export options object for the specified format

        Raises:
            ValueError: If the format is not supported
        """
        format_map = {
            "jpg": JPEGSaveOptions,
            "jpeg": JPEGSaveOptions,
            "png": PNGSaveOptions,
            "gif": GIFSaveOptions,
            "bmp": BMPSaveOptions,
            "eps": EPSSaveOptions,
            "pdf": PDFSaveOptions,
            "psd": PhotoshopSaveOptions,
            "tga": TargaSaveOptions,
            "tiff": TiffSaveOptions,
        }

        format_lower = file_format.lower()
        if format_lower in format_map:
            return format_map[format_lower]()
        raise ValueError(f"Unsupported file format: {file_format}")


class ColorFactory:
    """Factory class for creating color objects"""

    @staticmethod
    def rgb_to_hex(r, g, b):
        """
        将RGB颜色值转换为十六进制颜色值

        :param r: 红色值
        :param g: 绿色值
        :param b: 蓝色值
        :return: 16进制颜色值
        """
        return f"#{r:02x}{g:02x}{b:02x}"

    @staticmethod
    def hex_to_rgb(hex_color: str) -> SolidColor:
        """
        将十六进制颜色值转换为Photoshop的SolidColor对象

        :param hex_color: 16进制颜色值
        :return: photoshop的SolidColor对象
        """

        def hex_to_tuple(hex_color):
            hex_color = hex_color.lstrip("#")
            return tuple(int(hex_color[i : i + 2], 16) for i in (0, 2, 4))

        r, g, b = hex_to_tuple(hex_color)
        text_color = SolidColor()
        text_color.rgb.red = r
        text_color.rgb.green = g
        text_color.rgb.blue = b
        return text_color


class LayerOperationFactory:
    """Factory class for creating layer operations"""

    @staticmethod
    def create_visibility_operation(visible: bool) -> dict:
        """
        Create visibility operation

        Args:
            visible (bool): Visibility state

        Returns:
            dict: Operation dictionary
        """
        return {"visible": visible}

    @staticmethod
    def create_text_operation(contents=None, size=None, color=None) -> dict:
        """
        Create text operation

        Args:
            contents (str, optional): Text contents
            size (int, optional): Font size
            color (str, optional): Font color in hex

        Returns:
            dict: Operation dictionary
        """
        operation = {}
        text_item = {}

        if contents is not None:
            text_item["contents"] = contents
        if size is not None:
            text_item["size"] = int(size)
        if color is not None:
            text_item["color"] = color

        if text_item:
            operation["textItem"] = text_item

        return operation

    @staticmethod
    def create_move_operation(x: int, y: int) -> dict:
        """
        Create move operation

        Args:
            x (int): X coordinate
            y (int): Y coordinate

        Returns:
            dict: Operation dictionary
        """
        return {"move": (x, y)}

    @staticmethod
    def create_rotate_operation(angle: float) -> dict:
        """
        Create rotate operation

        Args:
            angle (float): Rotation angle in degrees

        Returns:
            dict: Operation dictionary
        """
        return {"rotate": angle}
