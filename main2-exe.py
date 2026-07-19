import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import subprocess
import os
import sys
import json

# ==================== 设置持久化 ====================
SETTINGS_FILE = "build_settings.json"


def load_settings():
    defaults = {
        "standalone": True,
        "onefile": False,
        "console": False,
        "follow_imports": 0,
        "icon": "",
        "output_dir": "",
        "company": "",
        "product": "",
        "version": "",
        "include_package": "",
        "include_data": "",
    }
    try:
        if os.path.exists(SETTINGS_FILE):
            with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
                saved = json.load(f)
            defaults.update(saved)
    except Exception:
        pass
    return defaults


def save_settings():
    data = {
        "standalone": var_standalone.get(),
        "onefile": var_onefile.get(),
        "console": var_console.get(),
        "follow_imports": var_follow_imports.current(),
        "icon": var_icon.get(),
        "output_dir": var_output.get(),
        "company": var_company.get(),
        "product": var_product.get(),
        "version": var_version.get(),
        "include_package": var_inc_pkg.get(),
        "include_data": var_inc_data.get(),
    }
    try:
        with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    except Exception:
        pass


# ==================== 核心逻辑 ====================

def build_cmd():
    """构建 Nuitka 命令列表，返回 (cmd_list, error_msg)"""
    python_code = var_script.get()
    if not python_code or not os.path.exists(python_code):
        return None, "请先选择一个有效的 .py 文件"

    cmd = [sys.executable, "-m", "nuitka", "--zig", "--enable-plugin=tk-inter"]

    if var_standalone.get():
        cmd.append("--standalone")
    if var_onefile.get():
        cmd.append("--onefile")
    if var_console.get():
        cmd.append("--windows-console-mode=force")

    # 输出目录
    out = var_output.get().strip()
    if out:
        cmd.extend([f"--output-dir={out}"])

    # 图标
    icon = var_icon.get().strip()
    if icon and os.path.exists(icon):
        cmd.extend(["--windows-icon-from-ico", icon])

    # 版本信息
    company = var_company.get().strip()
    if company:
        cmd.extend(["--company-name", company])

    product = var_product.get().strip()
    if product:
        cmd.extend(["--product-name", product])

    version = var_version.get().strip()
    if version:
        cmd.extend(["--file-version", version])

    # 包含模块
    inc_pkg = var_inc_pkg.get().strip()
    if inc_pkg:
        for pkg in inc_pkg.split(","):
            pkg = pkg.strip()
            if pkg:
                cmd.extend(["--include-package", pkg])

    # 包含数据目录
    inc_data = var_inc_data.get().strip()
    if inc_data and os.path.exists(inc_data):
        dir_name = os.path.basename(inc_data)
        cmd.extend(["--include-data-dir", f"{inc_data}={dir_name}"])

    # follow-imports
    fi = var_follow_imports.current()
    if fi > 0:
        cmd.extend(["--follow-imports", str(fi)])

    cmd.append(python_code)
    return cmd, None


def update_preview(*_args):
    """实时更新命令预览"""
    cmd, err = build_cmd()
    if err:
        preview_text.config(state="normal")
        preview_text.delete("1.0", "end")
        preview_text.insert("1.0", err)
        preview_text.config(state="disabled")
        return

    # 格式化显示（一行一个参数，方便阅读）
    lines = []
    for i, arg in enumerate(cmd):
        if i == 0:
            lines.append(arg)
        else:
            lines.append(f"    {arg}")
    preview_text.config(state="normal")
    preview_text.delete("1.0", "end")
    preview_text.insert("1.0", "\n".join(lines))
    preview_text.config(state="disabled")


def run_nuitka_cmd():
    cmd, err = build_cmd()
    if err:
        messagebox.showerror("错误", err)
        return
    save_settings()
    try:
        subprocess.Popen(cmd, creationflags=subprocess.CREATE_NEW_CONSOLE)
        status_var.set("Nuitka 编译已启动，请在弹出的控制台窗口查看进度")
    except FileNotFoundError:
        messagebox.showerror("错误", "Nuitka 未安装，请先执行: pip install nuitka")
    except Exception as e:
        messagebox.showerror("错误", f"启动失败:\n{e}")


