"""Windowed EXE entry point. Editable project files always live outside the bundle."""
from pathlib import Path
import sys
import tkinter as tk
from tkinter import filedialog, messagebox

from config_gui import ConfigApp
from gui_i18n import Translator
from pipeline_core import Pipeline


def is_project(path):
    path = Path(path)
    return ((path / "ConfigSource" / "validation_rules.json").is_file()
            and (path / "Assets").is_dir())


def find_project(start):
    """Prefer the nearest project containing the executable, independent of working directory."""
    start = Path(start).resolve()
    return next((path for path in (start, *start.parents) if is_project(path)), None)


def executable_directory():
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parent


def main(argv=None):
    args = sys.argv[1:] if argv is None else argv
    root = tk.Tk()
    root.withdraw()
    try:
        if args:
            if len(args) != 2 or args[0] != "--root":
                raise ValueError("用法：TDConfigTool.exe [--root 项目文件夹]")
            project = Path(args[1]).resolve()
            if not is_project(project):
                raise ValueError("所选目录需包含 ConfigSource/validation_rules.json 和 Assets 文件夹。")
        else:
            project = find_project(executable_directory())
            while project is None:
                selected = filedialog.askdirectory(
                    parent=root, title="选择 TD 项目文件夹 / Select project folder", mustexist=True)
                if not selected:
                    return 0
                if is_project(selected):
                    project = Path(selected).resolve()
                else:
                    messagebox.showerror("目录不正确", "请选择包含 ConfigSource 和 Assets 的项目文件夹。", parent=root)
        ConfigApp(root, Pipeline(root=project))
        root.deiconify()
        root.mainloop()
        return 0
    except (OSError, ValueError, tk.TclError) as exc:
        messagebox.showerror("无法打开配置工具", Translator().text(str(exc)), parent=root)
        return 1
    finally:
        try:
            root.destroy()
        except tk.TclError:
            pass


if __name__ == "__main__":
    raise SystemExit(main())
