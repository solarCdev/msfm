# MSfM

> **Minimal Script for Mathematics**

MSfM은 **수학적 표현을 그대로 코드로 작성할 수 있도록 설계된 기호 연산 중심의 프로그래밍 언어**입니다.
부동소수점 오차를 최소화하기 위해 수식을 가능한 한 **기호(Symbolic Form)** 로 유지하며, 함수·수열·집합·명제 등을 수학 교과서의 표기법과 유사하게 표현할 수 있습니다.

---

# Features

* ✨ **기호 연산(Symbolic Computation)**

  * 실수를 기호 형태로 유지하여 계산
  * 자동 약분 및 간소화
  * 필요할 때만 근삿값 계산

* 📖 **수학 친화적 문법**

  * 함수
  * 수열
  * 집합
  * 정의역 제한
  * 명제 표현

* 📈 **내장 그래프 시각화**

  * 함수 그래프 출력
  * 다중 그래프 관리
  * 이미지 저장 지원

* 🧮 **고등학교 수학 특화**

  * 제곱근
  * 삼각함수
  * 지수/로그
  * 집합과 명제
  * 함수와 수열

---

# Hello, MathLang

```text
f(x) := x^2 + 2

for (x := -2, 2) {
    out f(x)
}
```

---

# Symbolic Number System

MSfM은 실수를 가능한 한 **기호적으로 유지**합니다.

```text
sqrt(12)
```

↓

```text
2sqrt(3)
```

또한,

```text
sin(PI / 6)
```

↓

```text
1 / 2
```

처럼 특수각은 자동으로 계산됩니다.

실수 근삿값은 그래프 출력이나 대소 비교 등 필요한 경우에만 생성됩니다.

---

# Function Definition

수학 교과서와 유사한 형태로 함수를 정의할 수 있습니다.

```text
f(x) := x^2 + 1
```

정의역 제한도 지원합니다.

```text
f(x) 단 (x in [-5, 5]) := x^2 + 2
```

---

# Sequence

수열은 정의역이 자연수인 특수한 함수로 취급됩니다.

```text
A[n] := 2 * n - 1

out A[10]
```

---

# Sets

MSfM은 다양한 집합 표기법을 지원합니다.

원소 나열

```text
{1, 2, 3}
```

구간

```text
[-1, 3)
```

조건 제시

```text
{x | x > 0}
```

---

# Assumptions

특정 조건을 가정한 상태에서 계산을 수행할 수 있습니다.

```text
assume (x > 0) {

    out sqrt(x^2)

} contradict {

    out "Contradiction"

}
```

필요한 결과만 전역 환경에 반영할 수도 있습니다.

```text
apply x
```

---

# Plotting

그래프 출력은 `plot` 키워드 하나로 수행됩니다.

함수 출력

```text
plot f [-PI, PI] "r--"
```

그래프 저장

```text
plot "save" "graph.png"
```

그래프 표시

```text
plot "show"
```

그래프 초기화

```text
plot "clear"
```

---

# Basic Syntax

출력

```text
out "Hello, World!"
```

입력

```text
get n
```

조건문

```text
if (n > 0) {
    out "positive"
}
elif (n == 0) {
    out "zero"
}
else {
    out "negative"
}
```

반복문

```text
for (i := 1, 10) {
    out i
}
```

---

# Operators

| Category   | Operators         |
| ---------- | ----------------- |
| Arithmetic | `+ - * / ^ %`     |
| Comparison | `== != < <= > >=` |
| Logical    | `and or not`      |
| Set        | `and or - ~ in`   |
| Definition | `:=`              |

---

# Design Philosophy

MSfM은 수학을 표현하기 위한 DSL입니다.
언어의 핵심 목표는 다음과 같습니다.

* 수학 교과서와 유사한 문법
* 기호 계산 중심의 연산
* 부동소수점 오차 최소화
* 교육 환경에서 직관적인 사용성
* 함수·수열·집합·명제의 자연스러운 표현

