import json
import os


class AppInfo:
    @staticmethod
    def get_latest_info() -> dict[str, str | dict[str, dict[str, str]]]:
        if os.path.exists("./assets/latest.json"):
            with open("./assets/latest.json", "r", encoding="utf-8") as file:
                data = json.load(file)
            return data
        else:
            return {
                "name": "My_App",
                "version": "None",
                "pub_date": "2099-12-31 24:59:59",
                "platforms": {"windows-x86_64": {"signature": "", "url": ""}},
            }
