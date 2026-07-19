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

    def __repr__(self):
        return f"[Function: {self.name}({self.param_name} in {self.domain_set_node}) := {self.elements}]"