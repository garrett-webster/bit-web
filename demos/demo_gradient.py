
from byubit import Bit
from byubit.bit import css_colors


sorted_colors = [c for c in css_colors if c.lower() != 'black']


def back(bit):
    bit.turn_right()
    bit.turn_right()
    while bit.can_move_front():
        bit.move()
    bit.turn_right()
    bit.move()
    bit.turn_right()


@Bit.empty_world(12, 12)
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
