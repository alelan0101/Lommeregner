
print("#" * 50)
print("ADVANCED CALCULATOR")
print("#" * 50)
print("Enter a full calculation on one line, e.g. 2+3*12/3+1%2*4")
print("Operators: + - * / %  and parentheses ( )")
print("Type 'stop' or press Enter on an empty line to exit")

def tokenize(text: str) -> list[str]:
    tokens = []
    i = 0
    while i < len(text):
        char = text[i]
        if char.isspace():
            i += 1
        elif char.isdigit() or char == ".":
            start = i
            while i < len(text) and (text[i].isdigit() or text[i] == "."):
                i += 1
            number_text = text[start:i]
            try:
                tokens.append(float(number_text))
            except ValueError:
                raise ValueError(f"Invalid number: '{number_text}'")
        elif char in "+-*/%()":
            tokens.append(char)
            i += 1
        else:
            raise ValueError(f"Invalid character: '{char}'")
    return tokens

PRECEDENCE = {"+": 1, "-": 1, "*": 2, "/": 2, "%": 2, "neg": 3}

def apply_top_operator(values: list[float], ops: list[str]):
    op = ops.pop()

    if op == "neg":
        if not values:
            raise ValueError("Unexpected end of expression")
        values[-1] = -values[-1]
        return

    if len(values) < 2:
        raise ValueError("Unexpected end of expression")

    right = values.pop()
    left = values.pop()

    if op == "+":
        values.append(left + right)
    elif op == "-":
        values.append(left - right)
    elif op == "*":
        values.append(left * right)
    elif op == "/":
        if right == 0:
            raise ZeroDivisionError("Cannot divide by zero")
        values.append(left / right)
    else:
        if right == 0:
            raise ZeroDivisionError("Cannot take modulo by zero")
        values.append(left % right)


def calculate(expression):
    tokens = tokenize(expression)
    if not tokens:
        return None

    values: list[float] = []
    ops: list[str] = []
    prev = None

    for token in tokens:
        if isinstance(token, float):
            values.append(token)

        elif token == "(":
            ops.append(token)

        elif token == ")":
            while ops and ops[-1] != "(":
                apply_top_operator(values, ops)
            if not ops:
                raise ValueError("Missing opening parenthesis")
            ops.pop()

        else:
            after_operator = prev is None or prev == "(" or prev in ("+", "-", "*", "/", "%")
            if after_operator:
                if token == "-":
                    ops.append("neg")
                    prev = token
                    continue
                if token == "+":
                    prev = token
                    continue

            while ops and ops[-1] != "(" and PRECEDENCE[ops[-1]] >= PRECEDENCE[token]:
                apply_top_operator(values, ops)
            ops.append(token)

        prev = token

    while ops:
        if ops[-1] == "(":
            raise ValueError("Missing closing parenthesis")
        apply_top_operator(values, ops)

    if len(values) != 1:
        raise ValueError("Invalid expression")

    return values[0]

try:
    while True:
        expression = input("\nEnter a calculation: ").strip()

        if expression.lower() == "stop" or expression == "":
            break

        try:
            result = calculate(expression)
            if result is not None:
                print(f"{expression} = {result}")
        except ZeroDivisionError as e:
            print(f"Invalid calculation. {e}")
        except ValueError as e:
            print(f"Invalid expression. {e}")

except KeyboardInterrupt:
    print("\n\nExiting... ")

finally:
    print("#" * 50)
    print("GOODBYE")
    print("#" * 50)
