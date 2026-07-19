from fractions import Fraction
import math
from abc import abstractmethod, ABC

def get_prime_factors(n: int):
    factors = {}
    
    while n % 2 == 0:
        factors[2] = factors.get(2, 0) + 1
        n //= 2
        
    d = 3
    while d * d <= n:
        while n % d == 0:
            factors[d] = factors.get(d, 0) + 1
            n //= d
        d += 2
        
    if n > 1:
        factors[n] = factors.get(n, 0) + 1
        
    return factors

class Number(ABC):
    @abstractmethod
    def __eq__(self):
        pass
    @abstractmethod
    def simplify(self):
        pass
    @abstractmethod
    def invert(self):
        pass
    @abstractmethod
    def __mul__(self, other):
        pass
    @abstractmethod
    def to_float(self):
        pass
    @abstractmethod
    def __add__(self, other):
        pass
    @abstractmethod
    def __repr__(self):
        pass
    def __radd__(self, other):
        self.__add__(other)
    def __sub__(self, other):
        return self + (other * RationalNumber(-1))
    def __rsub__(self, other):
        return other + (self * RationalNumber(-1))
    def __truediv__(self, other):   
        if isinstance(other, Number):
            inverted_other = other.invert()
            return self * inverted_other
        return NotImplemented
    def __rtruediv__(self, other):
        inverted_self = self.invert()
        return other * inverted_self
    def __pow__(self, exponent):
        return ExponentialNumber(coeff=1, base=self, exponent=exponent).simplify()
    def __float__(self):
        return self.to_float()

class RealNumber(Number):
    def __init__(self, *args):
        self.expression = list(args)

    def simplify(self):
        cleaned_terms = [t.simplify() for t in self.expression]

        final_expression = []
        for term in cleaned_terms:
            if hasattr(term, 'coeff') and term.coeff == 0:
                continue
            if term == 0:
                continue
            final_expression.append(term)
            
        if not final_expression:
            return RationalNumber(0)
        
        total_result = sum(final_expression)
        return total_result
    
    def to_float(self) -> float:
        return sum(float(term) for term in self.expression)

    def __repr__(self):
        if not self.expression:
            return "0"
        return " + ".join(str(term) for term in self.expression).replace("+ -", "- ")
    
    def __add__(self, other):
        if isinstance(other, RealNumber):
            return RealNumber(*(self.expression), *(other.expression)).simplify()
        if other == 0:
            return self
        return RealNumber(*(self.expression), other).simplify()

    def __radd__(self, other):
        return self.__add__(other)

    def __mul__(self, other):
        self_terms = self.expression
        
        if isinstance(other, RealNumber):
            other_terms = other.expression
        else:
            other_terms = [other]
            
        new_num = RealNumber([])
        
        for s_term in self_terms:
            for o_term in other_terms:
                product = s_term * o_term
                
                new_num += product
                    
        if new_num.expression:
            return RationalNumber(0)
            
        return new_num.simplify()

    def __rmul__(self, other):
        return self.__mul__(other)

    def invert(self):
        return Division(numerator=RationalNumber(1), denominator=self).simplify()

