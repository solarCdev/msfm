from fractions import Fraction
import math

class RealNumber:
    def __init__(self, rational_part=0, surd_coeff=0, surd_root=1):
        self.a = rational_part
        self.b = surd_coeff
        self.c = surd_root

    def to_float(self):
        """맷플롯립 plot이나 크기 비교용 소수점 변환 메서드"""
        
        # a 평가
        val_a = self.a.to_float() if hasattr(self.a, 'to_float') else float(self.a)
        # b 평가
        val_b = self.b.to_float() if hasattr(self.b, 'to_float') else float(self.b)
        # c 평가
        val_c = self.c.to_float() if hasattr(self.c, 'to_float') else float(self.c)
        
        if val_c < 0:
            raise RuntimeError("루트 안이 음수가 될 수 없습니다 (실수 범위 제한).")
            
        return val_a + (val_b * math.sqrt(val_c))

    def simplify(self):
        """
        스스로를 최적화하는 메서드
        1. c가 완전제곱수인지 판별하여 b와 곱한 뒤 a로 흡수
        2. c 내부의 제곱수를 꺼내 b를 업데이트
        3. b가 0이 되면 c를 1로 초기화하여 메모리 절약
        """
        # 앞서 정립한 simplify_surd 로직을 내부 시스템에 맞게 적용
        # (여기에 분모의 유리화 및 동류항 묶기 필터가 추가됩니다)
        return self

    def __repr__(self):
        # 출력을 깔끔하게 보기 위한 문자열 포맷팅
        if self.b == 0:
            return f"{self.a}"
        if self.a == 0:
            return f"{self.b}*sqrt({self.c})"
        return f"({self.a} + {self.b}*sqrt({self.c}))"