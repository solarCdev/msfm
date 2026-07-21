# MSFM
## Minimal Script for Math

> A minimal scripting language designed for expressing mathematical ideas naturally.

MSFM(Minimal Script for Math)은 수학적 표현과 탐구를 위해 설계된 프로그래밍 언어입니다.

일반적인 소프트웨어 개발보다 함수, 수열, 집합, 그래프 등
수학적 객체를 코드로 표현하고 탐구하는 것을 목표로 합니다.

---

## Features

- Mathematical function definition
- Sequence handling
- Set operations
- Mathematical expressions
- Function visualization
- Built-in mathematical functions
- Simple procedural programming

---

# Philosophy

기존 프로그래밍 언어에서는 수학 개념을 표현하기 위해
복잡한 자료구조와 라이브러리가 필요합니다.

MSFM은 수학적 표현을 직접 코드로 나타내는 것을 목표로 합니다.

Example:

Mathematics:

```
f(x) = x^2 + 2x + 1
```

MSFM:

```msfm
f(x) := x^2 + 2*x + 1
```

---

# Syntax

## Output

```msfm
out "Hello MSFM"
```

---

## Variables

변수 대입은 `:=` 연산자를 사용합니다.

```msfm
a := 10
b := 3.14
```

`=`는 수학적 등호 및 조건 비교에 사용됩니다.

---

# Functions

## Function Definition

```msfm
f(x) := x^2 + 1
```

정의역을 제한할 수 있습니다.

```msfm
f(x in {1,2,3}) := x^2
```

정의역을 지정하지 않으면 기본적으로 실수 전체를 사용합니다.

---

# Sets

집합은 `{}`를 사용합니다.

```msfm
A := {1,2,3}
```

## Set Operations

| Operator | Meaning |
|---|---|
| `\|` | Union |
| `&` | Intersection |
| `-` | Difference |
| `not` | Complement |

Example:

```msfm
A := {1,2,3}
B := {3,4,5}

C := A | B
```

---

# Sequences

MSFM은 수열을 직접 표현할 수 있습니다.

## Sequence Literal

```msfm
a := seq[1,4,7,2,60]
```

## Function-style Sequence

```msfm
a(n in N) := n^2
```

---

## Sequence Operations

Add element:

```msfm
a + 10
```

Concatenate:

```msfm
a + b
```

Remove element:

```msfm
a - 3
```

Length:

```msfm
len(a)
```

---

# Control Flow

## if

```msfm
if (x > 0) {

}
elif (x = 0) {

}
else {

}
```

---

## for

```msfm
for (i=1,10) {

}
```

---

## while

```msfm
while (condition) {

}
```

---

# Built-in Mathematical Functions

| Function | Description |
|---|---|
| `sin(x)` | Sine |
| `cos(x)` | Cosine |
| `tan(x)` | Tangent |
| `log(x)` | Natural logarithm |
| `abs(x)` | Absolute value |

Example:

```msfm
f(x) := abs(x)
```

Trigonometric functions use radians.

```msfm
sin(PI/2)
```

---

# Plotting

MSFM supports mathematical visualization.

## Add Function Plot

```msfm
plot "add" f (-5,5) "b-"
```

## Add Sequence Plot

```msfm
plot "add" a [1,5] "ro"
```

## Show Graph

```msfm
plot "show"
```

## Manage Graph

```msfm
plot "remove"

plot "clear"
```

---

# Example

## Taylor Approximation of sin(x)

```msfm
out "Taylor Approximation"

f(x) := sin(x)

approx(x) := x - x^3/6 + x^5/120

error(x) := abs(f(x)-approx(x))

plot "add" f (-PI,PI) "b-"
plot "add" approx (-PI,PI) "r-"

plot "show"
```

This example uses:

- Function definition
- Mathematical functions
- Polynomial approximation
- Absolute error
- Visualization

---

# Implementation

MSFM interpreter is implemented in Python.

Architecture:

```
Source Code
     |
     v
Lexer
     |
     v
Parser
     |
     v
AST
     |
     v
Interpreter
```

---

# Future Plans

- More mathematical operators
- Calculus support
  - Limits
  - Differentiation
  - Integration
- Improved mathematical notation
- Better error messages
- Extended visualization

---

# Why MSFM?

Most programming languages are designed for computation.

MSFM is designed for mathematical thinking.

The goal is to make mathematical concepts executable
and allow users to explore equations, functions, and mathematical models through code.

---

## License

MIT License