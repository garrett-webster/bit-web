import byubit
from byubit import Bit
from byubit_mpl.mpl_renderer import MplRenderer


@Bit.worlds('test-world-right', 'test-world-wrong')
def main(bit: Bit):
    bit.paint('green')
    bit.snapshot('go team!')
    while bit.can_move_front():
        bit.move()
        bit.paint('blue')


if __name__ == '__main__':
    main(byubit.bit.NewBit(MplRenderer('mpl_demo.svg')))

    # main(byubit.bit.NewBit(MplRenderer()))
