import tempfile
import pathlib

from utilities.fs import open_url


def start_desmos(equation: str = None):
    """
    Starts Desmos in a web browser
    :param equation: Optional equation to graph
    :return: None
    """
    # read template html file
    url = str(pathlib.Path(__file__).parent.absolute()) + '/desmos.html'
    with open(url, 'r') as f:
        html = f.readlines()

    # add equation if exist
    if equation is not None:
        html.insert(3, f"<script>var e = '{equation}';</script>")
    else:
        html.insert(3, f"<script>var e = null;</script>")
    html = '\n'.join(html)

    # create temp file with html
    with tempfile.NamedTemporaryFile('w', delete=False, suffix='.html') as f:
        url = 'file://' + f.name
        f.write(html)

        # open html
        print("temp file:", f.name)
        open_url(url)
