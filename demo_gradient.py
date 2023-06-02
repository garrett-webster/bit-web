from byubit import Bit
import colorsys
from matplotlib import colors
from byubit.core import css_colors

def rgb_to_hls(r, g, b):
    h, l, s = colorsys.rgb_to_hls(r, g, b)
    return int(h * 360), int(l * 100), int(s * 100)


def color_name_to_hsl(color_name):
    r, g, b = colors.to_rgb(color_name)
    h, l, s = rgb_to_hls(r, g, b)
    return l//21, s//51,  h


sorted_colors = sorted(css_colors, key=color_name_to_hsl)


def back(bit):
    bit.right()
    bit.right()
    while bit.front_clear():
        bit.move()
    bit.right()
    bit.move()
    bit.right()


@Bit.empty_world(12,12)
@Bit.pictures('demo-images/', ext='svg')
def main(bit):
    count = 0
    while bit.front_clear() and bit.left_clear():
        color = sorted_colors[count]
        bit.paint(color)
        bit.move()
        count += 1
        if not bit.front_clear():
            bit.paint(sorted_colors[count])
            back(bit)

    while bit.front_clear():
        color = sorted_colors[count]
        bit.paint(color)
        bit.move()
        count += 1

    bit.paint(sorted_colors[count])


if __name__ == '__main__':
    main(Bit.new_bit)
