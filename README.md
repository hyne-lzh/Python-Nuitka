# README.md 多引擎复合混淆工具双语文档

# Multi-Engine Python Obfuscator GUI
A bilingual multi-layer composite Python code obfuscation tool based on `python-obfuscator` + AES symmetric encryption + anti-debug detection, with complete Tkinter graphical interactive interface.
一款基于 python-obfuscator + AES对称加密 + 反调试检测构建的双语多层复合Python代码混淆工具，配套完整Tkinter图形交互界面。

## Project Overview | 项目概述
This tool abandons single single-library obfuscation and adopts multi-engine composite reinforcement pipeline, supporting single file obfuscation, batch multi-file processing, code real-time preview, drag-and-drop loading, dark theme switching, configuration import/export, log saving and other practical functions.
本工具摒弃单一库混淆，采用多引擎复合加固流水线，支持单文件混淆、批量多文件处理、代码实时预览、拖拽加载、深色主题切换、配置导入导出、日志保存等实用功能。

### Multi-layer Obfuscation Pipeline | 多层混淆流水线
1. Stage 1: Safe comment cleaning (only delete standalone line `#` comments, no damage to string internal symbols)
   阶段1：安全注释清除（仅删除独立行#注释，不破坏字符串内部符号）
2. Stage 2: Base grammar obfuscation via python-obfuscator (variable/function renaming, dead junk code, control flow flattening, hex/xor string encryption)
   阶段2：python-obfuscator基础语法混淆（变量/函数重命名、垃圾无效代码、控制流扁平化、十六进制/异或字符串加密）
3. Stage 3: AES-128 full text string symmetric encryption (optional, custom 16-bit encryption key supported)
   阶段3：AES-128全文字符串对称加密（可选，支持自定义16位加密密钥）
4. Stage 4: Inject cross-platform anti-debug detection code (block debugger attachment, auto exit program if detected)
   阶段4：注入跨平台反调试检测代码（阻断调试器附加，检测到调试自动退出程序）
5. Optional extra: Compile and export encrypted `.pyc` bytecode file for secondary anti-decompilation reinforcement
   可选附加：编译导出加密pyc字节码文件，二次反编译加固

## Core Functions | 核心功能清单
### 1. File Operation | 文件操作
- Single file selection & automatic output path filling
  单文件选择、输出路径自动填充
- Batch multi-python script one-click obfuscation
  批量多Python脚本一键混淆
- Drag-and-drop file import: Directly drag `.py` into the window to load source code
  拖拽文件导入：直接将py文件拖入窗口加载源码
- Real-time dual split code preview panel (raw source / obfuscated code)
  实时双分栏代码预览面板（原始代码 / 混淆后代码）
- Code difference comparison pop-up window, view text changes before and after obfuscation
  代码差异对比弹窗，查看混淆前后文本改动

### 2. Multi-engine Encryption & Obfuscation | 多引擎加密混淆模块
#### Base Obfuscation Module (python-obfuscator) 基础混淆模块
- String Hex Encrypt / 字符串十六进制加密
- Number Constant Encrypt / 数字常量运算伪装
- Rename Variables / 变量随机乱码重命名
- Rename Functions / 函数随机乱码重命名
- Inject Dead Junk Code / 插入不可执行垃圾分支代码
- Fake Exception Branches / 虚假异常捕获干扰逆向
- Control Flow Flatten / 控制流扁平化打乱原始逻辑
- String XOR Encrypt / 字符串异或二次加密
- Random Indent Disturb / 随机缩进干扰代码可读性
- Remove Type Annotations / 删除类型注解文本

#### Advanced Multi-engine Encryption Module 高级多引擎加密模块
- AES String Encrypt / AES-128对称加密全部明文字符串 (Custom key support 支持自定义密钥)
- Anti-Debug Detect / 跨平台反调试检测（Python trace hook + Windows IsDebuggerPresent API + stack debugger recognition）
- Export Encrypted Pyc / 导出加密字节码pyc文件，提升反编译难度

### 3. Auxiliary Practical Functions | 辅助实用功能
- Dark / Light dual theme switch, eye-care dark mode
  深色/浅色双主题切换，护眼暗色模式
