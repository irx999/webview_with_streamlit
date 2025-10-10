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
import os
import shutil
import sys


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
            delete_dir_prompt = input('Do you want to delete "build" directory? (y/n) ')
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
        print("Running PyInstaller:", pyi_args)
        PyInstaller.__main__.run(pyi_args)

    except ImportError as e:
        print("Please install PyInstaller module to use flet pack command:", e)
        sys.exit(1)


if __name__ == "__main__":
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
        icon="app.ico",
        name=name,
        product_name=name,
        non_interactive=True,
        onedir=True,  # 对应 -D 参数
        distpath="dist",
        add_data=[
            ["streamlit_app.py:."],
            # ["src:src"],
            ["src/ui:src/ui"],
            ["assets:assets"],
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

    pack_path = f"{options.distpath}/{name}/{contents_directory}"
    # shutil.copy("pyproject.toml", f"{pack_path}/pyproject.toml")
    # shutil.copytree("src", f"{pack_path}/src", dirs_exist_ok=True)

    def compress():
        print(f"\n 🌟 Compressing  -> {options.distpath}/{name}.zip {version} \n")
        shutil.make_archive(
            base_name=f"{options.distpath}/{name}",
            format="zip",
            root_dir=f"{options.distpath}/{name}",
        )
        print(f"\n ✅ Compress Success {version}  \n")

    def delete_build_dir():
        try:
            shutil.rmtree("build", ignore_errors=True)
            os.remove(f"{name}.spec")
        except FileNotFoundError:
            pass

    print(f"\n 🌟 Building {name} -> {version} \n")
    # 构建
    build(options)

    print(f"\n ✅ Build Success {version} \n")

    # compress()

    delete_build_dir()

    print(f"\n ✅ All Done spend{time.time() - strat_time:.2f}s ")
