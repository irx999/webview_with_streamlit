import argparse
import datetime
import json
import os
import shutil
import sys
import time

import toml

# 尝试导入 PyInstaller，若失败则在运行时处理
try:
    import PyInstaller.__main__
except ImportError:
    PyInstaller = None


def _is_dir_not_empty(dir_path: str) -> bool:
    """检查目录是否存在且非空。"""
    return os.path.isdir(dir_path) and len(os.listdir(dir_path)) != 0


def _safe_remove_directory(dir_path: str, non_interactive: bool) -> bool:
    """
    安全删除目录。

    :param dir_path: 目录路径
    :param non_interactive: 是否非交互模式（直接删除不询问）
    :return: 是否成功删除或无需删除
    """
    if not _is_dir_not_empty(dir_path):
        return True

    if non_interactive:
        shutil.rmtree(dir_path, ignore_errors=True)
        return True

    dir_name = os.path.basename(dir_path)
    response = input(f'是否删除 "{dir_name}" 目录？(y/n): ').lower()
    if response != "n":
        shutil.rmtree(dir_path, ignore_errors=True)
        return True
    else:
        print(f'操作取消："{dir_name}" 目录必须为空才能继续。')
        return False


def _delete_build_artifacts(name: str) -> None:
    """删除构建产生的临时文件 (build 目录和 .spec 文件)。"""
    print("\n正在清理构建临时文件 (build & spec)...")
    try:
        shutil.rmtree("build", ignore_errors=True)
        spec_file = f"{name}.spec"
        if os.path.exists(spec_file):
            os.remove(spec_file)
        print("✅ 临时文件清理完成。")
    except Exception as e:
        print(f"❌ 清理失败：{e}")


def _generate_version_info(dist_path: str, name: str, version: str) -> None:
    """生成最新版本信息文件 (latest.json)。"""
    print(f"\n正在生成版本信息 -> {dist_path}/latest.json")
    try:
        now = datetime.datetime.now()
        # 版本号格式：主版本 + auto_build.月日时分
        auto_version = (
            f"{version}+auto_build.{now.month}{now.day}{now.hour}{now.minute}"
        )

        info = {
            "name": name,
            "version": auto_version,
            "pub_date": now.strftime("%Y-%m-%d %H:%M:%S"),
            "download_url": "",
            "update_info": "This is an auto build version",
        }

        os.makedirs(dist_path, exist_ok=True)
        with open(os.path.join(dist_path, "latest.json"), "w", encoding="utf-8") as f:
            json.dump(info, f, indent=4, ensure_ascii=False)
        print("✅ 版本信息生成成功。")
    except Exception as e:
        print(f"❌ 生成版本信息失败：{e}")


def _copy_assets_to_dist(pack_path: str, dist_path: str) -> None:
    """将资源文件复制到打包目录。"""
    print("\n正在复制资源文件到发布目录...")
    try:
        # 复制 assets 目录
        if os.path.exists("assets"):
            shutil.copytree(
                "assets", os.path.join(pack_path, "assets"), dirs_exist_ok=True
            )

        # 复制 latest.json 到 assets
        latest_json_src = os.path.join(dist_path, "latest.json")
        latest_json_dst = os.path.join(pack_path, "assets", "latest.json")
        if os.path.exists(latest_json_src):
            shutil.copy2(latest_json_src, latest_json_dst)

        # 复制根目录文档
        root_files = ["README.md", "CHANGELOG.md", "pyproject.toml"]
        for file_name in root_files:
            if os.path.exists(file_name):
                shutil.copy2(file_name, os.path.join(pack_path, "assets"))

        print("✅ 资源文件复制完成。")
    except Exception as e:
        print(f"❌ 资源文件复制失败：{e}")


def _compress_distribution(dist_path: str, name: str, version: str) -> None:
    """压缩发布目录为 ZIP 文件。"""
    base_name = os.path.join(dist_path, f"{name}-{version}")
    source_dir = os.path.join(dist_path, name)

    print(f"\n正在压缩发布包 -> {base_name}.zip")
    try:
        if not os.path.exists(source_dir):
            raise FileNotFoundError(f"源目录不存在：{source_dir}")

        archive_path = shutil.make_archive(base_name, "zip", root_dir=source_dir)
        file_size = os.path.getsize(archive_path)
        print(f"✅ 压缩成功：{file_size / (1024 * 1024):.2f} MB")
    except Exception as e:
        print(f"❌ 压缩失败：{e}")