- Obfuscation configuration export & import (save preset as `.json`)
  混淆配置导出/导入（将预设方案保存为json文件）
- Complete running log box, support log export to local txt file
  完整运行日志框，支持日志导出本地txt存档
- One-click full dependency installation button (auto install all missing libraries)
  一键全依赖安装按钮（自动批量安装缺失库）
- MD5 hash calculation, verify text modification before and after obfuscation
  MD5哈希值计算，校验混淆前后文本改动
- Real-time progress bar to display obfuscation execution progress
  实时进度条展示混淆执行进度
- Built-in PyInstaller EXE packaging command prompt pop-up
  内置PyInstaller打包EXE命令提示弹窗
```
## Dependencies Installation | 依赖安装命令
```bash
pip install python-obfuscator tkinterdnd2 pycryptodome astor
```
### Library Function Description | 库作用说明
1. `python-obfuscator`: Base syntax obfuscation core library
   基础语法混淆核心库
2. `tkinterdnd2`: Window drag-and-drop file loading support
   窗口拖拽文件加载支持
3. `pycryptodome`: AES symmetric string encryption engine
   AES对称字符串加密引擎
4. `astor`: Abstract syntax tree parsing tool for string encryption
   字符串加密所需抽象语法树解析工具
5. `tkinter`: Built-in Python GUI library, no extra installation required
   Python自带图形界面库，无需额外安装

## How to Run | 运行方式
1. Save the code as `run_obf.py`
   将源码保存为 run_obf.py
2. Execute the script in terminal
   终端执行脚本：
```bash
python run_obf.py
```
3. After startup, operate through graphical buttons, all text supports Chinese-English dual display
   启动后通过图形按钮操作，全部界面文本支持中英双语同步展示

## GUI Button Guide | 图形界面按钮功能说明
### Top Toolbar | 顶部工具栏
- Dark Mode / 深色模式: Switch light/dark interface theme
  切换亮/暗界面主题
- Save Config / 导出配置: Save current obfuscation switch preset as json file
  将当前混淆勾选预设保存为json文件
- Load Config / 加载配置: Read saved json configuration preset
  读取已保存的json配置预设
- Save Log / 保存日志: Export all running log text to local txt
  将全部运行日志文本导出本地txt
- Custom AES Key / 自定义加密密钥: Input 16-bit custom key for AES string encryption
  输入16位自定义密钥用于AES字符串加密
- Random Seed / 随机种子: Reserved parameter, disabled (python-obfuscator has no set_seed method)
  随机种子：预留参数，已禁用（库无set_seed接口）
- Clear All Comments / 清空注释: Toggle safe single-line comment clearing function
  开关安全单行注释清除功能

### File Selection Area | 文件选择区域
- Source File | 待混淆源码: Input box to display selected single python script path
  输入框展示选中的单个Python脚本路径
- Browse Single / 单选文件: Pop up file selector to pick single source file
  弹出文件选择器选取单个源码文件
- Batch Select / 批量多选: Multi-select multiple `.py` files for batch obfuscation
  多选多个py文件用于批量混淆处理
- Output File | 混淆后输出: Input box to display output save path
  输入框展示输出保存路径
- Browse / 浏览: Pop up save file selector to customize output path
  弹出保存选择器自定义输出路径
- Auto Fill / 自动填充: Auto generate `obf_xxx.py` output path based on source file
  根据源码自动生成 obf_xxx.py 输出路径

### Obfuscation Options Panel | 混淆配置面板
#### Base Obfuscate | 基础语法混淆
Dual-column check box group for all python-obfuscator native obfuscation functions, support one-click full enable/disable
双栏复选框组，包含全部python-obfuscator原生混淆功能，支持一键全开启/全关闭

#### Advanced Multi-Engine Encrypt | 高级多引擎加密
- AES String Encrypt / AES字符串加密: Toggle AES full text string symmetric encryption module
  开关AES全文字符串对称加密模块
- Anti-Debug Detect / 反调试检测: Toggle injection of anti-debug code at file header
  开关在文件头部注入反调试检测代码
- Export Encrypted Pyc / 导出加密字节码: Auto compile `.pyc` bytecode after obfuscation completes
  混淆完成后自动编译pyc字节码文件

#### Preset Shortcut Buttons | 预设快捷按钮
- Enable All / 全选开启: Check all obfuscation & encryption switches
  勾选全部混淆加密开关
- Disable All / 全部关闭: Uncheck all obfuscation & encryption switches
  取消全部混淆加密开关
- Default Preset / 默认推荐配置: Load balanced high-strength composite obfuscation preset
  加载均衡高强度复合混淆预设
- Install All Dependencies / 一键安装全部依赖: Background batch install missing required libraries
  后台批量安装缺失的所需依赖库

### Operation Buttons Area | 操作按钮区
- Start Obfuscate / 开始混淆: Execute multi-layer composite obfuscation for single selected file
  对选中单个文件执行多层复合混淆
- Batch Obfuscate / 批量混淆: Process all batch-selected python files one by one
  逐个处理所有批量选中的Python文件
- Compare Diff / 对比差异: Pop up window to view raw & obfuscated code snippet comparison
  弹窗查看原始与混淆后代码片段对比
- Clear Log / 清空日志: Clear all text in running log box
  清空运行日志框全部文本
- Help Info / 功能说明: Pop up full bilingual function introduction document
  弹窗完整双语功能说明文档
- One-Click EXE Tip / EXE打包命令: Pop up PyInstaller single-file packaging command template
  弹窗PyInstaller单文件打包命令模板

## Fixed Critical Bug List | 已修复关键漏洞清单
1. Removed invalid `set_seed()` call (python-obfuscator library does not support this instance method, eliminate attribute error)
   移除无效set_seed()调用（python-obfuscator库不支持该实例方法，消除属性不存在报错）
2. Rewrote comment cleaning regular expression, only match standalone line `#` comments, avoid truncating string internal text (fix `unterminated string literal` syntax parsing error)
   重写注释清除正则，仅匹配独立行#注释，避免截断字符串内部文本（修复未闭合字符串字面量语法解析报错）
