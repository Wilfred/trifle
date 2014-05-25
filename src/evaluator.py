from trifle_types import (
    List, Bytestring, Character, Symbol,
    Integer, Float, Fraction,
    Null, NULL,
    Function, FunctionWithEnv, Lambda, Macro, Boolean,
    Keyword, String,
    TrifleExceptionInstance, TrifleExceptionType)
from errors import (
    error, wrong_type, no_such_variable, stack_overflow,
    ArityError, wrong_argument_number, value_error)
from almost_python import zip
from environment import Scope, LetScope, special_expressions
from parameters import is_variable_arity, check_parameters


# TODO: allow users to change this at runtime.
MAX_STACK_DEPTH = 100


class Stack(object):
    def __init__(self):
        self.values = []

    def __repr__(self):
        return "<Stack: %r>\n" % "\n".join(map(repr, self.values))

    def push(self, value):
        assert len(self.values) <= MAX_STACK_DEPTH + 1, "Stack should be checked for overflow!"
        self.values.append(value)

    def pop(self):
        return self.values.pop()

    def peek(self):
        return self.values[-1]

    def is_empty(self):
        return not bool(self.values)


class Frame(object):
    def __init__(self, expression, environment, as_block=False):
        # The expression we're evaluating, e.g. (if x y 2)
        self.expression = expression

        # The lexical environment, so any variables defined in this
        # function context and any enclosing contexts.
        self.environment = environment

        # The current point we've executed up to in the expression, e.g. 2.
        self.expression_index = 0

        # Used by let to track which assignments have been evaluated.
        self.let_assignment_index = 0

        # Used to keep track of the let environment as we add bindings.
        self.let_environment = None

        # Results of parts of the expression that we have evaluated, e.g.
        # [TRUE, Integer(3)]
        self.evalled = []

        # Is this a single expression to evaluate, or a block? If it's
        # a block, we evaluate each list element and return the
        # last.
        self.as_block = as_block

        # Is this a try expression that will catch certain error types?
        self.catch_error = None

    def __repr__(self):
        return ("expession: %r,\tindex: %d,\tas_block: %s,\tevalled: %r" %
                (self.expression, self.expression_index, self.as_block,
                 self.evalled))


# TODO: Remove this function, it promotes silently ignoring exceptions.
def evaluate_all(expressions, environment):
    """Evaluate a trifle List of expressions in the given environment.

    """
    result = NULL
    
    for expression in expressions.values:
        result = evaluate(expression, environment)

        if is_thrown_exception(result, error):
            return result

    return result


def is_error_instance(error_instance, error_type):
    """Is the type of error_instance the same as error_type, or inherit from it?

    >>> is_error_instance(division_by_zero_instance, division_by_zero)
    True
    >>> is_error_instance(division_by_zero_instance, error)
    True
    >>> is_error_instance(division_by_zero_instance, no_such_variable)
    False

    """
    if not isinstance(error_instance, TrifleExceptionInstance):
        return False

    exception_type_found = error_instance.exception_type

    while exception_type_found:
        if exception_type_found == error_type:
            return True

        exception_type_found = exception_type_found.parent

    return False


def is_thrown_exception(value, exception_type):
    if not is_error_instance(value, exception_type):
        return False
    else:
        return not value.caught


def evaluate(expression, environment):
    """Evaluate the given expression in the given environment.

    """
    stack = Stack()
    stack.push(Frame(expression, environment))

    # We evaluate expressions by pushing them on the stack, then
    # iterating through the elements of the list, evaluating as
    # appropriate. This ensures recursion in the Trifle program does
    # not require recursion in the interpreter.
    while stack:
        # TODO: ensure we can catch this error.
        if len(stack.values) > MAX_STACK_DEPTH:
            return TrifleExceptionInstance(
                # TODO: write a better exception message.
                stack_overflow, u"Stack overflow"
            )

        frame = stack.peek()

        if isinstance(frame.expression, List):
            list_elements = frame.expression.values

            if list_elements:
                head = list_elements[0]
                raw_arguments = list_elements[1:]

                # Handle special expressions.
                if isinstance(head, Symbol) and head.symbol_name in special_expressions:
                    special_expression = special_expressions[head.symbol_name]

                    try:
                        result = special_expression.call(raw_arguments, frame.environment, stack)
                    except ArityError as e:
                        return TrifleExceptionInstance(
                            wrong_argument_number, e.message)

                else:
                    try:
                        result = evaluate_function_call(stack)
                    except ArityError as e:
                        return TrifleExceptionInstance(
                            wrong_argument_number,
                            e.message
                        )

            else:
                result = TrifleExceptionInstance(
                    value_error, u"Can't evaluate an empty list."
                )
            
        else:
            result = evaluate_value(frame.expression, frame.environment)

        # Returning None means we have work left to do, but a Trifle value means
        # we're done with this frame.
        if not result is None:

            if isinstance(result, TrifleExceptionInstance) and not result.caught:
                # We search any try blocks starting from the
                # innermost, and evaluate the first matching :catch we find.

                while not stack.is_empty():
                    # TODO: a proper condition system rather than
                    # always unwinding the stack.
                    # TODO: disinguish between a function throwing an
                    # exception and returning it.
                    frame = stack.pop()
                    expected_error = frame.catch_error

                    if expected_error and is_thrown_exception(result, expected_error):
                        result.caught = True
                        
                        # Execute the catch body.
                        exception_symbol = frame.expression.values[4]
                        catch_body = frame.expression.values[5]
                        
                        catch_body_scope = LetScope({
                            exception_symbol.symbol_name: result
                        })
                        catch_env = frame.environment.with_nested_scope(catch_body_scope)

                        stack.push(Frame(catch_body, catch_env))
                        break

                else:
                    # Otherwise, just propagate the error to the toplevel.
                    return result

            else:
                stack.pop()

                if not stack.is_empty():
                    frame = stack.peek()
                    frame.evalled.append(result)
                else:
                    # We evaluated a value at the top level, nothing left to do.
                    return result


