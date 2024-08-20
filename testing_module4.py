from byubit import Bit


@Bit.worlds('test-world-right')
def paint(bit):
    # This method will fail because the argument passed to it is not Bit.new_bit
    bit.paint("green")


@Bit.worlds('test-world-right')
def run(bit):
    paint(bit)


run(Bit.new_bit)
