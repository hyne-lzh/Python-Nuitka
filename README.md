# Python-Nuitka Toolchain | Python-Nuitka 工具链

A complete Python code protection and distribution toolchain: **Multi-Engine Obfuscation → Nuitka EXE Compilation → UPX Compression**, three tools working together to maximize the protection strength and minimize the distribution size of Python programs.

一套完整的 Python 代码保护与分发工具链：**多引擎代码混淆 → Nuitka EXE 编译 → UPX 压缩优化**，三项工具协同工作，最大化提升 Python 程序的保护强度并缩减分发体积。

---

## Project Overview | 项目概览

| Tool / 工具 | File / 文件 | Description / 功能 |
|-------------|-------------|---------------------|
| Multi-Engine Obfuscator / 多引擎混淆器 | `run_obf.py` | python-obfuscator + AES encryption + anti-debug → outputs obfuscated `.py` |
|  |  | python-obfuscator + AES 加密 + 反调试 → 输出混淆后的 `.py` |
| UPX Compressor / UPX 压缩器 | `upx.py` | UPX GUI frontend for compressing final `.exe` size |
|  |  | UPX GUI 前端，用于压缩最终 `.exe` 体积 |
| One-Click Launcher / 一键打包启动器 | `main2-exe.py` | Integrated launcher: Nuitka compilation + obfuscator + UPX compression |
|  |  | 集成启动器：调用 Nuitka 编译 + 混淆器 + UPX 压缩 |

Typical workflow | 典型工作流：

```
Source .py → [run_obf.py Multi-Layer Obfuscation] → Obfuscated .py
原始 .py 源码 → [run_obf.py 多层混淆] → 混淆 .py
                                                   → [Nuitka Compile] → .exe
                                                   → [Nuitka 编译] → .exe
                                                   → [UPX Compress] → Compact final exe
                                                   → [UPX 压缩] → 精简最终 exe
```

---

## 1. Multi-Engine Obfuscator | 多引擎复合混淆工具 (`run_obf.py`)

A multi-layer composite Python code obfuscation tool based on python-obfuscator + AES-128 symmetric encryption + anti-debug detection, with a complete Tkinter graphical interface.

基于 python-obfuscator + AES-128 对称加密 + 反调试检测的多层复合 Python 代码混淆工具，配套完整 Tkinter 图形交互界面。

### Multi-Layer Obfuscation Pipeline | 多层混淆流水线

| Stage / 阶段 | Operation / 操作 | Description / 说明 |
|--------------|-------------------|---------------------|
| Stage 1 | Safe Comment Cleaning / 安全注释清除 | Only delete standalone `#` comments, never damage characters inside strings |
|  |  | 仅删除独立行 `#` 注释，不破坏字符串内部符号 |
| Stage 2 | Base Obfuscation via python-obfuscator | Variable/function renaming, dead junk code, control flow flattening, hex/xor string encryption |
|  | python-obfuscator 基础混淆 | 变量/函数重命名、垃圾无效代码、控制流扁平化、十六进制/异或字符串加密 |
| Stage 3 | AES-128 String Encryption | Full-text string symmetric encryption (optional, custom 16-byte key supported) |
|  | AES-128 字符串加密 | 全文字符串对称加密（可选，支持自定义 16 位密钥） |
| Stage 4 | Anti-Debug Injection / 反调试检测注入 | Cross-platform anti-debug code; auto-exit when debugger detected |
|  |  | 跨平台反调试代码，检测到调试自动退出 |
| Stage 5 | Export Encrypted Pyc / 导出加密 pyc | Optional compilation to encrypted `.pyc` bytecode for secondary anti-decompilation |
|  |  | 可选编译导出加密 `.pyc` 字节码文件，二次反编译加固 |

### Core Features | 核心功能

- **File Operations / 文件操作**：Single file selection, batch multi-file processing, drag-and-drop loading, auto-fill output path
  单文件选择、批量多文件处理、拖拽加载、自动填充输出路径
- **Code Preview / 代码预览**：Real-time dual-pane split view (raw code / obfuscated code), diff comparison popup
  原始代码 / 混淆代码双栏实时预览，差异对比弹窗
- **10 Base Obfuscation Strategies / 10 项基础混淆策略**：String hex encrypt, number constant encrypt, variable/function renaming, dead junk code injection, fake exception branches, control flow flattening, string XOR encrypt, random indent disturbance, type annotation removal
  字符串十六进制加密、数字常量加密、变量/函数重命名、垃圾代码注入、虚假异常分支、控制流扁平化、字符串异或加密、随机缩进干扰、类型注解删除
- **3 Advanced Encryption Modules / 3 项高级加密**：AES string encryption, anti-debug detection, export encrypted bytecode
  AES 字符串加密、反调试检测、导出加密字节码
