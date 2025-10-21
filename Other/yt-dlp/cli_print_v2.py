import datetime
import re
import time
from shutil import get_terminal_size as size

LOCAL_VERSION = "2.02"


class ANSI:
    # Colors
    Black = "\033[30m"
    Red = "\033[31m"
    Green = "\033[32m"
    Yellow = "\033[33m"
    Blue = "\033[34m"
    Magenta = "\033[35m"
    Cyan = "\033[36m"
    Gray = "\033[37m"
    BrBlack = "\033[90m"
    BrRed = "\033[91m"
    BrGreen = "\033[92m"
    BrYellow = "\033[93m"
    BrBlue = "\033[94m"
    BrMagenta = "\033[95m"
    BrCyan = "\033[96m"
    White = "\033[97m"
    Default = "\033[39m"
    # Background colors
    BGBlack = "\033[40m"
    BGRed = "\033[41m"
    BGGreen = "\033[42m"
    BGYellow = "\033[43m"
    BGBlue = "\033[44m"
    BGMagenta = "\033[45m"
    BGCyan = "\033[46m"
    BGGray = "\033[47m"
    BGBrBlack = "\033[100m"
    BGBrRed = "\033[101m"
    BGBrGreen = "\033[102m"
    BGBrYellow = "\033[103m"
    BGBrBlue = "\033[104m"
    BGBrMagenta = "\033[105m"
    BGBrCyan = "\033[106m"
    BGWhite = "\033[107m"
    BGDefault = "\033[49m"
    # Font control
    Bold = "\033[1m"
    Dim = "\033[2m"
    ResetBold = ResetDim = "\033[22m"
    Italic = "\033[3m"
    ResetItalic = "\033[23m"
    Underline = "\033[4m"
    DoubleUnderline = "\033[21m"
    CurlyUnderline = "\033[4:3m"
    DottedUnderline = "\033[4:4m"
    DashedUnderline = "\033[4:5m"
    ResetUnderline = "\033[24m"
    Overline = "\033[53m"
    ResetOverline = "\033[55m"
    Blink = "\033[5m"
    ResetBlink = "\033[25m"
    Inverse = "\033[7m"
    ResetInverse = "\033[27m"
    Hidden = "\033[8m"
    ResetHidden = "\033[28m"
    Strike = "\033[9m"
    ResetStrike = "\033[29m"
    # Control codes
    Reset = "\033[0m"
    ClearLine = "\033[0m\033[2K"  # Reset + erase line
    ClearEOL = "\033[0m\033[0K"  # Reset + erase to end of line
    ClearBefore = "\033[0m\033[1K"  # Reset + erase to beginning of line
    ClearScreen = "\033[0m\033[2J"  # Reset + clear screen
    ClearBelow = "\033[0m\033[0J"  # Reset + clear screen from cursor and down
    ClearAbove = "\033[0m\033[1J"  # Reset + clear screen from cursor and up
    Return = "\033[0m\033[0K\033[1F"  # Reset + erase to eol + return 1 line up
    Home = "\033[0m\033[H"  # Reset and home cursor (pos 0,0)
    Up = "\033[1A"  # Cursor up
    Down = "\033[1B"  # Cursor down
    Right = "\033[1C"  # Cursor right
    Left = "\033[1D"  # Cursor left
    Save = "\0337"  # Saves cursor position
    Restore = "\0338"  # Restores it
    CursorOff = "\033[?25l"  # Turns off cursor
    CursorOn = "\033[?25h"  # Turns on cursor
    CursorBlinkBlock = "\033[0 q"  # Blinking block
    CursorSteadyBlock = "\033[2 q"  # Steady block
    CursorBlinkUnderline = "\033[3 q"  # Blinking line
    CursorSteadyUnderline = "\033[4 q"  # Steady line
    CursorBlinkBar = "\033[5 q"  # Blinking bar
    CursorSteadyBar = "\033[6 q"  # Steady bar
    SaveScreen = "\033[?47h"  # Saves the screen
    RestoreScreen = "\033[?47h"  # Restores screen
    Bell = "\007"

    # Statics
    @staticmethod
    def color(hex: str) -> str:
        code = ""
        if len(hex) == 6:
            try:
                r = int(hex[0:2], 16)
                g = int(hex[2:4], 16)
                b = int(hex[4:6], 16)
                code = f"\033[38;2;{r};{g};{b}m"
            except ValueError:
                pass
        return code

    @staticmethod
    def bg_color(hex: str) -> str:
        code = ""
        if len(hex) == 6:
            try:
                r = int(hex[0:2], 16)
                g = int(hex[2:4], 16)
                b = int(hex[4:6], 16)
                code = f"\033[48;2;{r};{g};{b}m"
            except ValueError:
                pass
        return code

    @staticmethod
    def pos(x: int, y: int) -> str:
        return f"\033[{y};{x}H"

    @staticmethod
    def gray(pct: int, bg: bool = False) -> str:
        val = 0
        if 0 <= pct <= 100:
            val = int(pct * 24 / 100)
        if bg:
            return f"\033[48;5;{232 + val}m"
        return f"\033[38;5;{232 + val}m"

    @staticmethod
    def len(text: str) -> int:
        code = re.compile(r"\x1B\[[0-?]*[ -/]*[@-~]")
        clean = code.sub("", text)
        return len(clean)