class Product(Number):
    def __init__(self, coeff=1, terms=None):
        self.coeff = RationalNumber(coeff)
        self.terms = terms if terms is not None else []

    def simplify(self):
        
        cleaned_terms = []
        accumulated_coeff = self.coeff

        for term in self.terms:
            ts = term.simplify() if hasattr(term, 'simplify') else term
            
            if isinstance(ts, (int, RationalNumber)):
                accumulated_coeff *= RationalNumber(ts)
            elif isinstance(ts, Product):
                accumulated_coeff *= ts.coeff
                cleaned_terms.extend(ts.terms)
            else:
                # 일반 단항식 객체인 경우
                if hasattr(ts, 'coeff') and ts.coeff != 1:
                    accumulated_coeff *= ts.coeff
                    # 계수를 부모 모르게 1로 직접 바꾸는 대신, 
                    # 안전하게 계수가 1인 새 객체를 생성하는 것이 디버깅에 안전합니다.
                    import copy
                    ts_pure = copy.copy(ts)
                    ts_pure.coeff = RationalNumber(1)
                    cleaned_terms.append(ts_pure)
                else:
                    cleaned_terms.append(ts)

        # 2. 계수가 0이면 전체가 0
        if accumulated_coeff == 0:
            return RationalNumber(0)

        # 3. 같은 종류의 초월함수/무리수가 리스트 안에 남아있다면 여기서 상쇄/약분 시도
        # 예: [log(2,3), log(3,2)] 또는 [2^√3, 2^-√3]
        final_terms = []
        skip_indices = set()
        
        for i in range(len(cleaned_terms)):
            if i in skip_indices: continue
            term_i = cleaned_terms[i]
            
            matched = False
            for j in range(i + 1, len(cleaned_terms)):
                if j in skip_indices: continue
                term_j = cleaned_terms[j]
                
                # 두 단항식을 곱해봅니다. (각 클래스의 __mul__ 가동)
                # 만약 같은 종류라면 Product가 아닌 유리수나 단일 단항식으로 합쳐질 것입니다.
                prod = term_i * term_j
                if not isinstance(prod, Product):
                    # 성공적으로 합쳐짐! 결과를 계수에 반영하거나 항에 반영
                    if isinstance(prod, (int, RationalNumber)):
                        accumulated_coeff *= RationalNumber(prod)
                    elif hasattr(prod, 'coeff'):
                        accumulated_coeff *= prod.coeff
                        import copy
                        prod_pure = copy.copy(prod)
                        prod_pure.coeff = RationalNumber(1)
                        final_terms.append(prod_pure)
                    else:
                        final_terms.append(prod)
                        
                    skip_indices.add(j)
                    matched = True
                    break
            
            if not matched:
                final_terms.append(term_i)

        # 4. 최종 정리된 항이 없다면 순수 유리수 반환
        if not final_terms:
            return RationalNumber(accumulated_coeff)

        # 5. 알맹이가 1개면 껍데기 탈출
        if len(final_terms) == 1:
            single_term = final_terms[0]
            if hasattr(single_term, 'coeff'):
                import copy
                res = copy.copy(single_term)
                res.coeff = accumulated_coeff
                return res
            return single_term

        return Product(coeff=accumulated_coeff, terms=final_terms)

    def float(self) -> float:
        val = float(self.coeff)
        for term in self.terms:
            val *= term.float() if hasattr(term, 'float') else float(term)
        return val

    def __str__(self):
        terms_str = " * ".join(str(t) for t in self.terms)
        if self.coeff == 1:
            return terms_str
        return f"{self.coeff} * {terms_str}"
    
    def __mul__(self, other):
        
        if isinstance(other, (int, RationalNumber)):
            return Product(coeff=self.coeff * RationalNumber(other), terms=self.terms).simplify()
            
        if isinstance(other, Product):
            return Product(coeff=self.coeff * other.coeff, terms=self.terms + other.terms).simplify()
            
        if isinstance(other, RealNumber):
            return other.__rmul__(self)
            
        if hasattr(other, 'coeff'):
            return Product(coeff=self.coeff, terms=self.terms + [other]).simplify()
            
        return NotImplemented

    def __rmul__(self, other):
        return self.__mul__(other)
    
    def invert(self):
        numerator_coeff = RationalNumber(1) / self.coeff
        
        numerator_terms = []
        denominator_terms = []
        
        for term in self.terms:
            inverted = term.invert() if hasattr(term, 'invert') else term
            if isinstance(inverted, Division):
                denominator_terms.append(inverted.denominator)
            else:
                numerator_terms.append(inverted)
                
        if numerator_terms:
            new_num = Product(coeff=numerator_coeff, terms=numerator_terms).simplify()
        else:
            new_num = numerator_coeff
            
        if denominator_terms:
            new_den = Product(coeff=1, terms=denominator_terms).simplify()
        else:
            new_den = RationalNumber(1)
            
        if new_den == 1:
            return new_num
            
        return Division(numerator=new_num, denominator=new_den).simplify()

class Division(Number):
    def __init__(self, numerator, denominator):
        self.numerator = numerator
        self.denominator = denominator

    def simplify(self):
        num = self.numerator.simplify() if hasattr(self.numerator, 'simplify') else self.numerator
        den = self.denominator.simplify() if hasattr(self.denominator, 'simplify') else self.denominator

        if isinstance(den, (int, RationalNumber)):
            if den == 0: raise ZeroDivisionError()
            return num / den

        if isinstance(den, RealNumber) and len(den.expression) == 2:
            terms = den.expression
            
            if any(isinstance(t, IrrationalNumber) for t in terms):
                conjugate_den = terms[0] - terms[1]
                
                new_num = num * conjugate_den
                new_den = den * conjugate_den
                if isinstance(new_den, Number):
                    new_den = new_den.simplify()
                return Division(numerator=new_num.simplify(), denominator=new_den)
        if isinstance(den, Number):
            den = den.simplify()
        return Division(numerator=num.simplify(), denominator=den)

    def to_float(self) -> float:
        if isinstance(self.numerator, RationalNumber):
            return float(self.numerator) / float(self.denominator)
        return float(self.numerator) / float(self.denominator)

    def __repr__(self):
        return f"({self.numerator}) / ({self.denominator})"
    
    def invert(self):
        return Division(self.denominator, self.numerator).simplify()
    
    def __mul__(self, other):
        return Division(numerator=self.numerator * other, denominator=self.denominator).simplify()

    def __rmul__(self, other):
        return Division(numerator=other * self.numerator, denominator=self.denominator).simplify()

