"""
Build standalone .exe for run_obf.py and upx.py using Nuitka.
Recommended: Python 3.11 or 3.12 with latest Nuitka.

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


def build_exe(script: str):
    """Compile a single .py to standalone .exe, then copy exe to project root."""
    print(f"\n{'='*60}")
    print(f"Building: {script}")
    print(f"{'='*60}")

    # Nuitka 编译参数说明：
    # 1. --standalone 自动检测依赖，无需 --enable-plugin=tk-inter
    # 2. --include-package=encodings 解决 Python 3.14 冻结错误
    # 3. 显式 include tkinter 子模块，防止 Nuitka 漏掉
    # 4. --include-package=tkinter 替代已废弃的 --enable-plugin=tk-inter
    cmd = [
        sys.executable, "-m", "nuitka",
        "--standalone",
        "--include-package=tkinter",
        "--include-package=tkinterdnd2",
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
    print(f"Python: {sys.version}")
    print("Compiling run_obf.py and upx.py into standalone .exe files...")
    print("正在将 run_obf.py 和 upx.py 编译为独立 .exe 文件...\n")

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
