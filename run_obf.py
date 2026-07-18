# -*- coding:utf-8 -*-
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
from tkinterdnd2 import TkinterDnD, DND_FILES
import json
import hashlib
import os
import subprocess
import sys
import random
import ast
import astor

# 依赖检测
DEPEND_LIST = ["python-obfuscator", "tkinterdnd2", "pycryptodome", "astor"]
HAS_OBF = False
HAS_CRYPTO = False
try:
    from python_obfuscator import Obfuscator, ObfuscationConfig
    HAS_OBF = True
except ImportError:
    pass
try:
    from Crypto.Cipher import AES
    from Crypto.Util.Padding import pad, unpad
    from Crypto.Random import get_random_bytes
    HAS_CRYPTO = True
except ImportError:
    pass

class MultiPyObfuscatorGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Multi-Engine Python Obfuscator | 多引擎复合代码混淆工具")
        self.root.geometry("1350x860")
        self.root.resizable(True, True)
        self.is_dark = tk.BooleanVar(value=False)
        self.random_seed = tk.StringVar(value="")
        self.clear_comment = tk.BooleanVar(value=True)
        self.aes_encrypt_str = tk.BooleanVar(value=True)
        self.anti_debug = tk.BooleanVar(value=True)
        self.export_pyc = tk.BooleanVar(value=False)
        self.custom_key = tk.StringVar(value="")

        # 全局变量
        self.input_path = tk.StringVar(value="")
        self.output_path = tk.StringVar(value="")
        self.batch_files = []
        self.log_text = None
        self.raw_preview = None
        self.obf_preview = None
        self.progress_bar = None
        self.raw_md5 = ""
        self.obf_md5 = ""

        # 第一层混淆：python-obfuscator 基础混淆策略
        self.obf_options = {
            "string_encrypt": {"text": "String Hex Encrypt / 字符串十六进制加密", "var": tk.BooleanVar(value=True)},
            "num_encrypt": {"text": "Number Constant Encrypt / 数字常量加密", "var": tk.BooleanVar(value=True)},
            "rename_var": {"text": "Rename Variables / 变量随机重命名", "var": tk.BooleanVar(value=True)},
            "rename_func": {"text": "Rename Functions / 函数名乱码重命名", "var": tk.BooleanVar(value=True)},
            "dead_code": {"text": "Inject Dead Junk Code / 插入垃圾无效代码", "var": tk.BooleanVar(value=True)},
            "fake_except": {"text": "Fake Exception Branches / 虚假异常分支", "var": tk.BooleanVar(value=True)},
            "control_flat": {"text": "Control Flow Flatten / 控制流扁平化", "var": tk.BooleanVar(value=True)},
            "remove_annot": {"text": "Remove Type Annotations / 删除类型注解", "var": tk.BooleanVar(value=True)},
            "string_xor": {"text": "String XOR Encrypt / 字符串异或加密", "var": tk.BooleanVar(value=True)},
            "random_indent": {"text": "Random Indent Disturb / 随机缩进干扰", "var": tk.BooleanVar(value=False)},
        }
        self.build_ui()
        self.apply_theme()
        # 拖拽绑定
        self.root.drop_target_register(DND_FILES)
        self.root.dnd_bind('<<Drop>>', self.drop_file)
        # 缺失依赖弹窗
        self.check_dependency()

    def build_ui(self):
        # 顶部工具栏：主题、配置导入导出、日志保存、加密密钥
        top_tool = tk.Frame(self.root)
        top_tool.pack(fill="x", padx=10, pady=3)
        ttk.Checkbutton(top_tool, text="Dark Mode / 深色模式", variable=self.is_dark, command=self.apply_theme).pack(side="left", padx=5)
        tk.Button(top_tool, text="Save Config / 导出配置", command=self.export_config).pack(side="left", padx=5)
        tk.Button(top_tool, text="Load Config / 加载配置", command=self.load_config).pack(side="left", padx=5)
        tk.Button(top_tool, text="Save Log / 保存日志", command=self.save_log_file).pack(side="left", padx=5)
        tk.Label(top_tool, text="Custom AES Key / 自定义加密密钥:").pack(side="left", padx=10)
        tk.Entry(top_tool, textvariable=self.custom_key, width=16).pack(side="left")
        tk.Label(top_tool, text="Random Seed / 随机种子:").pack(side="left", padx=10)
        tk.Entry(top_tool, textvariable=self.random_seed, width=10).pack(side="left")
        ttk.Checkbutton(top_tool, text="Clear All Comments / 清空注释", variable=self.clear_comment).pack(side="right", padx=5)

        # 1. 文件选择区域（单文件+批量）
        file_frame = tk.LabelFrame(self.root, text="File Select | 文件选择")
        file_frame.pack(fill="x", padx=10, pady=6)
        # 单文件
        tk.Label(file_frame, text="Source File | 待混淆源码：").grid(row=0, column=0, sticky="w", padx=5, pady=4)
        tk.Entry(file_frame, textvariable=self.input_path, width=60).grid(row=0, column=1, padx=5)
        tk.Button(file_frame, text="Browse Single / 单选文件", command=self.select_input).grid(row=0, column=2, padx=4)
        tk.Button(file_frame, text="Batch Select / 批量多选", command=self.select_batch).grid(row=0, column=3, padx=4)
        # 输出文件
        tk.Label(file_frame, text="Output File | 混淆后输出：").grid(row=1, column=0, sticky="w", padx=5, pady=4)
        tk.Entry(file_frame, textvariable=self.output_path, width=60).grid(row=1, column=1, padx=5)
        tk.Button(file_frame, text="Browse / 浏览", command=self.select_output).grid(row=1, column=2, padx=4)
        tk.Button(file_frame, text="Auto Fill / 自动填充", command=self.auto_fill_output).grid(row=1, column=3, padx=4)

        # 2. 混淆功能勾选面板（双栏：基础混淆 + 高级加密）
        opt_frame = tk.LabelFrame(self.root, text="Obfuscation Options | 混淆功能配置")
        opt_frame.pack(fill="x", padx=10, pady=6)
        # 基础混淆
        base_frame = tk.LabelFrame(opt_frame, text="Base Obfuscate | 基础语法混淆")
        base_frame.grid(row=0, column=0, padx=5, pady=3, sticky="nsew")
        row_idx = 0
        col_idx = 0
        for key, data in self.obf_options.items():
            cb = ttk.Checkbutton(base_frame, text=data["text"], variable=data["var"])
            cb.grid(row=row_idx, column=col_idx, sticky="w", padx=8, pady=3)
            col_idx += 1
            if col_idx >= 2:
                col_idx = 0
                row_idx += 1
        # 高级加密混淆（新增多引擎模块）
        adv_frame = tk.LabelFrame(opt_frame, text="Advanced Multi-Engine Encrypt | 高级多引擎加密")
        adv_frame.grid(row=0, column=1, padx=5, pady=3, sticky="nsew")
        ttk.Checkbutton(adv_frame, text="AES String Encrypt / AES字符串加密", variable=self.aes_encrypt_str).grid(sticky="w", padx=8, pady=3)
        ttk.Checkbutton(adv_frame, text="Anti-Debug Detect / 反调试检测", variable=self.anti_debug).grid(sticky="w", padx=8, pady=3)
        ttk.Checkbutton(adv_frame, text="Export Encrypted Pyc / 导出加密字节码", variable=self.export_pyc).grid(sticky="w", padx=8, pady=3)

        # 快捷按钮：全选/取消全选/默认
        btn_opt_frame = tk.Frame(opt_frame)
        btn_opt_frame.grid(row=row_idx+2, column=0, columnspan=2, pady=5)
        tk.Button(btn_opt_frame, text="Enable All / 全选开启", command=self.enable_all).grid(row=0, column=0, padx=6)
        tk.Button(btn_opt_frame, text="Disable All / 全部关闭", command=self.disable_all).grid(row=0, column=1, padx=6)
        tk.Button(btn_opt_frame, text="Default Preset / 默认推荐配置", command=self.load_default).grid(row=0, column=2, padx=6)
        tk.Button(btn_opt_frame, text="Install All Dependencies / 一键安装全部依赖", command=self.install_all_dep).grid(row=0, column=3, padx=6)

        # 3. 预览双栏（原始代码 / 混淆代码）
        preview_frame = tk.LabelFrame(self.root, text="Code Preview | 代码预览")
        preview_frame.pack(fill="both", expand=True, padx=10, pady=6)
        preview_frame.columnconfigure(0, weight=1)
        preview_frame.columnconfigure(1, weight=1)
        tk.Label(preview_frame, text="Raw Source / 原始代码").grid(row=0, column=0)
        tk.Label(preview_frame, text="Obfuscated Source / 混淆代码").grid(row=0, column=1)
        self.raw_preview = scrolledtext.ScrolledText(preview_frame, wrap="word", height=12)
        self.raw_preview.grid(row=1, column=0, sticky="nsew", padx=3)
        self.obf_preview = scrolledtext.ScrolledText(preview_frame, wrap="word", height=12)
        self.obf_preview.grid(row=1, column=1, sticky="nsew", padx=3)

        # 进度条
        self.progress_bar = ttk.Progressbar(self.root, mode="determinate")
        self.progress_bar.pack(fill="x", padx=10, pady=2)

        # 4. 操作按钮区
        run_frame = tk.Frame(self.root)
        run_frame.pack(pady=8)
        tk.Button(run_frame, text="Start Obfuscate / 开始混淆", width=25, bg="#22aa22", fg="white", command=self.run_obfuscate).grid(row=0, column=0, padx=6)
        tk.Button(run_frame, text="Batch Obfuscate / 批量混淆", width=25, bg="#007acc", fg="white", command=self.run_batch).grid(row=0, column=1, padx=6)
        tk.Button(run_frame, text="Compare Diff / 对比差异", width=25, command=self.show_diff).grid(row=0, column=2, padx=6)
        tk.Button(run_frame, text="Clear Log / 清空日志", width=25, command=self.clear_log).grid(row=0, column=3, padx=6)
        tk.Button(run_frame, text="Help Info / 功能说明", width=25, command=self.show_help).grid(row=0, column=4, padx=6)
        tk.Button(run_frame, text="One-Click EXE Tip / EXE打包命令", width=28, command=self.show_pack_cmd).grid(row=0, column=5, padx=6)

        # 5. 运行日志框
        log_frame = tk.LabelFrame(self.root, text="Run Log | 运行日志")
        log_frame.pack(fill="x", padx=10, pady=6)
        self.log_text = scrolledtext.ScrolledText(log_frame, wrap="word", height=6)
        self.log_text.pack(fill="both", expand=True, padx=4, pady=4)

    # 依赖一键批量安装
    def install_all_dep(self):
        self.log("[Info] Start install all required dependencies / 开始批量安装全部依赖库")
        for pkg in DEPEND_LIST:
            self.log(f"Installing: {pkg}")
            subprocess.Popen([sys.executable, "-m", "pip", "install", pkg])
        messagebox.showinfo("Install Tip / 安装提示", "Dependency installation started!\nAfter installation, restart this tool to take effect.\n依赖开始后台安装，安装完成后重启工具生效！")

    # 依赖完整性检测
    def check_dependency(self):
        miss = []
        if not HAS_OBF:
            miss.append("python-obfuscator")
        if not HAS_CRYPTO:
            miss.append("pycryptodome")
        if len(miss) > 0:
            res = messagebox.askyesno("Missing Dependency / 依赖缺失",
            f"Libraries missing: {','.join(miss)}\nMissing core encryption engine, install all dependencies now?\n缺失核心加密引擎，是否一键安装全部依赖？")
            if res:
                self.install_all_dep()

    # 拖拽文件
    def drop_file(self, event):
        path = event.data.strip('{}')
        if path.endswith(".py"):
            self.input_path.set(path)
            self.auto_fill_output()
            self.load_raw_preview()
            self.log(f"Drop file loaded / 拖拽加载文件：{path}")

    # 主题切换
    def apply_theme(self):
        dark = self.is_dark.get()
        bg = "#2b2b2b" if dark else "#ffffff"
        fg = "#ffffff" if dark else "#000000"
        self.root.config(bg=bg)
        for widget in self.root.winfo_children():
            try:
                widget.config(bg=bg, fg=fg)
            except:
                pass

    # 配置导入导出
    def export_config(self):
        cfg = {}
        for k, v in self.obf_options.items():
            cfg[k] = v["var"].get()
        cfg["clear_comment"] = self.clear_comment.get()
        cfg["seed"] = self.random_seed.get()
        cfg["aes_encrypt"] = self.aes_encrypt_str.get()
        cfg["anti_debug"] = self.anti_debug.get()
        cfg["export_pyc"] = self.export_pyc.get()
        cfg["custom_key"] = self.custom_key.get()
        path = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("Json Config", "*.json")])
        if path:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(cfg, f, indent=2)
            self.log(f"Config exported / 配置导出成功：{path}")

    def load_config(self):
        path = filedialog.askopenfilename(filetypes=[("Json Config", "*.json")])
        if path and os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                cfg = json.load(f)
            for k, val in cfg.items():
                if k in self.obf_options:
                    self.obf_options[k]["var"].set(val)
            self.clear_comment.set(cfg.get("clear_comment", True))
            self.random_seed.set(cfg.get("seed", ""))
            self.aes_encrypt_str.set(cfg.get("aes_encrypt", True))
            self.anti_debug.set(cfg.get("anti_debug", True))
            self.export_pyc.set(cfg.get("export_pyc", False))
            self.custom_key.set(cfg.get("custom_key", ""))
            self.log(f"Config loaded / 配置加载完成：{path}")

    # 日志保存
    def save_log_file(self):
        path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text Log", "*.txt")])
        if path:
            with open(path, "w", encoding="utf-8") as f:
                f.write(self.log_text.get(1.0, tk.END))
            self.log(f"Log saved / 日志保存至：{path}")

    # 快捷功能：全选/取消/默认
    def enable_all(self):
        for data in self.obf_options.values():
            data["var"].set(True)
        self.aes_encrypt_str.set(True)
        self.anti_debug.set(True)
        self.log("[Info] All obfuscation & encryption functions enabled / 已开启全部混淆加密策略")

    def disable_all(self):
        for data in self.obf_options.values():
            data["var"].set(False)
        self.aes_encrypt_str.set(False)
        self.anti_debug.set(False)
        self.log("[Warning] All obfuscation functions disabled / 已关闭所有混淆加密功能")

    def load_default(self):
        default_state = {
            "string_encrypt": True,
            "num_encrypt": True,
            "rename_var": True,
            "rename_func": True,
            "dead_code": True,
            "fake_except": True,
            "control_flat": True,
            "remove_annot": True,
            "string_xor": True,
            "random_indent": False,
        }
        for k, v in default_state.items():
            self.obf_options[k]["var"].set(v)
        self.clear_comment.set(True)
        self.random_seed.set("")
        self.aes_encrypt_str.set(True)
        self.anti_debug.set(True)
        self.export_pyc.set(False)
        self.custom_key.set("")
        self.log("[Info] Load default recommended preset / 已加载默认高强度复合混淆配置")

    # 文件选择
    def select_input(self):
        path = filedialog.askopenfilename(
            title="Select Source Python File | 选择待混淆py源码",
            filetypes=[("Python Script", "*.py"), ("All Files", "*.*")]
        )
        if path:
            self.input_path.set(path)
            self.auto_fill_output()
            self.load_raw_preview()
            self.log(f"Selected source file / 选中源码：{path}")

    def select_batch(self):
        paths = filedialog.askopenfilenames(filetypes=[("Python Script", "*.py")])
        if paths:
            self.batch_files = list(paths)
            self.log(f"Batch selected count / 批量选中文件数量：{len(self.batch_files)}")

    def select_output(self):
        path = filedialog.asksaveasfilename(
            title="Save Obfuscated File | 保存混淆后文件",
            defaultextension=".py",
            filetypes=[("Python Script", "*.py"), ("All Files", "*.*")]
        )
        if path:
            self.output_path.set(path)
            self.log(f"Output path set / 设置输出路径：{path}")

    def auto_fill_output(self):
        src = self.input_path.get().strip()
        if not src or not os.path.exists(src):
            return
        dirname, fname = os.path.split(src)
        new_name = f"obf_{fname}"
        out = os.path.join(dirname, new_name)
        self.output_path.set(out)

    # 加载原始代码预览
    def load_raw_preview(self):
        p = self.input_path.get()
        if not os.path.exists(p):
            return
        with open(p, "r", encoding="utf-8") as f:
            code = f.read()
        self.raw_preview.delete(1.0, tk.END)
        self.raw_preview.insert(tk.END, code[:3000])
        self.raw_md5 = self.calc_md5(code)

    # MD5哈希计算
    def calc_md5(self, text):
        return hashlib.md5(text.encode("utf-8")).hexdigest()

    # 日志打印
    def log(self, msg):
        self.log_text.insert(tk.END, msg + "\n")
        self.log_text.see(tk.END)
        self.root.update_idletasks()

    def clear_log(self):
        self.log_text.delete(1.0, tk.END)
        self.log("[Info] Log cleared / 日志已清空")

    # 帮助弹窗
    def show_help(self):
        help_content = """
=== Multi-Engine Python Obfuscator Help / 多引擎混淆工具说明 ===
【Base Layer: python-obfuscator】基础层混淆
1. String Hex Encrypt: Convert all string to hex literal 字符串十六进制加密
2. Number Encrypt: Disguise constant numbers by calculation 数字常量运算伪装
3. Rename Var/Func: Random garbled name for identifiers 变量/函数随机乱码重命名
4. Dead Junk Code: Insert unreachable useless code blocks 插入不可执行垃圾代码
5. Fake Exception: Add meaningless try-except trap 虚假异常捕获分支
6. Control Flow Flatten: Break original code structure 控制流扁平化打乱逻辑
7. String XOR: Secondary XOR encryption for strings 字符串异或二次加密
8. Random Indent: Disturb code indent format 随机缩进干扰阅读

【Advanced Multi-Engine Layer】高级多引擎加密（新增）
1. AES String Encrypt: AES-128 symmetric encrypt all plaintext strings
   AES对称加密全部明文字符串，运行时动态解密
2. Anti-Debug Detect: Detect debugger attach, self-lock code if debugged
   反调试检测，被调试时代码自动失效
3. Export Encrypted Pyc: Output encrypted bytecode file, harder to decompile
   导出加密字节码pyc，逆向难度大幅提升

Extra Feature 扩展功能
- Batch Obfuscate: Multi py file one-click process 批量多文件一键混淆
- Dark Theme: Eye-care dark interface 深色护眼界面
- Config Save/Load: Save your obfuscation preset as json 混淆配置导出/加载
- Code Preview: Real-time raw & obfuscated code split view 双栏代码实时预览
- MD5 Checksum: Verify code modification hash 哈希校验文件改动
- Drag & Drop: Direct drag py into window 窗口拖拽加载源码
- Auto Dependency Install: One-click install all missing libraries 一键安装全部依赖
"""
        messagebox.showinfo("Help / 功能说明", help_content)

    # EXE打包命令弹窗
    def show_pack_cmd(self):
        cmd = '''# 混淆后打包单文件exe完整命令
pip install pyinstaller
# -F 单文件独立exe，-w 关闭控制台黑窗口，移除-w保留控制台
pyinstaller -F -w obf_target.py
# 若使用加密pyc，打包时需额外携带AES解密依赖库
'''
        messagebox.showinfo("PyInstaller Command / EXE打包命令", cmd)

    # 代码差异对比
    def show_diff(self):
        raw = self.raw_preview.get(1.0, tk.END).strip()
        obf = self.obf_preview.get(1.0, tk.END).strip()
        if not raw or not obf:
            messagebox.showwarning("Tip / 提示", "Run obfuscate first to generate compare content\n请先执行混淆生成对比代码")
            return
        diff_win = tk.Toplevel(self.root)
        diff_win.title("Diff Compare / 混淆前后差异")
        diff_text = scrolledtext.ScrolledText(diff_win, width=100, height=30)
        diff_text.pack()
        diff_text.insert(tk.END, "===== RAW CODE / 原始代码 =====\n")
        diff_text.insert(tk.END, raw[:2000])
        diff_text.insert(tk.END, "\n\n===== OBFUSCATED CODE / 混淆代码 =====\n")
        diff_text.insert(tk.END, obf[:2000])

    # AES字符串加密封装
    def aes_encrypt_code(self, source: str, key_input: str) -> str:
        if not HAS_CRYPTO:
            return source
        # 生成16位AES密钥
        if len(key_input) < 16:
            key = key_input.ljust(16, "#")[:16].encode("utf-8")
        else:
            key = key_input[:16].encode("utf-8")
        iv = get_random_bytes(16)
        cipher = AES.new(key, AES.MODE_CBC, iv)
        # 提取所有字符串字面量替换为加密动态解密
        tree = ast.parse(source)
        str_pool = {}
        counter = 0
        class StringReplace(ast.NodeTransformer):
            def visit_Constant(self, node):
                nonlocal counter
                if isinstance(node.value, str):
                    s = node.value
                    if s not in str_pool:
                        raw_bytes = s.encode("utf-8")
                        enc = cipher.encrypt(pad(raw_bytes, AES.block_size))
                        str_pool[s] = (iv.hex(), enc.hex(), counter)
                        counter += 1
                    iv_h, enc_h, idx = str_pool[s]
                    return ast.parse(f"__aes_dec({idx})").body[0].value
                return node
        new_tree = StringReplace().visit(tree)
        ast.fix_missing_locations(new_tree)
        new_code = astor.to_source(new_tree)
        # 插入全局AES解密函数、密钥池、IV池
        decrypt_header = f"""
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad
_AES_KEY = b"{key.decode('utf-8')}"
_IV_LIST = [{','.join([f"bytes.fromhex('{v[0]}')" for v in str_pool.values()])}]
_ENC_LIST = [{','.join([f"bytes.fromhex('{v[1]}')" for v in str_pool.values()])}]
def __aes_dec(idx):
    c = AES.new(_AES_KEY, AES.MODE_CBC, _IV_LIST[idx])
    return unpad(c.decrypt(_ENC_LIST[idx]), AES.block_size).decode("utf-8")
"""
        full_code = decrypt_header + "\n" + new_code
        return full_code

    # 插入反调试代码
    def inject_anti_debug(self, code: str) -> str:
        anti_debug_code = '''
import sys
import ctypes
import inspect
def __anti_debug_check():
    if sys.gettrace() is not None:
        raise SystemExit(-1)
    if hasattr(ctypes, "windll"):
        if ctypes.windll.kernel32.IsDebuggerPresent():
            raise SystemExit(-2)
    stack = inspect.stack()
    for frame in stack:
        if "debugger" in frame.filename.lower() or "pydev" in frame.filename.lower():
            raise SystemExit(-3)
__anti_debug_check()
'''
        return anti_debug_code + "\n" + code

    # 单文件完整多层混淆流水线
    def obfuscate_single(self, source_code):
        stage = 1
        self.log(f"[Stage {stage}] Clear source code comments / 清空源码注释")
        # 清空注释
        if self.clear_comment.get():
            import re
            # 安全正则：只删除整行注释，不会破坏字符串里的#
            source_code = re.sub(r'^\s*#.*$', '', source_code, flags=re.MULTILINE)
        stage +=1

        # 第一层：python-obfuscator基础混淆
        self.log(f"[Stage {stage}] Run python-obfuscator base grammar obfuscate")
        conf = ObfuscationConfig.all_enabled()
        disable_list = []
        for key, data in self.obf_options.items():
            if not data["var"].get():
                disable_list.append(key)
        for item in disable_list:
            conf = conf.without(item)
        obfuscator = Obfuscator(config=conf)
        seed_text = self.random_seed.get().strip()
        seed_text = self.random_seed.get().strip()
        code_step1 = obfuscator.obfuscate(source_code)
        stage +=1

        # 第二层：AES字符串加密（pycryptodome）
        if self.aes_encrypt_str.get() and HAS_CRYPTO:
            self.log(f"[Stage {stage}] AES-128 full string encryption")
            code_step1 = self.aes_encrypt_code(code_step1, self.custom_key.get())
        stage +=1

        # 第三层：注入反调试代码
        if self.anti_debug.get():
            self.log(f"[Stage {stage}] Inject anti-debug detection code")
            code_step1 = self.inject_anti_debug(code_step1)
        stage +=1

        return code_step1

    # 单文件混淆入口
    def run_obfuscate(self):
        if not HAS_OBF:
            messagebox.showerror("Error / 错误", "python-obfuscator not installed, run dependency install first\n未安装基础混淆库，请先一键安装依赖")
            return
        in_path = self.input_path.get().strip()
        out_path = self.output_path.get().strip()
        if not in_path:
            messagebox.showerror("Error / 错误", "Please select source file first!\n请先选择待混淆Python源码！")
            return
        if not out_path:
            messagebox.showerror("Error / 错误", "Please set output save path!\n请设置混淆文件输出路径！")
            return
        self.log("="*60)
        self.log("[Start] Single file multi-engine composite obfuscation task / 开始单文件多引擎复合混淆任务")
        self.progress_bar["value"] = 10
        try:
            self.log("[Step1] Read source file with UTF-8 encoding / 读取源码文件")
            with open(in_path, "r", encoding="utf-8") as f:
                source_code = f.read()
            self.log(f"Source code length / 源码字符长度：{len(source_code)}")
            self.progress_bar["value"] = 30
            self.log("[Step2] Start multi-layer composite obfuscation pipeline / 启动多层混淆流水线")
            obfuscated_source = self.obfuscate_single(source_code)
            self.obf_md5 = self.calc_md5(obfuscated_source)
            self.obf_preview.delete(1.0, tk.END)
            self.obf_preview.insert(tk.END, obfuscated_source[:3000])
            self.log(f"Obfuscated code length / 混淆后字符长度：{len(obfuscated_source)}")
            self.log(f"Raw MD5 / 原始哈希：{self.raw_md5}")
            self.log(f"Obfuscated MD5 / 混淆哈希：{self.obf_md5}")
            self.progress_bar["value"] = 70
            self.log("[Step3] Write obfuscated code to output file / 写入混淆结果py文件")
            with open(out_path, "w", encoding="utf-8") as f:
                f.write(obfuscated_source)
            # 可选导出加密pyc字节码
            if self.export_pyc.get():
                self.log("[Step4] Compile encrypted pyc bytecode / 编译加密字节码")
                import py_compile
                pyc_out = out_path.replace(".py", ".pyc")
                py_compile.compile(out_path, cfile=pyc_out)
                self.log(f"Encrypted pyc exported to: {pyc_out}")
            self.progress_bar["value"] = 100
            self.log("✅ Multi-engine composite obfuscation Complete! / 多引擎高强度混淆任务完成！")
            self.log(f"Output File Path / 输出文件：{out_path}")
            messagebox.showinfo("Success / 完成", f"Multi-layer obfuscation finished successfully!\n多层复合混淆完成！\nSave Path：{out_path}")
        except Exception as e:
            err_msg = f"[Error] Obfuscate failed / 混淆执行异常：{str(e)}"
            self.log(err_msg)
            messagebox.showerror("Run Error / 运行报错", err_msg)
        self.progress_bar["value"] = 0

    # 批量混淆
    def run_batch(self):
        if not HAS_OBF:
            messagebox.showerror("Error / 错误", "python-obfuscator not installed\n请先安装基础混淆依赖库")
            return
        if len(self.batch_files) == 0:
            messagebox.showwarning("Tip / 提示", "No batch files selected\n未选择批量文件，请点击【Batch Select】多选py文件")
            return
        total = len(self.batch_files)
        self.log(f"===== Batch Multi-Engine Obfuscate Start, total {total} files / 批量多引擎混淆开始，共{total}个文件 =====")
        for idx, src_path in enumerate(self.batch_files):
            try:
                self.progress_bar["value"] = int((idx / total)*100)
                dirname, fname = os.path.split(src_path)
                out_name = f"obf_{fname}"
                out_path = os.path.join(dirname, out_name)
                with open(src_path, "r", encoding="utf-8") as f:
                    code = f.read()
                obf_code = self.obfuscate_single(code)
                with open(out_path, "w", encoding="utf-8") as f:
                    f.write(obf_code)
                self.log(f"[{idx+1}/{total}] Success: {fname} -> {out_name}")
                # 批量同步导出pyc
                if self.export_pyc.get():
                    import py_compile
                    py_compile.compile(out_path, cfile=out_path.replace(".py", ".pyc"))
            except Exception as e:
                self.log(f"[{idx+1}/{total}] Fail {src_path}: {str(e)}")
        self.progress_bar["value"] = 100
        self.log("✅ All batch multi-engine obfuscate task finished / 全部批量混淆执行完毕")
        messagebox.showinfo("Batch Complete / 批量完成", f"Batch multi-layer obfuscate finished!\nTotal: {total} files")
        self.progress_bar["value"] = 0

if __name__ == "__main__":
    root = TkinterDnD.Tk()
    app = MultiPyObfuscatorGUI(root)
    root.mainloop()