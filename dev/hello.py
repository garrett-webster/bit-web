def hello(name):
    ending = '!'
    if 'o' in name:
        ending = '?'
    print('hello', name + ending)


def main():
    name = 'Susan'
    hello(name)

    name = 'George'
    hello(name)


if __name__ == '__main__':
    main()