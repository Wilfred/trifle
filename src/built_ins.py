import errno

from trifle_types import (Function, FunctionWithEnv, Lambda, Macro, Special,
                          Integer, Float, List, Keyword,
                          FileHandle, Bytestring,
                          Boolean, TRUE, FALSE, NULL, Symbol, String)
from errors import (TrifleTypeError, ArityError, DivideByZero, FileNotFound,
                    TrifleValueError, UsingClosedFile)
from almost_python import deepcopy, copy, raw_input, zip
from parameters import validate_parameters
from lexer import lex
from trifle_parser import parse


class SetSymbol(FunctionWithEnv):
    def call(self, args, env):
        if len(args) != 2:
            raise ArityError(
                u"set-symbol! takes 2 arguments, but got: %s" % List(args).repr())

        variable_name = args[0]
        variable_value = args[1]

        if not isinstance(variable_name, Symbol):
            raise TrifleTypeError(
                u"The first argument to set-symbol! must be a symbol, but got: %s"
                % variable_name.repr())

        env.set(variable_name.symbol_name, variable_value)

        return NULL


class Let(Special):
    def call(self, args, env):
        if not args:
            raise ArityError(
                u"let takes at least 1 argument, but got: %s" % List(args).repr())

        bindings = args[0]
        expressions = args[1:]

        # todo: it would be easier if we passed List objects around,
        # and implemented a slice method on them.
        list_expressions = List(expressions)

        if not isinstance(bindings, List):
            raise TrifleTypeError(
                u"let requires a list as its first argument, but got: %s"
                % bindings.repr()
            )

        for index, expression in enumerate(bindings.values):
            if index % 2 == 0:
                if not isinstance(expression, Symbol):
                    raise TrifleTypeError(
                        u"Expected a symbol for a let-bound variable, but got: %s"
                        % expression.repr()
                    )

        if len(bindings.values) % 2 == 1:
            raise ArityError(
                u"no value given for let-bound variable: %s"
                % bindings.values[-1].repr())

        # Fix circular import by importing here.
        from evaluator import evaluate, evaluate_all
        from environment import LetScope

        # Build a scope with the let variables
        let_scope = LetScope({})
        let_env = env.with_nested_scope(let_scope)

        # Bind each symbol to the result of evaluating each
        # expression. We allow access to previous symbols in this let.
        for i in range(len(bindings.values) / 2):
            symbol = bindings.values[2 * i]
            value = evaluate(bindings.values[2 * i + 1], let_env)
            let_scope.set(symbol.symbol_name, value)

        return evaluate_all(list_expressions, let_env)


class LambdaFactory(Special):
    """Return a fresh Lambda object every time it's called."""

    def call(self, args, env):
        if not args:
            raise ArityError(
                u"lambda takes at least 1 argument, but got 0.")

        parameters = args[0]

        validate_parameters(parameters)

        lambda_body = List(args[1:])
        return Lambda(parameters, lambda_body, env)


# todo: do we want to support anonymous macros, similar to lambda?
# todo: expose macro expand functions to the user
# todo: support docstrings
class DefineMacro(Special):
    """Create a new macro object and bind it to the variable name given,
    in the global scope.

    """

    def call(self, args, env):
        if len(args) < 3:
            raise ArityError(
                u"macro takes at least 3 arguments, but got: %s" % List(args).repr())

        macro_name = args[0]
        parameters = args[1]
        
        if not isinstance(macro_name, Symbol):
            raise TrifleTypeError(
                u"macro name should be a symbol, but got: %s" %
                macro_name.repr())

        parameters = args[1]
        validate_parameters(parameters)

        macro_body = List(args[2:])
        env.set_global(macro_name.symbol_name,
                       Macro(parameters, macro_body))

        return NULL


