from byubit.bit import Bit
from byubit.core import GREEN

exp_bit = Bit.new_world(3, 3)
exp_bit.world[1, 0] = GREEN
exp_bit.pos = (1, 0)


@Bit.run(Bit.new_world(3, 3), exp_bit)
def move_bit(bit):
    bit.move()
    bit.paint("green")


# In student hands, there should never be more than one
#  @Bit.run in a single file (this messes with the PyQt application)
# But for testing purposes, because we have text-mode enabled,
#  this is fine
@Bit.run_from_empty(5, 3)
def will_fail(bit):
    bit.right()
    bit.move()
