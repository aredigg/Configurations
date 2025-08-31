import unicodedata
for c in range(0x0300, 0x0400):
    ch = chr(c)
    name = unicodedata.category(ch)
    es = " "
    try:
        name = unicodedata.name(ch)
    except ValueError:
        pass
    if unicodedata.east_asian_width(ch) == "W":
        es = ""
    if unicodedata.category(ch) in {"Cc", "Cf"}:
        print(f"{c:04X}    {unicodedata.category(ch):2} {unicodedata.east_asian_width(ch):2} {unicodedata.bidirectional(ch):3} '{name}'")
    elif unicodedata.category(ch) in {"Mn", "Me"}:
        print(f"{c:04X} {chr(0x25CC)}{ch}{es} {unicodedata.category(ch):2} {unicodedata.east_asian_width(ch):2} {unicodedata.bidirectional(ch):3} '{name}'")
    elif unicodedata.category(ch) in {"Mc"}:
        print(f"{c:04X} {chr(0x0A95)}{ch}{es}{unicodedata.category(ch):2} {unicodedata.east_asian_width(ch):2} {unicodedata.bidirectional(ch):3} '{name}'")
    else:
        print(f"{c:04X} {ch}{es} {unicodedata.category(ch):2} {unicodedata.east_asian_width(ch):2} {unicodedata.bidirectional(ch):3} '{name}'")
