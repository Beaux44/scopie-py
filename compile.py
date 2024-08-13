# ruff: noqa: F405, F403
from collections.abc import Generator
from .tokens import * 
class Block:
    def __init__(self, inner):
        self.inner = inner

    def __repr__(self):
        return f"{self.__class__.__name__}()"

class Variable(Block):
    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return f"Variable({self.name})"

class WildBlock(Block):
    def __init__(self):
        pass

class SuperWildBlock(Block):
    def __init__(self):
        pass

class Array(Block):
    def __repr__(self):
        return f"Array({self.inner})"

class Literal(Block):
    def __repr__(self):
        return f"Literal({self.inner!r})"

class Scope:
    def __init__(self, allow: bool, scope: list[Block]):
        self.allow = allow
        self.scope = scope

    def __str__(self):
        return f"{['Deny', 'Allow'][self.allow]}({self.scope})"

    def __repr__(self):
        return str(self)

class Scopes:
    def __init__(self, scopes: list[Scope]):
        self.scopes = scopes

    def __str__(self):
        return f"Scopes({self.scopes})"

    def __repr__(self):
        return str(self)

def create_id(val: str) -> Id:
    match val:
        case "allow":
            return Allow(val)
        case "deny":
            return Deny(val)
        case _:
            return Id(val)

class Parser:
    def __init__(self, actor: str):
        self.actor = actor
        self.tokens = lex(actor)
        self.cur, self.seek = next(self.tokens), next(self.tokens)
        self.ast = Scopes([])
    
    def parse(self):
        scopes = []
        while self.cur is not None:
            match self.cur:
                case Allow() | Deny():
                    scopes.append(self.parse_scope())
                    self.skip()
                case _:
                    raise NotImplementedError(f"{self.cur}, {scopes}")

        return Scopes(scopes)

    def parse_scope(self):
        allow = isinstance(self.cur, Allow)
        assert self.seek == BlockSep("/")
        self.step()
        blocks = []
        while True:
            blocks.append(self.parse_block())
            if self.seek == BlockSep("/"):
                self.step()
            else:
                break

        return Scope(allow, blocks)

    def parse_block(self) -> Block:
        self.step()
        match self.cur:
            case Var() as var:
                return Variable(var.val)
            case Id() as id:
                if self.seek == ArraySep("|"):
                    return self.parse_array()
                else:
                    return Literal(id.val)
            case Wild():
                return WildBlock()
            case SuperWild():
                return SuperWildBlock()
            case _:
                raise NotImplementedError(self.cur)

    def parse_array(self):
        inner = []
        while isinstance(self.seek, ArraySep):
            if isinstance(self.cur, Id):
                inner.append(Literal(self.cur.val))
                self.skip()
            else:
                raise InvalidSymbol() # Only literals allowed in arrays
        if isinstance(self.cur, Id):
            inner.append(Literal(self.cur.val))
        return Array(inner)

    def step(self):
        self.cur, self.seek = self.seek, next(self.tokens)

    def skip(self):
        self.step()
        self.step()


def lex(actor: str) -> Generator[Tok | None]:
    pos = 0
    while pos < len(actor):
        cur = actor[pos]
        if cur.isidentifier():
            tmp, pos = lex_id(actor, pos)
            yield tmp
        elif cur in "/,|*":
            tmp, pos = lex_sym(actor, pos)
            yield tmp
        elif cur == "@":
            if pos + 1 < len(actor) and actor[pos + 1].isidentifier():
                tmp, pos = lex_id(actor, pos + 1)
                yield Var(tmp.val)
            else:
                raise InvalidIdentifier(f"pos {pos + 1}")
        else:
            raise InvalidSyntax()
    while True:
        yield None
    
def lex_id(actor: str, pos: int) -> tuple[Id, int]:
    start = pos
    while pos < len(actor):
        if actor[pos].isalnum() or actor[pos] in "-_":
            pos += 1
        else:
            break
    return create_id(actor[start:pos]), pos

def lex_sym(actor: str, pos: int) -> tuple[Sym, int]:
    match actor[pos]:
        case "/":
            return BlockSep("/"), pos + 1
        case ",":
            return ScopeSep(","), pos + 1
        case "|":
            return ArraySep("|"), pos + 1
        case "*":
            if actor[pos + 1] == "*":
                return SuperWild("**"), pos + 2
            else:
                return Wild("*"), pos + 1
        case _:
            raise InvalidSymbol()

