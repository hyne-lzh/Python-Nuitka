import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import subprocess
import threading
import json
import os
import sys
import shlex

CONFIG_FILE = "upx_gui_config.json"
LANG_FILE = "upx_lang.json"
proc = None

# 双语文本库
LANG_DATA = {
    "zh": {
        "win_title": "UPX 可执行文件压缩工具 v1.0",
        "path_frame": "基础路径配置",
        "upx_label": "UPX程序路径:",
        "file_label": "待处理文件(多选EXE):",
        "out_label": "输出目录(可选):",
        "browse_btn": "浏览",
        "add_file_btn": "添加文件",
        "clear_file_btn": "清空文件列表",
        "mode_frame": "压缩模式设置",
        "level_label": "压缩等级:",
        "level_fast": "1-快速",
        "level_bal": "5-均衡",
        "level_best": "9-高压缩",
        "level_ultra": "--ultra-brute(极致压缩,极慢)",
        "opt_frame": "可选参数",
        "opt_quiet": "-q 静默输出",
        "opt_force": "-f 强制压缩可疑文件",
        "opt_backup": "-k 保留备份文件",
        "opt_strip_reloc": "--strip-relocs=1 剥离重定位(仅纯EXE可用，DLL/PYD禁止)",
        "opt_all_icon": "--compress-icons=3 压缩全部图标",
        "opt_no_color": "--no-color 无彩色输出",
        "func_frame": "操作功能",
        "btn_compress": "开始压缩",
        "btn_decompress": "解压文件 -d",
        "btn_test": "校验文件 -t",
        "btn_list": "查看文件信息 -l",
        "btn_fileinfo": "查看压缩参数 --fileinfo",
        "log_frame": "实时运行日志",
        "auto_scroll": "自动滚动日志",
        "clear_log_btn": "清空日志",
        "lang_switch": "切换中英文 / Switch Language ",
        "save_cfg": "保存配置",
        "load_cfg": "加载配置",
        "warn_upx_miss": "UPX程序路径不存在，请重新选择！",
        "tip_file_empty": "请至少选择一个exe文件",
        "cmd_title": "执行命令: ",
        "err_title": "错误输出",
        "task_done": "操作执行完成，退出码: {}"
    },
    "en": {
        "win_title": "UPX Executable Compressor GUI v1.0",
        "path_frame": "Basic Path Config",
        "upx_label": "UPX Binary Path:",
        "file_label": "Target EXE Files(Multi Select):",
        "out_label": "Output Dir(Optional):",
        "browse_btn": "Browse",
        "add_file_btn": "Add Files",
        "clear_file_btn": "Clear File List",
        "mode_frame": "Compress Mode",
        "level_label": "Compress Level:",
        "level_fast": "1-Fast",
        "level_bal": "5-Balance",
        "level_best": "9-Best",
        "level_ultra": "--ultra-brute(Max Compress, Very Slow)",
        "opt_frame": "Extra Options",
        "opt_quiet": "-q Quiet Mode",
        "opt_force": "-f Force Suspect Files",
        "opt_backup": "-k Keep Backup Files",
        "opt_strip_reloc": "--strip-relocs=1 Strip Relocs(Only pure EXE, DLL/PYD forbidden)",
        "opt_all_icon": "--compress-icons=3 Compress All Icons",
        "opt_no_color": "--no-color Disable Color",
        "func_frame": "Functions",
        "btn_compress": "Compress",
        "btn_decompress": "Decompress -d",
        "btn_test": "Test File -t",
        "btn_list": "List Info -l",
        "btn_fileinfo": "Show Params --fileinfo",
        "log_frame": "Real-time Log",
        "auto_scroll": "Auto Scroll Log",
        "clear_log_btn": "Clear Log",
        "lang_switch": "Switch Language",
        "save_cfg": "Save Config",
        "load_cfg": "Load Config",
        "warn_upx_miss": "UPX binary not found, reselect path!",
        "tip_file_empty": "Please select at least one exe file",
        "cmd_title": "Running Command: ",
        "err_title": "STDERR Output",
        "task_done": "Task finished, exit code: {}"
    }
}

