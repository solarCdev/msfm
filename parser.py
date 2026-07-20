from tokenizer import TokenType

class ASTNode:
    pass

class NumberNode(ASTNode):
    def __init__(self, token):
        self.token = token
        self.value = token.value

    def __repr__(self):
        return f"{self.value}"

class BinOpNode(ASTNode):
    def __init__(self, left, op_token, right):
        self.left = left
        self.op_token = op_token
        self.right = right

    def __repr__(self):
        return f"({self.left} {self.op_token.value} {self.right})"

class BooleanNode(ASTNode):
    def __init__(self, token):
        self.token = token
        self.value = True if token.value == 'true' else False

    def __repr__(self):
        return "true" if self.value else "false"

class UnaryOpNode(ASTNode):
    def __init__(self, op_token, expr):
        self.op_token = op_token
        self.expr = expr

    def __repr__(self):
        if self.op_token.type == TokenType.NOT:
            return f"not {self.expr}"
        return f"({self.op_token.value}{self.expr})"
    
class VariableNode(ASTNode):
    def __init__(self, token):
        self.token = token
        self.value = token.value

    def __repr__(self):
        return f"var({self.value})"

class LogNode(ASTNode):
    def __init__(self, base, argument):
        self.base = base
        self.argument = argument
        
    def __repr__(self):
        return f"log_{self.base} ({self.argument})"

class AssignNode(ASTNode):
    def __init__(self, left, right):
        self.left = left
        self.right = right

    def __repr__(self):
        return f"({self.left} := {self.right})"    

class GetNode(ASTNode):
    def __init__(self, var_token):
        self.var_token = var_token
        self.var_name = var_token.value

    def __repr__(self):
        return f"get {self.var_name}"    

class StringNode(ASTNode):
    def __init__(self, token):
        self.token = token
        self.value = token.value

    def __repr__(self):
        return f'"{self.value}"'

class OutNode(ASTNode):
    def __init__(self, tokens):
        self.expressions = tokens

    def __repr__(self):
        return f"out {', '.join(repr(expr) for expr in self.expressions)}"

class BreakNode(ASTNode):
    def __repr__(self):
        return "break"
    
class ContinueNode(ASTNode):
    def __repr__(self):
        return "continue"
    
class BlockNode(ASTNode):
    def __init__(self, statements):
        self.statements = statements

    def __repr__(self):
        return '{' + '; '.join(repr(expr) for expr in self.statements) + '}'    

class ForNode(ASTNode):
    def __init__(self, var_node, start_expr, end_expr, body_block):
        self.var_node = var_node
        self.start_expr = start_expr  
        self.end_expr = end_expr      
        self.body_block = body_block

    def __repr__(self):
        return f"for ({self.var_node} := {self.start_expr}, {self.end_expr}) {self.body_block}"
    
class WhileNode(ASTNode):
    def __init__(self, cond_expr, body_block):
        self.cond_expr = cond_expr      
        self.body_block = body_block

    def __repr__(self):
        return f"while ({self.cond_expr}) {self.body_block}"

class IfNode(ASTNode):
    def __init__(self, condition, body, else_body=None):
        self.condition = condition
        self.body = body
        self.else_body = else_body

    def __repr__(self):
        if self.else_body:
            return f"if ({self.condition}) {self.body} else {self.else_body}"
        return f"if ({self.condition}) {self.body}"

class ApplyNode(ASTNode):
    def __init__(self, vars_list=None):
        self.vars_list = vars_list if vars_list else []

    def __repr__(self):
        if self.vars_list:
            return f"apply {', '.join(self.vars_list)}"
        return "apply"

class AssumeNode(ASTNode):
    def __init__(self, condition, body, contradict_body):
        self.condition = condition
        self.body = body
        self.contradict_body = contradict_body

    def __repr__(self):
        return f"assume ({self.condition}) {self.body} contradict {self.contradict_body}"