class AutoBuildMainApp:
    """主应用程序自动构建类。"""

    @staticmethod
    def build(options: argparse.Namespace) -> None:
        """执行 PyInstaller 构建过程。"""
        if PyInstaller is None:
            print("错误：请安装 PyInstaller 模块 (pip install pyinstaller)")
            sys.exit(1)

        # 清理 build 目录
        build_dir = os.path.join(os.getcwd(), "build")
        if not _safe_remove_directory(build_dir, options.non_interactive):
            sys.exit(1)

        # 清理 dist 目录
        dist_dir = (
            os.path.join(os.getcwd(), options.distpath)
            if options.distpath
            else os.path.join(os.getcwd(), "dist")
        )
        if not _safe_remove_directory(dist_dir, options.non_interactive):
            sys.exit(1)

        try:
            pyi_args = [options.script, "--noconfirm"]

            # Streamlit 特定配置
            pyi_args.extend(["--collect-all", "streamlit"])
            pyi_args.extend(["--copy-metadata", "streamlit"])

            # 可选参数配置
            if options.contents_directory:
                pyi_args.extend(["--contents-directory", options.contents_directory])
            if not options.debug_console:
                pyi_args.append("--noconsole")
            if options.icon:
                pyi_args.extend(["--icon", options.icon])
            if options.name:
                pyi_args.extend(["--name", options.name])
            if options.distpath:
                pyi_args.extend(["--distpath", options.distpath])

            # 处理 add-data
            if options.add_data:
                for data_group in options.add_data:
                    for item in data_group:
                        pyi_args.extend(["--add-data", item])

            # 处理 add-binary
            if options.add_binary:
                for binary_group in options.add_binary:
                    for item in binary_group:
                        pyi_args.extend(["--add-binary", item])

            # 处理 hidden-import
            if options.hidden_import:
                for import_group in options.hidden_import:
                    for item in import_group:
                        pyi_args.extend(["--hidden-import", item])

            if options.uac_admin:
                pyi_args.append("--uac-admin")

            # 打包模式：单文件或单目录
            pyi_args.append("--onedir" if options.onedir else "--onefile")

            # 额外自定义参数
            if options.pyinstaller_build_args:
                for arg_group in options.pyinstaller_build_args:
                    pyi_args.extend(arg_group)

            print(f"\n🚀 开始构建：{options.name} (v{options.version})")
            print(f"⚙️  PyInstaller 参数：{pyi_args}\n")

            PyInstaller.__main__.run(pyi_args)

            print(f"\n✅ 构建成功：{options.distpath}/{options.name}")

        except Exception as e:
            print(f"❌ 构建过程中发生错误：{e}")
            sys.exit(1)

    @staticmethod
    def main(need_debug_console: bool = False, need_compress: bool = False) -> None:
        """主入口函数：加载配置并执行构建流程。"""
        start_time = time.time()

        # 加载 pyproject.toml 配置
        if not os.path.exists("pyproject.toml"):
            print("❌ 错误：未找到 pyproject.toml 文件")
            sys.exit(1)

        pyproject_info = toml.load("pyproject.toml")
        project_meta = pyproject_info.get("project", {})

        name = project_meta.get("name", "unknown_app")
        version = project_meta.get("version", "0.0.0")
        description = project_meta.get("description", "")

        contents_directory = f"app-{version}"
        dist_path = "dist"
        pack_path = os.path.join(dist_path, name)

        # 构建配置对象
        options = argparse.Namespace(
            script="main.py",
            icon="assets/ico/main.ico",
            name=name,
            product_name=name,
            version=version,
            non_interactive=True,
            onedir=True,  # 对应 -D 参数 (单目录模式)
            distpath=dist_path,
            add_data=[
                ["src:src"],
                ["src/ui:src/ui"],
                ["pyproject.toml:."],
                # 插件资源
                ["plugins/ps_of_py/src:plugins/ps_of_py/src"],
                ["plugins/ps_of_py/pyproject.toml:plugins/ps_of_py/"],
                ["plugins/ps_of_py/README.md:plugins/ps_of_py/"],
                ["plugins/ps_of_py/CHANGELOG.md:plugins/ps_of_py/"],
            ],
            add_binary=[],
            hidden_import=[],
            uac_admin=False,
            debug_console=need_debug_console,
            product_version=version,
            file_version=version,
            file_description=description,
            contents_directory=contents_directory,
            pyinstaller_build_args=[],
            codesign_identity=None,
            bundle_id=None,
            company_name=None,
            copyright=None,
        )

        # 1. 执行构建
        AutoBuildMainApp.build(options)
        elapsed_time = time.time() - start_time
        print(f"\n🎉 构建完成！耗时：{elapsed_time:.2f} 秒")

        # 2. 清理临时文件
        _delete_build_artifacts(name)

        # 3. 生成版本信息
        _generate_version_info(dist_path, name, version)

        # 4. 复制资源文件
        _copy_assets_to_dist(pack_path, dist_path)

        # 5. 压缩 (可选)
        if need_compress:
            _compress_distribution(dist_path, name, version)

        elapsed_time = time.time() - start_time
        print(f"\n🎉 全部完成！耗时：{elapsed_time:.2f} 秒")


