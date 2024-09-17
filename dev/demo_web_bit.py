from pathlib import Path

from web_bit import Bit
import webview


if __name__ == '__main__':
    @Bit.worlds('fix-tree','fix-another-tree')
    def run(bit):
        bit.move()
        bit.paint('green')
        bit.turn_left()
        bit.move()
        bit.paint('red')


    run(Bit.new_bit)

    html = (Path('render_bit.html')
            .read_text()
            .replace('"%%DATA%%"', Bit.get_json_results()))
    window = webview.create_window('Bit Results', html=html)
    webview.start()
    print(Bit.get_json_results())
