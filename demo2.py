from byubit import Bit


@Bit.worlds("demo2")
@Bit.pictures('demo-images/', ext='svg')
def main(bit, first_color, second_color):
    bit.paint(first_color)
    while bit.front_clear():
        bit.move()
        bit.paint(second_color)
        if bit.left_clear():
            bit.left()


if __name__ == '__main__':
    main(Bit.new_bit, 'blue', second_color='gold')
