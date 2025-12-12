"""
import PyInstaller.__main__

name = "streamlitapp"
script_path = "streamlit_app.py"
args = [
    "--name",
    name,
    "--paths",
    ".",
    "--collect-all",
    "streamlit",
    "--copy-metadata",
    "streamlit",
    "--add-data",
    f"{script_path}:.",  # Add the script as a data file
    "--onedir",
    "main.py",
    "-w",
]


PyInstaller.__main__.run(args)
"""

import argparse
import datetime
import json
import os
import shutil
import sys


class AutoBuild_main_app:
    @staticmethod
    def build(options: argparse.Namespace) -> None:
        # is_dir_not_empty = lambda dir: os.path.isdir(dir) and len(os.listdir(dir)) != 0
        def is_dir_not_empty(dir: str) -> bool:
            """Check if a directory is not empty."""
            return os.path.isdir(dir) and len(os.listdir(dir)) != 0

        # delete "build" directory
        build_dir = os.path.join(os.getcwd(), "build")
        if is_dir_not_empty(build_dir):
            if options.non_interactive:
                shutil.rmtree(build_dir, ignore_errors=True)
            else:
                delete_dir_prompt = input(
                    'Do you want to delete "build" directory? (y/n) '
                )
                if not delete_dir_prompt.lower() == "n":
                    shutil.rmtree(build_dir, ignore_errors=True)
                else:
                    print('Failing... "build" directory must be empty to proceed.')
                    exit(1)

        # delete "dist" directory or DISTPATH directory
        # if --distpath cli option is specified
        if options.distpath:
            dist_dir = os.path.join(os.getcwd(), options.distpath)
        else:
            dist_dir = os.path.join(os.getcwd(), "dist")
        if is_dir_not_empty(dist_dir):
            if options.non_interactive:
                shutil.rmtree(dist_dir, ignore_errors=True)
            else:
                delete_dir_prompt = input(
                    f'Do you want to delete "{os.path.basename(dist_dir)}" directory? (y/n) '
                )
                if not delete_dir_prompt.lower() == "n":
                    shutil.rmtree(dist_dir, ignore_errors=True)
                else:
                    print(
                        f'Failing... DISTPATH "{os.path.basename(dist_dir)}" directory must be empty to proceed.'
                    )
                    exit(1)

        try:
            import PyInstaller.__main__

            pyi_args = [options.script, "--noconfirm"]

            # add streamlit
            pyi_args.extend(["--collect-all", "streamlit"])
            pyi_args.extend(["--copy-metadata", "streamlit"])
            # pyi_args.extend(["--add-data", f"{options.streamlit_script}:."])

            if options.contents_directory:
                pyi_args.extend(["--contents-directory", options.contents_directory])
            if not options.debug_console:
                pyi_args.extend(["--noconsole"])
            if options.icon:
                pyi_args.extend(["--icon", options.icon])
            if options.name:
                pyi_args.extend(["--name", options.name])
            if options.distpath:
                pyi_args.extend(["--distpath", options.distpath])
            if options.add_data:
                for add_data_arr in options.add_data:
                    for add_data_item in add_data_arr:
                        pyi_args.extend(["--add-data", add_data_item])
            if options.add_binary:
                for add_binary_arr in options.add_binary:
                    for add_binary_item in add_binary_arr:
                        pyi_args.extend(["--add-binary", add_binary_item])
            if options.hidden_import:
                for hidden_import_arr in options.hidden_import:
                    for hidden_import_item in hidden_import_arr:
                        pyi_args.extend(["--hidden-import", hidden_import_item])

            if options.uac_admin:
                pyi_args.append("--uac-admin")
            if options.onedir:
                pyi_args.append("--onedir")
            else:
                pyi_args.append("--onefile")

            if options.pyinstaller_build_args:
                for pyinstaller_build_arg_arr in options.pyinstaller_build_args:
                    pyi_args.extend(pyinstaller_build_arg_arr)

            # run PyInstaller!
            print(f"\n 🌟 Building {options.name} -> {options.version} \n")

            print(f"\n 💐 Running PyInstaller:{pyi_args} \n")

            PyInstaller.__main__.run(pyi_args)

            print(f"\n ✅ Build Success {options.distpath}/{options.name}  \n")

        except ImportError as e:
            print("Please install PyInstaller module to use flet pack command:", e)
            sys.exit(1)

    @staticmethod
    def main():
        import time

        import toml

        strat_time = time.time()

        pyproject_info = toml.load("pyproject.toml")

        name = pyproject_info["project"]["name"]
        version = pyproject_info["project"]["version"]
        description = pyproject_info["project"]["description"]

        contents_directory = f"app-{version}"

        options = argparse.Namespace(
            script="main.py",
            # streamlit_script="streamlit_app.py",
            icon="assets/ico/app.ico",
            name=name,
            product_name=name,
            version=version,
            non_interactive=True,
            onedir=True,  # 对应 -D 参数
            distpath="dist",
            add_data=[
                # ["streamlit_app.py:."],
                ["src:src"],
                ["src/ui:src/ui"],
                ["pyproject.toml:pyproject.toml"],
            ],
            add_binary=[],
            hidden_import=[
                ["xlwings"],
            ],
            codesign_identity=None,
            bundle_id=None,
            uac_admin=False,
            debug_console=True,
            product_version=version,
            file_version=version,
            company_name=None,
            copyright=None,
            pyinstaller_build_args=[],
            file_description=description,
            contents_directory=contents_directory,
        )

        import shutil

        pack_path = f"{options.distpath}/{name}"

        # shutil.copy("pyproject.toml", f"{pack_path}/pyproject.toml")
        # shutil.copytree("src", f"{pack_path}/src", dirs_exist_ok=True)
        @staticmethod
        def delete_build_file():
            """删除 build & spec"""
            try:
                print("\n 🌟 Delete build & spec \n")
                shutil.rmtree("build", ignore_errors=True)
                os.remove(f"{name}.spec")
            except Exception as e:
                print(f"\n ❌️ Failing... {e}.")

        def generating_file_information() -> None:
            """生成文件信息"""
            try:
                print(
                    f"\n 🌟 Generating_latest.json -> {options.distpath}/latest.json \n"
                )
                info = {
                    "name": name,
                    "version": f"{version}+auto_build.{time.time()}",
                    "pub_date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "download_url": "",
                    "update_info": "🌟 This is an auto build version",
                }
                with open(f"{options.distpath}/latest.json", "w") as f:
                    f.write(json.dumps(info, indent=4))
            except Exception as e:
                print(f"\n ❌️ Failing... {e}.")

        def copy_file():
            """复制文件"""
            try:
                print("\n 🌟 Copy file -> dist \n")
                shutil.copytree("assets", f"{pack_path}/assets", dirs_exist_ok=True)
                shutil.copy(
                    f"{options.distpath}/latest.json",
                    f"{pack_path}/assets/latest.json",
                )
            except Exception as e:
                print(f"\n ❌️ Failing... {e}.")

        def compress():
            """压缩文件"""
            try:
                file_name = f"{options.distpath}/{name}-{version}"
                print(f"\n 🌟 Compressing  -> {file_name}.zip \n")
                shutil.make_archive(
                    base_name=file_name,
                    format="zip",
                    root_dir=f"{options.distpath}/{name}",
                )
                file_size = os.path.getsize(f"{file_name}.zip")
                print(f"\n ✅ Compress Success {file_size / (1024 * 1024):.2f} MB  \n")
            except Exception as e:
                print(f"\n ❌️ Failing... {e}.")

        # 构建
        AutoBuild_main_app.build(options)

        # 删除构建文件
        delete_build_file()

        # 生成文件信息
        generating_file_information()

        # 复制文件
        copy_file()

        # 压缩
        compress()

        print(f"\n ✅ All Done spend {time.time() - strat_time:.2f} s")


class AutoBuild_update_app:
    @staticmethod
    def build(options):
        import PyInstaller.__main__

        pyi_args = [options.script, "--noconfirm"]

        if options.icon:
            pyi_args.extend(["--icon", options.icon])
        if options.name:
            pyi_args.extend(["--name", options.name])
        if options.distpath:
            pyi_args.extend(["--distpath", options.distpath])
        PyInstaller.__main__.run(pyi_args)

    @staticmethod
    def main():
        name = "updater"
        version = "0.0.1"
        options = argparse.Namespace(
            script="updater.py",
            icon="assets/ico/app.ico",
            name=name,
            product_name=name,
            version=version,
            non_interactive=True,
            onedir=False,  # 对应 -D 参数
            distpath="dist",
        )
        AutoBuild_update_app.build(options)


if __name__ == "__main__":
    mode = input("Plese input mode: \n 1   🌟: main \n 2   🌟: update \n")
    match mode:
        case "" | None:
            sys.exit()
        case "1":
            AutoBuild_main_app.main()
        case "2":
            AutoBuild_update_app.main()
