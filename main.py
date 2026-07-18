import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import subprocess
import threading
import json
import os
import sys
import shlex
import time

CONFIG_FILE = "nuitka_config.json"
LANG_CONFIG_FILE = "lang_config.json"
proc = None  # 打包进程全局句柄

# 双语文字字典（新增UPX相关词条）
LANG_DATA = {
    "zh": {
        "window_title": "Nuitka 图形打包工具 v1.0",
        "base_frame": "基础路径配置",
        "script_label": "主Python脚本:",
        "select_btn": "选择",
        "output_label": "输出目录:",
        "venv_label": "虚拟环境(可选):",
        "mode_frame": "打包模式选项",
        "onefile_text": "单文件打包 --onefile",
        "noconsole_text": "无控制台窗口 --windows-disable-console",
        "standalone_text": "独立运行环境 --standalone",
        "follow_import_text": "跟随全部导入模块 --follow-imports",
        "use_upx_text": "启用UPX压缩EXE",
        "upx_path_label": "UPX程序路径:",
        "info_frame": "EXE信息配置(Windows)",
        "ico_label": "程序图标(.ico):",
        "ico_btn": "选择ICO",
        "product_label": "产品名称:",
        "version_label": "版本号:",
        "copyright_label": "版权信息:",
        "adv_frame": "高级配置",
        "cache_label": "缓存目录:",
        "browse_btn": "浏览",
        "exclude_label": "排除模块(逗号分隔):",
        "extra_label": "自定义附加参数:",
        "asset_btn": "添加静态资源(文件/文件夹)",
        "asset_tip": "已添加资源: {}",
        "save_cfg_btn": "保存配置",
        "load_cfg_btn": "加载配置",
        "start_btn": "开始打包",
        "stop_btn": "终止进程",
        "clear_log_btn": "清空日志",
        "log_frame": "打包实时日志",
        "lang_switch_btn": "切换中英文",
        "auto_scroll_text": "自动滚动日志",
        "nuitka_check_title": "未检测到Nuitka",
        "nuitka_check_msg": "未找到Nuitka，是否自动执行 pip install nuitka 安装？",
        "save_cfg_success": "保存成功",
        "save_cfg_tip": "配置已保存至 {}",
        "load_cfg_fail": "加载配置失败: {}",
        "script_empty_err": "请选择有效的主Python脚本",
        "log_nuitka_ok": "[√] Nuitka 已安装",
        "log_install_start": "开始安装 Nuitka ...",
        "log_install_done": "[完成] 安装结束，请重启工具生效",
        "log_kill_proc": "[!] 打包进程已强制终止",
        "log_cmd_title": "执行命令: ",
        "log_err_title": "[错误输出]",
        "log_success": "[√] 打包完成！",
        "log_fail": "[×] 打包失败，退出码: {}",
        "log_exception": "[异常] {}",
        "upx_not_found_warn": "未找到UPX程序，将跳过压缩"
    },
    "en": {
        "window_title": "Nuitka Packer GUI v1.0",
        "base_frame": "Basic Path Config",
        "script_label": "Main Python Script:",
        "select_btn": "Select",
        "output_label": "Output Dir:",
        "venv_label": "Venv Path (Optional):",
        "mode_frame": "Pack Mode Options",
        "onefile_text": "Single File --onefile",
        "noconsole_text": "No Console --windows-disable-console",
        "standalone_text": "Standalone Runtime --standalone",
        "follow_import_text": "Follow All Imports --follow-imports",
        "use_upx_text": "Enable UPX Compress",
        "upx_path_label": "UPX Binary Path:",
        "info_frame": "EXE Info Config (Windows)",
        "ico_label": "Icon File (.ico):",
        "ico_btn": "Choose ICO",
        "product_label": "Product Name:",
        "version_label": "Version:",
        "copyright_label": "Copyright:",
        "adv_frame": "Advanced Settings",
        "cache_label": "Cache Directory:",
        "browse_btn": "Browse",
        "exclude_label": "Exclude Modules (split by comma):",
        "extra_label": "Custom Extra Args:",
        "asset_btn": "Add Static Assets (File/Folder)",
        "asset_tip": "Assets Added: {}",
        "save_cfg_btn": "Save Config",
        "load_cfg_btn": "Load Config",
        "start_btn": "Start Pack",
        "stop_btn": "Stop Process",
        "clear_log_btn": "Clear Log",
        "log_frame": "Real-time Build Log",
        "lang_switch_btn": "Switch Language",
        "auto_scroll_text": "Auto Scroll Log",
        "nuitka_check_title": "Nuitka Not Found",
        "nuitka_check_msg": "Nuitka is missing, auto install via pip install nuitka?",
        "save_cfg_success": "Saved",
        "save_cfg_tip": "Config saved to {}",
        "load_cfg_fail": "Load config failed: {}",
        "script_empty_err": "Please select valid main python script",
        "log_nuitka_ok": "[√] Nuitka detected",
        "log_install_start": "Installing Nuitka ...",
        "log_install_done": "[Done] Install finished, restart app to take effect",
        "log_kill_proc": "[!] Build process terminated",
        "log_cmd_title": "Running Command: ",
        "log_err_title": "[Error Output]",
        "log_success": "[√] Build Completed!",
        "log_fail": "[×] Build failed, exit code: {}",
        "log_exception": "[Error] {}",
        "upx_not_found_warn": "UPX binary not found, skip compression"
    }
}

