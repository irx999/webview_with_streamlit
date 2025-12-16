from dataclasses import dataclass

from src.utils import Config_reader

from .hidden_import import load_hidden_import

PYPROJECT = Config_reader(["pyproject.toml", "assets/pyproject.toml"])
LATESTINFO = Config_reader("assets/latest.json")
HIDDEN_IMPORT = load_hidden_import()


@dataclass
class App:
    name: str = PYPROJECT["project"]["name"]
    description: str = PYPROJECT["project"]["description"]
    version: str = PYPROJECT["project"]["version"]
    mtime: str = PYPROJECT.mtime
    # dependencies: str = str(PYPROJECT["project"]["dependencies"])
    latestinfo = LATESTINFO
    hidden_import = HIDDEN_IMPORT


@dataclass
class App_streamlit(App):
    """celery 配置"""

    name: str = "app_streamlit"
    host: str = "localhost"
    port: int = 38501
    base_url: str = f"http://{host}:{port}"


@dataclass
class App_fastapi(App):
    """fastapi 配置"""

    name: str = "app_fastapi"
    host: str = "localhost"
    port: int = 38502
    root_path: str = "/api/v1"
    base_url: str = f"http://{host}:{port}{root_path}"
