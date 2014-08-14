import os

_PATH = os.path.abspath(os.path.dirname(__file__))

def get_page(fname, encoding='utf-8'):
    html_page = os.path.join(_PATH, 'samples', fname + ".html")
    if not os.path.exists(html_page):
        return
    html_str = open(html_page, 'rb').read()
    return html_str.decode(encoding)