- **Auxiliary / 辅助功能**：Dark/light dual theme, config import/export (JSON), log saving, one-click dependency install, MD5 checksum, progress bar
  深色/浅色双主题、配置导入导出（JSON）、日志保存、一键安装依赖、MD5 校验、进度条展示
- **Presets / 预设方案**：Enable all, disable all, default recommended preset (one-click balanced high-strength config)
  全选开启、全部关闭、默认推荐配置（一键加载均衡高强度预设）

### GUI Layout Overview | GUI 布局速览

```
┌─ Top Toolbar: Dark Mode / Config Save&Load / Log Save / AES Key / Clear Comments ──────────────────┐
┌─ 顶部工具栏：主题切换 / 配置导入导出 / 日志保存 / AES密钥 / 清空注释 ──────────────────────────────────┘
├─ File Select: Source Path + Single/Batch Buttons | Output Path + Browse/Auto Fill ─────────────────┤
├─ 文件选择区：源文件路径 + 单选/批量按钮 | 输出路径 + 浏览/自动填充按钮 ──────────────────────────────────┤
├─ Obfuscation Options Panel / 混淆配置面板 ──────────────────────────────────────────────────────────┤
│  ┌── Base Obfuscate (10 options, 2 columns) ──┐  ┌── Advanced Multi-Engine Encrypt ──┐           │
│  │ String Encrypt / Number Encrypt            │  │ AES String Encrypt                │           │
│  │ Rename Var / Rename Func                   │  │ Anti-Debug Detect                 │           │
│  │ Dead Code / Fake Exception                 │  │ Export Encrypted Pyc              │           │
│  │ Control Flat / Remove Annot                │  └──────────────────────────────────┘           │
│  │ String XOR / Random Indent                 │                                                │
│  └────────────────────────────────────────────┘                                                │
│  [Enable All] [Disable All] [Default Preset] [Install All Dependencies]                         │
│  [全选开启] [全部关闭] [默认推荐] [一键安装依赖]                                                  │
├─ Code Preview: Dual Pane Split (Raw Source | Obfuscated Source) ─────────────────────────────────┤
├─ 代码预览：双栏分屏（原始代码 | 混淆代码）─────────────────────────────────────────────────────────┤
├─ Progress Bar / 进度条 ───────────────────────────────────────────────────────────────────────────┤
├─ Buttons: [Start Obfuscate] [Batch Obfuscate] [Compare Diff] [Clear Log] [Help] [EXE Pack Cmd] ──┤
├─ 操作按钮：[开始混淆] [批量混淆] [对比差异] [清空日志] [功能说明] [EXE打包命令] ──────────────────────┤
└─ Run Log Box / 运行日志框 ───────────────────────────────────────────────────────────────────────┘
```

---

## 2. UPX Executable Compressor | UPX 可执行文件压缩工具 (`upx.py`)

A graphical interface for the UPX command-line tool, supporting compression optimization for compiled `.exe` / `.dll` / `.pyd` files.

为 UPX 命令行工具提供图形化界面，支持对已编译的 `.exe` / `.dll` / `.pyd` 文件进行压缩优化。

### Feature List | 功能清单

- **Compression Levels / 压缩等级**：Fast(1) / Balanced(5) / Best(9) / Ultra Brutal(--ultra-brute)
  快速(1) / 均衡(5) / 高压缩(9) / 极致压缩(--ultra-brute)
- **Operation Modes / 操作模式**：Compress / Decompress(-d) / Test(-t) / List Info(-l) / Show Params(--fileinfo)
  压缩 / 解压(-d) / 校验(-t) / 查看信息(-l) / 查看参数(--fileinfo)
- **Extra Options / 可选参数**：Quiet(-q), Force(-f), Keep Backup(-k), Strip Relocs, Compress Icons, No Color
  静默输出(-q)、强制压缩(-f)、保留备份(-k)、剥离重定位、压缩全部图标、无彩色输出
- **Safety Mechanism / 安全机制**：Auto-filter forbidden VC runtime libraries (`vcruntime140.dll`, `msvcp140.dll`, etc.)
  自动过滤禁止压缩的 VC 运行库（`vcruntime140.dll`、`msvcp140.dll` 等）
- **Smart Detection / 智能检测**：Auto-disable `--strip-relocs` when `.dll` / `.pyd` files are present to prevent crashes
  存在 `.dll` / `.pyd` 时自动禁用 `--strip-relocs` 防止崩溃
- **Bilingual Interface / 双语界面**：One-click Chinese/English switch, full UI text internationalization
  中英文一键切换，界面文本完整国际化
- **Config Persistence / 配置持久化**：Save/load JSON config file
  保存/加载 JSON 配置文件
- **Real-time Log / 实时日志**：Background threaded execution, separated stdout/stderr output with auto-scroll
  后台线程执行命令，标准输出/错误输出分离显示，支持自动滚动

