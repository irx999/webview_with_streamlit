from src.ui.utils import st_markdown
from src.utils import get_resource_path

if __name__ == "__main__":
    FILE_PATH = get_resource_path(["README.md", "assets/README.md"])

    with open(FILE_PATH, "r", encoding="utf-8") as f:
        readme_text = f.read()

        st_markdown(readme_text)