class AutoBuildUpdateApp:
    """更新程序自动构建类。"""

    @staticmethod
    def build(options: argparse.Namespace) -> None:
        """执行更新程序的 PyInstaller 构建。"""
        if PyInstaller is None:
            print("错误：请安装 PyInstaller 模块")
            sys.exit(1)

        pyi_args = [options.script, "--noconfirm"]

        if options.icon:
            pyi_args.extend(["--icon", options.icon])
        if options.name:
            pyi_args.extend(["--name", options.name])
        if options.distpath:
            pyi_args.extend(["--distpath", options.distpath])

        # 更新程序通常为单文件模式
        pyi_args.append("--onefile")

        print(f"\n🔧 正在构建更新程序：{options.name}")
        PyInstaller.__main__.run(pyi_args)
        print("✅ 更新程序构建完成。")

    @staticmethod
    def main() -> None:
        """更新程序构建入口。"""
        options = argparse.Namespace(
            script="updater.py",
            icon="assets/ico/main.ico",
            name="updater",
            product_name="updater",
            version="0.0.1",
            non_interactive=True,
            onedir=False,
            distpath="dist",
        )
        AutoBuildUpdateApp.build(options)


def main_entry():
    """命令行交互入口。"""
    modes = {
        1: "构建主程序 (Main)",
        2: "构建更新程序 (Update)",
        3: "快速打包 (无控制台，无压缩)",
        4: "完整打包 (无控制台，含压缩)",
    }

    print("\n❓ 请选择构建模式:")
    for key, value in modes.items():
        print(f"   {key}: {value}")

    try:
        choice = int(input("请输入选项编号 (1-4): "))
    except ValueError:
        print("无效输入，退出。")
        sys.exit(1)

    if choice == 1:
        # 交互式构建主程序
        debug_input = input("❓ 是否需要调试控制台？(y/n): ").lower()
        compress_input = input("❓ 是否需要生成压缩包？(y/n): ").lower()

        need_debug = debug_input in ["y", "yes", "1"]
        need_compress = compress_input in ["y", "yes", "1"]

        AutoBuildMainApp.main(
            need_debug_console=need_debug, need_compress=need_compress
        )

    elif choice == 2:
        AutoBuildUpdateApp.main()

    elif choice == 3:
        AutoBuildMainApp.main(need_debug_console=False, need_compress=False)

    elif choice == 4:
        AutoBuildMainApp.main(need_debug_console=False, need_compress=True)

    else:
        print("无效的选项。")
        sys.exit(1)

    # 构建完成后打开 dist 目录
    dist_full_path = os.path.join(os.getcwd(), "dist")
    if os.path.exists(dist_full_path):
        print(f"\n📂 正在打开发布目录：{dist_full_path}")
        os.startfile(dist_full_path)


if __name__ == "__main__":
    main_entry()
