import tkinter as tk
from tkinter import ttk, filedialog,messagebox
import subprocess,os

def select_script():
    path = filedialog.askopenfilename(filetypes=[("Python Script", "*.py")])
    if path:
        var_script.set(path)

def run_nuitka_cmd():
    cmd = [r"C:\Program Files\Python314\python.exe","-m","nuitka","--zig","--enable-plugin=tk-inter"]
    is_standalone = var_standalone.get()
    if is_standalone:
        cmd.append("--standalone")
    python_code = code.get()
    file = os.path.exists(python_code)
    if file:
        cmd.append(python_code)
        print(cmd)
    else:
        messagebox.showerror("程序","程序不在")
        return

    proc = subprocess.Popen(cmd,creationflags=subprocess.CREATE_NEW_CONSOLE)


root = tk.Tk()
run_obf_b = ttk.Button(root,text="混淆程序",command=lambda:subprocess.Popen("python run_obf.py"))
upx_b = ttk.Button(root,text="UPX压缩",command=lambda:subprocess.Popen("python upx.py"))
run_nuitka = ttk.Button(root,text="开始打包",command=run_nuitka_cmd)
c_code = ttk.Button(root, text="选择程序", command=select_script)
l_code = ttk.Label(root, text="程序:")
var_standalone = tk.BooleanVar(value=True)
stand = ttk.Checkbutton(root, text="独立运行环境 --standalone",variable=var_standalone)
var_script = tk.StringVar(root)
code = ttk.Entry(root, textvariable=var_script, width=60)
l_code.grid(row=0, column=1)
code.grid(row=0, column=2)
c_code.grid(row=0, column=3)
run_obf_b.grid(row=1, column=1)
upx_b.grid(row=1, column=3)
run_nuitka.grid(row=1, column=2)
stand.grid(row=2, column=1)
root.geometry("800x600")

root.mainloop()
