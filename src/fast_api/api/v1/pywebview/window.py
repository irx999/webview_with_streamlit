import webview
from fastapi import APIRouter, Body, Query
from webview import Window

# 创建路由路由器
router = APIRouter(
    prefix="/pywebview/window",  # 为该路由器下所有路由添加前缀
    tags=["/pywebview/window"],  # 为该路由器下所有路由添加标签，便于文档分类
)


@router.get("/get")
async def resize_window_get(
    property: str = Query(),
):
    # global window
    try:
        window: Window = webview.windows[0]
        if window is None:
            return {"status": "error", "data": "Window not initialized"}

        if hasattr(window, property):
            # 直接返回属性值，保持原始类型（包括布尔值）
            value = getattr(window, property)
            return {"status": "success", "data": value}
        else:
            return {"status": "error", "data": "Property not found"}

    except Exception as e:
        return {"status": "error", "data": str(e)}


@router.post("/set")
async def resize_window_post(
    data: dict = Body(...),
):
    try:
        window: Window = webview.windows[0]
        if window is None:
            return {"status": "error", "data": "Window not initialized"}
        match data["func"]:
            case "resize":
                # 正确处理resize参数，从字典中提取width和height
                width = data.get("width")
                height = data.get("height")
                if width is not None and height is not None:
                    window.resize(width, height)
                else:
                    return {
                        "status": "error",
                        "data": "Missing width or height",
                    }

            case "toggle_fullscreen":
                window.toggle_fullscreen()
            case "on_top":
                window.on_top = not window.on_top
            case _:
                return {
                    "status": "error",
                    "data": f"Unknown function: {data['func']}",
                }
        return {"status": "success"}
    except Exception as e:
        return {"status": "error", "data": str(e)}
