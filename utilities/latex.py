import tempfile

import sympy

from utilities.fs import open_file


def open_latex(latex):
    """
    Create and open latex text
    :param latex:
    :return:
    """
    with tempfile.NamedTemporaryFile('w', delete=False, suffix='.png') as f:
        path = f.name
        try:
            sympy.preview(f"${latex}$", viewer='file', filename=path,
                          dvioptions=['-D', '600', '-z', '0', '--truecolor'], euler=False)
        except Exception as e:
            print("error writing latex file")
            print(e)
            return
        print(f"temp file: {path}")
        open_file(path)
