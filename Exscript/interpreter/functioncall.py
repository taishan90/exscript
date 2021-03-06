#
# Copyright (C) 2010-2017 Samuel Abels
# The MIT License (MIT)
#
# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and associated documentation files
# (the "Software"), to deal in the Software without restriction,
# including without limitation the rights to use, copy, modify, merge,
# publish, distribute, sublicense, and/or sell copies of the Software,
# and to permit persons to whom the Software is furnished to do so,
# subject to the following conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
# IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
# CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
# TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
# SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
from __future__ import print_function, absolute_import
from ..parselib import Token
from .expression import Expression
from .exception import PermissionError


class FunctionCall(Token):

    def __init__(self, lexer, parser, parent):
        Token.__init__(self, 'FunctionCall', lexer, parser, parent)
        self.funcname = None
        self.arguments = []

        # Extract the function name.
        _, token = lexer.token()
        lexer.expect(self, 'open_function_call')
        self.funcname = token[:-1]
        function = self.parent.get(self.funcname)
        if function is None:
            lexer.syntax_error('Undefined function %s' % self.funcname, self)

        # Parse the argument list.
        _, token = lexer.token()
        while 1:
            if lexer.next_if('close_bracket'):
                break
            self.arguments.append(Expression(lexer, parser, parent))
            ttype, token = lexer.token()
            if not lexer.next_if('comma') and not lexer.current_is('close_bracket'):
                error = 'Expected separator or argument list end but got %s'
                lexer.syntax_error(error % ttype, self)

        if parser.secure_only and not hasattr(function, '_is_secure'):
            msg = 'Use of insecure function %s is not permitted' % self.funcname
            lexer.error(msg, self, PermissionError)

        self.mark_end()

    def dump(self, indent=0):
        print((' ' * indent) + self.name, self.funcname, 'start')
        for argument in self.arguments:
            argument.dump(indent + 1)
        print((' ' * indent) + self.name, self.funcname, 'end.')

    def value(self, context):
        argument_values = [arg.value(context) for arg in self.arguments]
        function = self.parent.get(self.funcname)
        if function is None:
            self.lexer.runtime_error(
                'Undefined function %s' % self.funcname, self)
        return function(self.parent, *argument_values)
