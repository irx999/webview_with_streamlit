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