class BxDraw:
    class Round:
        LT = "╭"
        RT = "╮"
        LB = "╰"
        RB = "╯"

    class Squared:
        LT = "┌"
        RT = "┐"
        LB = "└"
        RB = "┘"
        V = "│"
        H = "─"
        ML = "├"
        MR = "┤"
        MT = "┬"
        MB = "┴"
        MC = "┼"
        XT = "╵"
        XB = "╷"
        XL = "╴"
        XR = "╶"

    class Double:
        LT = "╒"
        RT = "╕"
        LB = "╘"
        RB = "╛"
        H = "═"
        ML = "╞"
        MR = "╡"
        MT = "╤"
        MB = "╧"
        MC = "╪"

    class Heavy:
        LT = "┍"
        RT = "┑"
        LB = "┕"
        RB = "┙"
        H = "━"
        ML = "┝"
        MR = "┥"
        MT = "┯"
        MB = "┷"
        MC = "┿"

    class Diagonal:
        L = "╱"
        R = "╲"


class CLIPrint:
    def __init__(self, slots: int = 1, headers: int = 2, logfile: str | None = None, debug: bool = False) -> None:
        self._w: int = size().columns - 2
        self._h: int = size().lines
        self._slots: int = slots
        self._headers: int = headers
        self._logfile: str | None = logfile
        self._debug: bool = debug
        self._lines: list[str | None] = []
        self._hlines: list[str | None] = [""] * self._headers
        self._slines: list[tuple[str, str, str, str] | None] = [("", "", "", "")] * self._slots
        self._mlines: list[list[str]] = []
        self._status: str = "CLI Print Ready"
        self._last_update: float = time.time()
        print(ANSI.CursorOff)

    def __del__(self) -> None:
        print(ANSI.CursorOn)

    def cls(self):
        print(ANSI.ClearScreen)
        self._update()

    def status_line(self, text: str) -> None:
        dt = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self._status = f"{ANSI.Blue} ► {dt}   {ANSI.gray(pct=0, bg=False)} {text:{self._w - 25}.{self._w - 25}}"
        self._print_status()
        self._update()

    def slot_print(self, content: tuple[str, str, str], index: int):
        dt = datetime.datetime.now().strftime("%H:%M")
        if index < len(self._slines):
            status, resolution, channel = content
            self._slines[index] = dt, status, resolution, channel
        self._update()

    def tree_print(self, text: str, index: int = 0, line: int = 0):
        while len(self._mlines) <= index:
            self._mlines.append([""])
        while len(self._mlines) > index + 1:
            self._mlines.pop()
        if line == 0:
            self._mlines[index] = ["  " * index + text]
        else:
            while len(self._mlines[index]) <= line:
                self._mlines[index].append("")
            self._mlines[index][line] = "  " * index + text
        self._update()

    def header_print(self, text, index, color=ANSI.Default):
        if index == 0:
            text += f" (CLP {LOCAL_VERSION})"
        if index >= self._headers:
            self.status_line(f"Incorrect header {index} > " + text)
        if index < len(self._hlines):
            self._hlines[index] = f"{color}{text}{ANSI.Reset}"
        self._update()

    def _update(self) -> None:
        if self._w != size().columns or self._h != size().lines:
            self._w: int = size().columns - 2
            self._h: int = size().lines
        elif (self._last_update + 5) > time.time():
            return
        buffer: list[str | None] = []
        self._redraw_headers(buffer)
        self._redraw_main_body(buffer)
        self._redraw_slots(buffer)
        self._lines = buffer
        print(ANSI.Home)
        for line in self._lines:
            if line is not None:
                print(line + ANSI.ClearEOL)
            else:
                print(ANSI.ClearEOL)
        print(ANSI.ClearBelow)
        self._print_status()
        self._last_update = time.time()

    def _print_status(self) -> None:
        diff = len(self._status) - ANSI.len(self._status)
        ln = (
            ANSI.pos(1, self._h - 2)
            + ANSI.gray(pct=75, bg=True)
            + ANSI.gray(pct=0, bg=False)
            + f" {self._status:<{self._w - 2}.{self._w - 2}} "
            + " " * diff
            + ANSI.ClearEOL
        )
        print(ln)

    def _hrline(self, top: bool) -> str:
        if top:
            return BxDraw.Round.LT + BxDraw.Squared.H * (self._w - 2) + BxDraw.Round.RT
        return BxDraw.Round.LB + BxDraw.Squared.H * (self._w - 2) + BxDraw.Round.RB

    def _hsline(self, top: bool) -> str:
        if top:
            return BxDraw.Squared.LT + BxDraw.Squared.H * (self._w - 2) + BxDraw.Squared.RT
        return BxDraw.Squared.LB + BxDraw.Squared.H * (self._w - 2) + BxDraw.Squared.RB

    def _hmline(self) -> str:
        return BxDraw.Squared.ML + BxDraw.Squared.H * (self._w - 2) + BxDraw.Squared.MR

    def _hline(self, text: str, centered: bool = False) -> str:
        ln = BxDraw.Squared.V
        diff = len(text) - ANSI.len(text)
        if centered:
            ln += f" {text:^{self._w - 4}.{self._w - 4}} " + " " * diff
        else:
            ln += f" {text:<{self._w - 4}.{self._w - 4}} " + " " * diff
        ln += BxDraw.Squared.V
        return ln

    def _redraw_headers(self, buffer: list[str | None]) -> None:
        buffer.append(self._hrline(top=True))
        if self._hlines and self._hlines[0]:
            buffer.append(self._hline(self._hlines[0], True))
        if self._headers > 1:
            for text in self._hlines[1:]:
                buffer.append(self._hmline())
                if text:
                    buffer.append(self._hline(text))
                else:
                    buffer.append(self._hline(""))
        buffer.append(self._hrline(top=False))

    def _wnline(self, text: str) -> str:
        text = text[: self._w - 8]
        ext = self._w - 6 - ANSI.len(text)
        return BxDraw.Double.LT + BxDraw.Double.H * 2 + f" {text} " + BxDraw.Double.H * ext + BxDraw.Double.RT

    def _redraw_main_body(self, buffer: list[str | None]) -> None:
        if self._mlines and self._mlines[0] and self._mlines[0][0]:
            buffer.append(self._wnline(self._mlines[0][0]))
            for branch in self._mlines[1:]:
                for text in branch:
                    if text:
                        buffer.append(self._hline(text))
                    else:
                        buffer.append(self._hline(""))
            buffer.append(self._hsline(top=False))

    slot_header = [" Slot ", " Time ", " Status", " Resolution", "Channel"]

    def _sshline(self) -> str:
        ln = BxDraw.Squared.LT + BxDraw.Squared.H
        for h in CLIPrint.slot_header:
            h_len = ANSI.len(h)
            if h != CLIPrint.slot_header[4]:
                ln += BxDraw.Squared.H * h_len + BxDraw.Squared.H + BxDraw.Squared.MT
            else:
                length = self._w - len(ln) - 2
                ln += BxDraw.Squared.H * length + BxDraw.Squared.H
        ln += BxDraw.Squared.RT + "\n"
        ln2 = BxDraw.Squared.V + " "
        for h in CLIPrint.slot_header:
            h_len = ANSI.len(h)
            if h != CLIPrint.slot_header[4]:
                ln2 += f"{h:{h_len}.{h_len}} " + BxDraw.Squared.V
            else:
                length = self._w - len(ln2) - 2
                ln2 += f" {h:{length}.{length}}" + BxDraw.Squared.V
        return ln + ln2

    def _ssxline(self) -> str:
        ln = BxDraw.Squared.LB + BxDraw.Squared.H
        for h in CLIPrint.slot_header:
            h_len = ANSI.len(h)
            if h != CLIPrint.slot_header[4]:
                ln += BxDraw.Squared.H * h_len + BxDraw.Squared.H + BxDraw.Squared.MB
            else:
                length = self._w - len(ln) - 2
                ln += BxDraw.Squared.H * length + BxDraw.Squared.H
        ln += BxDraw.Squared.RB
        return ln

    def _ssline(self, content: list[str]) -> str:
        ln = BxDraw.Squared.ML + BxDraw.Squared.H
        for h in CLIPrint.slot_header:
            h_len = len(h)
            if h != CLIPrint.slot_header[4]:
                ln += BxDraw.Squared.H * h_len + BxDraw.Squared.H + BxDraw.Squared.MC
            else:
                length = self._w - len(ln) - 2
                ln += BxDraw.Squared.H * length + BxDraw.Squared.H
        ln += BxDraw.Squared.MR + "\n"
        ln2 = BxDraw.Squared.V + " "
        for h, hc in zip(CLIPrint.slot_header, content):
            h_len = len(h)
            if h == CLIPrint.slot_header[2]:
                ln2 += f"{hc} " + BxDraw.Squared.V
            elif h != CLIPrint.slot_header[4]:
                diff = len(hc) - ANSI.len(hc)
                ln2 += f"{hc:{h_len}.{h_len}} " + " " * diff + BxDraw.Squared.V
            else:
                diff = len(hc) - ANSI.len(hc)
                length = self._w - ANSI.len(ln2) - 2
                ln2 += f" {hc:{length}.{length}}" + " " * diff + BxDraw.Squared.V
        return ln + ln2

    def _redraw_slots(self, buffer: list[str | None]) -> None:
        if self._slines:
            buffer.append(self._sshline())
            for i, slot in enumerate(self._slines, start=1):
                if slot:
                    time, status, res, channel = slot
                    slot_content = [
                        f" {str(i):>5.5} ",
                        f" {time} ",
                        f"   {status}   ",
                        f" {res:<9.9}",
                        f"{channel}",
                    ]
                    buffer.append(self._ssline(slot_content))
            buffer.append(self._ssxline())
