from colors import sorted_colors
from byubit import Bit


def back(bit):
    bit.right()
    bit.right()
    while bit.front_clear():
        bit.move()
    bit.right()
    bit.move()
    bit.right()


@Bit.empty_world(12,12)
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
