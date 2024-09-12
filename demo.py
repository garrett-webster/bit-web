from byubit import Bit


@Bit.worlds('test-world-right', 'test-world-wrong', 'test-world-right')
# @Bit.pictures('demo-images/', ext='svg')
def demo(bit):
    bit.paint('green')
    bit.snapshot(bit.get_color())
    while bit.can_move_front():
        bit.move()


if __name__ == '__main__':
    demo(Bit.new_bit)
