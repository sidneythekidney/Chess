class Example:
    def __init__(self):
        self.name = "Toto"

a = Example()
b = a
b.name = "Sid"
print(a.name)