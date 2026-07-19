import math

class Number:
    """최상위 부모 클래스 (타입 검사용 뼈대)"""
    def to_float(self) -> float:
        raise NotImplementedError()

class RealNumber(Number):
    def __init__(self, value):
        if isinstance(value, RealNumber):
            self.value = value.value
        else:
            self.value = float(value)

    # --- 산술 연산 ---
    def __add__(self, other): return RealNumber(self.value + RealNumber(other).value)
    def __radd__(self, other): return self.__add__(other)
    def __sub__(self, other): return RealNumber(self.value - RealNumber(other).value)
    def __rsub__(self, other): return RealNumber(RealNumber(other).value - self.value)
    def __mul__(self, other): return RealNumber(self.value * RealNumber(other).value)
    def __rmul__(self, other): return self.__mul__(other)
    def __truediv__(self, other): return RealNumber(self.value / RealNumber(other).value)
    def __rtruediv__(self, other): return RealNumber(RealNumber(other).value / self.value)
    def __pow__(self, other): return RealNumber(self.value ** RealNumber(other).value)
    def __mod__(self, other): return RealNumber(self.value % RealNumber(other).value)
    def __neg__(self): return RealNumber(-self.value)

    # --- 부등호 비교 ---
    def __lt__(self, other): return self.value < RealNumber(other).value
    def __le__(self, other): return self.value <= RealNumber(other).value
    def __gt__(self, other): return self.value > RealNumber(other).value
    def __ge__(self, other): return self.value >= RealNumber(other).value
    def __eq__(self, other):
        if not isinstance(other, RealNumber):
            try: other = RealNumber(other)
            except: return False
        return self.value == other.value

    # --- 출력 및 변환 ---
    def to_float(self) -> float:
        return self.value

    def __str__(self):
        if self.value.is_integer():
            return str(int(self.value))
        return str(self.value)

    def __repr__(self):
        return f"RealNumber({self.value})"


# =========================================================================
# 🔥 클래스인 척하는 초월함수 팩토리 함수들 (생성 즉시 RealNumber 반환)
# =========================================================================

def TrigonometricNumber(func_type, coeff, angle):
    c = float(coeff.to_float()) if hasattr(coeff, 'to_float') else float(coeff)
    a = float(angle.to_float()) if hasattr(angle, 'to_float') else float(angle)
    
    ftype = func_type.upper()
    rad = math.radians(a)
    
    if ftype == "SIN": val = math.sin(rad)
    elif ftype == "COS": val = math.cos(rad)
    elif ftype == "TAN": val = math.tan(rad)
    else: raise ValueError(f"지원하지 않는 삼각함수 타입: {func_type}")
    
    return RealNumber(c * val)


def LogarithmicNumber(base, argument, coeff=1.0):
    b = float(base.to_float()) if hasattr(base, 'to_float') else float(base)
    arg = float(argument.to_float()) if hasattr(argument, 'to_float') else float(argument)
    c = float(coeff.to_float()) if hasattr(coeff, 'to_float') else float(coeff)
    
    return RealNumber(c * math.log(arg, b))


def ExponentialNumber(base, exponent, coeff=1.0):
    b = float(base.to_float()) if hasattr(base, 'to_float') else float(base)
    e = float(exponent.to_float()) if hasattr(exponent, 'to_float') else float(exponent)
    c = float(coeff.to_float()) if hasattr(coeff, 'to_float') else float(coeff)
    
    return RealNumber(c * (b ** e))


def IrrationalNumber(root, coeff=1.0):
    r = float(root.to_float()) if hasattr(root, 'to_float') else float(root)
    c = float(coeff.to_float()) if hasattr(coeff, 'to_float') else float(coeff)
    
    return RealNumber(c * math.sqrt(r))