from byubit import Bit


def go_paint(bit, color):
    while bit.can_move_front():
        bit.move()
        bit.paint(color)


@Bit.worlds('test-world-right', 'test-world-wrong', 'test-world-right')
def demo(bit: Bit):
    bit.paint('green')
    bit.snapshot(bit.get_color())
    go_paint(bit, 'blue')
    bit.turn_right()
    bit.turn_right()
    bit.turn_right()
    bit.turn_right()


if __name__ == '__main__':
    demo(Bit.new_bit)
