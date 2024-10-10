from collections.abc import Iterable


def make_iterable(x, type_check=True):
    if type_check:
        if isinstance(x, Iterable):
            return x
        else:
            return [x]
    else:
        try:
            _ = iter(x)
        except TypeError:
            x = [x]
        return x


def read_multiline_input(prefix=""):
    contents = []
    while True:
        try:
            line = input(prefix)
        except EOFError:
            break
        contents.append(line)
    print()
    return "\n".join(contents)
