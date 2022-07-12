from string import ascii_uppercase, digits


class CodeIterator:
    def __init__(self):
        self.stack = [iter(ascii_uppercase)]
        self.values = [None]

    def __iter__(self):
        return self

    def __next__(self):
        while self.stack:  # mientras se pueda iterar
            new_value = next(self.stack[-1], None)  # obtener el sig valor
            if new_value:
                self.values[-1] = new_value
                return "".join(self.values)
            self.stack.pop()
            self.values.pop()
        raise StopIteration

    def add_depth(self):
        if len(self.stack) <= 2:
            self.stack.append(iter(ascii_uppercase))
        elif len(self.stack) <= 6:
            self.stack.append(iter(digits))
        else:
            raise Exception
        self.values.append(None)