class RationalNumber(Number):
    def __init__(self, value):
        if isinstance(value, RationalNumber):
            self.value = value.value
        elif isinstance(value, Fraction):
            self.value = value
        else:
            self.value = Fraction(value)

    def simplify(self):
        return self

    def invert(self):
        return RationalNumber(1 / self.value)

    def to_float(self):
        return float(self.value)

    def __add__(self, other):
        if isinstance(other, RationalNumber):
            return RationalNumber(self.value + other.value)
        return NotImplemented

    def __mul__(self, other):
        if isinstance(other, (int, Fraction)):
            return RationalNumber(self.value * Fraction(other))
            
        if isinstance(other, RationalNumber):
            return RationalNumber(self.value * other.value)
            
        return NotImplemented

    def __rmul__(self, other):
        return self.__mul__(other)

    def __repr__(self):
        return str(self.value)
    
    def __eq__(self, other):
        if isinstance(other, RationalNumber):
            return self.value == other.value
        return False

class IrrationalNumber(Number):
    def __init__(self, coeff=1, root=1):
        self.coeff = RationalNumber(coeff)
        self.root = RationalNumber(root)

    def simplify(self):
        if self.root.value <= 1:
            if self.root.value == 0:
                return RationalNumber(0)
            if self.root.value == 1:
                return RationalNumber(self.coeff)

        root_val = self.root.value
        outside_multiplier = 1
        d = 2
        
        while d * d <= root_val:
            target_square = d * d
            while root_val % target_square == 0:
                outside_multiplier *= d
                root_val //= target_square
            d += 1

        new_coeff = self.coeff * outside_multiplier
        
        if root_val == 1:
            return RationalNumber(new_coeff)
        return IrrationalNumber(coeff=RationalNumber(new_coeff), root=RationalNumber(root_val))
    
    def to_float(self) -> float:
        return float(self.coeff) * math.sqrt(self.root)

    def __repr__(self):
        if self.coeff == 0:
            return "0"
        if self.coeff == 1:
            return f"√{self.root}"
        if self.coeff == -1:
            return f"-√{self.root}"
        return f"({self.coeff})*√{self.root}"
    
    def __add__(self, other):
        if isinstance(other, IrrationalNumber) and self.root == other.root:
            new_coeff = self.coeff + other.coeff
            if new_coeff == 0:
                
                return RationalNumber(0)
            return IrrationalNumber(coeff=new_coeff, root=self.root).simplify()
        if isinstance(other, RealNumber):
            return other.__radd__(self)
        if isinstance(other, Number):
            return RealNumber(self, other)
        if other == 0:
            return self
        return RealNumber(self, RationalNumber(other))
    
    def __mul__(self, other):
        if isinstance(other, (int, RationalNumber)):
            if other == 0: return RationalNumber(0)
            return IrrationalNumber(coeff=self.coeff * RationalNumber(other), root=self.root).simplify()

        if isinstance(other, IrrationalNumber):
            return IrrationalNumber(coeff=self.coeff * other.coeff, root=self.root * other.root).simplify()

        if isinstance(other, RealNumber):
            return other.__rmul__(self)

        return Product(coeff=1, terms=[self, other]).simplify()

    def __rmul__(self, other):
        return self.__mul__(other)

    def invert(self):
        new_coeff = RationalNumber(1) / (self.coeff * self.root)
        return IrrationalNumber(coeff=new_coeff, root=self.root).simplify()
    
    def __eq__(self, other):
        if isinstance(other, IrrationalNumber):
            return self.coeff == other.coeff and self.root == other.root
        return False

