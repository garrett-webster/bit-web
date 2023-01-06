from byubit import Bit


@Bit.worlds('test-world1')
def move_bit(bit):
    bit.paint("green")


move_bit(Bit.new_bit)
