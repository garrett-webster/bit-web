from byubit import Bit


@Bit.worlds("demo2")
@Bit.pictures('demo-images/', ext='svg')
def main(bit):
    bit.paint('gold')
    while bit.front_clear():
        bit.move()
        bit.paint('gold')
        if bit.left_clear():
            bit.left()


if __name__ == '__main__':
    main(Bit.new_bit)
