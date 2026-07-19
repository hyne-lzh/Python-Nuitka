"""
UPX Executable Compressor GUI | UPX 可执行文件压缩工具
Features: multi-file, real-time log, config save/load, bilingual UI
"""
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import subprocess
import threading
import json
import os
import sys


CONFIG_FILE = "upx_gui_config.json"
LANG_FILE = "upx_lang.json"

# 双语文本库 / Bilingual text
_T = {
    "zh": {
        "title": "UPX 可执行文件压缩工具",
        "path_frame": "基础路径",
        "upx_label": "UPX 路径:",
        "out_label": "输出目录:",
        "browse": "浏览",
        "add_file": "添加文件",
        "clear_file": "清空列表",
        "mode_frame": "压缩模式",
        "level": "压缩等级:",
        "level_1": "1 - 快速",
        "level_5": "5 - 均衡",
        "level_9": "9 - 高压缩",
        "ultra": "--ultra-brute (极致, 慢)",
        "opt_frame": "可选参数",
        "quiet": "-q 静默",
        "force": "-f 强制",
        "backup": "-k 备份",
        "strip": "--strip-relocs=1 (仅纯EXE)",
        "icons": "--compress-icons=3",
        "nocolor": "--no-color",
        "func_frame": "操作",
        "compress": "压缩",
        "decompress": "解压 -d",
        "test": "校验 -t",
        "list": "查看 -l",
        "fileinfo": "参数 --fileinfo",
        "log_frame": "运行日志",
        "auto_scroll": "自动滚动",
        "clear_log": "清空",
        "lang_btn": "Switch to English",
        "save_cfg": "保存配置",
        "load_cfg": "加载配置",
        "warn_upx": "UPX 程序不存在，请重新选择！",
        "warn_file": "请至少选择一个文件",
        "cmd_prefix": "执行命令:",
        "err_prefix": "错误输出:",
        "done": "完成，退出码: {}",
        "cfg_saved": "配置已保存",
        "ready": "就绪",
    },
    "en": {
        "title": "UPX Executable Compressor",
        "path_frame": "Paths",
        "upx_label": "UPX Binary:",
        "out_label": "Output Dir:",
        "browse": "Browse",
        "add_file": "Add Files",
        "clear_file": "Clear List",
        "mode_frame": "Compression Mode",
        "level": "Compression Level:",
        "level_1": "1 - Fast",
        "level_5": "5 - Balanced",
        "level_9": "9 - Best",
        "ultra": "--ultra-brute (Extreme, Slow)",
        "opt_frame": "Options",
        "quiet": "-q Quiet",
        "force": "-f Force",
        "backup": "-k Backup",
        "strip": "--strip-relocs=1 (Pure EXE only)",
        "icons": "--compress-icons=3",
        "nocolor": "--no-color",
        "func_frame": "Actions",
        "compress": "Compress",
        "decompress": "Decompress -d",
        "test": "Test -t",
        "list": "List -l",
        "fileinfo": "Info --fileinfo",
        "log_frame": "Log",
        "auto_scroll": "Auto Scroll",
        "clear_log": "Clear",
        "lang_btn": "切换到中文",
        "save_cfg": "Save Config",
        "load_cfg": "Load Config",
        "warn_upx": "UPX binary not found, please reselect!",
        "warn_file": "Please select at least one file",
        "cmd_prefix": "Running:",
        "err_prefix": "Error Output:",
        "done": "Finished, exit code: {}",
        "cfg_saved": "Config saved",
        "ready": "Ready",
    },
}

# VC 运行时黑名单 - 压缩会导致程序崩溃
VC_BLOCKLIST = {"vcruntime140.dll", "vcruntime140_1.dll", "msvcp140.dll",
                "msvcp140_1.dll", "vcruntime140d.dll", "msvcp140d.dll",
                "ucrtbase.dll"}


