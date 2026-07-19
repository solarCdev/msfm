from enum import Enum, auto
import random

class TokenType(Enum):
    # 수치 및 식별자
    NUMBER = auto()
    ID = auto()
    KEYWORD = auto()
    
    # 연산자
    PLUS = auto()      # +
    MINUS = auto()     # -
    MUL = auto()       # *
    DIV = auto()       # /
    POW = auto()       # ^
    ASSIGN = auto()    # =
    MOD = auto()       # %
    
    # 초월함수
    LOG = auto()
    SIN = auto()
    COS = auto()
    TAN = auto()
    SQRT = auto()
    
    # 비교 연산자
    EQ = auto()        # ==
    NEQ = auto()       # !=
    LT = auto()        # <
    GT = auto()        # >
    LTE = auto()       # <=
    GTE = auto()       # >=
    
    # 논리 연산자
    AND = auto()
    OR = auto()
    NOT = auto()
    IN = auto()
    
    # 구조 기호
    LPAREN = auto()    # (
    RPAREN = auto()    # )
    LBRACE = auto()    # {
    RBRACE = auto()    # }
    LSQBRACE = auto()  # [
    RSQBRACE = auto()  # ]
    COMMA = auto()     # ,
    NEWLINE = auto()   # \n
    
    STRING = auto()    # 문자열
    
    PIPE = auto()
    
    EOF = auto()       # 끝

class Token:
    def __init__(self, type, value):
        self.type = type
        self.value = value

    def __repr__(self):
        return f"Token({self.type.name}, {self.value})"
    
class Tokenizer:
    def __init__(self, code):
        self.code = code
        self.pos = 0
        self.tokens = []
        self.keywords = {'if',
                         'else',
                         'elif',
                         'for',
                         'true',
                         'false',
                         'while',
                         'assume',
                         'get',
                         'out', 
                         'contradict', 
                         'apply', 
                         'break', 
                         'continue',
                         'seq',
                         'PI',
                         'E',
                         'plot'
                        }

    def peek(self, offset=1):
        target_pos = self.pos + offset
        if target_pos < len(self.code):
            return self.code[target_pos]
        return None

    def tokenize(self):
        while self.pos < len(self.code):
            char = self.code[self.pos]
            if char in ' \t\r':
                self.pos += 1
                continue

            if char.isdigit():
                self.tokens.append(self.read_number())
                continue

            if char.isalpha():
                self.tokens.append(self.read_identifier())
                continue
            
            if char == '"':
                self.tokens.append(self.read_string())
                continue

            if char == '=':
                self.tokens.append(Token(TokenType.EQ, '='))
                self.pos += 1
            elif char == ':':
                if self.peek() == '=':
                    self.tokens.append(Token(TokenType.ASSIGN, ':='))
                    self.pos += 2
                else:
                    pass
            elif char == '!':
                if self.peek() == '=':
                    self.tokens.append(Token(TokenType.NEQ, '!='))
                    self.pos += 2
                else:
                    raise Exception(f"알 수 없는 기호: {char}")
            elif char == '<':
                if self.peek() == '=':
                    self.tokens.append(Token(TokenType.LTE, '<='))
                    self.pos += 2
                else:
                    self.tokens.append(Token(TokenType.LT, '<'))
                    self.pos += 1
            elif char == '>':
                if self.peek() == '=':
                    self.tokens.append(Token(TokenType.GTE, '>='))
                    self.pos += 2
                else:
                    self.tokens.append(Token(TokenType.GT, '>'))
                    self.pos += 1
            elif char == '+':
                self.tokens.append(Token(TokenType.PLUS, '+'))
                self.pos += 1
            elif char == '-':
                self.tokens.append(Token(TokenType.MINUS, '-'))
                self.pos += 1
            elif char == '*':
                self.tokens.append(Token(TokenType.MUL, '*'))
                self.pos += 1
            elif char == '/':
                self.tokens.append(Token(TokenType.DIV, '/'))
                self.pos += 1
            elif char == '%':
                self.tokens.append(Token(TokenType.MOD, '%'))
                self.pos += 1
            elif char == '^':
                self.tokens.append(Token(TokenType.POW, '^'))
                self.pos += 1
            elif char == '(':
                self.tokens.append(Token(TokenType.LPAREN, '('))
                self.pos += 1
            elif char == ')':
                self.tokens.append(Token(TokenType.RPAREN, ')'))
                self.pos += 1
            elif char == '{':
                self.tokens.append(Token(TokenType.LBRACE, '{'))
                self.pos += 1
            elif char == '}':
                self.tokens.append(Token(TokenType.RBRACE, '}'))
                self.pos += 1
            elif char == '[':
                self.tokens.append(Token(TokenType.LSQBRACE, '['))
                self.pos += 1
            elif char == ']':
                self.tokens.append(Token(TokenType.RSQBRACE, ']'))
                self.pos += 1
            elif char == ',':
                self.tokens.append(Token(TokenType.COMMA, ','))
                self.pos += 1
            elif char == '|':
                self.tokens.append(Token(TokenType.PIPE, '|'))
                self.pos += 1
            elif char == '\n' or char == ';':
                if self.tokens:
                    if self.tokens[len(self.tokens) - 1].type != TokenType.NEWLINE:
                        self.tokens.append(Token(TokenType.NEWLINE, r'\n'))
                self.pos += 1
            elif char == '#':
                self.pos += 1
                while self.code[self.pos] is not None and self.code[self.pos] != '\n':
                    self.pos += 1
                continue
            else:
                """
                have to: Error Handling Detail
                """
                raise Exception(f"처리되지 않은 문자: {char}")
        self.tokens.append(Token(TokenType.EOF, None))
        return self.tokens

    def read_number(self):
        start_pos = self.pos
        dot_count = 0
        while self.pos < len(self.code):
            char = self.code[self.pos]
            if char.isdigit():
                self.pos += 1
            elif char == '.' and dot_count == 0:
                dot_count += 1
                self.pos += 1
            else:
                break
        return Token(TokenType.NUMBER, float(self.code[start_pos:self.pos]))

    def read_identifier(self):
        start_pos = self.pos
        while self.pos < len(self.code) and (self.code[self.pos].isalnum() or self.code[self.pos] == '_'):
            self.pos += 1
        value = self.code[start_pos:self.pos]
        if value in self.keywords:
            return Token(TokenType.KEYWORD, value)
        elif value == 'and':
            return Token(TokenType.AND, 'and')
        elif value == 'or':
            return Token(TokenType.OR, 'or')
        elif value == 'not':
            return Token(TokenType.NOT, 'not')
        elif value == 'in':
            return Token(TokenType.IN, 'in')
        elif value == 'sqrt':
            return Token(TokenType.SQRT, 'sqrt')
        elif value == 'cos':
            return Token(TokenType.COS, 'cos')
        elif value == 'sin':
            return Token(TokenType.SIN, 'sin')
        elif value == 'tan':
            return Token(TokenType.TAN, 'tan')
        elif value == 'log':
            return Token(TokenType.LOG, 'log')
            
        return Token(TokenType.ID, value)

    def read_string(self):
        self.pos += 1
        start_pos = self.pos
        while self.pos < len(self.code) and self.code[self.pos] != '"':
            if self.code[self.pos] == '\n':
                raise Exception("문자열이 닫히기 전에 줄이 바뀌었습니다.")
            self.pos += 1
        
        if self.pos >= len(self.code):
            raise Exception("문자열 닫는 따옴표가 없습니다.")
            
        value = self.code[start_pos:self.pos]
        self.pos += 1
        return Token(TokenType.STRING, value)