3. Retained AES encryption module but fixed AST string replacement syntax compatibility defects, no longer generate broken cross-line string nodes
   保留AES加密模块，修复AST字符串替换语法兼容缺陷，不再生成破损跨行字符串节点
4. Optimized multi-layer obfuscation execution order, strictly separate comment cleaning, base obfuscation, AES encryption, anti-debug injection to avoid syntax damage
   优化多层混淆执行顺序，严格分隔注释清除、基础混淆、AES加密、反调试注入流程，避免语法损坏
5. Optimized batch processing logic, single file processing failure will not interrupt the entire batch task, log separate record failure file information
   优化批量处理逻辑，单个文件处理失败不会中断整批任务，日志单独记录失败文件信息
[Python-Nuitka](../Python-Nuitka)

## Project File Structure | 项目文件目录
```
obfuscator-tool/
├─ run_obf.py          # Main multi-engine obfuscator GUI source code 多引擎混淆图形工具主程序
├─ README.md           # Bilingual project documentation 本双语项目说明文档
├─ .gitignore          # Git ignore configuration (shield cache, temporary files, pyc, log)
└─ obf_config.json     # Optional custom obfuscation preset configuration file 可选自定义混淆预设配置文件
```

## Notes | 注意事项
1. When using AES string encryption, the target source code cannot contain incomplete escape characters or unclosed triple quotation strings, otherwise AST parsing will fail
   使用AES字符串加密时，目标源码不能包含残缺转义字符、未闭合三引号字符串，否则AST解析会失败
2. The anti-debug code only blocks conventional debuggers, cannot completely prevent reverse analysis; it is recommended to match AES + python-obfuscator composite reinforcement for best effect
   反调试代码仅阻断常规调试器，无法彻底杜绝逆向分析，建议搭配AES+python-obfuscator复合加固效果最优
3. If the obfuscation reports syntax error, you can temporarily uncheck `Clear All Comments` and `AES String Encrypt` to narrow down the problematic module
   若混淆报语法错误，可临时取消勾选「清空注释」「AES字符串加密」缩小故障模块范围
4. The exported `.pyc` bytecode can only run under the same Python major version as the compilation environment
   导出的pyc字节码仅能在编译环境相同大版本Python下运行