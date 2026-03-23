import os
import sys
from pathlib import Path

# 全局变量用于持有锁文件对象/句柄，防止被垃圾回收
_single_instance_lock_file = None
_single_instance_lock_fd = None


def check_single_instance():
    """
    检查是否已有程序实例在运行。
    """
    global _single_instance_lock_file, _single_instance_lock_fd

    # 定义锁文件路径 (放在软件目录，避免权限问题)
    lock_filename = "webview_streamlit_app.lock"
    lock_path = Path(os.getcwd()) / lock_filename

    try:
        if os.name == "nt":  # Windows 系统
            # Windows 下使用 os.open 配合 O_EXCL 尝试独占创建
            # 如果文件存在，这会抛出 FileExistsError
            try:
                # 尝试以独占方式打开/创建文件
                # O_CREAT | O_EXCL | O_RDWR: 如果文件存在则失败，否则创建并以读写模式打开
                _single_instance_lock_fd = os.open(
                    str(lock_path), os.O_CREAT | os.O_EXCL | os.O_RDWR
                )

                # 写入当前进程 ID
                os.write(_single_instance_lock_fd, str(os.getpid()).encode())

                # 将文件描述符转换为文件对象以便后续操作（可选，主要用于保持引用）
                _single_instance_lock_file = os.fdopen(_single_instance_lock_fd, "r+")

            except FileExistsError:
                # 文件已存在，说明可能有其他实例在运行
                # 为了严谨，可以检查该文件是否真的被锁定，但简单场景下认为存在即占用
                print("检测到程序已在运行，当前实例将退出。")
                return False
                # sys.exit(0)

            # 注册退出时的清理函数
            import atexit

            def release_lock_windows():
                global _single_instance_lock_file, _single_instance_lock_fd
                try:
                    if _single_instance_lock_file:
                        _single_instance_lock_file.close()  # 这会关闭底层的 fd
                    elif _single_instance_lock_fd is not None:
                        os.close(_single_instance_lock_fd)

                    if lock_path.exists():
                        lock_path.unlink()
                except Exception:
                    pass

            atexit.register(release_lock_windows)
            return True

    except (IOError, OSError, PermissionError) as e:
        if _single_instance_lock_file:
            _single_instance_lock_file.close()
        if _single_instance_lock_fd is not None:
            try:
                os.close(_single_instance_lock_fd)
            except Exception:  # 忽略任何异常
                pass

        print(f"检测到程序已在运行或无法获取锁 ({e})，当前实例将退出。")
        return False
    except Exception as e:
        print(f"单例检查发生未知错误：{e}")
        # 出错时为了不阻断用户，选择继续运行
        return True


def ensure_shortcut_in_start_menu_and_desktop(create_desktop_shortcut: bool = True):
    """
    检测开始菜单中是否存在当前应用的快捷方式，如果不存在则创建。
    可选控制是否创建桌面快捷方式。
    注意：无论快捷方式是否存在，都会强制重新创建以覆盖可能失效的旧路径（应对程序目录移动）。

    :param create_desktop_shortcut: 是否创建桌面快捷方式，默认为 True
    依赖：pip install pywin32
    """
    import win32com.client

    try:
        shell = win32com.client.Dispatch("WScript.Shell")

        # 获取当前脚本或可执行文件的路径
        # 如果是打包后的 exe，sys.executable 是 exe 路径；如果是源码运行，则是 python 解释器路径 + 脚本参数
        if getattr(sys, "frozen", False):
            # 打包后的环境 (PyInstaller 等)
            app_path = sys.executable
            app_name = Path(app_path).stem
        else:
            # 非打包环境可能需要默认名称，防止未定义错误
            app_name = "WebViewStreamlitApp"
            app_path = sys.executable

        # 确定开始菜单的程序文件夹路径
        # CSIDL_PROGRAMS 对应的是当前用户的开始菜单 -> 程序
        start_menu_programs = shell.SpecialFolders("Programs")
        shortcut_dir = os.path.join(start_menu_programs, "WebViewStreamlitApp")
        shortcut_filename = f"{app_name}.lnk"

        # 修正：获取桌面路径
        desktop_path = shell.SpecialFolders("Desktop")

        # 修正变量命名：原代码此处赋值的是桌面路径，但变量名叫 start_menu_shortcut_path，容易混淆
        desktop_shortcut_path = os.path.join(desktop_path, shortcut_filename)
        start_menu_shortcut_path = os.path.join(shortcut_dir, shortcut_filename)

        # 确保目录存在
        if not os.path.exists(shortcut_dir):
            os.makedirs(shortcut_dir)

        # 修改逻辑：不再检查是否存在，直接强制创建/覆盖，以应对程序目录移动导致的路径失效
        create_start_menu = True

        # 创建开始菜单快捷方式 (强制覆盖)
        if create_start_menu:
            start_menu_shortcut = shell.CreateShortCut(start_menu_shortcut_path)
            if getattr(sys, "frozen", False):
                start_menu_shortcut.Targetpath = app_path
                start_menu_shortcut.WorkingDirectory = os.path.dirname(app_path)
            start_menu_shortcut.IconLocation = app_path  # 使用自身图标
            start_menu_shortcut.Description = "Launch WebView with Streamlit"
            start_menu_shortcut.save()
            print(f"开始菜单快捷方式已更新：{start_menu_shortcut_path}")

        # 控制桌面快捷方式的创建 (如果开启，也强制覆盖)
        if create_desktop_shortcut:
            desktop_shortcut = shell.CreateShortCut(desktop_shortcut_path)
            if getattr(sys, "frozen", False):
                desktop_shortcut.Targetpath = app_path
                desktop_shortcut.WorkingDirectory = os.path.dirname(app_path)
            desktop_shortcut.IconLocation = app_path  # 使用自身图标
            desktop_shortcut.Description = "Launch WebView with Streamlit (Desktop)"
            desktop_shortcut.save()
            print(f"桌面快捷方式已更新：{desktop_shortcut_path}")
        else:
            # 如果明确不创建桌面快捷方式，且存在旧的，可以选择删除以避免误导，这里选择保留但不更新
            # 若需删除可取消下面注释：
            # if os.path.exists(desktop_shortcut_path):
            #     os.remove(desktop_shortcut_path)
            pass

        return (
            start_menu_shortcut_path,
            desktop_shortcut_path,
        )
    except Exception as e:
        print(f"创建快捷方式时发生错误：{e}")
