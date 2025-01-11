import datetime
import json
import webbrowser
from pathlib import Path
from urllib.parse import quote

from ..rendering import BitRenderer, BitHistoryRecord


class HTMLRenderer(BitRenderer):
    def __init__(self):
        self._html_folder = Path(__file__).parent / 'html'
        self._html_template = self._html_folder / 'render_bit.html'

    def render(self, code_file: Path, histories: dict[str, list[BitHistoryRecord]]):
        """
        Present the history.
        """
        bit_view = code_file.with_suffix('.html')
        bit_view.write_text(
            self._html_template
            .read_text()
            .replace('"%%DATA%%"', json.dumps(histories))
            .replace("%%TITLE%%", code_file.name)
            .replace('%%CODE%%', code_file.read_text())
            .replace('%%TIMESTAMP%%', str(datetime.datetime.now()))
        )
        url = f'file://{quote(str(bit_view))}'
        webbrowser.open(url)
        return url