class NuitkaPackerGUI:
    def __init__(self, root):
        self.root = root
        # 加载语言配置
        self.current_lang = "zh"
        if os.path.exists(LANG_CONFIG_FILE):
            try:
                with open(LANG_CONFIG_FILE, "r", encoding="utf-8") as f:
                    lang_save = json.load(f)
                    self.current_lang = lang_save.get("lang", "zh")
            except Exception:
                self.current_lang = "zh"

        self.root.geometry("920x720")
        self.root.resizable(False, False)

        # 配置变量
        self.var_script = tk.StringVar()
        self.var_output = tk.StringVar()
        self.var_env = tk.StringVar()
        self.var_icon = tk.StringVar()
        self.var_product_name = tk.StringVar()
        self.var_version = tk.StringVar(value="1.0.0.0")
        self.var_copyright = tk.StringVar()
        self.var_onefile = tk.BooleanVar()
        self.var_noconsole = tk.BooleanVar(value=False)  # 默认不勾选，打包弹出CMD
        self.var_follow_imports = tk.BooleanVar(value=True)
        self.var_standalone = tk.BooleanVar(value=True)
        self.var_cache_dir = tk.StringVar()
        self.var_extra_args = tk.StringVar()
        self.var_exclude_modules = tk.StringVar()
        self.var_assets = []
        self.var_auto_scroll = tk.BooleanVar(value=True)
        # UPX新增变量
        self.var_use_upx = tk.BooleanVar(value=False)
        # 默认填充你的UPX路径
        self.var_upx_path = tk.StringVar(value=r"upx\upx.exe")

        # 控件文字映射，用于双语切换
        self.widget_text_map = {}
        self.build_ui()
        self.refresh_lang()
        self.load_config()
        self.check_nuitka_install()

    def get_text(self, key):
        return LANG_DATA[self.current_lang][key]

    def switch_language(self):
        self.current_lang = "en" if self.current_lang == "zh" else "zh"
        with open(LANG_CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump({"lang": self.current_lang}, f, ensure_ascii=False, indent=2)
        self.refresh_lang()

    def refresh_lang(self):
        self.root.title(self.get_text("window_title"))
        for widget, key in self.widget_text_map.items():
            widget.config(text=self.get_text(key))
        self.lbl_asset.config(text=self.get_text("asset_tip").format(len(self.var_assets)))

    def build_ui(self):
        main_frame = ttk.Frame(self.root, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # 顶部语言切换按钮
        lang_btn = ttk.Button(main_frame, command=self.switch_language)
        lang_btn.pack(anchor="e", pady=(0, 6))
        self.widget_text_map[lang_btn] = "lang_switch_btn"

        # ========== 基础路径区域 ==========
        frame_base = ttk.LabelFrame(main_frame)
        frame_base.pack(fill=tk.X, pady=6)
        self.widget_text_map[frame_base] = "base_frame"

        lab_script = ttk.Label(frame_base)
        lab_script.grid(row=0, column=0, sticky="w")
        self.widget_text_map[lab_script] = "script_label"
        ttk.Entry(frame_base, textvariable=self.var_script, width=60).grid(row=0, column=1, padx=5)
        btn_sel_script = ttk.Button(frame_base, command=self.select_script)
        btn_sel_script.grid(row=0, column=2)
        self.widget_text_map[btn_sel_script] = "select_btn"

        lab_out = ttk.Label(frame_base)
        lab_out.grid(row=1, column=0, sticky="w", pady=4)
        self.widget_text_map[lab_out] = "output_label"
        ttk.Entry(frame_base, textvariable=self.var_output, width=60).grid(row=1, column=1, padx=5)
        btn_sel_out = ttk.Button(frame_base, command=self.select_out)
        btn_sel_out.grid(row=1, column=2)
        self.widget_text_map[btn_sel_out] = "select_btn"

        lab_venv = ttk.Label(frame_base)
        lab_venv.grid(row=2, column=0, sticky="w", pady=4)
        self.widget_text_map[lab_venv] = "venv_label"
        ttk.Entry(frame_base, textvariable=self.var_env, width=60).grid(row=2, column=1, padx=5)
        btn_sel_venv = ttk.Button(frame_base, command=self.select_venv)
        btn_sel_venv.grid(row=2, column=2)
        self.widget_text_map[btn_sel_venv] = "select_btn"

        # ========== 打包模式区域（新增UPX复选框） ==========
        frame_mode = ttk.LabelFrame(main_frame)
        frame_mode.pack(fill=tk.X, pady=6)
        self.widget_text_map[frame_mode] = "mode_frame"

        ck_one = ttk.Checkbutton(frame_mode, variable=self.var_onefile)
        ck_one.grid(row=0, column=0)
        self.widget_text_map[ck_one] = "onefile_text"

        ck_con = ttk.Checkbutton(frame_mode, variable=self.var_noconsole)
        ck_con.grid(row=0, column=1, padx=10)
        self.widget_text_map[ck_con] = "noconsole_text"

        ck_std = ttk.Checkbutton(frame_mode, variable=self.var_standalone)
        ck_std.grid(row=0, column=2)
        self.widget_text_map[ck_std] = "standalone_text"

        ck_import = ttk.Checkbutton(frame_mode, variable=self.var_follow_imports)
        ck_import.grid(row=1, column=0)
        self.widget_text_map[ck_import] = "follow_import_text"

        # UPX压缩开关
        ck_upx = ttk.Checkbutton(frame_mode, variable=self.var_use_upx)
        ck_upx.grid(row=1, column=1, padx=10)
        self.widget_text_map[ck_upx] = "use_upx_text"

        # UPX路径输入行
        lab_upx = ttk.Label(frame_mode)
        lab_upx.grid(row=2, column=0, sticky="w", pady=3)
        self.widget_text_map[lab_upx] = "upx_path_label"
        ttk.Entry(frame_mode, textvariable=self.var_upx_path, width=45).grid(row=2, column=1, padx=5)
        btn_upx = ttk.Button(frame_mode, command=self.select_upx)
        btn_upx.grid(row=2, column=2)
        self.widget_text_map[btn_upx] = "browse_btn"

        # ========== EXE信息配置 ==========
        frame_info = ttk.LabelFrame(main_frame)
        frame_info.pack(fill=tk.X, pady=6)
        self.widget_text_map[frame_info] = "info_frame"

        lab_ico = ttk.Label(frame_info)
        lab_ico.grid(row=0, column=0, sticky="w")
        self.widget_text_map[lab_ico] = "ico_label"
        ttk.Entry(frame_info, textvariable=self.var_icon, width=45).grid(row=0, column=1, padx=5)
        btn_ico = ttk.Button(frame_info, command=self.select_icon)
        btn_ico.grid(row=0, column=2)
        self.widget_text_map[btn_ico] = "ico_btn"

        lab_prod = ttk.Label(frame_info)
        lab_prod.grid(row=1, column=0, sticky="w", pady=3)
        self.widget_text_map[lab_prod] = "product_label"
        ttk.Entry(frame_info, textvariable=self.var_product_name, width=30).grid(row=1, column=1, padx=5)

        lab_ver = ttk.Label(frame_info)
        lab_ver.grid(row=1, column=2)
        self.widget_text_map[lab_ver] = "version_label"
        ttk.Entry(frame_info, textvariable=self.var_version, width=15).grid(row=1, column=3, padx=5)

        lab_cop = ttk.Label(frame_info)
        lab_cop.grid(row=2, column=0, sticky="w", pady=3)
        self.widget_text_map[lab_cop] = "copyright_label"
        ttk.Entry(frame_info, textvariable=self.var_copyright, width=60).grid(row=2, column=1, columnspan=3, padx=5)

        # ========== 高级配置 ==========
        frame_adv = ttk.LabelFrame(main_frame)
        frame_adv.pack(fill=tk.X, pady=6)
        self.widget_text_map[frame_adv] = "adv_frame"

        lab_cache = ttk.Label(frame_adv)
        lab_cache.grid(row=0, column=0, sticky="w")
        self.widget_text_map[lab_cache] = "cache_label"
        ttk.Entry(frame_adv, textvariable=self.var_cache_dir, width=40).grid(row=0, column=1, padx=5)
        btn_cache = ttk.Button(frame_adv, command=self.select_cache)
        btn_cache.grid(row=0, column=2)
        self.widget_text_map[btn_cache] = "browse_btn"

        lab_exc = ttk.Label(frame_adv)
        lab_exc.grid(row=1, column=0, sticky="w", pady=3)
        self.widget_text_map[lab_exc] = "exclude_label"
        ttk.Entry(frame_adv, textvariable=self.var_exclude_modules, width=30).grid(row=1, column=1, padx=5)

        lab_extra = ttk.Label(frame_adv)
        lab_extra.grid(row=1, column=2)
        self.widget_text_map[lab_extra] = "extra_label"
        ttk.Entry(frame_adv, textvariable=self.var_extra_args, width=32).grid(row=1, column=3, padx=5)

        btn_asset = ttk.Button(frame_adv, command=self.add_asset)
        btn_asset.grid(row=2, column=0, pady=4)
        self.widget_text_map[btn_asset] = "asset_btn"
        self.lbl_asset = ttk.Label(frame_adv)
        self.lbl_asset.grid(row=2, column=1, sticky="w")

        # ========== 操作按钮区 ==========
        frame_btn = ttk.Frame(main_frame)
        frame_btn.pack(fill=tk.X, pady=5)

        btn_save = ttk.Button(frame_btn, command=self.save_config)
        btn_save.pack(side=tk.LEFT, padx=3)
        self.widget_text_map[btn_save] = "save_cfg_btn"

        btn_load = ttk.Button(frame_btn, command=self.load_config)
        btn_load.pack(side=tk.LEFT, padx=3)
        self.widget_text_map[btn_load] = "load_cfg_btn"

        btn_start = ttk.Button(frame_btn, command=self.start_pack_thread)
        btn_start.pack(side=tk.LEFT, padx=3)
        self.widget_text_map[btn_start] = "start_btn"

        btn_stop = ttk.Button(frame_btn, command=self.kill_proc)
        btn_stop.pack(side=tk.LEFT, padx=3)
        self.widget_text_map[btn_stop] = "stop_btn"

        # 自动滚动复选框
        ck_scroll = ttk.Checkbutton(frame_btn, variable=self.var_auto_scroll)
        ck_scroll.pack(side=tk.RIGHT, padx=10)
        self.widget_text_map[ck_scroll] = "auto_scroll_text"

        # 仅保留一个清空日志按钮（修复重复控件BUG）
        btn_clear = ttk.Button(frame_btn, command=self.clear_log)
        btn_clear.pack(side=tk.RIGHT)
        self.widget_text_map[btn_clear] = "clear_log_btn"

        # ========== 日志框 ==========
        frame_log = ttk.LabelFrame(main_frame)
        frame_log.pack(fill=tk.BOTH, expand=True)
        self.widget_text_map[frame_log] = "log_frame"
        self.log_text = scrolledtext.ScrolledText(frame_log, wrap=tk.WORD)
        self.log_text.pack(fill=tk.BOTH, expand=True)

    # 文件选择弹窗（新增UPX选择）
    def select_script(self):
        path = filedialog.askopenfilename(filetypes=[("Python Script", "*.py"), ("All Files", "*.*")])
        if path:
            self.var_script.set(path)
    def select_out(self):
        path = filedialog.askdirectory()
        if path:
            self.var_output.set(path)
    def select_venv(self):
        path = filedialog.askdirectory()
        if path:
            self.var_env.set(path)
    def select_icon(self):
        path = filedialog.askopenfilename(filetypes=[("ICO Icon", "*.ico")])
        if path:
            self.var_icon.set(path)
    def select_cache(self):
        path = filedialog.askdirectory()
        if path:
            self.var_cache_dir.set(path)
    def select_upx(self):
        path = filedialog.askopenfilename(filetypes=[("UPX Executable", "upx.exe"), ("All Files", "*.*")])
        if path:
            self.var_upx_path.set(path)
    def add_asset(self):
        path = filedialog.askopenfilename() or filedialog.askdirectory()
        if path and path not in self.var_assets:
            self.var_assets.append(path)
            self.lbl_asset.config(text=self.get_text("asset_tip").format(len(self.var_assets)))

    # 日志写入（主线程安全刷新，限制最大行数）
    def log(self, msg):
        MAX_LOG_LINES = 2000
        def _update_ui():
            self.log_text.insert(tk.END, msg + "\n")
            lines = int(self.log_text.count("1.0", tk.END)[0])
            if lines > MAX_LOG_LINES:
                self.log_text.delete("1.0", f"{lines - MAX_LOG_LINES}.0")
            if self.var_auto_scroll.get():
                self.log_text.see(tk.END)
        self.root.after_idle(_update_ui)

    def clear_log(self):
        self.log_text.delete(1.0, tk.END)

    # 检测Nuitka是否安装，缺失一键安装
    def check_nuitka_install(self):
        def check():
            try:
                subprocess.check_output([sys.executable, "-m", "nuitka", "--version"], stderr=subprocess.STDOUT)
                self.log(self.get_text("log_nuitka_ok"))
            except Exception:
                res = messagebox.askyesno(self.get_text("nuitka_check_title"), self.get_text("nuitka_check_msg"))
                if res:
                    self.log(self.get_text("log_install_start"))
                    p = subprocess.Popen([sys.executable, "-m", "pip", "install", "nuitka"],
                                         stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
                    for line in p.stdout:
                        self.log(line.strip())
                    for line in p.stderr:
                        self.log(line.strip())
                    p.wait()
                    self.log(self.get_text("log_install_done"))
        threading.Thread(target=check, daemon=True).start()

    # 强制终止打包进程
    def kill_proc(self):
        global proc
        if proc and proc.poll() is None:
            proc.terminate()
            self.log(self.get_text("log_kill_proc"))

    # 配置保存/加载（新增UPX字段）
    def save_config(self):
        cfg = {
            "script": self.var_script.get(),
            "output": self.var_output.get(),
            "venv": self.var_env.get(),
            "icon": self.var_icon.get(),
            "product": self.var_product_name.get(),
            "version": self.var_version.get(),
            "copyright": self.var_copyright.get(),
            "onefile": self.var_onefile.get(),
            "noconsole": self.var_noconsole.get(),
            "standalone": self.var_standalone.get(),
            "follow_imports": self.var_follow_imports.get(),
            "cache": self.var_cache_dir.get(),
            "exclude": self.var_exclude_modules.get(),
            "extra": self.var_extra_args.get(),
            "assets": self.var_assets,
            "use_upx": self.var_use_upx.get(),
            "upx_path": self.var_upx_path.get()
        }
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(cfg, f, ensure_ascii=False, indent=2)
        messagebox.showinfo(self.get_text("save_cfg_success"), self.get_text("save_cfg_tip").format(CONFIG_FILE))

    def load_config(self):
        if not os.path.exists(CONFIG_FILE):
            return
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                cfg = json.load(f)
            self.var_script.set(cfg.get("script", ""))
            self.var_output.set(cfg.get("output", ""))
            self.var_env.set(cfg.get("venv", ""))
            self.var_icon.set(cfg.get("icon", ""))
            self.var_product_name.set(cfg.get("product", ""))
            self.var_version.set(cfg.get("version", "1.0.0.0"))
            self.var_copyright.set(cfg.get("copyright", ""))
            self.var_onefile.set(cfg.get("onefile", False))
            self.var_noconsole.set(cfg.get("noconsole", False))
            self.var_standalone.set(cfg.get("standalone", True))
            self.var_follow_imports.set(cfg.get("follow_imports", True))
            self.var_cache_dir.set(cfg.get("cache", ""))
            self.var_exclude_modules.set(cfg.get("exclude", ""))
            self.var_extra_args.set(cfg.get("extra", ""))
            self.var_assets = cfg.get("assets", [])
            # 加载UPX配置
            self.var_use_upx.set(cfg.get("use_upx", False))
            self.var_upx_path.set(cfg.get("upx_path", r"upx\upx.exe"))
            self.lbl_asset.config(text=self.get_text("asset_tip").format(len(self.var_assets)))
        except Exception as e:
            self.log(self.get_text("load_cfg_fail").format(str(e)))

    # 构建Nuitka命令（新增UPX参数逻辑）
    def build_command(self):
        cmd = [sys.executable, "-m", "nuitka"]
        cmd.append("--assume-yes")  # 自动同意所有交互，无需手动输入
        script = self.var_script.get().strip()
        if not script or not os.path.exists(script):
            raise Exception(self.get_text("script_empty_err"))
        # 开关参数
        if self.var_onefile.get():
            cmd.append("--onefile")
        if self.var_noconsole.get():
            cmd.append("--windows-disable-console")
        if self.var_standalone.get():
            cmd.append("--standalone")
        if self.var_follow_imports.get():
            cmd.append("--follow-imports")
        # UPX压缩逻辑
        if self.var_use_upx.get():
            upx_bin = self.var_upx_path.get().strip()
            if os.path.exists(upx_bin):
                cmd.append(f"--upx-binary={upx_bin}")
            else:
                self.log(self.get_text("upx_not_found_warn"))
        # 路径/值参数（新版=格式）
        out = self.var_output.get().strip()
        if out:
            cmd.append(f"--output-dir={out}")
        cache = self.var_cache_dir.get().strip()
        if cache:
            cmd.append(f"--cache-dir={cache}")
        ico = self.var_icon.get().strip()
        if ico:
            cmd.append(f"--windows-icon-from-ico={ico}")
        prod = self.var_product_name.get().strip()
        ver = self.var_version.get().strip()
        copyr = self.var_copyright.get().strip()
        if prod:
            cmd.append(f"--product-name={prod}")
        if ver:
            cmd.append(f"--product-version={ver}")
        if copyr:
            cmd.append(f"--copyright={copyr}")
        # 排除模块
        exclude = self.var_exclude_modules.get().strip()
        if exclude:
            for mod in exclude.split(","):
                mod = mod.strip()
                if mod:
                    cmd.append(f"--nofollow-import-to={mod}")
        # 静态资源
        for asset in self.var_assets:
            src = asset
            dst = os.path.basename(asset)
            cmd.append(f"--include-data-dir={src}={dst}")
        # 虚拟环境
        venv = self.var_env.get().strip()
        if venv:
            cmd.append(f"--python-installation={venv}")
        # 自定义附加参数
        extra = self.var_extra_args.get().strip()
        if extra:
            cmd.extend(shlex.split(extra))
        # 入口脚本放末尾
        cmd.append(script)
        return cmd

    # 打包后台线程入口
    def start_pack_thread(self):
        t = threading.Thread(target=self.pack_process, daemon=True)
        t.start()

    # 打包核心逻辑：弹出CMD窗口、双线程分流读取、心跳监控
    def pack_process(self):
        global proc
        try:
            cmd = self.build_command()
            self.log("=" * 60)
            self.log(self.get_text("log_cmd_title") + " ".join(cmd))
            self.log("=" * 60)
            self.log("[INFO] Starting Nuitka process, please wait...")

            # 取消CREATE_NO_WINDOW，打包时弹出CMD黑窗口
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            creation_flags = 0

            proc = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,
                startupinfo=startupinfo,
                creationflags=creation_flags
            )

            # 独立流读取函数
            def stream_reader(stream, tag):
                while proc.poll() is None:
                    line = stream.readline()
                    if line:
                        self.log(f"{tag} {line.rstrip()}")
                    else:
                        time.sleep(0.05)
                rest = stream.read()
                if rest.strip():
                    self.log(f"\n{tag} \n{rest}")

            # 双线程分别读取标准输出、错误输出
            t_out = threading.Thread(target=stream_reader, args=(proc.stdout, "[STDOUT]"), daemon=True)
            t_err = threading.Thread(target=stream_reader, args=(proc.stderr, "[STDERR]"), daemon=True)
            t_out.start()
            t_err.start()

            # 10秒心跳日志，证明进程存活
            def heartbeat():
                while proc and proc.poll() is None:
                    time.sleep(10)
                    self.log("[HEARTBEAT] Building in progress, still running...")
            threading.Thread(target=heartbeat, daemon=True).start()

            # 等待进程结束
            proc.wait()
            t_out.join(timeout=2)
            t_err.join(timeout=2)

            exit_code = proc.returncode
            if exit_code == 0:
                self.log("\n" + self.get_text("log_success"))
            else:
                self.log(f"\n{self.get_text('log_fail').format(exit_code)}")

        except Exception as e:
            import traceback
            err_trace = traceback.format_exc()
            self.log(f"\n{self.get_text('log_exception').format(str(e))}\n详细堆栈：\n{err_trace}")

if __name__ == "__main__":
    root = tk.Tk()
    app = NuitkaPackerGUI(root)
    root.mainloop()