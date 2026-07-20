from typing import List, Tuple, Iterable
from number_temp import RealNumber

type RangeStr = Tuple[str, RealNumber, RealNumber, str]

class Marker:
    def __init__(self, closed: bool, is_start: bool, value: RealNumber):
        self.closed = closed
        self.is_start = is_start
        self.value = value
    def __str__(self):
        return f"{str(self.value) + '<' + ('=' if self.closed else '') if self.is_start else ''}x{'' if self.is_start else '<' + ('=' if self.closed else '') + str(self.value)}"
    def __eq__(self, other: 'Marker') -> bool:
        if not isinstance(other, Marker):
            return False
        return (self.closed == other.closed and self.is_start == other.is_start and self.value == other.value)

class Interval():
    def __init__(self, start: RealNumber, end: RealNumber, start_closed: bool = True, end_closed: bool = True):
        self.start = start
        self.end = end
        self.start_closed = start_closed
        self.end_closed = end_closed
    def __str__(self):
        if self.start == self.end and self.start_closed and self.end_closed:
            return f"x={self.start}"
        return f"{f'{self.start}<{'=' if self.start_closed else ''}' if self.start != RealNumber('-inf') else ''}\
x{f'<{'=' if self.end_closed else ''}{self.end}' if self.end != RealNumber('inf') else ''}"
    def __eq__(self, value: 'Interval') -> bool:
        if not isinstance(value, Interval):
            return False
        return (self.start == value.start and self.end == value.end and
                self.start_closed == value.start_closed and self.end_closed == value.end_closed)
    def __contains__(self, value: RealNumber) -> bool:
        if not isinstance(value, RealNumber):
            raise TypeError(
                f"타입 에러: 집합 포함 여부 검사(in)는 오직 RealNumber 타입만 가능합니다. "
                f"(받은 타입: {type(value).__name__})"
            )
        if self.start < value < self.end:
            return True
        if self.start_closed and value == self.start:
            return True
        if self.end_closed and value == self.end:
            return True
        return False

def create_interval_from_markers(marker1: Marker, marker2: Marker) -> Interval:
    if marker1.is_start and marker2.is_start:
        raise ValueError("두 마커 모두 시작점입니다.")
    if not marker1.is_start and not marker2.is_start:
        raise ValueError("두 마커 모두 끝점입니다.")
    if marker1.value > marker2.value == marker1.is_start:
        raise ValueError("시작점이 끝점보다 큽니다.")
    
    start = marker1 if marker1.is_start else marker2
    end = marker2 if marker1.is_start else marker1
    if start.value == end.value and (not start.closed or not end.closed):
        return None
    return Interval(
        start.value, end.value,
        start.closed,
        end.closed
    )
        

class RangeSet: 
    def __init__(self, *intervals: Interval):
        self.intervals: List[Interval] = list(intervals)

    def normalize(self) -> None:
        tmp: RangeSet = RangeSet()
        for interval in self.intervals:
            set_ = RangeSet(interval)
            tmp = union(tmp, set_)
        if tmp.intervals:
            if tmp.intervals[0].start == RealNumber('-inf'):
                tmp.intervals[0].start_closed = True
            if tmp.intervals[-1].end == RealNumber('inf'):
                tmp.intervals[-1].end_closed = True
        self.intervals = tmp.intervals
        
    def __str__(self):
        res = []
        for i in range(len(self.intervals)):
            interval = self.intervals[i]
            res.append(str(interval))
        if len(self.intervals) == 1 and self.intervals[0].start == RealNumber('-inf') and self.intervals[0].end == RealNumber('inf'):
            return "{x|x∈ℝ}"
        if len(self.intervals) == 0:
            return "∅"
        return "{x|" + " or ".join(res) + "}"

    def __eq__(self, value):
        if not isinstance(value, RangeSet):
            return False
        if len(self.intervals) != len(value.intervals):
            return False
        for i in range(len(self.intervals)):
            if self.intervals[i] != value.intervals[i]:
                return False
        return True

    def __contains__(self, value: RealNumber) -> bool:
        st = 0
        en = len(self.intervals) - 1
        while st <= en:
            mid = (st + en) // 2
            if value < self.intervals[mid].start:
                en = mid - 1
            elif value > self.intervals[mid].end:
                st = mid + 1
            else:
                return value in self.intervals[mid]
        return False
    
    def append(self, element: RealNumber) -> None:
        return union(self, create_range_set_from_iterable({element}))
        
    def is_subset_of(self, other: 'RangeSet') -> bool:
        return union(self, other) == other
    
    def is_superset_of(self, other: 'RangeSet') -> bool:
        return union(self, other) == self
    
    def __and__(self, other: 'RangeSet') -> 'RangeSet':
        return intersection(self, other)
    
    def __or__(self, other: 'RangeSet') -> 'RangeSet':
        return union(self, other)
    
    def __invert__(self) -> 'RangeSet':
        return complement(self)
    
    def __xor__(self, other: 'RangeSet') -> 'RangeSet':
        return exclusive(self, other)
    
    def __sub__(self, other: 'RangeSet') -> 'RangeSet':
        return subtract(self, other)
    
    def len(self) -> float:
        length = 0
        for interval in self.intervals:
            if interval.start == interval.end and interval.start_closed and interval.end_closed:
                length += 1
            else:
                return float('inf')
        return length