# todo: this would be simpler if `values` was also a trifle List
def build_scope(name, parameters, values):
    """Build a single scope where every value in values (a python list) is
    bound to a symbol according to the parameters List given.

    If the parameters list contains `:rest foo`, any remaining arguments
    are passed a list in the named parameter.

    """
    varargs = is_variable_arity(parameters)

    if varargs:
        # The only negative slice supported by RPython is -1, so we
        # have to do it twice.
        normal_parameters = parameters.values[:-1][:-1]
    else:
        normal_parameters = parameters.values

    # Ensure we have the right number of arguments:
    check_parameters(name, parameters, List(values))

    scope = Scope({})
    for variable, value in zip(normal_parameters, values):
        scope.set(variable.symbol_name,  value)

    # todoc: varargs on macros
    # todo: consistently use the terms 'parameters' and 'arguments'
    if varargs:
        # Create a Trifle list of any remaining arguments.
        remaining_args = List(values[len(normal_parameters):])

        # Assign it to the variable args symbol.
        scope.set(parameters.values[-1].symbol_name, remaining_args)

    return scope


def expand_macro(macro, arguments, environment):
    """Expand the given macro by one iteration. Arguments should be a
    Python list of unevaluated Trifle values.

    """
    # Build a new environment to evaluate with.
    inner_scope = build_scope(macro.name, macro.arguments, arguments)
    macro_env = environment.globals_only().with_nested_scope(inner_scope)

    return evaluate_all(macro.body, macro_env)


def evaluate_function_call(stack):
    """Given a stack, where the the top element is a single Trifle call
    (either a function or a macro), execute it iteratively.

    """
    frame = stack.peek()
    environment = frame.environment
    expression = frame.expression

    if frame.expression_index == 1:
        # If the head of the list evaluated to a macro, we skip
        # evaluating the arguments. Otherwise, continue as evaluating
        # as normal.
        evalled_head = frame.evalled[-1]
        macro_arguments = frame.expression.values[1:]
        
        if isinstance(evalled_head, Macro):
            expanded = expand_macro(evalled_head, macro_arguments, environment)

            # If macro expansion throws an error, terminate, returning that error.
            if is_thrown_exception(expanded, error):
                return expanded
                
            stack.push(Frame(expanded, environment))

            # Ensure we don't evaluate any of arguments to the macro.
            frame.expression_index = len(expression.values) + 1
            return None

    if frame.expression_index < len(expression.values):
        # Evaluate the remaining elements of this list (we work left-to-right).
        raw_argument = expression.values[frame.expression_index]
        stack.push(Frame(raw_argument, environment))

        frame.expression_index += 1
        return None

    elif frame.expression_index == len(expression.values):
        # We've evalled all the elements of the list.

        # This list doesn't represent a function call, rather it's
        # just a lambda body. We just want the last result.
        if frame.as_block:
            return frame.evalled[-1]
        
        # We've evaluated the function and its arguments, now call the
        # function with the evalled arguments.
        function = frame.evalled[0]
        arguments = frame.evalled[1:]

        if isinstance(function, Function):
            return function.call(arguments)

        elif isinstance(function, FunctionWithEnv):
            return function.call(arguments, environment, stack)

        elif isinstance(function, Lambda):
            # Build a new environment to evaluate with.
            inner_scope = build_scope(u"<lambda>", function.arguments, arguments)

            lambda_env = function.env.with_nested_scope(inner_scope)

            # Evaluate the lambda's body in our new environment.
            # TODO: by replacing the stack here, we could do TCO.
            stack.push(Frame(function.body, lambda_env, as_block=True))

            frame.expression_index += 1
            return None

        else:
            # todoc: this error
            return TrifleExceptionInstance(
                wrong_type,
                u"You can only call functions or macros, but got: %s"
                % function.repr())

    else:
        # We had a lambda body or expanded macro and we've now evalled
        # it, so we're done.
        return frame.evalled[-1]


def evaluate_value(value, environment):
    if isinstance(value, Integer):
        return value
    elif isinstance(value, Float):
        return value
    elif isinstance(value, Fraction):
        return value
    elif isinstance(value, Boolean):
        return value
    elif isinstance(value, Null):
        return value
    elif isinstance(value, Keyword):
        return value
        
    # String and bytestring literals should evaluate to a copy of
    # themselves, so we can safely use string literals in function
    # bodies and then mutate them.
    elif isinstance(value, String):
        char_list = value.string
        return String([char for char in char_list])
    elif isinstance(value, Bytestring):
        byte_list = value.byte_value
        return Bytestring([byte for byte in byte_list])
        
    elif isinstance(value, Character):
        return value
    elif isinstance(value, Lambda):
        return value
    elif isinstance(value, Function):
        return value
    elif isinstance(value, Macro):
        return value
    elif isinstance(value, TrifleExceptionInstance):
        return value
    elif isinstance(value, TrifleExceptionType):
        return value
    elif isinstance(value, Macro):
        return value
    elif isinstance(value, Symbol):
        symbol_name = value.symbol_name
        if environment.contains(symbol_name):
            return environment.get(symbol_name)
        else:
            # TODO: suggest variables with similar spelling.
            return TrifleExceptionInstance(
                no_such_variable,
                u"No such variable defined: '%s'" % symbol_name)
    else:
        assert False, "I don't know how to evaluate that value: %s" % value
