import unicodedata
from datetime import datetime, timezone, timedelta
from pathlib import Path
from urllib.error import URLError
from urllib.request import HTTPError, Request, urlopen

UNICODE_URL = "https://www.unicode.org/Public/UCD/latest/ucd/"
UNICODE_BLOCKS_TXT = "Blocks.txt"
UNICODE_SCRIPTS_TXT = "Scripts.txt"

SCRIPT_BASECHAR = {
    "Myanmar":  0x1000,
    "Gujarati": 0x0A95
}

SELECTED_CODEPLANE = 16
CHAR_COLUMNS = 32
CHAR_REPLACEMENT = {
    "Cc": f" {chr(0xFFFD)} ",
    "Cf": f" {chr(0xFFFD)} ",
    "Cs": f" {chr(0xFFFD)} ",
    "Zs": f" {chr(0xFFFD)} ",
    "Zl": f" {chr(0xFFFD)} ",
    "Zp": f" {chr(0xFFFD)} "
}

def download_from_unicode(blocks_path: Path, txt_file: str):
    r = False
    request = Request(UNICODE_URL+txt_file)
    try:
        with urlopen(request) as response:
            blocks_path.write_bytes(response.read())
            r = True
    except HTTPError as e:
        print(f"Error {e.code} {e.reason}")
    except URLError as e:
        print(f"Error {e.reason}")
    return r

def check_file(txt_file: str) -> str:
    path = Path(txt_file)
    if not path.exists():
        if not download_from_unicode(path, txt_file):
            print(f"Could not download {txt_file}")
            return ""
    else:
        modify_time = datetime.now(timezone.utc)-datetime.fromtimestamp(path.stat().st_mtime, timezone.utc)
        if modify_time > timedelta(days=180):
            download_from_unicode(path, txt_file)
    return path.read_text() or ""

def parse_blocks():
    blocks_table = []
    blocks_text = check_file(UNICODE_BLOCKS_TXT)
    for line in blocks_text.splitlines():
        if not line or line.startswith("#"):
            continue
        try:
            ranges, block_name = line.split(";", 1)
            begin, end = ranges.split("..", 1)
            block_name = block_name.strip()
            begin = int(begin, 16)
            end = int(end, 16)
            blocks_table.append((begin, end, block_name))
        except ValueError:
            continue
    return blocks_table

def parse_scripts():
    scripts_table = []
    scripts_text = check_file(UNICODE_SCRIPTS_TXT)
    for line in scripts_text.splitlines():
        if not line or line.startswith("#"):
            continue
        try:
            values = line.split("#", 1)[0].strip()
            if not values:
                continue
            ranges, script_name = values.split(";", 1)
            ranges = ranges.strip()
            script_name = script_name.strip()
            begin, end = ranges.split("..", 1)
            begin = int(begin, 16)
            end = int(end, 16)
            scripts_table.append((begin, end, script_name))
        except ValueError:
            continue
    return scripts_table

def get_script(c, scripts):
    for b, e, n in scripts:
        if b <= c <= e:
            return n
    return None

def get_unicode_char(c):
    if unicodedata.category(c) in CHAR_REPLACEMENT:
        return CHAR_REPLACEMENT[unicodedata.category(c)]
    spacer = 1
    if unicodedata.east_asian_width(c) in {"F", "W"}:
        spacer -= 1
    if unicodedata.category(c) in {"Mn", "Me"}:
        spacer += 1
    if unicodedata.category(c) in {"Mc"}:
        return f" {chr(0x25CC)}{c}"+" "*spacer
    return f" {c}"+" "*spacer

def main():
    blocks = parse_blocks()
    scripts = parse_scripts()
    # print(get_script(0x1083, scripts))
    # print(f" {chr(0x1000)} !")
    # print(f" {chr(0x1000)}{chr(0x1083)}!")
    print("─"*(CHAR_COLUMNS*5+10))
    for b, e, d in blocks:
        if (b >> 16) != SELECTED_CODEPLANE:
            continue
        s = "8" if b > 0x10000 else "4"
        header = f"{b:0{s}X}–{e:0{s}X} {d} "
        print(header + "│\n" + "─"*len(header) + "╯")
        print(f"{" ":{s}} │" + "".join(f"  {x:02X} " for x in list(range(CHAR_COLUMNS))))
        print(f"{"─"*(int(s))}─┼" + "─"*(CHAR_COLUMNS*5))
        for c in range(b, e+1):
            if c % CHAR_COLUMNS == 0:
                if c > b:
                    print()
                print(f"{c:0{s}X} │", end="")
            elif c == b:
                print(f"{b-b%CHAR_COLUMNS:0{s}X} │", end="")
                print(" "*(b%CHAR_COLUMNS*5), end="")
#                pad = 10 if b > 0x10000 else 6
#                print(" "*(b%CHAR_COLUMNS*5+pad), end="")
            print(f" {get_unicode_char(chr(c))} ", end="")
        print("\n" + "─"*(CHAR_COLUMNS*5+10))

if __name__ == "__main__":
    main()
