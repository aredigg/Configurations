import re


class Logger:
    def __init__(self):
        self.__messages = []
        self.__error_messages = []

    def debug(self, msg):
        self.__messages.append(msg)

    def info(self, msg):
        self.__messages.append(msg)

    def warning(self, msg):
        self.__messages.append(msg)

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
        self.__error_messages.append((extractor, id, error_msg))
        self.__messages.append(msg)

    def _remove_ansi(self, string):
        code = re.compile(r"\x1B\[[0-?]*[ -/]*[@-~]")
        return code.sub("", string)

    def if_error(self):
        return len(self.__error_messages) > 0

    def read_error(self):
        return self.__error_messages.pop(0)

    def read(self):
        return self.__messages.pop(0)

    def count(self):
        return len(self.__messages)

    def flush(self):
        self.__messages.clear()
        self.__error_messages.clear()