def run_tool(name):
    exe_path = f"{name}.exe"
    py_path = f"{name}.py"
    if os.path.exists(exe_path):
        try:
            subprocess.Popen([exe_path])
            status_var.set(f"已启动 {exe_path}")
            return
        except Exception as e:
            messagebox.showerror("Error", f"无法启动 {exe_path}:\n{e}")
            return
    if os.path.exists(py_path):
        try:
            subprocess.Popen([sys.executable, py_path])
            status_var.set(f"已启动 {py_path}")
            return
        except Exception as e:
            messagebox.showerror("Error", f"无法启动 {py_path}:\n{e}")
            return
    messagebox.showerror("Error",
        f"未找到 {exe_path} 或 {py_path}\n请先运行 build_tools.py 编译子工具")


def run_obfuscator():
    run_tool("run_obf")


def run_upx():
    upx_exe = os.path.join("upx", "upx.exe")
    if os.path.exists(upx_exe):
        try:
            subprocess.Popen([upx_exe])
            status_var.set(f"已启动 {upx_exe}")
        except Exception as e:
            messagebox.showerror("Error", f"无法启动 UPX:\n{e}")
    else:
        run_tool("upx")


# ==================== 文件/目录选择 ====================

def select_script():
    path = filedialog.askopenfilename(
        title="选择 Python 脚本",
        filetypes=[("Python Script", "*.py"), ("All Files", "*.*")]
    )
    if path:
        var_script.set(path)


def select_icon():
    path = filedialog.askopenfilename(
        title="选择图标文件",
        filetypes=[("Icon Files", "*.ico"), ("All Files", "*.*")]
    )
    if path:
        var_icon.set(path)


def select_output_dir():
    path = filedialog.askdirectory(title="选择输出目录")
    if path:
        var_output.set(path)


def select_data_dir():
    path = filedialog.askdirectory(title="选择要包含的数据目录")
    if path:
        var_inc_data.set(path)


def on_drop(event):
    """处理拖拽文件（简化实现：通过 Entry 的插入事件处理）"""
    # Tkinter 原生的 DnD 需要 tkdnd 扩展，这里用简化方案：
    # 检测剪贴板路径或 event.data
    data = event.data
    if data:
        # 清理可能的花括号（Windows 拖拽路径格式）
        path = data.strip().strip("{}").strip()
        if os.path.isfile(path) and path.endswith(".py"):
            var_script.set(path)


def toggle_advanced():
    """展开/收起高级选项"""
    if advanced_frame.winfo_ismapped():
        advanced_frame.grid_remove()
        btn_advanced.config(text="▶ 高级选项")
    else:
        advanced_frame.grid()
        btn_advanced.config(text="▼ 高级选项")


# ==================== GUI 构建 ====================

