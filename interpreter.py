from tokenizer import TokenType
from number_temp import RealNumber, TrigonometricNumber, LogarithmicNumber, IrrationalNumber


class BreakException(Exception): pass
class ContinueException(Exception): pass
class LoopVarException(Exception): pass
class ApplyException(Exception): pass

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
    _current_instance = None
    def __init__(self):
        self.global_env = Environment()
        self.current_env = self.global_env
        
        self.plot_fig = None
        self.plot_ax = None

    def interpret(self, statements):
        Interpreter._current_instance = self
        result = None
        try:
            for statement in statements:
                result = self.visit(statement)
        finally:
            Interpreter._current_instance = None
        return result

    def visit(self, node):
        method_name = f"visit_{type(node).__name__}"
        visitor = getattr(self, method_name)
        return visitor(node)

    def visit_NumberNode(self, node):
        val = node.value
        import math
        if val == 'PI':
            val = math.pi
        elif val == 'E':
            val = math.e
            
        return RealNumber(val)

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
        from set import RangeSet, IntensionalSet
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
        
        elif op_type == TokenType.AND:
            if isinstance(left_val, RangeSet) and isinstance(right_val, RangeSet):
                return left_val & right_val
            return left_val and right_val
        elif op_type == TokenType.OR or op_type == TokenType.PIPE:
            if isinstance(left_val, RangeSet) and isinstance(right_val, RangeSet):
                return left_val | right_val
            return left_val or right_val
        elif op_type == TokenType.IN:
            
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
        elif op_type == TokenType.NOT:
            from set import RangeSet
            if isinstance(expr_val, RangeSet):
                return ~expr_val
            return not expr_val
        
        if op_type == TokenType.SQRT:    return IrrationalNumber(expr_val)
        elif op_type == TokenType.SIN:   return TrigonometricNumber("SIN", 1.0, expr_val)
        elif op_type == TokenType.COS:   return TrigonometricNumber("COS", 1.0, expr_val)
        elif op_type == TokenType.TAN:   return TrigonometricNumber("TAN", 1.0, expr_val)
        elif op_type == TokenType.ABS:   return abs(expr_val)

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
                condition_node=data['condition'],
                interpreter=self
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
        from parser import SequenceLiteralNode
        from function import Function, Sequence
        

        # 1. 수열 정의인 경우 (body가 SequenceLiteralNode 인 경우)
        if isinstance(node.body, SequenceLiteralNode):
            # 💡 수열 안의 원소 노드들을 지금 즉시 평가하여 진짜 값의 리스트로 만듭니다.
            evaluated_elements = [self.visit(expr) for expr in node.body.elements]
            
            seq_obj = Sequence(
                name=node.name,
                param_name=node.param_name,
                domain_set_node=node.domain,
                elements=evaluated_elements
            )
            return self.current_env.define(node.name, seq_obj)

        # 2. 일반 심볼릭 함수 정의인 경우 (기존의 기호적 보존 유지)
        func_obj = Function(
            name=node.name,
            param_name=node.param_name,
            domain_set_node=node.domain,
            body=node.body,
            interpreter=self
        )
        return self.current_env.define(node.name, func_obj)

    def visit_CallNode(self, node):
        from function import Function, Sequence
        target = self.current_env.lookup(node.name)
        arg_val = self.visit(node.arg)

        if isinstance(target, Function):
            if target.domain_set_node is not None:
                domain_set = self.visit(target.domain_set_node)
                if not (arg_val in domain_set):
                    raise ValueError(f"대수 에러: 입력값 {arg_val}이 정의역을 벗어났습니다.")

            isolated_env = Environment(parent=target.defining_env)
            isolated_env.define(target.param_name, arg_val)

            old_env = self.current_env
            self.current_env = isolated_env
            try:
                return self.visit(target.body)
            finally:
                self.current_env = old_env

        # 수열 항 참조
        elif isinstance(target, Sequence):
            if target.domain_set_node is not None:
                domain_set = self.visit(target.domain_set_node)
                if not (arg_val in domain_set):
                    raise ValueError(
                        f"대수 오류: 인덱스 {arg_val}이(가) "
                        f"수열 '{target.name}'에 지정된 인덱스 범위({domain_set})를 벗어났습니다."
                    )

            # 2. 타입 검증 및 1-based 인덱스 보정
            if not isinstance(arg_val, RealNumber):
                raise TypeError("타입 에러: 수열의 인덱스는 숫자여야 합니다.")
            
            idx = int(arg_val.to_float())
            adjusted_idx = idx - 1
            try:
                return target.elements[adjusted_idx]
            except IndexError:
                raise RuntimeError(f"런타임 에러: 수열 '{target.name}'의 범위를 벗어난 항입니다. (인덱스: {idx})")

        raise TypeError(f"타입 에러: '{node.name}'은(는) 호출 가능한 함수나 수열이 아닙니다.")

    def visit_SequenceLiteralNode(self, node):
        return [self.visit(e) for e in node.elements]

    def visit_AssumeNode(self, node):
        # 1. 진입할 때는 일단 '가정이 성립할 수 있는 가능성'만 보고 임시 환경을 엽니다.
        # (진입 시점에 조건식이 False여도, 블록 내부에서 변수를 수정해 True로 만들 수도 있으므로 일단 진입 허용!)
        assume_env = Environment(parent=self.current_env)
        old_env = self.current_env
        self.current_env = assume_env

        try:
            # assume 본문 블록 실행
            self.visit(node.body)
            
            # apply를 만나지 못하고 정상 종료되면 실패(모순)로 간주하여 강제 예외 발생
            raise RuntimeError("Apply 없는 종료")
            
        except ApplyException:
            # ✨ apply 키워드를 만난 시점 (최종 확정 심사)
            # 💡 [핵심] 중간에 어떤 일이 있었든, '지금 이 순간' 최초의 assume 조건식이 참인지 다시 검사합니다!
            final_check = self.visit(node.condition)
            
            if isinstance(final_check, bool) and final_check == True:
                # 조건이 최종적으로 완벽하게 들어맞았으므로 바깥 세계에 변경 사항을 적용(Commit)합니다.
                for var_name, value in assume_env.bindings.items():
                    old_env.bindings[var_name] = value
                return None  # 정상 탈출 (contradict 블록은 무시됨)
            
            # 만약 apply 시점에 조건이 False라면 예외를 터트려 아래의 contradict 분기로 보냅니다.
            # (즉, 최종 시점까지 모순을 해결하지 못한 경우입니다.)
            pass 
            
        except (ValueError, TypeError, RuntimeError):
            # 블록 내부에서 대수적 도메인 오류나 모순이 터진 경우도 실패로 간주
            pass
            
        finally:
            # 어떤 경우든 임시 환경은 걷어내고 원래 세계관으로 복구
            self.current_env = old_env

        # 3. 최종 심사에서 탈락(모순 발생)했거나 예외가 발생한 경우 복구 블록 실행
        if node.contradict_body:
            return self.visit(node.contradict_body)
        return None

    def visit_ApplyNode(self, node):
        raise ApplyException()

    def visit_PlotNode(self, node):
        import matplotlib.pyplot as plt
        import numpy as np
        from set import RangeSet

        # -----------------------------------------------------------------
        # 0. 맷플롯립 세션(캔버스) 자동 활성화 및 유지
        # -----------------------------------------------------------------
        if self.plot_fig is None or not plt.fignum_exists(self.plot_fig.number):
            self.plot_fig, self.plot_ax = plt.subplots(figsize=(8, 5))
            self.plot_ax.grid(True)
            self.plot_ax.set_title("Algebraic Visualization Session")
            self.plot_ax.set_xlabel("x / n")
            self.plot_ax.set_ylabel("y")

        # 파서가 넘겨준 메인 커맨드 문자열 추출 (예: "add", "show", "clear", "save", "remove")
        cmd = node.command

        # -----------------------------------------------------------------
        # 1. 제어 명령 모드 ("show", "clear", "save", "remove")
        # -----------------------------------------------------------------
        if cmd == "show":
            plt.show()
            self.plot_fig = None
            self.plot_ax = None
            return None

        elif cmd == "clear":
            self.plot_ax.clear()
            self.plot_ax.grid(True)
            self.plot_ax.set_title("Algebraic Visualization Session")
            return None

        elif cmd == "save":
            print('saving?')
            filename = getattr(node, 'filename', None)
            if not filename:
                raise ValueError("대수 오류: 'save' 명령에 저장할 파일명이 지정되지 않았습니다.")
            self.plot_fig.savefig(filename, bbox_inches='tight')
            return None

        elif cmd == "remove":
            # remove할 대상은 파서 구조상 node.func에 문자열 ID로 들어옵니다.
            target_label = getattr(node, 'func', None)
            if not target_label:
                raise ValueError("대수 오류: 'remove' 명령에 삭제할 대상 ID가 지정되지 않았습니다.")
            
            removed = False
            for line in self.plot_ax.get_lines():
                if line.get_label() == target_label:
                    line.remove()
                    removed = True
            for coll in self.plot_ax.collections:
                if coll.get_label() == target_label:
                    coll.remove()
                    removed = True
                    
            if not removed:
                raise RuntimeError(f"런타임 에러: 캔버스에서 '{target_label}' 그래프를 찾을 수 없습니다.")
            
            self.plot_ax.legend()
            plt.draw()
            return None

        # -----------------------------------------------------------------
        # 2. 시각화 모드 ("add")
        # -----------------------------------------------------------------
        elif cmd == "add":
            target_name = getattr(node, 'func', None)
            if not target_name:
                raise ValueError("대수 오류: 'add' 명령에 플롯할 대상 ID가 지정되지 않았습니다.")
                
            target = self.current_env.lookup(target_name)

            # 도메인 세트 노드 가져와서 평가
            domain_node = getattr(node, 'domain', None)
            if not domain_node:
                raise ValueError(f"대수 오류: '{target_name}'을 그리기 위한 정의역 구간이 누락되었습니다.")
                
            domain_set = self.visit(domain_node)
            if not isinstance(domain_set, RangeSet):
                raise TypeError("타입 에러: plot의 범위는 반드시 구간 집합(RangeSet)이어야 합니다.")
            if len(domain_set.intervals) == 0:
                raise ValueError("대수 오류: 빈 집합 구간은 플롯할 수 없습니다.")

            start = domain_set.intervals[0].start
            end = domain_set.intervals[0].end

            if start == float('-inf') or end == float('inf'):
                raise ValueError("대수 오류: 무한대 구간은 플롯할 수 없습니다. 유한한 구간을 주십시오.")

            # 파서 구조상 domain이 있을 때만 style이 존재할 수 있음
            style_str = getattr(node, 'style', "")

            from function import Function, Sequence
            
            # 갈래 2-1: 함수형 플롯
            if isinstance(target, Function):
                x_vals = np.linspace(start, end, 500)
                y_vals = []

                for x in x_vals:
                    wrapped_x = RealNumber(x) if 'RealNumber' in globals() else x
                    isolated_env = Environment(parent=None)
                    isolated_env.define(target.param_name, wrapped_x)
                    
                    old_env = self.current_env
                    self.current_env = isolated_env
                    try:
                        y_res = self.visit(target.body)
                        y_vals.append(y_res.to_float() if hasattr(y_res, 'to_float') else float(y_res))
                    finally:
                        self.current_env = old_env

                if style_str:
                    self.plot_ax.plot(x_vals, y_vals, style_str, label=target_name, linewidth=2)
                else:
                    self.plot_ax.plot(x_vals, y_vals, label=target_name, linewidth=2)
    # 갈래 2-2: 수열형 플롯 (오직 점만 찍기!)
            elif isinstance(target, Sequence):
                istart = int(np.ceil(start))
                iend = int(np.floor(end))
                x_vals = []
                y_vals = []

                for idx in range(istart, iend + 1):
                    adjusted_idx = idx - 1
                    if 0 <= adjusted_idx < len(target.elements):
                        x_vals.append(idx)
                        val = target.elements[adjusted_idx]
                        y_vals.append(val.to_float() if hasattr(val, 'to_float') else float(val))

                # 💡 사용자가 지정한 스타일이 있으면 쓰고, 없으면 기본 빨간 점('ro')으로 처리
                marker_style = style_str if style_str else 'ro'
                
                # linestyle='None'을 주면 점들 사이에 선이 절대 이어지지 않고 점만 찍힙니다.
                self.plot_ax.plot(x_vals, y_vals, marker_style, label=target_name, linestyle='None')

            self.plot_ax.legend()
            plt.draw()
            return None

        raise ValueError(f"대수 오류: 올바르지 않은 plot 명령어입니다. ('{cmd}')")
    
    def visit_LenNode(self, node):
        from function import Sequence
        from set import RangeSet
        
        res = self.visit(node.value)
        if isinstance(res, Sequence):
            return RealNumber(len(res.elements))
        if isinstance(res, RangeSet):
            return RealNumber(res.len())
        raise ValueError(f"대수 오류: len 안에는 집합과 수열만 들어갈 수 있습니다. ('{node.value}')")
