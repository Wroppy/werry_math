"""
Build script to create a exe of the gui
"""
import os
import subprocess
import shutil
import sys

exec('import PyInstaller')

# if first argument is -y
if sys.argv[1] == '-y':
    auto_confirm = True
else:
    auto_confirm = False

if sys.platform == 'win32':
    exec('import win32com')


def run_win_cmd(cmd):
    subprocess.call(cmd, shell=True)


def confirm_or_quit(message):
    global auto_confirm
    if auto_confirm:
        return

    while True:
        r = input(f'{message} [Y/N]: ')
        if r == 'Y':
            return
        elif r == 'N':
            print("Exiting")
            quit(0)
        print("input not Y or N")

def confirm(message):
    global auto_confirm
    if auto_confirm:
        return True

    while True:
        r = input(f'{message} [Y/N]: ')
        if r == 'Y':
            return True
        elif r == 'N':
            return False
        print("input not Y or N")

sep = ":"
if sys.platform == "win32":
    sep = ";"

application_name = 'WerryMath'
script_folder = 'scripts'
math_modules = ['chemistry', 'mathmatics', 'physics', 'utilities', 'libraries']
target_folder = 'release'
target_path = os.path.abspath(target_folder)
script_path = os.path.dirname(os.path.realpath(__file__))
build_script = rf"""
pyinstaller
--name {application_name}
--clean
--specpath {target_path}
--workpath {os.path.join(target_path, 'build')}
--distpath {os.path.join(target_path, 'dist')}
-y
-w
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


yes = confirm("is upx installed?")
if yes:
    res = input("where is upx's folder located: ")
    res = r"D:\Downloads\12_2020\upx-3.96-win64\upx-3.96-win64"
    build_script.insert(-1, f"--upx-dir {res}")
    if sys.platform == 'win32':
        build_script.insert(-1, f"--upx-exclude vcruntime140.dll")

print("starting pyinstaller build")
run_win_cmd(' '.join(build_script))
confirm_or_quit("did the build process succeed?")

final_path = os.path.join(target_path, 'dist', application_name)

print("copying werry_math modules")
for module in math_modules:
    print(f'copying {module}')
    shutil.copytree(os.path.join(script_path, module),
                    os.path.join(final_path, script_folder, module))


if os.path.isfile('pythonlib.zip'):
    print(f"found pythonlib, copying")
    shutil.copy(os.path.join(script_path, 'pythonlib.zip'), os.path.join(final_path, 'pythonlib.zip'))


if sys.platform == 'win32':
    from win32com.client import Dispatch

    path = os.path.join(final_path, f'{application_name}.lnk')
    yes = confirm(f"create shortcut at {path}?")
    if yes:
        target = os.path.join(final_path, f'{application_name}.exe')
        wdir = final_path
        icon = target

        shell = Dispatch('WScript.Shell')
        shortcut = shell.CreateShortCut(path)
        shortcut.TargetPath = target
        shortcut.WorkingDirectory = wdir
        shortcut.IconLocation = icon
        shortcut.Arguments = f'cdir={script_folder}'
        shortcut.save()

print(f"Done, the files are at {final_path}")
try:
    os.startfile(final_path)
except:
    subprocess.Popen(['xdg-open', final_path])
