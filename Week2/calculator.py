from typing import Union


def compute(operator: str, num1: float, num2: float) -> Union[float, str]:
    """Compute a simple binary operation.

    Returns a float for successful operations or a string error message for invalid input.
    """
    op = operator.strip()

    if op == '+':
        return num1 + num2
    if op == '-':
        return num1 - num2
    if op == '*':
        return num1 * num2
    if op == '/':
        if num2 == 0:
            return "Error: Division by zero"
        return num1 / num2

    return "Invalid operator"


def _cli():
    operator = input("Enter operator (+, -, *, /): ").strip()
    try:
        num1 = float(input("Enter first number: "))
        num2 = float(input("Enter second number: "))
    except ValueError:
        print("Error: please enter valid numbers")
        return

    result = compute(operator, num1, num2)
    print(result)


if __name__ == "__main__":
    _cli()

