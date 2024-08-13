class Tok:
    def __init__(self, val: str):
        self.val = val

    def __eq__(self, other: "Tok"):
        return str(self) == str(other)

    def __str__(self):
        return f"{self.__class__.__name__}({self.val!r})"

    def __repr__(self) -> str:
        return str(self)

class Id(Tok):
    pass

class Allow(Id):
    pass

class Deny(Id):
    pass

class Var(Id):
    pass

class Sym(Tok):
    pass

class BlockSep(Sym):
    pass

class ScopeSep(Sym):
    pass

class ArraySep(Sym):
    pass

class Wild(Sym):
    pass

class SuperWild(Sym):
    pass

class InvalidSyntax(BaseException):
    pass

class InvalidSymbol(BaseException):
    pass

class InvalidIdentifier(BaseException):
    pass

