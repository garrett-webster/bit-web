from byubit import Bit


def foo(bit):
    bit.paint("green")


# This should fail because foo is not decorated
foo(Bit.new_bit)
