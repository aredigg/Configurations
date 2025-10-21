import re

LOCAL_VERSION = "1.01"


class Logger:
    def __init__(self, max_len=100, clp=None):
        self._messages = []
        self._error_messages = []
        self._max_len = max_len
        self.LOCAL_VERSION = LOCAL_VERSION
        self._cli_print = clp

    def _append(self, msg):
        if self._cli_print:
            self._cli_print.debug_line(msg)
        if len(self._messages) > self._max_len:
            self._messages.pop(0)
        self._messages.append(msg)

    def _append_error(self, msg):
        if len(self._error_messages) > self._max_len:
            self._error_messages.pop(0)
        self._error_messages.append(msg)

    def debug(self, msg):
        self._append(msg)

    def info(self, msg):
        self._append(msg)

    def warning(self, msg):
        self._append(msg)

    def error(self, msg):
        msg = self._remove_ansi(msg)
        error_msg = msg
        extractor = None
        id = None
        parts_msg: list[str] = msg.split()
        if len(parts_msg) >= 2:
            if parts_msg[1].startswith("[") and parts_msg[1].endswith("]"):
                extractor = parts_msg[1][1:-1]
                id = parts_msg[2]
                error_msg = " ".join(parts_msg[1:])
                if id.endswith(":"):
                    error_msg = " ".join(parts_msg[3:])
                    id = id[:-1]
        self._append_error((extractor, id, error_msg))
        self._append(msg)

    def _remove_ansi(self, string):
        code = re.compile(r"\x1B\[[0-?]*[ -/]*[@-~]")
        return code.sub("", string)

    def if_error(self):
        return len(self._error_messages) > 0

    def read_error(self):
        return self._error_messages.pop(0)

    def read(self):
        return self._messages.pop(0)

    def count(self):
        return len(self._messages)

    def flush(self):
        self._messages.clear()
        self._error_messages.clear()