# todo: it would be nice to define this as a trifle macro using a quote primitive
# (e.g. elisp defines backquote in terms of quote)
class Quote(Special):
    def is_unquote(self, expression):
        """Is this expression of the form (unquote expression)?"""
        if not isinstance(expression, List):
            return False

        if not expression.values:
            return False

        list_head = expression.values[0]
        if not isinstance(list_head, Symbol):
            return False

        if not list_head.symbol_name == u'unquote':
            return False

        return True

    def is_unquote_star(self, expression):
        """Is this expression of the form (unquote* expression)?"""
        if not isinstance(expression, List):
            return False

        if not expression.values:
            return False

        list_head = expression.values[0]
        if not isinstance(list_head, Symbol):
            return False

        if not list_head.symbol_name == u'unquote*':
            return False

        return True
    
    # todo: fix the potential stack overflow
    # todo: throw errors on (unquote two arguments!) and (unquote)
    def evaluate_unquote_calls(self, expression, env):
        from evaluator import evaluate
        if isinstance(expression, List):
            for index, item in enumerate(copy(expression).values):
                if self.is_unquote(item):
                    unquote_argument = item.values[1]
                    expression.values[index] = evaluate(unquote_argument, env)
                    
                elif self.is_unquote_star(item):
                    unquote_argument = item.values[1]
                    values_list = evaluate(unquote_argument, env)

                    # todo: unit test this error
                    if not isinstance(values_list, List):
                        raise TrifleTypeError(
                            u"unquote* must be used with a list, but got a %s" % values_list.repr())

                    # Splice in the result of evaluating the unquote* argument
                    expression.values = expression.values[:index] + values_list.values + expression.values[index+1:]

                elif isinstance(item, List):
                    # recurse the nested list
                    self.evaluate_unquote_calls(item, env)

        return expression
                        
    
    def call(self, args, env):
        if len(args) != 1:
            raise ArityError(
                u"quote takes 1 argument, but got: %s" % List(args).repr())

        return self.evaluate_unquote_calls(deepcopy(args[0]), env)


class If(Special):
    def call(self, args, env):
        if len(args) not in [2, 3]:
            raise ArityError(
                u"if takes 2 or 3 arguments, but got: %s" % List(args).repr())

        condition = args[0]
        then = args[1]

        from evaluator import evaluate
        if is_truthy(evaluate(condition, env)) == TRUE:
            return evaluate(then, env)
        else:
            if len(args) == 3:
                otherwise = args[2]
                return evaluate(otherwise, env)
            else:
                return NULL


def is_truthy(value):
    """Convert the value to the trifle values `#true` or `#false`
    depending on its truthiness.

    """
    if isinstance(value, Boolean):
        if value == FALSE:
            return FALSE

    if isinstance(value, Integer):
        if value.value == 0:
            return FALSE

    if isinstance(value, List):
        if len(value.values) == 0:
            return FALSE

    return TRUE

        
class Truthy(Function):
    def call(self, args):
        if len(args) != 1:
            raise ArityError(
                u"truthy? takes 1 argument, but got: %s" % List(args).repr())

        return is_truthy(args[0])


class While(Special):
    def call(self, args, env):
        if not args:
            raise TrifleTypeError(
                u"while takes at least one argument.")

        from evaluator import evaluate
        while True:
            condition = evaluate(args[0], env)
            if is_truthy(condition) == FALSE:
                break

            for arg in args[1:]:
                evaluate(arg, env)

        return NULL


# todo: implement in prelude in terms of writing to stdout
# todo: just print a newline if called without any arguments.
# todo: allow a separator argument, Python 3 style
class Print(Function):
    def call(self, args):
        if len(args) != 1:
            raise ArityError(
                u"print takes 1 argument, but got %s." % List(args).repr())

        if isinstance(args[0], String):
            print args[0].string
        else:
            print args[0].repr()

        return NULL


# todo: implement in prelude in terms of stdin and stdout
class Input(Function):
    def call(self, args):
        if len(args) != 1:
            raise ArityError(
                u"input takes 1 argument, but got %s." % List(args).repr())

        prefix = args[0]

        if not isinstance(prefix, String):
            raise TrifleTypeError(
                u"The first argument to input must be a string, but got: %s"
                % prefix.repr())

        user_input = raw_input(prefix.string)
        return String(user_input)


class Same(Function):
    def call(self, args):
        if len(args) != 2:
            raise ArityError(
                u"same? takes 2 arguments, but got: %s" % List(args).repr())

        # Sadly, we can't access .__class__ in RPython.
        # TODO: proper symbol interning.
        if isinstance(args[0], Symbol):
            if isinstance(args[1], Symbol):
                if args[0].symbol_name == args[1].symbol_name:
                    return TRUE

            return FALSE

        if args[0] is args[1]:
            return TRUE
        else:
            return FALSE


