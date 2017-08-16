from asteval import Interpreter as OrigInterpreter


class Interpreter(OrigInterpreter):
    def eval(self, expr, lineno=0, show_errors=False):
        return OrigInterpreter.eval(self, expr, lineno=lineno, show_errors=show_errors)
