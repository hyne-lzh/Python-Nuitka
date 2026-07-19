"""
Build standalone .exe for run_obf.py and upx.py using Nuitka.
Please run this script NOT using Python 3.14+. Python 3.11 or 3.12 is recommended.
如果 Python 3.14 编译失败，请切换到 Python 3.11/3.12 重新编译。

Usage / 用法:
    python build_tools.py
"""
import subprocess
import sys
import os
import shutil


TOOLS = [
    "run_obf.py",   # Multi-engine obfuscator / 多引擎混淆器
    "upx.py",       # UPX compressor GUI / UPX 压缩工具
]

# Python 3.14+ has known issues with Nuitka (encodings module frozen incorrectly).
# Python 3.14+ 与 Nuitka 存在已知兼容性问题（encodings 模块冻结失败）。
_UNSUPPORTED_PYTHON = sys.version_info >= (3, 14)


def build_exe(script: str):
    """Compile a single .py to standalone .exe, then copy exe to project root."""
    print(f"\n{'='*60}")
    print(f"Building: {script}")
    print(f"{'='*60}")

    # 核心修复：
    # 1. --include-package=encodings（而非 --include-module）确保整个包被打进去
    #    这是解决 "Frozen object named 'encodings' is invalid" 的关键
    # 2. 显式 include tkinter 子模块（防止 Nuitka 漏掉 ttk 等）
    # 3. --enable-plugin=tk-inter 处理 Tcl/Tk DLL 捆绑
    cmd = [
        sys.executable, "-m", "nuitka",
        "--standalone",
        "--enable-plugin=tk-inter",
        "--include-package=encodings",
        "--include-module=codecs",
        "--include-module=io",
        "--include-module=abc",
        "--include-module=tkinter",
        "--include-module=tkinter.ttk",
        "--include-module=tkinter.scrolledtext",
        "--include-module=tkinter.filedialog",
        "--include-module=tkinter.messagebox",
        "--include-module=json",
        "--include-module=threading",
        script,
    ]

    project_dir = os.path.dirname(os.path.abspath(__file__))
    result = subprocess.run(cmd, cwd=project_dir, creationflags=subprocess.CREATE_NEW_CONSOLE)

    if result.returncode != 0:
        print(f"\n[FAIL] {script} build failed with exit code {result.returncode}")
        return result.returncode

    # 编译成功后，把 .dist 里的 exe 复制到项目根目录
    base_name = os.path.splitext(script)[0]
    src = os.path.join(project_dir, f"{base_name}.dist", f"{base_name}.exe")
    dst = os.path.join(project_dir, f"{base_name}.exe")

    if os.path.exists(src):
        shutil.copy2(src, dst)
        print(f"[OK] Copied {base_name}.exe to project root / 已复制到项目根目录")

    print(f"\n[OK] {script} built successfully!")
    return 0


if __name__ == "__main__":
    print("Tool EXE Builder | 子工具 EXE 编译器")
    print("Compiling run_obf.py and upx.py into standalone .exe files...")
    print("正在将 run_obf.py 和 upx.py 编译为独立 .exe 文件...\n")

    if _UNSUPPORTED_PYTHON:
        print("=" * 60)
        print("WARNING: Python 3.14+ detected!")
        print("Nuitka may fail with 'encodings' freeze error on Python 3.14+.")
        print("If compilation fails, re-run with Python 3.11 or 3.12.")
        print()
        print("警告：检测到 Python 3.14+！")
        print("Nuitka 在 Python 3.14+ 上可能出现 encodings 冻结错误。")
        print("如编译失败，请换用 Python 3.11 或 3.12 重新运行。")
        print("=" * 60)
        print()

    failed = []
    for tool in TOOLS:
        if not os.path.exists(tool):
            print(f"[SKIP] {tool} not found, skipping / 文件不存在，跳过")
            failed.append(tool)
            continue
        if build_exe(tool) != 0:
            failed.append(tool)

    print(f"\n{'='*60}")
    if failed:
        print(f"Failed: {', '.join(failed)}")
        print(f"编译失败: {', '.join(failed)}")
    else:
        print("All tools built successfully! / 所有子工具编译完成！")
        print("\nReady-to-use .exe files (no Python required):")
        print("以下 .exe 可直接在没有 Python 的环境运行：")
        print("  - run_obf.exe")
        print("  - upx.exe")
