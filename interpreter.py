from tokenizer import TokenType

# 1. 루프 제어를 위한 뼈대 예외 처리
class BreakException(Exception): pass
class ContinueException(Exception): pass
class LoopVarException(Exception): pass

# 2. 가장 단순한 변수 저장소
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
        if self.parent:
            return self.parent.change(name, value)
        raise RuntimeError(f"정의되지 않은 변수/함수: {name}")

# 3. 메인 인터프리터 뼈대
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
        return float(node.value)

    def visit_BooleanNode(self, node):
        return node.value

    def visit_StringNode(self, node):
        return node.value

    def visit_VariableNode(self, node):
        return self.current_env.lookup(node.value)

    def visit_GetNode(self, node):
        return self.current_env.lookup(node.var_name)

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
        
        # 비교 연산
        elif op_type == TokenType.EQ:     return left_val == right_val
        elif op_type == TokenType.NEQ:    return left_val != right_val
        elif op_type == TokenType.LT:     return left_val < right_val
        elif op_type == TokenType.LTE:    return left_val <= right_val
        elif op_type == TokenType.GT:     return left_val > right_val
        elif op_type == TokenType.GTE:    return left_val >= right_val
        
        # 논리 및 포함 연산 (집합 구현 전이므로 임시 처리)
        elif op_type == TokenType.AND:    return left_val and right_val
        elif op_type == TokenType.OR:     return left_val or right_val
        elif op_type == TokenType.IN:     return False  # 일단 유예

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
        
        # 초월함수 연산도 일단 파이썬 기본 기능으로 임시 매핑
        import math
        if op_type == TokenType.SQRT:    return math.sqrt(expr_val)
        elif op_type == TokenType.SIN:   return math.sin(expr_val)
        elif op_type == TokenType.COS:   return math.cos(expr_val)
        elif op_type == TokenType.TAN:   return math.tan(expr_val)

        raise RuntimeError(f"지원하지 않는 단항 연산자: {node.op_token.value}")

    def visit_LogNode(self, node):
        import math
        base_val = self.visit(node.base)
        arg_val = self.visit(node.argument)
        return math.log(arg_val) / math.log(base_val)

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
        start_val = int(self.visit(node.start_expr))
        end_val = int(self.visit(node.end_expr))
        var_name = node.var_node.value
        
        for_env = Environment(parent=self.current_env)
        old_env = self.current_env
        self.current_env = for_env
        
        
        result = None
        
        try:
            for current_val in range(start_val, end_val + 1):
                self.current_env.define(var_name, float(current_val))
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

    # ---------------------------------------------------------
    # [구체적 구현을 완전히 유예한 선언 및 복합 노드들]
    # ---------------------------------------------------------
    def visit_SetNode(self, node):
        # 집합 및 구간 객체 생성을 유예하고 노드 구조나 기본 정보만 껍데기로 리턴
        return f"[SetNode: {node.set_type}]"

    def visit_FunctionDefNode(self, node):
        # 함수/수열 정의 자체를 유예하고, 이름만 스코프에 임시로 등록해둠
        return self.current_env.define(node.name, f"[Function: {node.name}]")

    def visit_SequenceLiteralNode(self, node):
        # seq 뒤의 리터럴은 임시로 파이썬 리스트로 풀어둠
        return [self.visit(e) for e in node.elements]

    def visit_CallNode(self, node):
        # 함수 호출/수열 인덱싱 유예. 
        # 일단 문법이 도는지만 보기 위해 인자값을 그대로 리턴하거나 더미값을 반환
        arg_val = self.visit(node.arg)
        print(f"-> {node.name} 호출 시도됨 (인자: {arg_val}, 수열 여부: {node.is_subscript})")
        return arg_val  # 더미 반환

    def visit_AssumeNode(self, node):
        # assume - contradict의 상위 흐름만 탈 수 있도록 참/거짓 분기만 연결
        if self.visit(node.condition):
            return self.visit(node.body)
        return self.visit(node.contradict_body)

    def visit_ApplyNode(self, node):
        # 증명 증서 적용부 유예
        return None

    def visit_OutNode(self, node):
        output_str = "".join(str(self.visit(expr)) for expr in node.expressions)
        print(output_str)
        return output_str
    
    def visit_GetNode(self, node):
        self.current_env.define(node.var_name, float(input()))