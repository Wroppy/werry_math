"""
Build script to create a exe of the gui
"""
import os
import subprocess
import shutil
import sys
exec('import PyInstaller')


def run_win_cmd(cmd):
    subprocess.call(cmd)


def confirm_or_quit(message):
    while True:
        r = input(f'{message} [Y/N]: ')
        if r == 'Y':
            return
        elif r == 'N':
            print("Exiting")
            quit(0)
        print("input not Y or N")


sep = ":"
if sys.platform == "win32":
    sep = ";"

math_modules = ['chemistry', 'mathmatics', 'physics', 'utilities', 'libraries']
target_folder = 'release'
target_path = os.path.abspath(target_folder)
script_path = os.path.dirname(os.path.realpath(__file__))
build_script = rf"""
pyinstaller
--name WerryMath
--clean
--onefile
--specpath {target_path}
--workpath {os.path.join(target_path, 'build')}
--distpath {os.path.join(target_path, 'dist')}
-y
-i {os.path.join(script_path, 'gui', 'resources', 'favicon.ico')}
--add-data {os.path.join(script_path, 'gui', 'resources')}{sep}gui{os.path.sep}resources
--hidden-import all.imports
display.py
""".strip().split('\n')

if os.path.isdir(target_path):
    confirm_or_quit(f"target folder {target_folder} exists, delete?")
    shutil.rmtree(target_path)
    # os.rmdir(target_path)
    print("target folder cleared")
else:
    confirm_or_quit(f"create folder {target_path}?")

try:
    os.mkdir(target_path)
except:
    print("Cannot create target folder")
    quit(1)

print("starting pyinstaller build")
run_win_cmd(' '.join(build_script))
confirm_or_quit("did the build process succeed?")

print("copying werry_math modules")
for module in math_modules:
    print(f'copying {module}')
    shutil.copytree(os.path.join(script_path, module), os.path.join(target_path, 'dist', module))

final_path = os.path.join(target_path, 'dist')
print(f"Done, the files are at {final_path}")
try:
    os.startfile(final_path)
except:
    subprocess.Popen(['xdg-open', final_path])