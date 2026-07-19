from tokenizer import Tokenizer
from parser import Parser
from interpreter import Interpreter

code = """
a := {x | x <= 2 or x > 9}
for (i:=1, 10) {
    if (i in a) {
        out i " is in a"
    }
    else {
        out i " is not in a"
    }
}
"""

tokenizer = Tokenizer(code)
tokens = tokenizer.tokenize()
parser = Parser(tokens)
ast = parser.parse_program()
interpreter = Interpreter()
interpreter.interpret(ast)
