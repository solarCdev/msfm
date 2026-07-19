from tokenizer import TokenType
from number_temp import RealNumber, TrigonometricNumber, LogarithmicNumber, IrrationalNumber


class BreakException(Exception): pass
class ContinueException(Exception): pass
class LoopVarException(Exception): pass

class Environment:
    def __init__(self, parent=None):
        self.bindings = {}
        self._for = None
        self.parent = parent

    def define(self, name, value):
        self.bindings[name] = value
        return value

    def lookup(self, name):
        if name in self.bindings:
            return self.bindings[name]
        if self.parent:
            return self.parent.lookup(name)
        raise RuntimeError(f"정의되지 않은 변수/함수: {name}")
    
    def change(self, name, value):
        if name in self.bindings:
            if self._for == name:
                raise LoopVarException(f"for문 전용 변수: {name}")
            self.bindings[name] = value
            return value
        if self.parent:
            return self.parent.change(name, value)
        raise RuntimeError(f"정의되지 않은 변수/함수: {name}")
    
    def __repr__(self):
        return f"Environment({self.bindings}, parent={self.parent.__repr__()})"

class Interpreter:
    def __init__(self):
        self.global_env = Environment()
        self.current_env = self.global_env

    def interpret(self, statements):
        result = None
        for statement in statements:
            result = self.visit(statement)
        return result

    def visit(self, node):
        method_name = f"visit_{type(node).__name__}"
        visitor = getattr(self, method_name)
        return visitor(node)

    def visit_NumberNode(self, node):
        return RealNumber(node.value)

    def visit_BooleanNode(self, node):
        return node.value

    def visit_StringNode(self, node):
        return node.value

    def visit_VariableNode(self, node):
        return self.current_env.lookup(node.value)
    
    # ---------------------------------------------------------
    # [이항 연산 및 할당 노드 방문]
    # ---------------------------------------------------------
    def visit_AssignNode(self, node):
        var_name = node.left.value
        val = self.visit(node.right)
        try:
            return self.current_env.change(var_name, val)
        except RuntimeError:
            return self.current_env.define(var_name, val)

    def visit_BinOpNode(self, node):
        left_val = self.visit(node.left)
        right_val = self.visit(node.right)
        op_type = node.op_token.type

        if op_type == TokenType.PLUS:     return left_val + right_val
        elif op_type == TokenType.MINUS:  return left_val - right_val
        elif op_type == TokenType.MUL:    return left_val * right_val
        elif op_type == TokenType.DIV:    return left_val / right_val
        elif op_type == TokenType.MOD:    return left_val % right_val
        elif op_type == TokenType.POW:    return left_val ** right_val
        
        elif op_type == TokenType.EQ:     return left_val == right_val
        elif op_type == TokenType.NEQ:    return left_val != right_val
        elif op_type == TokenType.LT:     return left_val < right_val
        elif op_type == TokenType.LTE:    return left_val <= right_val
        elif op_type == TokenType.GT:     return left_val > right_val
        elif op_type == TokenType.GTE:    return left_val >= right_val
        
        elif op_type == TokenType.AND:    return left_val and right_val
        elif op_type == TokenType.OR:     return left_val or right_val
        elif op_type == TokenType.IN:
            from set import RangeSet, IntensionalSet
            if not isinstance(right_val, (RangeSet, IntensionalSet)):
                raise TypeError(f"타입 에러: 'in' 연산의 우항은 반드시 집합이어야 합니다. (받은 타입: {type(right_val).__name__})")
            return left_val in right_val

        raise RuntimeError(f"지원하지 않는 이항 연산자: {node.op_token.value}")

    # ---------------------------------------------------------
    # [단항 연산 및 초월함수 노드 방문]
    # ---------------------------------------------------------
    def visit_UnaryOpNode(self, node):
        expr_val = self.visit(node.expr)
        op_type = node.op_token.type

        if op_type == TokenType.MINUS:   return -expr_val
        elif op_type == TokenType.PLUS:  return expr_val
        elif op_type == TokenType.NOT:   return not expr_val
        
        if op_type == TokenType.SQRT:    return IrrationalNumber(expr_val)
        elif op_type == TokenType.SIN:   return TrigonometricNumber("SIN", 1.0, expr_val)
        elif op_type == TokenType.COS:   return TrigonometricNumber("COS", 1.0, expr_val)
        elif op_type == TokenType.TAN:   return TrigonometricNumber("TAN", 1.0, expr_val)

        raise RuntimeError(f"지원하지 않는 단항 연산자: {node.op_token.value}")

    def visit_LogNode(self, node):
        base_val = self.visit(node.base)
        arg_val = self.visit(node.argument)
        return LogarithmicNumber(base_val, arg_val)

    # ---------------------------------------------------------
    # [블록 및 제어 흐름 노드 방문]
    # ---------------------------------------------------------
    def visit_BlockNode(self, node):
        local_env = Environment(parent=self.current_env)
        
        old_env = self.current_env
        self.current_env = local_env
        
        result = None
        try:
            for statement in node.statements:
                result = self.visit(statement)
        finally:
            self.current_env = old_env
            
        return result

    def visit_IfNode(self, node):
        if self.visit(node.condition):
            return self.visit(node.body)
        elif node.else_body:
            return self.visit(node.else_body)
        return None

    def visit_WhileNode(self, node):
        result = None
        while self.visit(node.cond_expr):
            try:
                result = self.visit(node.body_block)
            except BreakException:
                break
            except ContinueException:
                continue
        return result
    
    def visit_ForNode(self, node):
        start_val = int(self.visit(node.start_expr).to_float())
        end_val = int(self.visit(node.end_expr).to_float())
        var_name = node.var_node.value
        
        for_env = Environment(parent=self.current_env)
        old_env = self.current_env
        self.current_env = for_env
        
        result = None
        
        try:
            for current_val in range(start_val, end_val + 1):
                self.current_env.define(var_name, RealNumber(current_val))
                self.current_env._for = var_name
                    
                try:
                    result = self.visit(node.body_block)
                except BreakException:
                    break
                except ContinueException:
                    continue
        finally:
            self.current_env = old_env
                
        return result

    def visit_BreakNode(self, node):
        raise BreakException()

    def visit_ContinueNode(self, node):
        raise ContinueException()

    def visit_OutNode(self, node):
        output_str = "".join(str(self.visit(expr)) for expr in node.expressions)
        print(output_str)
        return output_str
    
    def visit_GetNode(self, node):
        input_val = RealNumber(input())
        return self.current_env.change(node.var_name, input_val)

    def visit_SetNode(self, node):
        from set import RangeSet, create_range_set_from_iterable, IntensionalSet

        # 1. 조건제시법 집합 (COMPREHENSION) -> { x | x > 0 }
        if node.set_type == 'COMPREHENSION':
            data = node.data
            return IntensionalSet(
                var_name=data['var_name'],
                condition_node=data['condition']
            )

        # 2. 원소 나열식 외연적 집합 (ELEMENTS) -> {1, 2, 3}
        elif node.set_type == 'ELEMENTS':
            evaluated_elements = [self.visit(expr) for expr in node.data]
            return create_range_set_from_iterable(evaluated_elements)

        # 3. 구간 표현식 집합 (INTERVAL) -> [1, 5)
        elif node.set_type == 'INTERVAL':
            data = node.data
            left_res = self.visit(data['left'])
            right_res = self.visit(data['right'])
            
            if not isinstance(left_res, RealNumber) or not isinstance(right_res, RealNumber):
                raise TypeError("타입 에러: 구간의 시작값과 끝값은 반드시 숫자여야 합니다.")
                
            st = left_res.to_float()
            en = right_res.to_float()
            st_closed = data['left_bracket'] == '['
            en_closed = data['right_bracket'] == ']'
            
            if st > en:
                raise ValueError("대수 에러: 구간의 시작값이 끝값보다 클 수 없습니다.")
            from set import Interval
            return RangeSet(Interval(st, en, st_closed, en_closed))

        raise RuntimeError(f"지원하지 않는 집합 타입 노드: {node.set_type}")

    def visit_FunctionDefNode(self, node):
        return self.current_env.define(node.name, f"[Function: {node.name}]")

    def visit_SequenceLiteralNode(self, node):
        return [self.visit(e) for e in node.elements]

    def visit_CallNode(self, node):
        arg_val = self.visit(node.arg)
        print(f"-> {node.name} 호출 시도됨 (인자: {arg_val}, 수열 여부: {node.is_subscript})")
        return arg_val 

    def visit_AssumeNode(self, node):
        if self.visit(node.condition):
            return self.visit(node.body)
        return self.visit(node.contradict_body)

    def visit_ApplyNode(self, node):
        return None

