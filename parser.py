from trifle_types import OpenParen, CloseParen

class ParsingError(Exception): pass

class Tree(object):
    """In order to appease RPython's type checker, we can't have an
    arbitrarily nested Python list. Instead, we have an explicit Tree
    type.

    """
    pass


class Node(Tree):
    def __init__(self):
        self.values = []

    def append(self, value):
        self.values.append(value)

    def __eq__(self, other):
        if not isinstance(other, Node):
            return False
        else:
            return self.values == other.values


class Leaf(Tree):
    def __init__(self, value):
        self.value = value

    def __eq__(self, other):
        if not isinstance(other, Leaf):
            return False
        else:
            return self.value == other.value


def parse_inner(tokens, top_level):
    parse_tree = Node()
    saw_closing_paren = False

    while tokens:
        token = tokens.pop(0)

        if isinstance(token, OpenParen):
            parse_tree.append(parse_inner(tokens, top_level=False))
        elif isinstance(token, CloseParen):
            if top_level:
                raise ParsingError('Closing paren does not have matching open paren.')
            else:
                saw_closing_paren = True
                break
        else:
            parse_tree.append(Leaf(token))

    if not top_level and not saw_closing_paren:
        raise ParsingError('Open paren was not closed.')

    return parse_tree


def parse(tokens):
    return parse_inner(tokens, True)


def parse_one(tokens):
    """Only return the first expression parsed. Useful when parsing short
    code snippets.

    """
    return parse(tokens).values[0]
