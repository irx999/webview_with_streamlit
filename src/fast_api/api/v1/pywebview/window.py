import webview
from fastapi import APIRouter, Query

# 创建路由路由器
router = APIRouter(
    prefix="/pywebview/window",  # 为该路由器下所有路由添加前缀
    tags=["/pywebview/window"],  # 为该路由器下所有路由添加标签，便于文档分类
)


@router.get("/resize")
def resize_window(
    width: int = Query(800, ge=100, le=5000), height: int = Query(600, ge=100, le=5000)
):
    # global window

    window = webview.windows[0]

    if window is None:
        return {"error": "Window not initialized"}
    try:
        window.resize(width, height)
        return {"status": "success", "width": width, "height": height}
    except Exception as e:
        return {"error": str(e)}
