from byubit import Bit
from byubit.core import css_colors


@Bit.worlds('democsv')
def main(bit):
    for color in css_colors:
        if bit.front_clear():
            bit.paint(color)
            bit.move()
        else:
            return


if __name__ == '__main__':
    main(Bit.new_bit)