if __name__ == "__main__":
    settings = load_settings()

    root = tk.Tk()
    root.title("Python-Nuitka EXE 打包工具")
    root.geometry("780x650")
    root.minsize(700, 550)
    root.resizable(True, True)

    # 尝试启用拖拽（Windows 下用 dnd 扩展 / 通用用 Tk 原生命令）
    try:
        root.tk.call("package", "require", "tkdnd")
        root.drop_target_register("DND_Files")
        root.dnd_bind("<<Drop>>", on_drop)
    except tk.TclError:
        pass  # tkdnd 不可用时静默跳过

    root.columnconfigure(1, weight=1)
    root.columnconfigure(2, weight=1)

    # ===== Row 0: 脚本选择 =====
    ttk.Label(root, text="脚本:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
    var_script = tk.StringVar()
    ent_script = ttk.Entry(root, textvariable=var_script)
    ent_script.grid(row=0, column=1, padx=5, pady=5, columnspan=2, sticky="ew")
    ttk.Button(root, text="选择程序", command=select_script, width=9).grid(
        row=0, column=3, padx=5, pady=5
    )

    # ===== Row 1: 主要编译选项 =====
    var_standalone = tk.BooleanVar(value=settings["standalone"])
    cb1 = ttk.Checkbutton(root, text="--standalone 独立环境", variable=var_standalone, command=update_preview)
    cb1.grid(row=1, column=1, padx=5, pady=3, sticky="w")

    var_onefile = tk.BooleanVar(value=settings["onefile"])
    cb2 = ttk.Checkbutton(root, text="--onefile 单文件", variable=var_onefile, command=update_preview)
    cb2.grid(row=1, column=2, padx=5, pady=3, sticky="w")

    var_console = tk.BooleanVar(value=settings["console"])
    cb3 = ttk.Checkbutton(root, text="--windows-console-mode=force", variable=var_console, command=update_preview)
    cb3.grid(row=1, column=3, padx=5, pady=3, sticky="w")

    # ===== Row 2: 图标 =====
    ttk.Label(root, text="图标:").grid(row=2, column=0, padx=5, pady=3, sticky="e")
    var_icon = tk.StringVar(value=settings["icon"])
    ttk.Entry(root, textvariable=var_icon).grid(
        row=2, column=1, padx=5, pady=3, columnspan=2, sticky="ew"
    )
    var_icon.trace_add("write", lambda *a: update_preview())
    ttk.Button(root, text="选择图标", command=select_icon, width=9).grid(
        row=2, column=3, padx=5, pady=3
    )

    # ===== Row 3: 输出目录 =====
    ttk.Label(root, text="输出:").grid(row=3, column=0, padx=5, pady=3, sticky="e")
    var_output = tk.StringVar(value=settings["output_dir"])
    ttk.Entry(root, textvariable=var_output).grid(
        row=3, column=1, padx=5, pady=3, columnspan=2, sticky="ew"
    )
    var_output.trace_add("write", lambda *a: update_preview())
    ttk.Button(root, text="选择目录", command=select_output_dir, width=9).grid(
        row=3, column=3, padx=5, pady=3
    )

    # ===== Row 4: 高级选项开关 =====
    btn_advanced = ttk.Button(root, text="▶ 高级选项", command=toggle_advanced, width=12)
    btn_advanced.grid(row=4, column=1, padx=5, pady=3, sticky="w")

    # ===== 高级选项面板（默认隐藏）=====
    advanced_frame = ttk.Frame(root)
    advanced_frame.grid(row=5, column=0, columnspan=4, sticky="ew", padx=5, pady=2)
    advanced_frame.columnconfigure(1, weight=1)
    advanced_frame.columnconfigure(2, weight=1)
    advanced_frame.grid_remove()

    r = 0
    ttk.Label(advanced_frame, text="公司名称:").grid(row=r, column=0, padx=5, pady=2, sticky="e")
    var_company = tk.StringVar(value=settings["company"])
    ttk.Entry(advanced_frame, textvariable=var_company).grid(
        row=r, column=1, padx=5, pady=2, columnspan=3, sticky="ew"
    )
    var_company.trace_add("write", lambda *a: update_preview())

    r += 1
    ttk.Label(advanced_frame, text="产品名称:").grid(row=r, column=0, padx=5, pady=2, sticky="e")
    var_product = tk.StringVar(value=settings["product"])
    ttk.Entry(advanced_frame, textvariable=var_product).grid(
        row=r, column=1, padx=5, pady=2, columnspan=3, sticky="ew"
    )
    var_product.trace_add("write", lambda *a: update_preview())

    r += 1
    ttk.Label(advanced_frame, text="文件版本:").grid(row=r, column=0, padx=5, pady=2, sticky="e")
    var_version = tk.StringVar(value=settings["version"])
    ttk.Entry(advanced_frame, textvariable=var_version, width=20).grid(
        row=r, column=1, padx=5, pady=2, sticky="w"
    )

    r += 1
    ttk.Label(advanced_frame, text="包含模块:").grid(row=r, column=0, padx=5, pady=2, sticky="e")
    var_inc_pkg = tk.StringVar(value=settings["include_package"])
    ttk.Entry(advanced_frame, textvariable=var_inc_pkg).grid(
        row=r, column=1, padx=5, pady=2, columnspan=3, sticky="ew"
    )
    var_inc_pkg.trace_add("write", lambda *a: update_preview())
    ttk.Label(advanced_frame, text="逗号分隔多个包名", foreground="gray").grid(
        row=r + 1, column=1, padx=5, sticky="w"
    )

    r += 2
    ttk.Label(advanced_frame, text="包含数据:").grid(row=r, column=0, padx=5, pady=2, sticky="e")
    var_inc_data = tk.StringVar(value=settings["include_data"])
    ttk.Entry(advanced_frame, textvariable=var_inc_data).grid(
        row=r, column=1, padx=5, pady=2, columnspan=2, sticky="ew"
    )
    var_inc_data.trace_add("write", lambda *a: update_preview())
    ttk.Button(advanced_frame, text="选择", command=select_data_dir, width=7).grid(
        row=r, column=3, padx=2, pady=2
    )

    r += 1
    ttk.Label(advanced_frame, text="导入模式:").grid(row=r, column=0, padx=5, pady=2, sticky="e")
    var_follow_imports = ttk.Combobox(
        advanced_frame, values=["0 - 不跟踪 (nofollow)", "1 - 标准", "2 - 深度"],
        state="readonly", width=25
    )
    var_follow_imports.current(settings["follow_imports"])
    var_follow_imports.grid(row=r, column=1, padx=5, pady=2, sticky="w")
    var_follow_imports.bind("<<ComboboxSelected>>", update_preview)

    # ===== 分隔线 =====
    ttk.Separator(root, orient="horizontal").grid(
        row=6, column=0, columnspan=4, sticky="ew", padx=10, pady=6
    )

    # ===== 命令预览 =====
    ttk.Label(root, text="命令预览:").grid(row=7, column=0, padx=5, pady=2, sticky="ne")
    preview_frame = ttk.Frame(root)
    preview_frame.grid(row=7, column=1, columnspan=3, padx=5, pady=2, sticky="ew")
    preview_frame.columnconfigure(0, weight=1)

    preview_text = tk.Text(preview_frame, height=6, width=60, wrap="none",
                           font=("Consolas", 9), bg="#1e1e1e", fg="#d4d4d4",
                           insertbackground="white", state="disabled")
    preview_text.grid(row=0, column=0, sticky="ew")

    preview_scroll = ttk.Scrollbar(preview_frame, orient="horizontal", command=preview_text.xview)
    preview_scroll.grid(row=1, column=0, sticky="ew")
    preview_text.config(xscrollcommand=preview_scroll.set)

    # 复制按钮
    def copy_cmd():
        cmd, _ = build_cmd()
        if cmd:
            root.clipboard_clear()
            root.clipboard_append(" ".join(cmd))
            status_var.set("命令已复制到剪贴板")

    ttk.Button(root, text="复制命令", command=copy_cmd, width=9).grid(
        row=7, column=0, padx=5, pady=2, sticky="se"
    )

    # ===== 分隔线 =====
    ttk.Separator(root, orient="horizontal").grid(
        row=8, column=0, columnspan=4, sticky="ew", padx=10, pady=6
    )

    # ===== 操作按钮 =====
    ttk.Button(root, text="混淆程序", command=run_obfuscator, width=18).grid(
        row=9, column=0, padx=5, pady=8
    )
    ttk.Button(root, text="打包 EXE", command=run_nuitka_cmd, width=18).grid(
        row=9, column=1, padx=5, pady=8
    )
    ttk.Button(root, text="UPX 压缩", command=run_upx, width=18).grid(
        row=9, column=2, padx=5, pady=8
    )

    # ===== 状态栏 =====
    status_var = tk.StringVar(value="就绪")
    ttk.Separator(root, orient="horizontal").grid(
        row=10, column=0, columnspan=4, sticky="ew", padx=0, pady=2
    )
    ttk.Label(root, textvariable=status_var, relief="sunken", anchor="w",
              padding=(5, 1)).grid(row=11, column=0, columnspan=4, sticky="ew", pady=0)

    # ===== 初始化和事件绑定 =====
    var_script.trace_add("write", lambda *a: update_preview())
    update_preview()

    def on_close():
        save_settings()
        root.destroy()

    root.protocol("WM_DELETE_WINDOW", on_close)
    root.mainloop()