class UPXGUI:
    def __init__(self, root):
        self.root = root
        self.root.geometry("920x700")
        self.root.minsize(800, 600)

        self.lang = self._load_lang()
        self.file_list = []
        self._proc = None
        self._widget_t = {}  # widget -> text_key 映射

        # 变量
        self.var_upx = tk.StringVar(value="upx\\upx.exe")
        self.var_out = tk.StringVar()
        self.var_level = tk.StringVar(value="5")
        self.var_quiet = tk.BooleanVar()
        self.var_force = tk.BooleanVar()
        self.var_backup = tk.BooleanVar()
        self.var_strip = tk.BooleanVar()
        self.var_icons = tk.BooleanVar()
        self.var_nocolor = tk.BooleanVar()
        self.var_auto_scroll = tk.BooleanVar(value=True)

        self._build_ui()
        self._refresh_lang()
        self._load_config()

    # ==================== 语言 ====================

    def _load_lang(self):
        if os.path.exists(LANG_FILE):
            try:
                with open(LANG_FILE, "r", encoding="utf-8") as f:
                    return json.load(f).get("lang", "zh")
            except Exception:
                pass
        return "zh"

    def _save_lang(self):
        try:
            with open(LANG_FILE, "w", encoding="utf-8") as f:
                json.dump({"lang": self.lang}, f, ensure_ascii=False, indent=2)
        except Exception:
            pass

    def t(self, key):
        return _T[self.lang].get(key, key)

    def switch_lang(self):
        self.lang = "en" if self.lang == "zh" else "zh"
        self._save_lang()
        self._refresh_lang()

    def _refresh_lang(self):
        self.root.title(self.t("title"))
        for widget, key in self._widget_t.items():
            try:
                widget.config(text=self.t(key))
            except tk.TclError:
                pass
        self._set_status(self.t("ready"))

    def _bind_text(self, widget, key):
        self._widget_t[widget] = key

    # ==================== UI 构建 ====================

    def _build_ui(self):
        pad = {"padx": 5, "pady": 3}

        # 顶部语言切换
        top = ttk.Frame(self.root)
        top.pack(fill=tk.X, padx=10, pady=(8, 0))
        btn = ttk.Button(top, text="", command=self.switch_lang)
        btn.pack(side=tk.RIGHT)
        self._bind_text(btn, "lang_btn")

        # --- 路径区 ---
        pf = ttk.LabelFrame(self.root)
        pf.pack(fill=tk.X, padx=10, pady=5)
        self._bind_text(pf, "path_frame")

        for col in range(4):
            pf.columnconfigure(col, weight=0)
        pf.columnconfigure(1, weight=1)

        # UPX 路径
        self._label(pf, "upx_label").grid(row=0, column=0, sticky="e", **pad)
        ttk.Entry(pf, textvariable=self.var_upx).grid(row=0, column=1, sticky="ew", **pad)
        btn = ttk.Button(pf, text="", command=self._select_upx, width=6)
        btn.grid(row=0, column=2, **pad)
        self._bind_text(btn, "browse")

        # 输出目录
        self._label(pf, "out_label").grid(row=1, column=0, sticky="e", **pad)
        ttk.Entry(pf, textvariable=self.var_out).grid(row=1, column=1, sticky="ew", **pad)
        btn = ttk.Button(pf, text="", command=self._select_out, width=6)
        btn.grid(row=1, column=2, **pad)
        self._bind_text(btn, "browse")

        # 添加/清空文件
        btn_add = ttk.Button(pf, text="", command=self._add_files)
        btn_add.grid(row=2, column=0, **pad)
        self._bind_text(btn_add, "add_file")
        btn_clr = ttk.Button(pf, text="", command=self._clear_files, width=10)
        btn_clr.grid(row=2, column=1, sticky="w", **pad)
        self._bind_text(btn_clr, "clear_file")

        # --- 压缩等级 ---
        mf = ttk.LabelFrame(self.root)
        mf.pack(fill=tk.X, padx=10, pady=5)
        self._bind_text(mf, "mode_frame")
        self._label(mf, "level").grid(row=0, column=0, **pad)

        for i, (val, key) in enumerate([("1", "level_1"), ("5", "level_5"),
                                         ("9", "level_9"), ("ultra", "ultra")]):
            rb = ttk.Radiobutton(mf, text="", variable=self.var_level, value=val)
            rb.grid(row=0, column=i + 1, **pad)
            self._bind_text(rb, key)

        # --- 可选参数 ---
        of = ttk.LabelFrame(self.root)
        of.pack(fill=tk.X, padx=10, pady=5)
        self._bind_text(of, "opt_frame")

        opts = [
            (self.var_quiet, "quiet"),
            (self.var_force, "force"),
            (self.var_backup, "backup"),
            (self.var_strip, "strip"),
            (self.var_icons, "icons"),
            (self.var_nocolor, "nocolor"),
        ]
        for i, (var, key) in enumerate(opts):
            cb = ttk.Checkbutton(of, text="", variable=var)
            cb.grid(row=i // 3, column=i % 3, sticky="w", **pad)
            self._bind_text(cb, key)

        # --- 操作按钮 ---
        aff = ttk.Frame(self.root)
        aff.pack(fill=tk.X, padx=10, pady=5)

        actions = [
            ("compress", self._compress),
            ("decompress", self._decompress),
            ("test", self._test),
            ("list", self._list),
            ("fileinfo", self._fileinfo),
        ]
        for key, cmd in actions:
            btn = ttk.Button(aff, text="", command=cmd, width=14)
            btn.pack(side=tk.LEFT, padx=2)
            self._bind_text(btn, key)

        # 配置按钮
        ttk.Separator(aff, orient=tk.VERTICAL).pack(side=tk.LEFT, padx=10, fill=tk.Y)
        btn = ttk.Button(aff, text="", command=self._save_config, width=10)
        btn.pack(side=tk.LEFT, padx=2)
        self._bind_text(btn, "save_cfg")
        btn = ttk.Button(aff, text="", command=self._load_config, width=10)
        btn.pack(side=tk.LEFT, padx=2)
        self._bind_text(btn, "load_cfg")

        # --- 日志区 ---
        lf = ttk.LabelFrame(self.root)
        lf.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        self._bind_text(lf, "log_frame")

        ctrl = ttk.Frame(lf)
        ctrl.pack(fill=tk.X, padx=3, pady=2)
        cb = ttk.Checkbutton(ctrl, text="", variable=self.var_auto_scroll)
        cb.pack(side=tk.RIGHT)
        self._bind_text(cb, "auto_scroll")
        btn = ttk.Button(ctrl, text="", command=self._clear_log)
        btn.pack(side=tk.RIGHT, padx=5)
        self._bind_text(btn, "clear_log")

        self.log_box = scrolledtext.ScrolledText(
            lf, wrap=tk.WORD, font=("Consolas", 9),
            bg="#1e1e1e", fg="#d4d4d4", insertbackground="white"
        )
        self.log_box.pack(fill=tk.BOTH, expand=True, padx=3, pady=(0, 3))

        # --- 底部状态栏 ---
        self._status = tk.StringVar()
        ttk.Separator(self.root, orient=tk.HORIZONTAL).pack(fill=tk.X, padx=10)
        ttk.Label(self.root, textvariable=self._status, anchor="w",
                  relief=tk.SUNKEN, padding=(5, 1)).pack(fill=tk.X, padx=10, pady=(0, 8))

    def _label(self, parent, key):
        lbl = ttk.Label(parent, text="")
        self._bind_text(lbl, key)
        return lbl

    # ==================== 文件选择 ====================

    def _select_upx(self):
        path = filedialog.askopenfilename(
            title="Select UPX",
            filetypes=[("UPX", "upx.exe"), ("All", "*.*")]
        )
        if path:
            self.var_upx.set(path)

    def _select_out(self):
        path = filedialog.askdirectory(title="Select output directory")
        if path:
            self.var_out.set(path)

    def _add_files(self):
        paths = filedialog.askopenfilenames(
            title="Select executables",
            filetypes=[("Executables", "*.exe;*.dll;*.pyd"), ("All", "*.*")]
        )
        for p in paths:
            name = os.path.basename(p).lower()
            if name in VC_BLOCKLIST:
                self._log(f"[SKIP] {p} (VC runtime, skip)")
                continue
            if p not in self.file_list:
                self.file_list.append(p)
                self._log(f"[ADD] {p}")

    def _clear_files(self):
        cnt = len(self.file_list)
        self.file_list.clear()
        self._log(f"[CLEAR] {cnt} file(s) removed")

    # ==================== 日志 ====================

    def _log(self, msg):
        def _write():
            self.log_box.insert(tk.END, msg + "\n")
            if self.var_auto_scroll.get():
                self.log_box.see(tk.END)
        self.root.after_idle(_write)

    def _clear_log(self):
        self.log_box.delete("1.0", tk.END)

    def _set_status(self, msg):
        self._status.set(msg)

    # ==================== 命令构建 ====================

    def _build_cmd(self, task):
        upx = self.var_upx.get().strip()
        if not os.path.exists(upx):
            messagebox.showerror("Error", self.t("warn_upx"))
            return None
        if not self.file_list:
            messagebox.showwarning("Warning", self.t("warn_file"))
            return None

        cmd = [upx]

        # 压缩等级
        lv = self.var_level.get()
        if task == "compress":
            cmd.append("--ultra-brute" if lv == "ultra" else f"-{lv}")

        # 可选参数
        if self.var_quiet.get():
            cmd.append("-q")
        if self.var_force.get():
            cmd.append("-f")
        if self.var_backup.get():
            cmd.append("-k")
        if self.var_nocolor.get():
            cmd.append("--no-color")
        if self.var_icons.get():
            cmd.append("--compress-icons=3")

        # strip-relocs 对 DLL/PYD 禁用
        has_dll = any(p.lower().endswith((".dll", ".pyd")) for p in self.file_list)
        if self.var_strip.get() and not has_dll:
            cmd.append("--strip-relocs=1")

        # 输出目录 (仅压缩时)
        out = self.var_out.get().strip()
        if out and task == "compress":
            cmd.extend(["-o" + out])

        # 任务参数
        task_flags = {
            "compress": [],
            "decompress": ["-d"],
            "test": ["-t"],
            "list": ["-l"],
            "fileinfo": ["--fileinfo"],
        }
        cmd.extend(task_flags.get(task, []))

        cmd.extend(self.file_list)
        return cmd

    # ==================== 任务执行 ====================

    def _run_task(self, task):
        def worker():
            cmd = self._build_cmd(task)
            if cmd is None:
                return
            self._log("=" * 60)
            self._log(f"{self.t('cmd_prefix')} {' '.join(cmd)}")
            self._log("=" * 60)
            self._set_status(f"Running {task}...")

            si = subprocess.STARTUPINFO()
            si.dwFlags |= subprocess.STARTF_USESHOWWINDOW

            self._proc = subprocess.Popen(
                cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                text=True, startupinfo=si
            )

            def _read(stream, tag):
                for line in iter(stream.readline, ""):
                    if line:
                        self._log(f"[{tag}] {line.rstrip()}")

            t1 = threading.Thread(target=_read, args=(self._proc.stdout, "OUT"), daemon=True)
            t2 = threading.Thread(target=_read, args=(self._proc.stderr, "ERR"), daemon=True)
            t1.start()
            t2.start()

            self._proc.wait()
            t1.join(timeout=1)
            t2.join(timeout=1)

            rc = self._proc.returncode
            self._log(self.t("done").format(rc))
            self._set_status(self.t("done").format(rc))

        threading.Thread(target=worker, daemon=True).start()

    def _compress(self):
        self._run_task("compress")
    def _decompress(self):
        self._run_task("decompress")
    def _test(self):
        self._run_task("test")
    def _list(self):
        self._run_task("list")
    def _fileinfo(self):
        self._run_task("fileinfo")

    # ==================== 配置持久化 ====================

    def _save_config(self):
        cfg = {
            "upx": self.var_upx.get(),
            "out": self.var_out.get(),
            "level": self.var_level.get(),
            "quiet": self.var_quiet.get(),
            "force": self.var_force.get(),
            "backup": self.var_backup.get(),
            "strip": self.var_strip.get(),
            "icons": self.var_icons.get(),
            "nocolor": self.var_nocolor.get(),
            "auto_scroll": self.var_auto_scroll.get(),
        }
        try:
            with open(CONFIG_FILE, "w", encoding="utf-8") as f:
                json.dump(cfg, f, ensure_ascii=False, indent=2)
            self._set_status(self.t("cfg_saved"))
        except Exception as e:
            self._log(f"[ERR] Save config: {e}")

    def _load_config(self):
        if not os.path.exists(CONFIG_FILE):
            return
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                cfg = json.load(f)
            self.var_upx.set(cfg.get("upx", "upx\\upx.exe"))
            self.var_out.set(cfg.get("out", ""))
            self.var_level.set(cfg.get("level", "5"))
            self.var_quiet.set(cfg.get("quiet", False))
            self.var_force.set(cfg.get("force", False))
            self.var_backup.set(cfg.get("backup", False))
            self.var_strip.set(cfg.get("strip", False))
            self.var_icons.set(cfg.get("icons", False))
            self.var_nocolor.set(cfg.get("nocolor", False))
            self.var_auto_scroll.set(cfg.get("auto_scroll", True))
            self._log("[OK] Config loaded")
        except Exception as e:
            self._log(f"[WARN] Load config: {e}")


if __name__ == "__main__":
    try:
        root = tk.Tk()
        app = UPXGUI(root)
        root.mainloop()
    except Exception:
        import traceback
        err = traceback.format_exc()
        try:
            with open("upx_crash.log", "w", encoding="utf-8") as f:
                f.write(err)
        except Exception:
            pass
        try:
            messagebox.showerror("Fatal Error", f"Startup failed:\n\n{err}")
        except Exception:
            pass
        sys.exit(1)
