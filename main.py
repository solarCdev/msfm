from tokenizer import Tokenizer
from parser import Parser
from interpreter import Interpreter

code = """
for (a := 1, 10){
    out a
    a := 1
}
"""

tokenizer = Tokenizer(code)
tokens_list = tokenizer.tokenize()
parser = Parser(tokens_list)
ast = parser.parse_program()
interpreter = Interpreter()
interpreter.interpret(ast)
    