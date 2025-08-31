import unicodedata

CATEGORY_TABLE = {
    "Lu": "Uppercase letter",
    "Ll": "Lowercase letter",
    "Lt": "Titlecase letter",
    "Lm": "Modifier letter",
    "Lo": "Other letter",
    "Mn": "Nonspacing mark",
    "Mc": "Spacing mark",
    "Me": "Enclsing mark",
    "Nd": "Decimal number",
    "Nl": "Letter number",
    "No": "Other number",
    "Pc": "Connector punctuation",
    "Pd": "Dash punctuation",
    "Ps": "Open punctuation",
    "Pe": "Close punctuation",
    "Pi": "Initial punctuation",
    "Pf": "Final punctuation",
    "Po": "Other punctuation",
    "Sm": "Math symbol",
    "Sc": "Currency symbol",
    "Sk": "Modifier symbol",
    "So": "Other symbol",
    "Zs": "Space separator",
    "Zl": "Line separator",
    "Zp": "Paragraph separator",
    "Cc": "Control code",
    "Cf": "Format code",
    "Cs": "Surrogate code",
    "Co": "Private use",
    "Cn": "Unassigned"
}

DIRECTIONAL_TABLE = {
    "L": "Left to right",
    "R": "Right to left",
    "AL": "Arabic letter",
    "EN": "European number",
    "ES": "European separator",
    "ET": "European terminator",
    "AN": "Arabic number",
    "CS": "Common separator",
    "NSM": "Nonspacing mark",
    "BN": "Boundary neutral",
    "B": "Paragraph separator",
    "S": "Segment separator",
    "WS": "Whitespace",
    "ON": "Other neutral",
    "LRE": "Left to right embedding",
    "LRO": "Left to right override",
    "RLE": "Right to left embedding",
    "RLO": "Right to left override",
    "PDF": "Pop directional format",
    "LRI": "Left to right isolate",
    "RLI": "Right to left isolate",
    "FSI": "First strong isolate",
    "PDI": "Pop directional isolate"
}

DOUBLEWIDTH_TABLE = {
    "A": "Ambiguous",
    "F": "Full-width",
    "H": "Half-width",
    "N": "Neutral",
    "Na": "Narrow",
    "W": "Wide"
}

def output(c):
    print(c)
    print(f"{ord(c):04X} ({ord(c)})")
    try:
        print(unicodedata.name(c))
    except ValueError:
        pass
    category = unicodedata.category(c)
    bidirectional = unicodedata.bidirectional(c)
    width = unicodedata.east_asian_width(c)
    decompose = unicodedata.decomposition(c)
    decomposed = decompose.split()
    print(CATEGORY_TABLE[category])
    print(DIRECTIONAL_TABLE[bidirectional])
    print(DOUBLEWIDTH_TABLE[width])
    print(unicodedata.combining(c))
    print(" +  ".join(chr(int(d, 16)) for d in decomposed))


def main():
    c = input("Input character: ")
    print("NFC:  " + str(unicodedata.is_normalized("NFC", c)))
    print("NFD:  " + str(unicodedata.is_normalized("NFD", c)))
    print("NFKC: " + str(unicodedata.is_normalized("NFKC", c)))
    print("NFKD: " + str(unicodedata.is_normalized("NFKD", c)))
    name = "CONTROL CHARACTER"
    try:
        name = unicodedata.name(c)
        c = [c]
    except ValueError:
        pass
    except TypeError:
        c = list(c)
    for n in c:
        output(n)

if __name__ == "__main__":
    main()