class SetNode(ASTNode):
    def __init__(self, set_type, data):
        self.set_type = set_type  # 'ELEMENTS', 'COMPREHENSION', 'INTERVAL'
        self.data = data
        # ELEMENTS -> [Node, Node, ...]
        # COMPREHENSION -> {'var_name': 'x', 'condition': Node}
        # INTERVAL -> {'left_bracket': '(', 'left': Node, 'right': Node, 'right_bracket': ']'}

    def __repr__(self):
        if self.set_type == 'ELEMENTS':
            return f"{{{', '.join(repr(e) for e in self.data)}}}"
        elif self.set_type == 'COMPREHENSION':
            return f"{{{self.data['var_name']} | {self.data['condition']}}}"
        elif self.set_type == 'INTERVAL':
            d = self.data
            return f"{d['left_bracket']}{d['left']}, {d['right']}{d['right_bracket']}"

class FunctionDefNode(ASTNode):
    def __init__(self, name, param_name, domain, body):
        self.name = name
        self.param_name = param_name
        self.domain = domain
        self.body = body

    def __repr__(self):
        if self.domain:
            return f"{self.name}({self.param_name} in {self.domain}) := {self.body}"
        return f"{self.name}({self.param_name}) := {self.body}"

class CallNode(ASTNode):
    def __init__(self, name, arg, is_subscript=False):
        self.name = name
        self.arg = arg
        self.is_subscript = is_subscript

    def __repr__(self):
        if self.is_subscript:
            return f"{self.name}[{self.arg}]"
        return f"{self.name}({self.arg})"

class SequenceLiteralNode(ASTNode):
    def __init__(self, elements):
        self.elements = elements

    def __repr__(self):
        return f"seq [{', '.join(repr(e) for e in self.elements)}]"

class PlotNode(ASTNode):
    def __init__(self, command, **kwargs):
        self.command = command
        if kwargs.get('func'):
            self.func = kwargs['func']
        if kwargs.get('domain'):
            self.domain = kwargs['domain']
            if kwargs['style']:
                self.style = kwargs['style']
        if kwargs.get('filename'):
            self.filename = kwargs['filename']
    def __repr__(self):
        return f"plot {self.command}"

