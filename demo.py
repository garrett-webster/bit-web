from byubit import Bit


@Bit.run('test-world1', 'test-world2')
def demo(bit):
    bit.move()
    bit.left()
    bit.left()
    bit.move()
    bit.paint('green')
    bit.right()
    bit.right()
