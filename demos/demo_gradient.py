import colorsys

from matplotlib import colors

from byubit import Bit
from byubit.bit import css_colors

def rgb_to_hls(r, g, b):
    h, l, s = colorsys.rgb_to_hls(r, g, b)
    return int(h * 360), int(l * 100), int(s * 100)


def color_name_to_hsl(color_name):
    r, g, b = colors.to_rgb(color_name)
    h, l, s = rgb_to_hls(r, g, b)
    return l // 21, s // 51, h


sorted_colors = sorted(css_colors, key=color_name_to_hsl)


def back(bit):
    bit.turn_right()
    bit.turn_right()
    while bit.can_move_front():
        bit.move()
    bit.turn_right()
    bit.move()
    bit.turn_right()


@Bit.empty_world(5, 12)
# @Bit.pictures('demo-images/', ext='svg')
def main(bit):
    count = 0
    while bit.can_move_front() and bit.can_move_left():
        color = sorted_colors[count]
        bit.paint(color)
        bit.move()
        count += 1
        if not bit.can_move_front():
            bit.paint(sorted_colors[count])
            back(bit)

    while bit.can_move_front():
        color = sorted_colors[count]
        bit.paint(color)
        bit.move()
        count += 1

    bit.paint(sorted_colors[count])


if __name__ == '__main__':
    main(Bit.new_bit)