def is_equal(x, y):
    """Return True if x and y are equal.

    TODO: fix the potential stack overflow here for deep lists.

    """
    if isinstance(x, Symbol):
        if isinstance(y, Symbol):
            return x.symbol_name == y.symbol_name

        return False

    elif isinstance(x, Float):
        if isinstance(y, Float):
            return x.float_value == y.float_value

        elif isinstance(y, Integer):
            return x.float_value == float(y.value)        

        return False

    elif isinstance(x, Integer):
        if isinstance(y, Integer):
            return x.value == y.value

        elif isinstance(y, Float):
            return float(x.value) == y.float_value

        return False

    elif isinstance(x, Integer):
        if isinstance(y, Integer):
            return x.value == y.value

        return False

    elif isinstance(x, String):
        if isinstance(y, String):
            return x.string == y.string

        return False

    elif isinstance(x, Bytestring):
        if isinstance(y, Bytestring):
            return x.byte_value == y.byte_value

        return False

    elif isinstance(x, List):
        if isinstance(y, List):
            if len(x.values) != len(y.values):
                return False

            for x_element, y_element in zip(x.values, y.values):
                if not is_equal(x_element, y_element):
                    return False
            return True

        return False

    return x is y


# TODO: Is there a better place in the docs for this, rather than under booleans?
# We're inconsistent between grouping by input type or output type.
class Equal(Function):
    def call(self, args):
        if len(args) != 2:
            raise ArityError(
                u"equal? takes 2 arguments, but got: %s" % List(args).repr())

        if is_equal(args[0], args[1]):
            return TRUE
        else:
            return FALSE


class FreshSymbol(Function):
    def __init__(self):
        self.count = 1

    def call(self, args):
        if args:
            raise TrifleTypeError(
                u"fresh-symbol takes 0 arguments, but got: %s" % List(args).repr())

        symbol_name = u"%d-unnamed" % self.count
        self.count += 1

        return Symbol(symbol_name)


class Add(Function):
    def call(self, args):
        float_args = False
        for arg in args:
            if not isinstance(arg, Integer):
                if isinstance(arg, Float):
                    float_args = True
                else:
                    raise TrifleTypeError(
                        u"+ requires numbers, but got: %s." % arg.repr())

        if float_args:
            total = 0.0
            for arg in args:
                if isinstance(arg, Integer):
                    total += float(arg.value)
                else:
                    total += arg.float_value

            return Float(total)

        else:
            total = 0
            for arg in args:
                total += arg.value
            return Integer(total)


class Subtract(Function):
    def call(self, args):
        float_args = False
        for arg in args:
            if not isinstance(arg, Integer):
                if isinstance(arg, Float):
                    float_args = True
                else:
                    raise TrifleTypeError(
                        u"- requires numbers, but got: %s." % arg.repr())

        if not args:
            return Integer(0)

        if len(args) == 1:
            if isinstance(args[0], Integer):
                return Integer(-args[0].value)
            else:
                return Float(-args[0].float_value)

        if float_args:
            if isinstance(args[0], Integer):
                total = float(args[0].value)
            else:
                total = args[0].float_value
                
            for arg in args[1:]:
                if isinstance(arg, Integer):
                    total -= float(arg.value)
                else:
                    total -= arg.float_value

            return Float(total)
        else:
            total = args[0].value
            for arg in args[1:]:
                total -= arg.value
            return Integer(total)


class Multiply(Function):
    def call(self, args):
        float_args = False
        for arg in args:
            if not isinstance(arg, Integer):
                if isinstance(arg, Float):
                    float_args = True
                else:
                    raise TrifleTypeError(
                        u"* requires numbers, but got: %s." % arg.repr())

        if float_args:
            product = 1.0
            for arg in args:
                if isinstance(arg, Integer):
                    product *= float(arg.value)
                else:
                    product *= arg.float_value

            return Float(product)

        else:
            product = 1
            for arg in args:
                product *= arg.value
            return Integer(product)


