# type: ignore[reportCallIssue]
"""

Denne version tager imod en HEL regnestykke-linje ad gangen, fx:  2+3*12/3+1%2*4
og respekterer de matematiske regler: gange/dividere før plus/minus,
og parenteser altid først.

Vi bruger en TO-STACKS-algoritme:

  - en VÆRDI-stak ("values"):  indeholder tal (og færdige mellemresultater)
  - en OPERATOR-stak ("ops"):  indeholder operatorer og "(", som venter på at blive brugt

Mentalt billede: En stak er som en stabel tallerkener - man lægger kun på øverst (push)
og tager kun fra øverst (pop). Operator-stakken er programmérets "hukommelse for,
hvor vi kom fra".

Hurtigt eksempel på "2+3*4":
  1. 2  -> på værdi-stakken              values: [2]        ops: []
  2. +  -> stakken er tom, "+" venter    values: [2]        ops: [+]
  3. 3  -> på værdi-stakken              values: [2, 3]     ops: [+]
  4. *  -> "*" binder STÆRKERE end "+" (prio 2 > 1), så "+" må IKKE udføres endnu.
           "*" lægges øverst og venter   values: [2, 3]     ops: [+, *]
  5. 4  -> på værdi-stakken              values: [2, 3, 4]  ops: [+, *]
  6. Slut: vi tømmer operator-stakken baglæns:
           3*4=12  ->  values: [2, 12]   derefter 2+12=14  ->  values: [14]
  Svar: 14. Det er præcis sådan, prik- før komma-reglen opstår her.
"""

print("#" * 50)
print("ADVANCED CALCULATOR")
print("#" * 50)
print("Enter a full calculation on one line, e.g. 2+3*12/3+1%2*4")
print("Operators: + - * / %  and parentheses ( )")
print("Type 'stop' or press Enter on an empty line to exit")


# ======================================================================
# TRIN 1: TOKENIZER - omsæt tekststrengen til en liste af "tokens"
# ======================================================================
# Tokenize betyder: opdel teksten i de mindste meningsbærende bidder.
# Fx bliver strengen "12+3.5*2" til listen [12.0, "+", 3.5, "*", 2.0].
# Det gør resten af programmet meget lettere: vi behandler ÉN token ad gangen.
def tokenize(text):
    tokens = []       # den liste vi fylder op og returnerer til sidst
    i = 0             # vores "læseposition" i strengen (0 = første tegn)
    while i < len(text):
        char = text[i]  # peg på det aktuelle tegn

        if char.isspace():
            # Mellemrum skal ikke bruges til noget - bare hop over dem.
            i += 1
        elif char.isdigit() or char == ".":
            # TAL: vi skal læse HELE tallet, ikke kun ét tegn.
            # Derfor kører en indre løkke videre, så længe der stadig er
            # cifre eller punktum. Fx læser "3.14" som ÉN token.
            start = i
            while i < len(text) and (text[i].isdigit() or text[i] == "."):
                i += 1
            number_text = text[start:i]   # klip tallet ud af strengen
            try:
                tokens.append(float(number_text))  # lav tekst om til decimaltal
            except ValueError:
                # fx "3.1.4" kan ikke være et tal -> forklar fejlen til brugeren
                raise ValueError(f"Invalid number: '{number_text}'")
        elif char in "+-*/%()":
            # Operatoren/parentesen er kun ét tegn: gem den og gå videre.
            tokens.append(char)
            i += 1
        else:
            # Et tegn vi ikke kender (fx et bogstav) -> afvis med en pænt besked.
            raise ValueError(f"Invalid character: '{char}'")

    return tokens


# ======================================================================
# PRIORITET-Regler: hvor stærkt binder hver operator?
# ======================================================================
# Højere tal = strammere binding = udføres FØRST.
# Det er programmérets måde at kende "prik før komma"-reglen på:
#   * / % har prio 2, + - har prio 1 -> derfor udføres * / % før + -
# "neg" er unaert minus, altså et minus der BETYDER "gør negativt"
# (fx i "-3" eller "-(2+1)"). Det binder allermest strakt.
PRECEDENCE = {"+": 1, "-": 1, "*": 2, "/": 2, "%": 2, "neg": 3}


# ======================================================================
# TRIN 2: Udfør ÉN OPERATOR fra toppen af operator-stakken
# ======================================================================
def apply_top_operator(values, ops):
    """Tag den øverste operator af `ops` og udfør den på tallene i `values`.

    Eksempel: values=[2, 3] og ops=[+]  ->  efter kaldet: values=[5]
    Bemærk rækkefølgen: vi tager FØRST højre-tallet, DEREFTER venstre-tallet.
    Det er vigtigt for - og /, fordi 5-3 IKKE er det samme som 3-5.
    """
    op = ops.pop()  # .pop() tager OG fjerner det øverste element af stakken

    if op == "neg":
        # Unaert minus: der skal kun ÉT tal til.
        # values[-1] er det øverste element - vi negerer det i stedet for
        # at poppe og skubbe tilbage (samme resultat, kortere kode).
        if not values:
            raise ValueError("Unexpected end of expression")
        values[-1] = -values[-1]
        return

    # Alle andre operatorer skal bruge to tal (en venstre og en højre side).
    if len(values) < 2:
        raise ValueError("Unexpected end of expression")

    right = values.pop()  # sidst påfyldte tal = højre side
    left = values.pop()   # tallet før igen = venstre side

    if op == "+":
        values.append(left + right)
    elif op == "-":
        values.append(left - right)
    elif op == "*":
        values.append(left * right)
    elif op == "/":
        if right == 0:
            # Vi smider en "exception" (fejl), som hovedprogrammet fanger og viser pænt.
            raise ZeroDivisionError("Cannot divide by zero")
        values.append(left / right)
    else:  # % (modulo: resten efter division, fx 7 % 3 = 1)
        if right == 0:
            raise ZeroDivisionError("Cannot take modulo by zero")
        values.append(left % right)