def intersection(*sets: RangeSet) -> RangeSet:
    opened = 0
    markers: List[Tuple[Marker, int]] = []
    cnt = 0
    for s in sets:
        for interval in s.intervals:
            marker1 = Marker(interval.start_closed, True, interval.start)
            markers.append((marker1, cnt))
            marker2 = Marker(interval.end_closed, False, interval.end)
            markers.append((marker2, cnt))
        cnt += 1

    full = [False for _ in range(cnt + 1)]
    markers.sort(key=lambda x: (x[0].value, x[0].is_start != x[0].closed, not x[0].is_start))
    result: List[Interval] = []
    starter: Marker = None
    for v in markers:
        marker, idx = v
        if marker.is_start:
            if not full[idx]:
                opened += 1
                full[idx] = True
            if opened == cnt:
                starter = marker
        else:
            if opened == cnt:
                if starter is not None:
                    intv = create_interval_from_markers(starter, marker)
                    if intv is not None:
                        result.append(intv)
                    starter = None
                else:
                    raise ValueError("범위의 시작점이 없습니다.")
            if full[idx]:
                opened -= 1
                full[idx] = False
    return RangeSet(*result)

def union(*sets: RangeSet) -> RangeSet:
    opened = 0
    markers: List[Marker] = []
    for s in sets:
        for marker in s.intervals:
            marker1 = Marker(marker.start_closed, True, marker.start)
            markers.append(marker1)
            marker2 = Marker(marker.end_closed, False, marker.end)
            markers.append(marker2)
    markers.sort(key=lambda x: (x.value, x.is_start != x.closed, not x.is_start))
    result: List[Interval] = []
    starter: Marker = None
    for marker in markers:
        if marker.is_start:
            if opened == 0:
                starter = marker
            opened += 1
        else:
            opened -= 1
            if opened == 0:
                if starter is not None:
                    intv = create_interval_from_markers(starter, marker)
                    if intv is not None:
                        result.append(intv)
                    starter = None
                else:
                    raise ValueError("범위의 시작점이 없습니다.")
    return RangeSet(*result)

def complement(set_: RangeSet) -> RangeSet:
    markers: List[Marker] = []
    for marker in set_.intervals:
        marker1 = Marker(not marker.start_closed, False, marker.start)
        markers.append(marker1)
        marker2 = Marker(not marker.end_closed, True, marker.end)
        markers.append(marker2)
    if len(markers):
        if markers[0].value == RealNumber('-inf'):
            markers.remove(markers[0])
        else:
            markers.insert(0, Marker(True, True, RealNumber('-inf')))
        if markers[-1].value == RealNumber('inf'):
            markers.pop()
        else:
            markers.append(Marker(True, False, RealNumber('inf')))
    result: List[Interval] = []
    for i in range(len(markers) // 2):
        result.append(create_interval_from_markers(markers[i * 2], markers[i * 2 + 1]))
    return RangeSet(*result)

def exclusive(set1: RangeSet, set2: RangeSet) -> RangeSet:
    return union(intersection(set1, complement(set2)), intersection(complement(set1), set2))

def subtract(set1: RangeSet, set2: RangeSet) -> RangeSet:
    return intersection(set1, complement(set2))

def create_range_set_from_range(*args: RangeStr) -> RangeSet:
    sets = []
    for v in args:
        if not (v[0] in ('(', '[') and v[3] in (')', ']')):
            raise ValueError(f"{v}는 올바른 범위 문자열이 아닙니다.")
        st, en = v[1], v[2]
        st_closed, en_closed = st == RealNumber('-inf') or v[0] == '[', en == RealNumber('inf') or v[3] == ']'
        try:
            st = RealNumber(st)
            en = RealNumber(en)
        except:
            raise ValueError(f"{st} 또는 {en}는 숫자가 아닙니다.")
        if st > en:
            raise ValueError("범위의 시작값이 끝값보다 작아야 합니다.")
        sets.append(RangeSet(Interval(st, en, st_closed, en_closed)))
    if len(sets) == 1:
        return sets[0]
    union_set = union(*sets)
    return union_set

def create_range_set_from_iterable(items: Iterable[RealNumber]) -> RangeSet:
    sorted_items = sorted(items)
    intervals: List[Interval] = []
    for item in sorted_items:
        try:
            item = RealNumber(item)
        except:
            raise ValueError(f"{item}는 숫자가 아닙니다.")
        intervals.append(Interval(item, item, True, True))
    return RangeSet(*intervals)

def universe() -> RangeSet:
    return RangeSet(Interval(RealNumber('-inf'), RealNumber('inf'), True, True))

def empty() -> RangeSet:
    return RangeSet()


class IntensionalSet:
    def __init__(self, var_name: str, condition_node, interpreter):
        self.var_name = var_name            
        self.condition_node = condition_node
        from copy import deepcopy
        self.defining_env = deepcopy(interpreter.current_env)

    def contains(self, interpreter, value: 'RealNumber') -> bool:
        if not isinstance(value, RealNumber):
            raise TypeError(f"타입 에러: 집합 검사는 오직 숫자(RealNumber)만 가능합니다. (받은 타입: {type(value).__name__})")

        from interpreter import Environment
        isolated_env = Environment(parent=self.defining_env) 
        isolated_env.define(self.var_name, value)

        old_env = interpreter.current_env
        interpreter.current_env = isolated_env
        try:
            result = interpreter.visit(self.condition_node)
            if not isinstance(result, bool):
                raise TypeError(
                    f"타입 에러: 조건제시법 집합의 조건식 평가 결과는 불리언(bool)이어야 합니다. "
                    f"(받은 타입: {type(result).__name__})"
                )
            return result
        finally:
            interpreter.current_env = old_env


    def __contains__(self, value: 'RealNumber') -> bool:
        from interpreter import Interpreter
        interp = Interpreter._current_instance
        
        if interp is None:
            raise RuntimeError("조건제시법 집합은 인터프리터가 구동 중인 상태에서만 'in' 연산을 수행할 수 있습니다.")
            
        return self.contains(interp, value)

    def __str__(self):
        return f"{{ {self.var_name} | ... }}"