class Divide(Function):
    def call(self, args):
        if len(args) < 2:
            raise ArityError(
                u"/ takes at least 2 arguments, but got: %s" % List(args).repr())

        for arg in args:
            if not isinstance(arg, Integer) and not isinstance(arg, Float):
                raise TrifleTypeError(
                    u"/ requires numbers, but got: %s." % arg.repr())

        if isinstance(args[0], Integer):
            quotient = float(args[0].value)
        else:
            quotient = args[0].float_value

        for arg in args[1:]:
            try:
                if isinstance(arg, Integer):
                    quotient /= float(arg.value)
                else:
                    quotient /= arg.float_value
            except ZeroDivisionError:
                raise DivideByZero(u"Divided by zero: %s" % arg.repr())

        return Float(quotient)
            

class LessThan(Function):
    def call(self, args):
        if len(args) < 2:
            raise ArityError(
                u"< takes at least 2 arguments, but got: %s" % List(args).repr())
        
        float_args = False
        for arg in args:
            if not isinstance(arg, Integer):
                if isinstance(arg, Float):
                    float_args = True
                else:
                    raise TrifleTypeError(
                        u"< requires numbers, but got: %s." % arg.repr())

        if float_args:
            if isinstance(args[0], Integer):
                previous_number = float(args[0].value)
            else:
                previous_number = args[0].float_value

            for arg in args[1:]:
                if isinstance(arg, Integer):
                    number = float(arg.value)
                else:
                    number = arg.float_value

                if not previous_number < number:
                    return FALSE

                previous_number = number

            return TRUE

        else:
            # Only integers.
            previous_number = args[0].value
            for arg in args[1:]:
                number = arg.value

                if not previous_number < number:
                    return FALSE

                previous_number = number

            return TRUE


# TODO: name other FOO? functions as FooPredicate, and update doc names accordingly
class ListPredicate(Function):
    def call(self, args):
        if len(args) != 1:
            raise ArityError(
                u"list? takes 1 argument, but got: %s" % List(args).repr())

        value = args[0]

        if isinstance(value, List):
            return TRUE
        else:
            return FALSE


class GetIndex(Function):
    def call(self, args):
        if len(args) != 2:
            raise ArityError(
                u"get-index takes 2 arguments, but got: %s" % List(args).repr())

        sequence = args[0]
        index = args[1]

        if isinstance(sequence, List):
            sequence_length = len(sequence.values)
        elif isinstance(sequence, Bytestring):
            sequence_length = len(sequence.byte_value)
        else:
            raise TrifleTypeError(
                u"the first argument to get-index must be a sequence, but got: %s"
                % sequence.repr())

        if not isinstance(index, Integer):
            raise TrifleTypeError(
                u"the second argument to get-index must be an integer, but got: %s"
                % index.repr())

        if not sequence_length:
            raise TrifleValueError(u"can't call get-item on an empty sequence")

        # todo: use a separate error class for index errors
        if index.value >= sequence_length:
            raise TrifleValueError(
                u"the sequence has %d items, but you asked for index %d"
                % (sequence_length, index.value))

        if index.value < -1 * sequence_length:
            raise TrifleValueError(
                u"Can't get index %d of a %d element sequence (must be -%d or higher)"
                % (index.value, sequence_length, sequence_length))

        if isinstance(sequence, List):
            return sequence.values[index.value]
        elif isinstance(sequence, Bytestring):
            return Integer(sequence.byte_value[index.value])


class Length(Function):
    def call(self, args):
        if len(args) != 1:
            raise TrifleTypeError(
                u"length takes 1 argument, but got: %s" % List(args).repr())

        some_list = args[0]

        if isinstance(some_list, List):
            return Integer(len(some_list.values))
        elif isinstance(some_list, Bytestring):
            return Integer(len(some_list.byte_value))

        raise TrifleTypeError(
            u"the first argument to length must be a list, but got: %s"
            % some_list.repr())


