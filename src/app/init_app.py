from src.utils.config_manager import ConfigManager

from .app_utils import ensure_shortcut_in_start_menu_and_desktop

app_config = ConfigManager("assets/config.json", "app_config")


def init():
    if not app_config.get("first_run_completed", False):
        ensure_shortcut_in_start_menu_and_desktop(create_desktop_shortcut=True)
        app_config.set("first_run_completed", True)
    else:
        ensure_shortcut_in_start_menu_and_desktop(create_desktop_shortcut=False)
