import os
import subprocess

if __name__ == '__main__':
    for _, _, filenames in os.walk("./"):
        for filename in filenames:
            if filename.endswith(".ui"):
                args = ["pyuic6", "-o", f"../ui_py/ui_{filename}.py", filename]
                subprocess.call(args)