---

## 3. One-Click Launcher | 一键打包启动器 (`main2-exe.py`)

Integrated launcher GUI connecting all three tools into a unified entry point.

集成启动器 GUI，将三个工具串联为统一入口：

| Button / 按钮 | Function / 功能 |
|---------------|-----------------|
| Obfuscate Program / 混淆程序 | Launch `run_obf.exe` for source code obfuscation |
|  | 调用 `run_obf.exe` 进行源码混淆 |
| UPX Compress / UPX 压缩 | Launch `upx.exe` for EXE compression |
|  | 调用 `upx.exe` 进行 EXE 压缩 |
| Select Program / 选择程序 | Select the `.py` source file to compile |
|  | 选择待编译的 `.py` 源文件 |
| Start Package / 开始打包 | Invoke Nuitka (`--zig` + `--enable-plugin=tk-inter`) to compile into EXE |
|  | 调用 Nuitka（`--zig` + `--enable-plugin=tk-inter`）编译为 EXE |
| Standalone Mode / 独立运行环境 | Enable `--standalone` mode when checked |
|  | 勾选后启用 `--standalone` 模式 |

---

## Dependencies | 依赖安装

```bash
# Obfuscator dependencies / 混淆器依赖
pip install python-obfuscator tkinterdnd2 pycryptodome astor

# Packaging dependency / 打包依赖
pip install nuitka

# UPX is bundled in the upx/ directory, no extra installation needed
# UPX 已内置在 upx/ 目录，无需额外安装
```

### Dependency Description | 依赖作用说明

| Library / 库 | Purpose / 用途 |
|--------------|----------------|
| `python-obfuscator` | Base syntax obfuscation core library / 基础语法混淆核心库 |
| `tkinterdnd2` | Drag-and-drop file loading support / 窗口拖拽文件加载支持 |
| `pycryptodome` | AES-128 symmetric string encryption engine / AES-128 对称字符串加密引擎 |
| `astor` | AST parsing tool for string encryption code transformation / AST 语法树解析，用于字符串加密时的代码转换 |
| `nuitka` | Python-to-C compiler, generates native EXE / Python 到 C 编译器，生成原生 EXE |

---

## How to Run | 运行方式

### Obfuscator Tool | 混淆工具
```bash
python run_obf.py
```

### UPX Compressor Tool | UPX 压缩工具
```bash
python upx.py
```

### One-Click Launcher | 一键启动器
```bash
python main2-exe.py
```

---

## Project File Structure | 项目文件结构

```
Python-Nuitka/
├── run_obf.py          # Multi-engine obfuscator GUI / 多引擎复合混淆 GUI 主程序
├── upx.py              # UPX compressor GUI / UPX 压缩图形界面
├── main2-exe.py        # One-click packaging launcher / 一键打包启动器
├── README.md           # This document / 本说明文档
└── upx/                # UPX executable and docs / UPX 可执行文件及文档
    ├── upx.exe         # UPX main binary / UPX 主程序
    ├── LICENSE         # UPX license / UPX 许可证
    ├── README / NEWS   # UPX documentation / UPX 说明文档
    └── upx-doc.html    # UPX detailed docs / UPX 详细文档
```

---

## Notes | 注意事项

1. When using AES string encryption, the source code must not contain incomplete escape characters or unclosed triple-quoted strings, otherwise AST parsing will fail.
   使用 AES 字符串加密时，目标源码不能包含残缺转义字符或未闭合的三引号字符串，否则 AST 解析会失败。
2. Anti-debug code only blocks conventional debuggers (e.g. IDE debugger, `pdb`) and cannot completely prevent reverse analysis. For best results, combine AES + python-obfuscator for composite hardening.
   反调试代码仅阻断常规调试器（如 IDE 调试、`pdb`），无法彻底杜绝逆向分析，建议搭配 AES + python-obfuscator 复合加固效果最优。
3. If obfuscation reports a syntax error, try unchecking "Clear All Comments" and "AES String Encrypt" one by one to isolate the problematic module.
   若混淆报语法错误，可依次取消「清空注释」「AES 字符串加密」逐个排查问题模块。
4. Exported `.pyc` bytecode can only run under the same Python major version as the compilation environment.
   导出的 `.pyc` 字节码仅能在相同 Python 大版本下运行。
5. When UPX-compressing `.dll` / `.pyd` files, do NOT enable `--strip-relocs`. The tool has built-in auto-detection for this (but manual confirmation is still recommended).
   UPX 压缩 `.dll` / `.pyd` 文件时请勿勾选 `--strip-relocs`，工具已内置自动检测（仍需人工确认）。
6. Nuitka compilation requires a configured C compiler toolchain (zig is recommended). The first compilation may take a long time.
   Nuitka 编译需要配置 C 编译器环境（推荐 zig），首次编译耗时较长。
