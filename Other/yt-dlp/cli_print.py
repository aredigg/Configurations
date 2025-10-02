import datetime


class CLIPrint:
    RED = "\033[31m"
    GREEN = "\033[32m"
    BLUE = "\033[34m"
    PURPLE = "\033[35m"
    TEAL = "\033[36m"
    GRAY = "\033[37m"
    WHITE = "\033[38m"
    DEFAULT = "\033[39m"
    DIM_GRAY = "\033[38;5;8m"
    RESET = "\033[0m"
    CLEAR_LINE = "\033[0K"
    RETURN = "\033[0m\033[0K\033[1F"

    def __init__(self, slots=1, headers=2, logfile=None, debug=False):
        self._slots = slots
        self._headers = headers
        self._debugging = debug
        self._logfile = logfile
        self._line_index = 0

    def cls(self):
        print("\033[2J")

    def cursor_off(self):
        print("\033[?25l")

    def cursor_on(self):
        print("\033[?25h")

    def pass_cursor(self):
        if self._slots:
            print(f"{self.line(self._headers + 4 + self._slots)} | {CLIPrint.CLEAR_LINE}")
        else:
            print(f"{self.line(self._headers + 1)} | {CLIPrint.CLEAR_LINE}")

    def status_line(self, text):
        self._hprint()
        for _ in range(5):
            print(f"{CLIPrint.CLEAR_LINE}")
        self._hprint()
        dt = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"{CLIPrint.TEAL} > {dt} {CLIPrint.DEFAULT}{text}{CLIPrint.RETURN}")
        self.log("STATUS: " + f"{text}")

    def slot_print(self, text, index):
        dt = datetime.datetime.now().strftime("%H:%M")
        print(f"{self.line(self._headers + 1 + index)}Slot {index + 1}: {dt} {text}{CLIPrint.RETURN}")
        self._hprint()
        self.log("SLOT" + str(index + 1) + f": {dt} {text}")

    def tree_print(self, text, index=None, line=0):
        print_line = self._headers + 2 + line
        indent = ""
        if index:
            print_line += index
            indent = "  " * index
            self._line_index = index
        else:
            print_line += self._line_index
            indent = "  " * self._line_index
        for n in range(10):
            print(f"{self.line(print_line + n + 1)}{CLIPrint.CLEAR_LINE}")
        print(f"{self.line(print_line)}{indent}{text}{CLIPrint.RETURN}")
        # self.log("TREE:" + f"{indent}{text}")

    def header_print(self, text, index, color=DEFAULT):
        if index > self._headers:
            self.status_line(text)
        else:
            print(f"{self.line(index)}{color}{text}{CLIPrint.RETURN}")
            self._hprint()

    def debug_print(self, text):
        if not self._debugging:
            return
        if self._slots:
            print(f"{self.line(self._headers + 4 + self._slots)}")
        else:
            print(f"{self.line(self._headers + 4 + self._line_index)}")
        if isinstance(text, list):
            for line in text:
                print(f"{CLIPrint.DIM_GRAY}{line}{CLIPrint.CLEAR_LINE}")
        else:
            print(f"{CLIPrint.DIM_GRAY}{text}{CLIPrint.CLEAR_LINE}")
        # blank lines under
        for _ in range(5):
            print(f"{CLIPrint.CLEAR_LINE}")
        print(f"{CLIPrint.DEFAULT}")
        self._hprint()
        if isinstance(text, list):
            for line in text:
                self.log("DEBUG: " + f"{line}")
        else:
            self.log("DEBUG: " + f"{text}")

    def _hprint(self):
        if self._slots:
            print(f"{self.line(self._headers + 2 + self._slots)}")
        else:
            print(f"{self.line(self._headers + 4 + self._line_index)}")

    def increase(self, index=1):
        self._line_index += index

    def decrease(self, index=1):
        self._line_index -= index

    def line(self, n):
        return f"\033[{n};1H"

    def pos(self, x, y):
        return f"\033[{y};{x}H"

    def log(self, output):
        if self._logfile:
            dt = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            with open(self._logfile, "a") as log:
                log.write(dt + ": " + output + "\n")