class SetIndex(Function):
    def call(self, args):
        if len(args) != 3:
            raise ArityError(
                u"set-index! takes 3 arguments, but got: %s" % List(args).repr())

        sequence = args[0]
        index = args[1]
        value = args[2]

        if isinstance(sequence, List):
            sequence_length = len(sequence.values)
        elif isinstance(sequence, Bytestring):
            sequence_length = len(sequence.byte_value)
        else:
            raise TrifleTypeError(
                u"the first argument to set-index! must be a sequence, but got: %s"
                % sequence.repr())

        if not isinstance(index, Integer):
            raise TrifleTypeError(
                u"the second argument to set-index! must be an integer, but got: %s"
                % index.repr())

        if not sequence_length:
            raise TrifleValueError(u"can't call set-index! on an empty sequence")

        # todo: use a separate error class for index error
        if index.value >= sequence_length:
            raise TrifleValueError(
                u"the sequence has %d items, but you asked to set index %d"
                % (sequence_length, index.value))

        if index.value < -1 * sequence_length:
            raise TrifleValueError(
                u"Can't set index %d of a %d element sequence (must be -%d or higher)"
                % (index.value, sequence_length, sequence_length))

        if isinstance(sequence, List):
            sequence.values[index.value] = value
        elif isinstance(sequence, Bytestring):
            if not isinstance(value, Integer):
                raise TrifleTypeError(u"Permitted values for bytestrings are integers between 0 and 255, but got: %s"
                                      % value.repr())

            if not (0 <= value.value <= 255):
                raise TrifleValueError(u"Permitted values for bytestrings are integers between 0 and 255, but got: %s"
                                       % value.repr())

            sequence.byte_value[index.value] = value.value

        return NULL


class Append(Function):
    def call(self, args):
        if len(args) != 2:
            raise TrifleTypeError(
                u"append! takes 2 arguments, but got: %s" % List(args).repr())

        some_list = args[0]
        value = args[1]

        if not isinstance(some_list, List):
            raise TrifleTypeError(
                u"the first argument to append! must be a list, but got: %s"
                % some_list.repr())

        some_list.values.append(value)

        return NULL


# todo: replace with a prelude function that uses append!
class Push(Function):
    def call(self, args):
        if len(args) != 2:
            raise TrifleTypeError(
                u"push! takes 2 arguments, but got: %s" % List(args).repr())

        some_list = args[0]
        value = args[1]

        if not isinstance(some_list, List):
            raise TrifleTypeError(
                u"the first argument to push! must be a list, but got: %s"
                % some_list.repr())

        some_list.values.insert(0, value)

        return NULL


class Parse(Function):
    def call(self, args):
        if len(args) != 1:
            raise ArityError(
                u"parse takes 1 argument, but got: %s" % List(args).repr())

        program_string = args[0]

        if not isinstance(program_string, String):
            raise TrifleTypeError(
                u"the first argument to parse must be a list, but got: %s"
                % program_string.repr())

        tokens = lex(program_string.string)
        return parse(tokens)


# todo: consider allowing the user to pass in an environment for sandboxing
class Eval(FunctionWithEnv):
    def call(self, args, env):
        if len(args) != 1:
            raise ArityError(
                u"eval takes 1 argument, but got: %s" % List(args).repr())

        from evaluator import evaluate
        return evaluate(args[0], env)


class Call(FunctionWithEnv):
    def call(self, args, env):
        if len(args) != 2:
            raise ArityError(
                u"call takes 2 arguments, but got: %s" % List(args).repr())

        function = args[0]
        arguments = args[1]

        # TODO: should call accept macros and specials too?
        if not (isinstance(function, Function) or
                isinstance(function, Lambda)):
            raise TrifleTypeError(
                u"the first argument to call must be a function, but got: %s"
                % function.repr())

        if not isinstance(arguments, List):
            raise TrifleTypeError(
                u"the second argument to call must be a list, but got: %s"
                % arguments.repr())

        # Build an equivalent expression
        expression = List([function] + arguments.values)

        from evaluator import evaluate
        return evaluate(expression, env)
        

class Defined(FunctionWithEnv):
    def call(self, args, env):
        # TODO: a utility function for arity checking, which prints
        # both the number of args and shows the args themselves.
        if len(args) != 1:
            raise ArityError(
                u"defined? takes 1 argument, but got: %s" % List(args).repr())

        symbol = args[0]

        if not isinstance(symbol, Symbol):
            raise TrifleTypeError(
                u"the first argument to defined? must be a symbol, but got: %s"
                % symbol.repr())

        return Boolean(env.contains(symbol.symbol_name))