class TrigonometricNumber(Number):
    def __init__(self, func_type, coeff=RationalNumber(1), angle=RationalNumber(0)):
        self.func_type = func_type.upper() # SIN, COS, TAN
        self.coeff = RationalNumber(coeff)
        self.angle = angle

    def simplify(self):
        if isinstance(self.angle, Number):
            self.angle = self.angle.simplify()
        if not isinstance(self.angle, RationalNumber):
            return self

        angle_val = (self.angle.to_float()) % 360
        
        specials = {
            "SIN": {
                # 1사분면
                0: RationalNumber(Fraction(0, 1)), 
                30: RationalNumber(Fraction(1, 2)), 
                45: IrrationalNumber(coeff=RationalNumber(Fraction(1, 2)), root=2), 
                60: IrrationalNumber(coeff=RationalNumber(Fraction(1, 2)), root=3), 
                90: RationalNumber(Fraction(1, 1)),
                # 2사분면
                120: IrrationalNumber(coeff=RationalNumber(Fraction(1, 2)), root=3), 
                135: IrrationalNumber(coeff=RationalNumber(Fraction(1, 2)), root=2), 
                150: RationalNumber(Fraction(1, 2)), 
                180: RationalNumber(Fraction(0, 1)),
                # 3사분면
                210: RationalNumber(Fraction(-1, 2)), 
                225: IrrationalNumber(coeff=RationalNumber(Fraction(-1, 2)), root=2), 
                240: IrrationalNumber(coeff=RationalNumber(Fraction(-1, 2)), root=3), 
                270: RationalNumber(Fraction(-1, 1)),
                # 4사분면
                300: IrrationalNumber(coeff=RationalNumber(Fraction(-1, 2)), root=3), 
                315: IrrationalNumber(coeff=RationalNumber(Fraction(-1, 2)), root=2), 
                330: RationalNumber(Fraction(-1, 2))
            },
            "COS": {
                # 1사분면
                0: RationalNumber(Fraction(1, 1)), 
                30: IrrationalNumber(coeff=RationalNumber(Fraction(1, 2)), root=3), 
                45: IrrationalNumber(coeff=RationalNumber(Fraction(1, 2)), root=2), 
                60: RationalNumber(Fraction(1, 2)), 
                90: RationalNumber(Fraction(0, 1)),
                # 2사분면
                120: RationalNumber(Fraction(-1, 2)), 
                135: IrrationalNumber(coeff=RationalNumber(Fraction(-1, 2)), root=2), 
                150: IrrationalNumber(coeff=RationalNumber(Fraction(-1, 2)), root=3), 
                180: RationalNumber(Fraction(-1, 1)),
                # 3사분면
                210: IrrationalNumber(coeff=RationalNumber(Fraction(-1, 2)), root=3), 
                225: IrrationalNumber(coeff=RationalNumber(Fraction(-1, 2)), root=2), 
                240: RationalNumber(Fraction(-1, 2)), 
                270: RationalNumber(Fraction(0, 1)),
                # 4사분면
                300: RationalNumber(Fraction(1, 2)), 
                315: IrrationalNumber(coeff=RationalNumber(Fraction(1, 2)), root=2), 
                330: IrrationalNumber(coeff=RationalNumber(Fraction(1, 2)), root=3)
            },
            "TAN": {
                # 1사분면
                0: RationalNumber(Fraction(0, 1)), 
                30: IrrationalNumber(coeff=RationalNumber(Fraction(1, 3)), root=3), 
                45: RationalNumber(Fraction(1, 1)), 
                60: IrrationalNumber(coeff=RationalNumber(Fraction(1, 1)), root=3),
                # 2사분면
                120: IrrationalNumber(coeff=RationalNumber(Fraction(-1, 1)), root=3), 
                135: RationalNumber(Fraction(-1, 1)), 
                150: IrrationalNumber(coeff=RationalNumber(Fraction(-1, 3)), root=3), 
                180: RationalNumber(Fraction(0, 1)),
                # 3사분면
                210: IrrationalNumber(coeff=RationalNumber(Fraction(1, 3)), root=3), 
                225: RationalNumber(Fraction(1, 1)), 
                240: IrrationalNumber(coeff=RationalNumber(Fraction(1, 1)), root=3),
                # 4사분면
                300: IrrationalNumber(coeff=RationalNumber(Fraction(-1, 1)), root=3), 
                315: RationalNumber(Fraction(-1, 1)), 
                330: IrrationalNumber(coeff=RationalNumber(Fraction(-1, 3)), root=3)
                # 90도와 270도는 탄젠트 값이 정의되지 않으므로 제외
            }
        }
        
        if self.func_type in specials and angle_val in specials[self.func_type]:
            target_value = specials[self.func_type][angle_val]
            
            if isinstance(target_value, RationalNumber):
                return self.coeff * target_value
            
            elif isinstance(target_value, IrrationalNumber):
                return IrrationalNumber(coeff=self.coeff * target_value.coeff, root=target_value.root)

        return self

    def to_float(self) -> float:
        rad = math.radians(float(self.angle))
        if self.func_type == "SIN": return float(self.coeff) * math.sin(rad)
        if self.func_type == "COS": return float(self.coeff) * math.cos(rad)
        if self.func_type == "TAN": return float(self.coeff) * math.tan(rad)
        
    def __repr__(self):
        if self.coeff == 0: return "0"
        func_str = f"{self.func_type.lower()}({self.angle})"
        if self.coeff == 1: return func_str
        if self.coeff == -1: return f"-{func_str}"
        return f"{self.coeff}*{func_str}"
    
    def __add__(self, other):
        if isinstance(other, TrigonometricNumber) and self.func_type == other.func_type and self.angle == other.angle:
            new_coeff = self.coeff + other.coeff
            if new_coeff == 0:
                return RationalNumber(0)
            return TrigonometricNumber(func_type=self.func_type, coeff=new_coeff, angle=self.angle).simplify()

        if isinstance(other, RealNumber):
            return other.__radd__(self)
        if other == 0:
            return self
        return RealNumber(self, other).simplify()

    def __radd__(self, other):
        return self.__add__(other)

    def __mul__(self, other):
        if isinstance(other, RationalNumber):
            if other == 0: return RationalNumber(0)
            return TrigonometricNumber(func_type=self.func_type, coeff=self.coeff * RationalNumber(other), angle=self.angle).simplify()

        if isinstance(other, RealNumber):
            return other.__rmul__(self)

        return Product(coeff=1, terms=[self, other]).simplify()

    def __rmul__(self, other):
        return self.__mul__(other)

    def invert(self):
        return Division(numerator=RationalNumber(1), denominator=self)
    
    def __eq__(self, other):
        if not isinstance(other, TrigonometricNumber):
            return NotImplemented()
        return self.func_type == other.func_type and self.angle == other.angle and self.coeff == other.coeff
    
