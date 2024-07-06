import os
import subprocess

if __name__ == '__main__':
    for _, _, filenames in os.walk("./"):
        for filename in filenames:
            if filename.endswith(".ui"):
                args = ["pyside6-uic", filename, "-o", f"../ui_py/ui_{filename.split('.')[0]}.py"]
                subprocess.call(args)
