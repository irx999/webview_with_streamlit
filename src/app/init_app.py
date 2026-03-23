from src.utils.config_manager import ConfigManager

from .app_utils import ensure_shortcut_in_start_menu_and_desktop

app_config = ConfigManager("assets/config.json", "app_config")


def first_run():
    ensure_shortcut_in_start_menu_and_desktop(create_desktop_shortcut=True)


def init():
    if not app_config.get("first_run_completed", False):
        first_run()
        app_config.set("first_run_completed", True)