class UPXGUI:
    def __init__(self, root):
        self.root = root
        self.root.geometry("940x740")
        self.root.resizable(False, False)
        self.widget_map = {}
        # 语言加载
        self.lang = "zh"
        if os.path.exists(LANG_FILE):
            try:
                with open(LANG_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.lang = data.get("lang", "zh")
            except:
                pass
        # 变量
        self.var_upx_path = tk.StringVar(value=r"upx\upx.exe")
        self.var_out_dir = tk.StringVar()
        self.file_list = []
        self.var_level = tk.StringVar(value="5")
        self.var_quiet = tk.BooleanVar()
        self.var_force = tk.BooleanVar()
        self.var_backup = tk.BooleanVar()
        self.var_strip_reloc = tk.BooleanVar(value=False)
        self.var_all_icon = tk.BooleanVar()
        self.var_no_color = tk.BooleanVar()
        self.var_auto_scroll = tk.BooleanVar(value=True)
        self.build_ui()
        self.refresh_lang()
        self.load_config()

    def get_txt(self, key):
        return LANG_DATA[self.lang][key]

    def switch_lang(self):
        self.lang = "en" if self.lang == "zh" else "zh"
        with open(LANG_FILE, "w", encoding="utf-8") as f:
            json.dump({"lang": self.lang}, f, ensure_ascii=False, indent=2)
        self.refresh_lang()

    def refresh_lang(self):
        self.root.title(self.get_txt("win_title"))
        for widget, k in self.widget_map.items():
            widget.config(text=self.get_txt(k))

    def build_ui(self):
        main = ttk.Frame(self.root, padding=10)
        main.pack(fill=tk.BOTH, expand=True)
        # 顶部语言切换
        lang_btn = ttk.Button(main, command=self.switch_lang)
        lang_btn.pack(anchor="e", pady=(0,6))
        self.widget_map[lang_btn] = "lang_switch"

        # ========== 路径区域 ==========
        frame_path = ttk.LabelFrame(main)
        frame_path.pack(fill=tk.X, pady=5)
        self.widget_map[frame_path] = "path_frame"

        # UPX路径
        lu = ttk.Label(frame_path)
        lu.grid(row=0, column=0, sticky="w")
        self.widget_map[lu] = "upx_label"
        ttk.Entry(frame_path, textvariable=self.var_upx_path, width=58).grid(row=0, column=1, padx=4)
        bupx = ttk.Button(frame_path, command=self.select_upx)
        bupx.grid(row=0, column=2)
        self.widget_map[bupx] = "browse_btn"

        # 待处理文件
        lf = ttk.Label(frame_path)
        lf.grid(row=1, column=0, sticky="w", pady=3)
        self.widget_map[lf] = "file_label"
        badd = ttk.Button(frame_path, command=self.add_files)
        badd.grid(row=1, column=1, sticky="w", padx=4)
        self.widget_map[badd] = "add_file_btn"
        bclr = ttk.Button(frame_path, command=self.clear_files)
        bclr.grid(row=1, column=2)
        self.widget_map[bclr] = "clear_file_btn"

        # 输出目录
        lo = ttk.Label(frame_path)
        lo.grid(row=2, column=0, sticky="w", pady=3)
        self.widget_map[lo] = "out_label"
        ttk.Entry(frame_path, textvariable=self.var_out_dir, width=58).grid(row=2, column=1, padx=4)
        bout = ttk.Button(frame_path, command=self.select_out)
        bout.grid(row=2, column=2)
        self.widget_map[bout] = "browse_btn"

        # ========== 压缩等级 ==========
        frame_level = ttk.LabelFrame(main)
        frame_level.pack(fill=tk.X, pady=5)
        self.widget_map[frame_level] = "mode_frame"
        ll = ttk.Label(frame_level)
        ll.grid(row=0, column=0, sticky="w")
        self.widget_map[ll] = "level_label"
        rb1 = ttk.Radiobutton(frame_level, text=self.get_txt("level_fast"), variable=self.var_level, value="1")
        rb1.grid(row=0, column=1, padx=6)
        rb5 = ttk.Radiobutton(frame_level, text=self.get_txt("level_bal"), variable=self.var_level, value="5")
        rb5.grid(row=0, column=2, padx=6)
        rb9 = ttk.Radiobutton(frame_level, text=self.get_txt("level_best"), variable=self.var_level, value="9")
        rb9.grid(row=0, column=3, padx=6)
        rbult = ttk.Radiobutton(frame_level, text=self.get_txt("level_ultra"), variable=self.var_level, value="ultra")
        rbult.grid(row=0, column=4, padx=6)
        self.widget_map[rb1] = "level_fast"
        self.widget_map[rb5] = "level_bal"
        self.widget_map[rb9] = "level_best"
        self.widget_map[rbult] = "level_ultra"

        # ========== 可选参数 ==========
        frame_opt = ttk.LabelFrame(main)
        frame_opt.pack(fill=tk.X, pady=5)
        self.widget_map[frame_opt] = "opt_frame"
        ck1 = ttk.Checkbutton(frame_opt, variable=self.var_quiet)
        ck1.grid(row=0, column=0)
        self.widget_map[ck1] = "opt_quiet"
        ck2 = ttk.Checkbutton(frame_opt, variable=self.var_force)
        ck2.grid(row=0, column=1, padx=8)
        self.widget_map[ck2] = "opt_force"
        ck3 = ttk.Checkbutton(frame_opt, variable=self.var_backup)
        ck3.grid(row=0, column=2, padx=8)
        self.widget_map[ck3] = "opt_backup"
        ck4 = ttk.Checkbutton(frame_opt, variable=self.var_strip_reloc)
        ck4.grid(row=1, column=0)
        self.widget_map[ck4] = "opt_strip_reloc"
        ck5 = ttk.Checkbutton(frame_opt, variable=self.var_all_icon)
        ck5.grid(row=1, column=1, padx=8)
        self.widget_map[ck5] = "opt_all_icon"
        ck6 = ttk.Checkbutton(frame_opt, variable=self.var_no_color)
        ck6.grid(row=1, column=2, padx=8)
        self.widget_map[ck6] = "opt_no_color"

        # ========== 功能按钮 ==========
        frame_func = ttk.Frame(main)
        frame_func.pack(fill=tk.X, pady=5)
        bc = ttk.Button(frame_func, command=lambda:self.run_task("compress"))
        bc.pack(side=tk.LEFT, padx=2)
        self.widget_map[bc] = "btn_compress"
        bd = ttk.Button(frame_func, command=lambda:self.run_task("decompress"))
        bd.pack(side=tk.LEFT, padx=2)
        self.widget_map[bd] = "btn_decompress"
        bt = ttk.Button(frame_func, command=lambda:self.run_task("test"))
        bt.pack(side=tk.LEFT, padx=2)
        self.widget_map[bt] = "btn_test"
        bl = ttk.Button(frame_func, command=lambda:self.run_task("list"))
        bl.pack(side=tk.LEFT, padx=2)
        self.widget_map[bl] = "btn_list"
        bfi = ttk.Button(frame_func, command=lambda:self.run_task("fileinfo"))
        bfi.pack(side=tk.LEFT, padx=2)
        self.widget_map[bfi] = "btn_fileinfo"
        ttk.Separator(frame_func, orient=tk.VERTICAL).pack(side=tk.LEFT, padx=8, fill=tk.Y)
        bsave = ttk.Button(frame_func, command=self.save_config)
        bsave.pack(side=tk.LEFT, padx=2)
        self.widget_map[bsave] = "save_cfg"
        bload = ttk.Button(frame_func, command=self.load_config)
        bload.pack(side=tk.LEFT, padx=2)
        self.widget_map[bload] = "load_cfg"
        # 右侧日志控制
        ckscroll = ttk.Checkbutton(frame_func, variable=self.var_auto_scroll)
        ckscroll.pack(side=tk.RIGHT, padx=10)
        self.widget_map[ckscroll] = "auto_scroll"
        bclear = ttk.Button(frame_func, command=self.clear_log)
        bclear.pack(side=tk.RIGHT)
        self.widget_map[bclear] = "clear_log_btn"

        # ========== 日志框 ==========
        frame_log = ttk.LabelFrame(main)
        frame_log.pack(fill=tk.BOTH, expand=True, pady=5)
        self.widget_map[frame_log] = "log_frame"
        self.log_box = scrolledtext.ScrolledText(frame_log, wrap=tk.WORD)
        self.log_box.pack(fill=tk.BOTH, expand=True)

    # 文件选择
    def select_upx(self):
        p = filedialog.askopenfilename(filetypes=[("UPX Executable", "upx.exe"), ("All", "*.*")])
        if p:
            self.var_upx_path.set(p)
    def select_out(self):
        p = filedialog.askdirectory()
        if p:
            self.var_out_dir.set(p)

    def add_files(self):
        # 禁止压缩的VC运行库黑名单
        block_list = {"vcruntime140.dll", "vcruntime140_1.dll", "msvcp140.dll", "msvcp140_1.dll"}
        paths = filedialog.askopenfilenames(filetypes=[("Executable", "*.exe;*.dll;*.pyd"), ("All", "*.*")])
        for f in paths:
            filename = os.path.basename(f).lower()
            # 过滤VC运行库
            if filename in block_list:
                self.log(f"[SKIP] 跳过禁止压缩的VC运行库：{f}")
                continue
            if f not in self.file_list:
                self.file_list.append(f)
                self.log(f"[ADD] {f}")
    def clear_files(self):
        self.file_list.clear()
        self.log("[CLEAR] All target files removed")

    # 日志
    def log(self, msg):
        def ui_update():
            self.log_box.insert(tk.END, msg + "\n")
            if self.var_auto_scroll.get():
                self.log_box.see(tk.END)
        self.root.after_idle(ui_update)
    def clear_log(self):
        self.log_box.delete(1.0, tk.END)

    # 构建命令
    # 构建命令
    def build_cmd(self, task_type):
        upx_bin = self.var_upx_path.get().strip()
        if not os.path.exists(upx_bin):
            messagebox.showerror("Error", self.get_txt("warn_upx_miss"))
            return None
        if len(self.file_list) == 0:
            messagebox.showwarning("Warn", self.get_txt("tip_file_empty"))
            return None
        cmd = [upx_bin]
        # 压缩等级
        level = self.var_level.get()
        if task_type == "compress":
            if level == "ultra":
                cmd.append("--ultra-brute")
            else:
                cmd.append(f"-{level}")
        # 基础参数开关
        if self.var_quiet.get():
            cmd.append("-q")
        if self.var_force.get():
            cmd.append("-f")
        if self.var_backup.get():
            cmd.append("-k")
        if self.var_no_color.get():
            cmd.append("--no-color")

        # 智能判断：存在dll/pyd自动禁用strip-relocs
        has_dll_pyd = any(f.lower().endswith((".dll", ".pyd")) for f in self.file_list)
        if self.var_strip_reloc.get() and not has_dll_pyd:
            cmd.append("--strip-relocs=1")

        if self.var_all_icon.get():
            cmd.append("--compress-icons=3")
        # 任务指令
        if task_type == "decompress":
            cmd.append("-d")
        elif task_type == "test":
            cmd.append("-t")
        elif task_type == "list":
            cmd.append("-l")
        elif task_type == "fileinfo":
            cmd.append("--fileinfo")
        # 输出目录 -o
        outdir = self.var_out_dir.get().strip()
        if outdir and task_type == "compress":
            # 批量输出到目标目录逻辑可自行扩展
            pass
        # 待处理文件
        cmd.extend(self.file_list)
        return cmd

    # 后台执行任务
    def run_task(self, task_type):
        def thread_work():
            global proc
            cmd = self.build_cmd(task_type)
            if cmd is None:
                return
            self.log("="*60)
            self.log(self.get_txt("cmd_title") + " ".join(cmd))
            self.log("="*60)
            startup = subprocess.STARTUPINFO()
            startup.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            proc = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                startupinfo=startup,
                creationflags=0
            )
            # 双线程读取输出
            def read_stream(stream, tag):
                while proc.poll() is None:
                    line = stream.readline()
                    if line:
                        self.log(f"{tag} {line.rstrip()}")
                rest = stream.read()
                if rest.strip():
                    self.log(f"\n{self.get_txt('err_title')}:\n{rest}")
            t1 = threading.Thread(target=read_stream, args=(proc.stdout, "[OUT]"), daemon=True)
            t2 = threading.Thread(target=read_stream, args=(proc.stderr, "[ERR]"), daemon=True)
            t1.start()
            t2.start()
            proc.wait()
            t1.join()
            t2.join()
            self.log("\n" + self.get_txt("task_done").format(proc.returncode))
        threading.Thread(target=thread_work, daemon=True).start()

    # 配置持久化
    def save_config(self):
        cfg = {
            "upx_path": self.var_upx_path.get(),
            "out_dir": self.var_out_dir.get(),
            "level": self.var_level.get(),
            "quiet": self.var_quiet.get(),
            "force": self.var_force.get(),
            "backup": self.var_backup.get(),
            "strip_reloc": self.var_strip_reloc.get(),
            "all_icon": self.var_all_icon.get(),
            "no_color": self.var_no_color.get(),
            "auto_scroll": self.var_auto_scroll.get()
        }
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(cfg, f, ensure_ascii=False, indent=2)
        messagebox.showinfo("OK", "Config Saved")
    def load_config(self):
        if not os.path.exists(CONFIG_FILE):
            return
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                cfg = json.load(f)
            self.var_upx_path.set(cfg.get("upx_path", r"upx\upx.exe"))
            self.var_out_dir.set(cfg.get("out_dir", ""))
            self.var_level.set(cfg.get("level", "5"))
            self.var_quiet.set(cfg.get("quiet", False))
            self.var_force.set(cfg.get("force", False))
            self.var_backup.set(cfg.get("backup", False))
            self.var_strip_reloc.set(cfg.get("strip_reloc", True))
            self.var_all_icon.set(cfg.get("all_icon", False))
            self.var_no_color.set(cfg.get("no_color", False))
            self.var_auto_scroll.set(cfg.get("auto_scroll", True))
        except Exception as e:
            self.log(f"Load config error: {e}")

if __name__ == "__main__":
    try:
        root = tk.Tk()
        app = UPXGUI(root)
        root.mainloop()
    except Exception as e:
        # Nuitka 编译后可能静默崩溃，这里兜底输出错误
        import traceback
        err_msg = traceback.format_exc()
        # 尝试弹窗
        try:
            import tkinter.messagebox as mb
            mb.showerror("Fatal Error", f"Application failed to start:\n\n{err_msg}")
        except Exception:
            pass
        # 也输出到文件方便排查
        with open("upx_crash.log", "w", encoding="utf-8") as f:
            f.write(err_msg)
        sys.exit(1)