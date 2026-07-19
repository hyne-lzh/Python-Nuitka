import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import subprocess
import os
import sys


def select_script():
    path = filedialog.askopenfilename(
        title="Select Python Script",
        filetypes=[("Python Script", "*.py")]
    )
    if path:
        var_script.set(path)


def run_nuitka_cmd():
    cmd = [sys.executable, "-m", "nuitka", "--zig", "--enable-plugin=tk-inter"]

    if var_standalone.get():
        cmd.append("--standalone")

    python_code = var_script.get()
    if not python_code or not os.path.exists(python_code):
        messagebox.showerror("Error", f"File not found:\n{python_code}\n文件不存在，请重新选择！")
        return

    cmd.append(python_code)

    try:
        subprocess.Popen(cmd, creationflags=subprocess.CREATE_NEW_CONSOLE)
    except FileNotFoundError:
        messagebox.showerror("Error", "Nuitka not found. Please install it first:\nnuitka 未安装，请先执行 pip install nuitka")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to start Nuitka:\n启动失败：{e}")


def run_tool(name):
    """Launch a tool: prefer compiled .exe first, fallback to .py via Python.
    启动子工具：优先使用已编译的 .exe（无需 Python 环境），否则用 Python 运行 .py。"""
    exe_path = f"{name}.exe"
    py_path = f"{name}.py"

    if os.path.exists(exe_path):
        try:
            subprocess.Popen([exe_path])
            return
        except Exception as e:
            messagebox.showerror("Error", f"Failed to start {exe_path}:\n{e}")
            return

    if os.path.exists(py_path):
        try:
            subprocess.Popen([sys.executable, py_path])
            return
        except Exception as e:
            messagebox.showerror("Error", f"Failed to start {py_path}:\n{e}")
            return

    messagebox.showerror("Error",
        f"Neither {exe_path} nor {py_path} found.\n"
        f"未找到 {exe_path} 或 {py_path}。\n\n"
        f"Tip: run build_tools.py to compile them into .exe first.\n"
        f"提示：请先运行 build_tools.py 将它们编译为 .exe")


def run_obfuscator():
    run_tool("run_obf")


def run_upx():
    run_tool("upx")


if __name__ == "__main__":
    root = tk.Tk()
    root.title("Python-Nuitka Toolchain Launcher")
    root.geometry("800x600")

    # Row 0: 文件选择
    tk.Label(root, text="Program:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
    var_script = tk.StringVar()
    tk.Entry(root, textvariable=var_script, width=60).grid(row=0, column=1, padx=5, pady=5)
    tk.Button(root, text="Select Program", command=select_script).grid(row=0, column=2, padx=5, pady=5)

    # Row 1: 操作按钮
    tk.Button(root, text="Obfuscate", command=run_obfuscator, width=14).grid(row=1, column=0, padx=5, pady=8)
    tk.Button(root, text="Package EXE", command=run_nuitka_cmd, width=14).grid(row=1, column=1, padx=5, pady=8)
    tk.Button(root, text="UPX Compress", command=run_upx, width=14).grid(row=1, column=2, padx=5, pady=8)

    # Row 2: standalone 选项
    var_standalone = tk.BooleanVar(value=True)
    tk.Checkbutton(root, text="Standalone mode (--standalone)", variable=var_standalone).grid(
        row=2, column=0, columnspan=3, pady=5
    )

    root.mainloop()
