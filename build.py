import os
import subprocess


def run_win_cmd(cmd):
    result = []
    process = subprocess.Popen(cmd,
                               shell=True,
                               stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE)
    for line in process.stdout:
        result.append(line)
    errcode = process.returncode
    for line in result:
        print(line)
    if errcode is not None:
        print(f'cmd {cmd} failed, see above for details')
        quit()


def confirm_or_quit(message):
    while True:
        r = input(f'{message} [Y/N]')
        if r == 'Y':
            return
        elif r == 'N':
            quit(0)
        print("input not Y or N")


target_folder = 'release'
build_script = r"""
pyinstaller --onefile --add-data gui\resources;gui\resources --add-data mathmatics\webserver;mathmatics\webserver --hidden-import all.imports display.py
""".strip()

path = os.path.abspath(target_folder)
confirm_or_quit(f"Creating folder {path}")
try:
    os.mkdir(path)
except:
    print("Cannot create target folder")
    quit(1)

run_win_cmd(build_script)
