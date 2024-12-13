import webbrowser
from pathlib import Path
import datetime

from web_bit import Bit

if __name__ == '__main__':
    @Bit.worlds('fix-tree', 'fix-another-tree')
    def run(bit):
        bit.move()
        bit.paint('green')
        bit.turn_left()
        bit.move()
        bit.paint('red')


    run(Bit.new_bit)

    bit_view = Path(__file__.replace('.py', '.html'))
    bit_view.write_text(
        Path('render_bit.html')
        .read_text()
        .replace('"%%DATA%%"', Bit.get_json_results())
        .replace("%%TITLE%%", __file__)
        .replace('%%CODE%%', Path(__file__).read_text())
        .replace('%%TIMESTAMP%%', str(datetime.datetime.now()))
    )
    webbrowser.open(f'file://{bit_view}')
