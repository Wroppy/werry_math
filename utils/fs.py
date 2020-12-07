import subprocess, os, platform
import webbrowser


def open_file(filepath: str):
    """
    https://stackoverflow.com/questions/434597/open-document-with-default-os-application-in-python-both-in-windows-and-mac-os

    :param filepath:
    :return:
    """
    if platform.system() == 'Darwin':  # macOS
        subprocess.call(('open', filepath))
    elif platform.system() == 'Windows':  # Windows
        os.startfile(filepath)
    else:  # linux variants
        subprocess.call(('xdg-open', filepath))


def open_url(url: str):
    webbrowser.open(url=url)