class LogarithmicNumber(Number):
    def __init__(self, base, arg, coeff=1):
        self.base = base
        self.arg = arg
        self.coeff = RationalNumber(coeff)

    def simplify(self):
        if isinstance(self.base, Number):
            self.base = self.base.simplify()
        if isinstance(self.arg, Number):
            self.arg = self.arg.simplify()
        if not isinstance(self.base, (int, RationalNumber)) or not isinstance(self.arg, (int, RationalNumber)):
            return self
        if self.arg == RationalNumber(0):
            return RationalNumber(self.coeff)

        if self.arg == RationalNumber(Fraction(1, 2)):
            
            if self.base == RationalNumber(1):
                return IrrationalNumber(coeff=self.coeff, root=base_frac.numerator).simplify()
            
            else:
                new_coeff = self.coeff / base_frac.denominator
                new_root = base_frac.numerator * base_frac.denominator
                return IrrationalNumber(coeff=new_coeff, root=new_root).simplify()

        if arg_frac.denominator == 1:
            try:
                val = base_frac ** arg_frac.numerator
                return self.coeff * val
            except ZeroDivisionError:
                return self

        return self

    def to_float(self) -> float:
        arg_value = float(self.arg)
        base_value = float(self.base)
        
        return float(self.coeff) * (math.log(arg_value) / math.log(base_value))
        
    def __repr__(self):
        if self.coeff == 0: return "0"
        log_str = f"log_{self.base}({self.arg})"
        if self.coeff == 1: return log_str
        if self.coeff == -1: return f"-{log_str}"
        return f"{self.coeff}*{log_str}"

    def __add__(self, other):
        if isinstance(other, LogarithmicNumber) and self.base == other.base and self.arg == other.arg:
            new_coeff = self.coeff + other.coeff
            if new_coeff == 0:
                return RationalNumber(0)
            return LogarithmicNumber(base=self.base, arg=self.arg, coeff=new_coeff).simplify()

        if isinstance(other, RealNumber):
            return other.__radd__(self)
        
        if other == 0:
            return self
            
        return RealNumber(self, other).simplify()

    def __radd__(self, other):
        return self.__add__(other)

    def __mul__(self, other):
        if isinstance(other, (int, RationalNumber)):
            if other == 0: return RationalNumber(0)
            return LogarithmicNumber(base=self.base, arg=self.arg, coeff=self.coeff * RationalNumber(other)).simplify()

        if isinstance(other, RealNumber):
            return other.__rmul__(self)

        return Product(coeff=1, terms=[self, other]).simplify()

    def __eq__(self, other):
        if not isinstance(other, LogarithmicNumber):
            return False
        return self.arg == other.arg and self.base == other.base and self.coeff == other.coeff

    def __rmul__(self, other):
        return self.__mul__(other)
    
    def invert(self):
        return LogarithmicNumber(
            coeff=RationalNumber(1) / self.coeff,
            base=self.arg,
            arg=self.base
        ).simplify()

