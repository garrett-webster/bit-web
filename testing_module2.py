from byubit import Bit
from testing_module import exp_bit

exp_bit  # needed for the specific pytest


@Bit.run_from_empty(5, 3)
def will_fail(bit):
    bit.right()
    bit.move()