# TODO: error on a file we can't write to
# TODO: error when we run out of file handles
# TODO: other errors the file system can throw at us
class Open(Function):
    def call(self, args):
        # todo: a utility function for arity checking.
        if len(args) != 2:
            raise ArityError(
                u"open takes 2 arguments, but got: %s" % List(args).repr())

        path = args[0]

        if not isinstance(path, String):
            raise TrifleTypeError(
                u"the first argument to open must be a string, but got: %s"
                % path.repr())

        flag = args[1]

        if not isinstance(flag, Keyword):
            raise TrifleTypeError(
                u"the first argument to open must be a string, but got: %s"
                % flag.repr())

        if flag.symbol_name == u'write':
            handle = open(path.string.encode('utf-8'), 'w')
        elif flag.symbol_name == u'read':
            try:
                handle = open(path.string.encode('utf-8'), 'r')
            except IOError as e:
                if e.errno == errno.ENOENT:
                    raise FileNotFound(u"No file found: %s" % path.string)
                else:
                    raise
        else:
            raise TrifleValueError(u"Invalid flag for open: :%s" % flag.symbol_name)

        return FileHandle(path.string, handle, flag)


class Close(Function):
    def call(self, args):
        # todo: a utility function for arity checking.
        if len(args) != 1:
            raise ArityError(
                u"close! takes 1 argument, but got: %s" % List(args).repr())

        handle = args[0]

        if not isinstance(handle, FileHandle):
            raise TrifleTypeError(
                u"the first argument to close! must be a file handle, but got: %s"
                % handle.repr())

        if handle.is_closed:
            raise UsingClosedFile(u"File handle for %s is already closed." % handle.file_name)
        else:
            handle.is_closed = True
            handle.file_handle.close()

        return NULL


# TODO: specify a limit for how much to read.
class Read(Function):
    def call(self, args):
        if len(args) != 1:
            raise ArityError(
                u"read takes 1 argument, but got: %s" % List(args).repr())

        handle = args[0]

        if not isinstance(handle, FileHandle):
            raise TrifleTypeError(
                u"the first argument to read must be a file handle, but got: %s"
                % handle.repr())

        return Bytestring(bytearray(handle.file_handle.read()))


class Write(Function):
    def call(self, args):
        if len(args) != 2:
            raise ArityError(
                u"write! takes 2 argument, but got: %s" % List(args).repr())

        handle = args[0]

        if not isinstance(handle, FileHandle):
            raise TrifleTypeError(
                u"the first argument to write! must be a file handle, but got: %s"
                % handle.repr())

        if handle.mode.symbol_name != u"write":
            raise ValueError(
                u"%s is a read-only file handle, you can't write to it."
                % handle.repr())

        to_write = args[1]

        if not isinstance(to_write, Bytestring):
            raise TrifleTypeError(
                u"the second argument to write! must be a bytes, but got: %s"
                % to_write.repr())

        handle.file_handle.write(str(to_write.byte_value))

        return NULL


# TODO: take a second argument that specifies the encoding.
class Encode(Function):
    def call(self, args):
        if len(args) != 1:
            raise ArityError(
                u"encode takes 1 argument, but got: %s" % List(args).repr())

        string = args[0]

        if not isinstance(string, String):
            raise TrifleTypeError(
                u"the first argument to encode must be a string, but got: %s"
                % string.repr())

        return Bytestring(bytearray(string.string.encode('utf-8')))


# TODO: take a second argument that specifies the encoding.
# TODO: throw an exception on bytes that aren't valid UTF-8.
class Decode(Function):
    def call(self, args):
        if len(args) != 1:
            raise ArityError(
                u"decode takes 1 argument, but got: %s" % List(args).repr())

        bytestring = args[0]

        if not isinstance(bytestring, Bytestring):
            raise TrifleTypeError(
                u"the first argument to decode must be bytes, but got: %s"
                % bytestring.repr())

        return String(str(bytestring.byte_value).decode('utf-8'))