class ExponentialNumber(Number):
    def __init__(self, base, exponent, coeff=1):
        self.base = base
        self.exponent = exponent
        self.coeff = RationalNumber(coeff)

    def simplify(self):
        if isinstance(self.base, Number):
            self.base.simplify()
            if isinstance(self.base, Number):
                return self
        if isinstance(self.exponent, Number):
            self.exponent.simplify()
            if isinstance(self.exponent, Number):
                return self
        base_frac = RationalNumber(self.base)
        exponent_frac = RationalNumber(self.exponent)

        if base_frac <= 0 or base_frac == 1 or exponent_frac <= 0:
            return self

        if exponent_frac == 1:
            return RationalNumber(0)
        if base_frac == exponent_frac:
            return self.coeff * RationalNumber(1)

        try:
            def get_frac_factors(frac):
                num_fact = get_prime_factors(frac.numerator)
                den_fact = get_prime_factors(frac.denominator)
                all_fact = {p: k for p, k in num_fact.items()}
                for p, k in den_fact.items():
                    all_fact[p] = all_fact.get(p, 0) - k
                return {p: k for p, k in all_fact.items() if k != 0}

            base_factors = get_frac_factors(base_frac)
            exponent_factors = get_frac_factors(exponent_frac)

            if len(base_factors) == 1 and len(exponent_factors) == 1:
                base_prime, base_exp = list(base_factors.items())[0]
                exponent_prime, exponent_exp = list(exponent_factors.items())[0]

                if base_prime == exponent_prime:
                    return self.coeff * RationalNumber(exponent_exp, base_exp)
        except Exception:
            pass

        return self

    def to_float(self):
        base_value = float(self.base)
        exponent_value = float(self.exponent)
        
        return float(self.coeff) * (base_value ** exponent_value)
        
    def __eq__(self, other):
        if not isinstance(other, ExponentialNumber):
            return False
        return self.base == other.base and self.coeff == other.coeff and self.exponent == other.exponent
    
    def __repr__(self):
        if self.coeff == 0: return "0"
        exp_str = f"{self.base}^{self.exponent}"
        if self.coeff == 1: return exp_str
        if self.coeff == -1: return f"-{exp_str}"
        return f"{self.coeff}*({exp_str})"
    
    def __add__(self, other):
        if isinstance(other, ExponentialNumber) and self.base == other.base and self.exponent == other.exponent:
            new_coeff = self.coeff + other.coeff
            if new_coeff == 0:
                return RationalNumber(0)
            return ExponentialNumber(base=self.base, exponent=self.exponent, coeff=new_coeff).simplify()

        if isinstance(other, RealNumber):
            return other.__radd__(self)
        
        if other == 0:
            return self
            
        return RealNumber(self, other).simplify()

    def __radd__(self, other):
        return self.__add__(other)

    def __mul__(self, other):
        if isinstance(other, (int, RationalNumber)):
            if other == 0: return RationalNumber(0)
            return ExponentialNumber(base=self.base, exponent=self.exponent, coeff=self.coeff * RationalNumber(other)).simplify()

        if isinstance(other, ExponentialNumber) and self.base == other.base:
            return ExponentialNumber(base=self.base, exponent=self.exponent + other.exponent, coeff=self.coeff * other.coeff).simplify()

        if isinstance(other, RealNumber):
            return other.__rmul__(self)

        return Product(coeff=1, terms=[self, other]).simplify()

    def __rmul__(self, other):
        return self.__mul__(other)
    
    def invert(self):
        return ExponentialNumber(
            coeff=RationalNumber(1) / self.coeff,
            base=self.base,
            exponent=self.exponent * -1
        ).simplify()