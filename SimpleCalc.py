print("#" * 50)
print("SIMPLE ACCUMULATING CALCULATOR")
print("#" * 50)
print("Enter numbers followed by operations (+, -, *, /)")
print("Type 'stop' to finish, or press Ctrl+C to exit")

result = 0.0

calc_history = []

def isValidFloat(num):
    try:
        float(num)
        return True
    except ValueError:
        return False


def requestAndValidateFloat():

    while True:
        num = input("\nEnter a number: ").strip()

        if num.lower() == "stop":
            return "stop"

        if isValidFloat(num):
            return float(num)

        print("Invalid input. Please enter a number.")


def requestAndValidateOperator():
    while True:
        op = input("\nEnter an operator (+, -, *, /, %, =): ").strip()

        if op.lower() == "stop":
            return "stop"

        if op in "+-*/%=":
            return op

        print("Invalid operator. Please enter a valid operator.")

first_input = True

try:
    while True:
        if first_input == True:
            num = requestAndValidateFloat()
            if num == "stop":
                break

            result = num

            calc_history.append(str(num))
        else:
            op = requestAndValidateOperator()
            if op == "stop" or op == "=":
                break

            num = requestAndValidateFloat()
            if num == "stop":
                break

            try:
                prev = result
                applied = True

                match op:
                    case "+":
                        result += num
                    case "-":
                        result -= num
                    case "*":
                        result *= num
                    case "%":
                        result %= num
                    case "/":
                        if num == 0:
                            print("Cannot divide by zero. Please try again.")
                            applied = False
                        else:
                            result /= num

                if applied:
                    print(f"{prev} {op} {num} = {result}")

                    calc_history.extend([op, str(num)])
            except Exception as e:  # noqa: BLE001
                print(f"Invalid calculation. {e}")
        first_input = False

except KeyboardInterrupt:
    print("\n\nExiting... ")

finally:
    print("#" * 50)
    print("FINAL CALCULATION SUMMARY")
    print("#" * 50)
    if calc_history:
        print(f"Full calculation: {' '.join(calc_history)}={result}")
    else:
        print("No calculations performed.")
    print("=" * 50)
