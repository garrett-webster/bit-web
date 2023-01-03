from byubit import Bit


@Bit.empty_world(5, 3)
def will_fail(bit):
    bit.right()
    bit.move()


will_fail(Bit.new_bit)
