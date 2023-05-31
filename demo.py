from byubit import Bit


@Bit.worlds('test-world1', 'test-world2')
@Bit.pictures('demo-images/', ext='svg')
def demo(bit):
    bit.move()
    bit.left()
    bit.left()
    bit.paint('red')
    bit.snapshot('Just painted red')
    bit.move()
    bit.paint('aqua')
    bit.right()
    bit.move()
    bit.right()
    bit.paint('antiquewhite')


demo(Bit.new_bit)
