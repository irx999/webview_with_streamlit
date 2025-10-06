# WebView 应用

这是一个使用 Python、Streamlit 和 pywebview 创建的桌面应用程序示例。

## 功能

- 使用Streamlit作为前端框架
- 通过pywebview包装为桌面应用
- 包含基本的交互元素

## 安装

```bash
pip install -e .
```

要安装开发依赖（如 PyInstaller）:

```bash
pip install -e .[dev]
```

## 运行

```bash
python main.py
```

## 直接运行Streamlit应用

```bash
streamlit run app.py
```

## 打包为可执行文件（使用 PyInstaller）

```bash
pyinstaller --onefile --windowed main.py
```

## 文件结构

- `main.py`: 主程序文件，使用pywebview包装Streamlit应用
- `app.py`: Streamlit应用文件
- `pyproject.toml`: 项目配置和依赖
```

```
# webview

一个使用pywebview和Streamlit构建的桌面应用示例。

## 项目结构

- [main.py](file:///c%3A/Users/irx999/Desktop/git-rep/webview/main.py): 主程序，启动Streamlit服务器并使用pywebview显示
- [app.py](file:///c%3A/Users/irx999/Desktop/git-rep/webview/app.py): Streamlit应用程序

## 安装依赖

```bash
pip install -e .
```

## 运行应用

```bash
python [main.py](file:///c%3A/Users/irx999/Desktop/git-rep/webview/main.py)
```

## 打包应用

使用PyInstaller进行打包:

```bash
pyinstaller webview.spec
```

打包后的可执行文件将位于 `dist` 目录中。

注意: 由于应用通过subprocess启动Streamlit服务器，所以需要使用spec文件明确指定所有依赖项，以确保PyInstaller能正确打包所有必要的模块。

## 打包后运行

打包后的应用会自动处理Streamlit服务器的启动和停止，无需额外操作。可执行文件将包含所有必要的依赖项，可以在没有Python环境的机器上运行。




datas = [(r".venv\Lib\site-packages\streamlit\runtime","./streamlit/runtime")]
datas += collect_data_files("streamlit")
datas += copy_metadata("streamlit")


datas += [('./streamlit_app.py', '.')]

block_cipher = None
