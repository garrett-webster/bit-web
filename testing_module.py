from byubit.bit import Bit
from byubit.core import GREEN

exp_bit = Bit.new_world(3, 3)
exp_bit.world[1, 0] = GREEN
exp_bit.pos = (1, 0)


@Bit.run_all([(Bit.new_world(3, 3), exp_bit)])
def move_bit(bit):
    bit.move()
    bit.paint("green")
