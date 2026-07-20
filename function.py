from number_temp import RealNumber

class Function:
    """정의역 검증 능력을 갖춘 심볼릭 함수 객체"""
    def __init__(self, name: str, param_name: str, domain_set_node, body):
        self.name = name
        self.param_name = param_name       # 매개변수 기호명 (예: "x")
        self.domain_set_node = domain_set_node # 정의역 AST 노드 (None일 수 있음)
        self.body = body
        
    def __repr__(self):
        return f"[Function: {self.name}({self.param_name} in {self.domain_set_node}) := {self.body}]"

class Sequence:
    """명시적 seq 키워드로 생성된 수열 객체"""
    def __init__(self, name: str, param_name: str, domain_set_node, elements: list):
        self.name = name
        self.param_name = param_name       # 인덱스 기호명 (예: "n")
        self.domain_set_node = domain_set_node # 인덱스 범위 정의역 노드 (None일 수 있음)
        self.elements = elements

    def __add__(self, other):
        if isinstance(other, RealNumber):
            # S := S + 10 구조: 새 원소를 추가한 새 시퀀스 반환
            return Sequence(self.name, self.param_name, self.domain_set_node, self.elements + [other])
        elif isinstance(other, Sequence):
            # S1 + S2 구조: 두 시퀀스를 합친 새 시퀀스 반환
            return Sequence(self.name, self.param_name, self.domain_set_node, self.elements + other.elements)
        else:
            raise TypeError("지원하지 않는 대수 연산 타입입니다.")

    def __sub__(self, other):
        if isinstance(other, RealNumber):
            new_elements = self.elements.copy()
            
            # 인덱스 범위를 벗어나지 않는지 체크
            if 0 <= other < len(new_elements):
                new_elements.pop(int(other.to_float())) # other번째 항목 삭제
                return Sequence(self.name, self.param_name, self.domain_set_node, new_elements)
            else:
                raise IndexError("[msfm Runtime Error]: 수열의 인덱스 범위를 벗어났습니다.")
        else:
            raise TypeError("[msfm Runtime Error]: 인덱스는 정수여야 합니다.")

    def __repr__(self):
        return f"[Function: {self.name}({self.param_name} in {self.domain_set_node}) := {self.elements}]"