from byubit import Bit


@Bit.worlds("demo2")
# @Bit.pictures('demo-images/', ext='svg')
def main(bit, first_color, second_color):
    bit.paint(first_color)
    while bit.can_move_front():
        bit.move()
        bit.paint(second_color)
        if bit.can_move_left():
            bit.turn_left()
            bit.snapshot('turned left')


if __name__ == '__main__':
    main(Bit.new_bit, 'blue', second_color='gold')
