from byubit import Bit


@Bit.worlds('test-world1', 'test-world1')
@Bit.pictures('demo-images/', ext='svg')
def demo(bit):
    bit.paint('green')
    while bit.front_clear():
        bit.move()

if __name__ == '__main__':
    demo(Bit.new_bit)
