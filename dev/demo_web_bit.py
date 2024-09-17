from web_bit import Bit

if __name__ == '__main__':
    @Bit.empty_world(5, 3)
    def run(bit):
        bit.move()
        bit.paint('green')


    run(Bit.new_bit)

    print(Bit.results)