# ======================================================================
# TRIN 3: HOVEDALGORITMEN - gennemløb tokens og styr de to stakke
# ======================================================================
def calculate(expression):
    tokens = tokenize(expression)  # trin 1: tekst -> token-liste
    if not tokens:
        return None  # tom input -> intet at regne på

    values = []  # værdi-stakken: tal og mellemresultater
    ops = []     # operator-stakken: operatorer og "(" der venter
    prev = None  # den FOREGÅENDE token - vi bruger den til at spotte unaert +/-


    for token in tokens:
        if isinstance(token, float):
            # Tilfælde A: et TAL. Tal skal bare huskes - læg det på værdi-stakken.
            values.append(token)

        elif token == "(":
            # Tilfælde B: en parentes starter.
            # "(" lægges på operator-stakken og virker som en "væg":
            # ingenting uden for parentesen må udføres, før vi rammer "væggen" igen.
            ops.append(token)

        elif token == ")":
            # Tilfælde C: en parentes slutter.
            # Udfør ALLE ventende operatorer indtil vi rammer "(".
            # Deraf kommer parentes-først-reglen: alt indeni er færdigregnet nu.
            while ops and ops[-1] != "(":
                apply_top_operator(values, ops)
            if not ops:
                # Vi fandt aldrig en "(" -> brugeren har skrevet for mange ")".
                raise ValueError("Missing opening parenthesis")
            ops.pop()  # fjern selve "(" fra stakken - den er nu "brugt op"

        else:  # Tilfælde D: en operator (+ - * / %)
            # UNAER TJEK: er +/- tænkt som fortegn og ikke som regneoperator
            # Det er tilfældet, hvis vi står:
            #   - først i udtrykket "-3"
            #   - lige efter "(" i "(-3)"
            #   - lige efter en anden operator fx, "2*-3"
            after_operator = prev is None or prev == "(" or prev in ("+", "-", "*", "/", "%")
            if after_operator:
                if token == "-":
                    ops.append("neg")  # "neg" er special-operatoren "gør det næste tal negativt"
                    prev = token
                    continue  # hop videre til næste token
                if token == "+":
                    # Unaert plus (fx "+3") ændrer ikke værdien - vi kan bare ignorere det.
                    prev = token
                    continue

            # NØGLETRINET:
            # Før vi lægger vores egen operator på stakken, skal alle operatorer,
            # der binder mindst lige så strakt, udføres først.
            # >= er afgørende: ved lige prio (fx "2+3+4") regner vi fra VENSTRE.
            # Er den nye operator STÆRKERE (fx "*" efter "+"), venter "+" stadig.
            while ops and ops[-1] != "(" and PRECEDENCE[ops[-1]] >= PRECEDENCE[token]:
                apply_top_operator(values, ops)
            ops.append(token)

        prev = token  # husk denne token til næste gennemløb (unaer-tjekket)

    # Der er ikke flere tokens: udfør alt, der stadig venter på operator-stakken.
    while ops:
        if ops[-1] == "(":
            # Der findes stadig en "(" uden matchende ")" -> brugeren glemte at lukke.
            raise ValueError("Missing closing parenthesis")
        apply_top_operator(values, ops)

    # Når alt er gået op, skal der ligge præcis ÉT tal tilbage: svaret.
    # Er der flere (fx input "2 3"), var udtrykket ikke gyldigt.
    if len(values) != 1:
        raise ValueError("Invalid expression")

    return values[0]


# ======================================================================
# HOPVEDPROGRAMMET: input-løkke
# ======================================================================
try:
    while True:
        # .strip() fjerner mellemrum i kanterne, så "  2+3  " også virker.
        expression = input("\nEnter a calculation: ").strip()

        # 'stop' eller en tom linje afslutter programmet.
        if expression.lower() == "stop" or expression == "":
            break

        try:
            result = calculate(expression)
            if result is not None:
                print(f"{expression} = {result}")
        except ZeroDivisionError as e:
            # En regne-fejl (fx 5/0) er IKKE en grund til at crashe:
            # vis beskeden og lad brugeren prøve igen.
            print(f"Invalid calculation. {e}")
        except ValueError as e:
            # En input-fejl (fx ugyldigt tegn eller parenteser, der ikke passer).
            print(f"Invalid expression. {e}")

except KeyboardInterrupt:
    # Ctrl+C: afslut pænt i stedet for at vise en rød traceback.
    print("\n\nExiting... ")

# `finally` kører altid, uanset hvordan programmet blev afsluttet.
finally:
    print("#" * 50)
    print("GOODBYE")
    print("#" * 50)