class LenNode(ASTNode):
    def __init__(self, value):
        self.value = value
    
    def __repr__(self):
        return f"n({self.value})"

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0
        self.current_token = self.tokens[self.pos] if self.tokens else None

    def advance(self):
        self.pos += 1
        if self.pos < len(self.tokens):
            self.current_token = self.tokens[self.pos]
        else:
            self.current_token = None
        return self.current_token

    def eat(self, token_type):
        if self.current_token and self.current_token.type == token_type:
            token = self.current_token
            self.advance()
            return token

        raise Exception(f"Syntax Error: Expected {token_type}, but got {self.current_token.type if self.current_token else 'EOF'}")
    
    def peek_token(self):
        peek_pos = self.pos + 1
        if peek_pos < len(self.tokens):
            return self.tokens[peek_pos]
        return None
    
    def parse_program(self):
        statements = []
        while self.current_token and self.current_token.type != TokenType.EOF:
            if self.current_token.type == TokenType.NEWLINE:
                self.advance()
                continue
            statements.append(self.parse_statement())
        return statements
    
    def parse_statement(self):
        token = self.current_token

        if token.type == TokenType.KEYWORD:
            if token.value == 'if': return self.parse_if_statement()
            elif token.value == 'assume': return self.parse_assume_statement()
            elif token.value == 'apply': return self.parse_apply_statement()
            elif token.value == 'for': return self.parse_for_statement()
            elif token.value == 'get': return self.parse_get_statement()
            elif token.value == 'out': return self.parse_out_statement()
            elif token.value == 'break': return self.parse_break_statement()
            elif token.value == 'while': return self.parse_while_statement()
            elif token.value == 'continue': return self.parse_continue_statement()
            elif token.value == 'plot': return self.parse_plot_statement()
            elif token.value == 'PI' or token.value == 'E': return self.parse_assignment_or_expression()
        elif token.type == TokenType.ID: return self.parse_assignment_or_expression()
        elif token.type == TokenType.LEN: return self.parse_assignment_or_expression()
        else:
            raise SyntaxError(f'Unexpected Token: {token}')
    
    def parse_block(self):
        self.eat(TokenType.LBRACE)
        statements = []
        while self.current_token and self.current_token.type != TokenType.RBRACE:
            if self.current_token.type == TokenType.NEWLINE:
                self.advance()
                continue
            statements.append(self.parse_statement())
        self.eat(TokenType.RBRACE)
        return BlockNode(statements)
    
    def parse_assignment_or_expression(self):
        if not self.has_assign_in_line():
            return self.parse_expression()

        first_token = self.current_token
        next_token = self.peek_token()

        if next_token and next_token.type == TokenType.LPAREN:
            return self.parse_function_definition()
        elif next_token and next_token.type == TokenType.ASSIGN:
            self.eat(TokenType.ID)    
            self.eat(TokenType.ASSIGN)
            right_node = self.parse_expression()
            return AssignNode(left=VariableNode(first_token), right=right_node)

        raise SyntaxError(f"잘못된 대입문 구조: {first_token}")

    def has_assign_in_line(self):
        idx = self.pos
        while idx < len(self.tokens):
            token = self.tokens[idx]
            if token.type in (TokenType.NEWLINE, TokenType.EOF):
                break
            if token.type == TokenType.ASSIGN:
                return True
            idx += 1
        return False

    def parse_expression(self):
        node = self.parse_comparison()

        while self.current_token and self.current_token.type in (TokenType.AND, TokenType.OR, TokenType.PIPE):
            token = self.current_token
            self.advance()
            node = BinOpNode(left=node, op_token=token, right=self.parse_comparison())
        return node

    def parse_function_definition(self):
        func_token = self.eat(TokenType.ID) 
        self.eat(TokenType.LPAREN)          
        
        param_token = self.eat(TokenType.ID)
        
        domain_set = None
        if self.current_token and self.current_token.type == TokenType.IN:
            self.advance()
            domain_set = self.parse_expression()
            
        self.eat(TokenType.RPAREN)          
        self.eat(TokenType.ASSIGN)
        
        if self.current_token.type == TokenType.KEYWORD and self.current_token.value == 'seq':
            self.eat(TokenType.KEYWORD)
            body_node = self.parse_sequence_literal()
        else:
            body_node = self.parse_expression()
        
        return FunctionDefNode(func_token.value, param_token.value, domain_set, body_node)

    def parse_sequence_literal(self):
        self.eat(TokenType.LSQBRACE)
        
        elements = []
        
        if self.current_token and self.current_token.type != TokenType.RSQBRACE and self.current_token.value != ']':
            elements.append(self.parse_expression())
            
            while self.current_token and self.current_token.type == TokenType.COMMA:
                self.eat(TokenType.COMMA)
                elements.append(self.parse_expression())
                
        if self.current_token and (self.current_token.type == TokenType.RSQBRACE or self.current_token.value == ']'):
             self.eat(TokenType.RSQBRACE)
        else:
            raise SyntaxError("불규칙 수열 리스트의 닫는 대괄호 ']'가 누락되었습니다.")
            
        return SequenceLiteralNode(elements)

    def parse_comparison(self):
        node = self.parse_arithmetic_expr()

        if self.current_token and self.current_token.type in (
            TokenType.EQ, TokenType.NEQ, 
            TokenType.LT, TokenType.LTE, 
            TokenType.GT, TokenType.GTE,
            TokenType.IN
        ):
            token = self.current_token
            self.advance()
            node = BinOpNode(left=node, op_token=token, right=self.parse_arithmetic_expr())
        return node

    def parse_arithmetic_expr(self):
        node = self.parse_term()

        while self.current_token and self.current_token.type in (TokenType.PLUS, TokenType.MINUS):
            token = self.current_token
            self.advance()
            node = BinOpNode(left=node, op_token=token, right=self.parse_term())
        
        return node
    
    def parse_term(self):
        node = self.parse_unary()

        while self.current_token.type in (TokenType.MUL, TokenType.DIV, TokenType.MOD):
            token = self.current_token
            self.advance()
            node = BinOpNode(left=node, op_token=token, right=self.parse_unary())
        
        return node
    
    def parse_unary(self):
        token = self.current_token
        if token.type == TokenType.MINUS:
            self.advance()
            return UnaryOpNode(op_token=token, expr=self.parse_power())
        elif token.type == TokenType.NOT:
            self.advance()
            return UnaryOpNode(op_token=token, expr=self.parse_power())
        elif token.type in (TokenType.SIN, TokenType.COS, TokenType.TAN):
            self.advance()
            return UnaryOpNode(op_token=token, expr=self.parse_power())
        elif token.type == TokenType.SQRT:
            self.advance()
            return UnaryOpNode(op_token=token, expr=self.parse_power())
        
        return self.parse_power()
    
    def parse_power(self):
        node = self.parse_factor()

        while self.current_token.type == TokenType.POW:
            token = self.current_token
            self.advance()
            node = BinOpNode(left=node, op_token=token, right=self.parse_factor())
        
        return node

    def parse_factor(self):
        token = self.current_token

        if token.type == TokenType.NUMBER:
            self.advance()
            return NumberNode(token)
        
        if token.type == TokenType.KEYWORD and token.value in ('PI', 'E'):
            self.advance()
            return NumberNode(token)
        
        elif token.type == TokenType.KEYWORD and token.value in ('true', 'false'):
            self.advance()
            return BooleanNode(token)
        
        elif token.type == TokenType.LBRACE:
            return self.parse_set_or_comprehension()

        elif token.value in ('(', '['):
            if token.value == '(' and not self.is_interval_peeking():
                self.advance()
                node = self.parse_expression()
                self.eat(TokenType.RPAREN)
                return node
            else:
                return self.parse_interval_expression()
        
        elif token.type == TokenType.LOG:
            self.eat(TokenType.LOG)
            self.eat(TokenType.LPAREN)
            base_node = self.parse_expression()    
            self.eat(TokenType.COMMA)              
            argument_node = self.parse_expression()
            self.eat(TokenType.RPAREN)             
            
            return LogNode(base_node, argument_node)
        
        elif token.type == TokenType.LEN:
            self.eat(TokenType.LEN)
            self.eat(TokenType.LPAREN)
            value_node = self.parse_expression()
            self.eat(TokenType.RPAREN)
            
            return LenNode(value_node)
        
        elif token.type == TokenType.ID:
            var_token = self.current_token
            self.eat(TokenType.ID)
            
            if self.current_token and self.current_token.type == TokenType.LPAREN:
                self.advance()
                arg = self.parse_expression()
                self.eat(TokenType.RPAREN)
                return CallNode(var_token.value, arg, is_subscript=False)
                
            elif self.current_token and self.current_token.type == TokenType.LSQBRACE:
                self.advance()
                arg = self.parse_expression()
                if self.current_token and self.current_token.type == TokenType.RSQBRACE:
                    self.advance()
                else:
                    raise SyntaxError("수열 호출의 닫는 대괄호 ']' 누락")
                return CallNode(var_token.value, arg, is_subscript=True)
                
            return VariableNode(var_token)

        raise Exception(f"Unexpected token: {token}")

    def is_interval_peeking(self):
        idx = self.pos + 1
        while idx < len(self.tokens) and self.tokens[idx].type != TokenType.NEWLINE:
            if self.tokens[idx].value == ',':
                return True
            if self.tokens[idx].value in (')', ']', '}'):
                return False
            idx += 1
        return False
    
    def parse_set_or_comprehension(self):
        self.eat(TokenType.LBRACE)
        
        if self.current_token.type == TokenType.ID and self.peek_token() and self.peek_token().type == TokenType.PIPE:
            var_token = self.eat(TokenType.ID)
            self.eat(TokenType.PIPE)
            
            condition = self.parse_expression()
            self.eat(TokenType.RBRACE)
            return SetNode('COMPREHENSION', {'var_name': var_token.value, 'condition': condition})
        
        else:
            elements = []
            if self.current_token.type != TokenType.RBRACE:
                elements.append(self.parse_expression())
                while self.current_token and self.current_token.type == TokenType.COMMA:
                    self.eat(TokenType.COMMA)
                    elements.append(self.parse_expression())
            self.eat(TokenType.RBRACE)
            return SetNode('ELEMENTS', elements)

    def parse_interval_expression(self):
        left_bracket = self.current_token.value
        self.advance()
        
        start_val = self.parse_expression()
        self.eat(TokenType.COMMA)
        end_val = self.parse_expression()
        
        if self.current_token.value not in (')', ']'):
            for i in range(len(self.tokens)):
                print(self.tokens[i])
                if i == self.pos:
                    print("^^^^^^^")
            raise SyntaxError("구간 표현의 닫는 괄호가 올바르지 않음")
        right_bracket = self.current_token.value
        self.advance()
        
        return SetNode('INTERVAL', {
            'left_bracket': left_bracket,
            'left': start_val,
            'right': end_val,
            'right_bracket': right_bracket
        })
    
    def parse_get_statement(self):
        self.eat(TokenType.KEYWORD)
        token = self.current_token
        self.eat(TokenType.ID)
        return GetNode(var_token=token)
    
    def parse_out_statement(self):
        self.eat(TokenType.KEYWORD)
        exprs = []
        while self.current_token and self.current_token.type not in (TokenType.NEWLINE, TokenType.EOF):
            if self.current_token.type == TokenType.STRING:
                exprs.append(StringNode(self.current_token))
                self.advance()
            else:
                exprs.append(self.parse_expression())
        return OutNode(exprs)
    
    def parse_break_statement(self):
        self.eat(TokenType.KEYWORD)
        return BreakNode()
    
    def parse_continue_statement(self):
        self.eat(TokenType.KEYWORD)
        return ContinueNode()
    
    def parse_for_statement(self):  
        self.eat(TokenType.KEYWORD)
        self.eat(TokenType.LPAREN)
            
        var_token = self.eat(TokenType.ID)
        var_node = VariableNode(var_token)
        
        self.eat(TokenType.ASSIGN)
        start_expr = self.parse_expression()
        self.eat(TokenType.COMMA)
        end_expr = self.parse_expression()
        self.eat(TokenType.RPAREN)
        
        body_block = self.parse_block()
        return ForNode(var_node, start_expr, end_expr, body_block)
    
    def parse_while_statement(self):
        self.eat(TokenType.KEYWORD)
        self.eat(TokenType.LPAREN)
        cond_expr = self.parse_expression()
        self.eat(TokenType.RPAREN)
        
        body_block = self.parse_block()
        return WhileNode(cond_expr, body_block)
    
    def parse_if_statement(self):
        self.eat(TokenType.KEYWORD)
        self.eat(TokenType.LPAREN)
        condition = self.parse_expression()
        self.eat(TokenType.RPAREN)
        
        body = self.parse_block()
        
        if self.current_token and self.current_token.type == TokenType.NEWLINE:
            self.advance()
        else_body = None
        if self.current_token and self.current_token.type == TokenType.KEYWORD:
            if self.current_token.value == 'else':
                self.advance()
                else_body = self.parse_block()
                
            elif self.current_token.value == 'elif':
                else_body = self.parse_if_statement()
        return IfNode(condition, body, else_body)
    
    def parse_apply_statement(self):
        self.eat(TokenType.KEYWORD)
        vars_list = []
        
        if self.current_token and self.current_token.type == TokenType.ID:
            vars_list.append(self.eat(TokenType.ID).value)
            while self.current_token and self.current_token.type == TokenType.COMMA:
                self.eat(TokenType.COMMA)
                vars_list.append(self.eat(TokenType.ID).value)
        
        if vars_list:
            return ApplyNode(vars_list)
        return ApplyNode()

    def parse_assume_statement(self):
        self.eat(TokenType.KEYWORD)
        
        self.eat(TokenType.LPAREN)
        condition = self.parse_expression()
        self.eat(TokenType.RPAREN)
        
        body = self.parse_block()
        
        if not (self.current_token and self.current_token.type == TokenType.KEYWORD and self.current_token.value == 'contradict'):
            raise SyntaxError("assume 구문 뒤에 반드시 'contradict' 블록 필요")
        self.eat(TokenType.KEYWORD)
        contradict_body = self.parse_block()
        
        return AssumeNode(condition, body, contradict_body)
    
    def parse_plot_statement(self):
        self.eat(TokenType.KEYWORD)
        
        command = self.eat(TokenType.STRING).value
        if command == 'show':
            return PlotNode('show')
        elif command == 'clear':
            return PlotNode('show')
        elif command == 'save':
            filename = self.eat(TokenType.STRING).value
            return PlotNode('show', filename=filename)
        elif command == 'add':
            func = self.eat(TokenType.ID).value
            domain = self.parse_expression()
            style = self.eat(TokenType.STRING).value
            return PlotNode('add', func=func, domain=domain, style=style)
        elif command == 'remove':
            func = self.eat(TokenType.ID).value
            return PlotNode('remove', func=func)
        else:
            raise SyntaxError("옳지 않은 plot 명령어")
