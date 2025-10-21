import os
import time

import ytb

LOCAL_VERSION = "2.01"

ytb.ACCEPT_VERTICAL = True
ytb.CHANNELS_FILE = ytb.CONFIG_DIRECTORY + "/vertical_channels"
ytb.ARCHIVED_FILE = ytb.CONFIG_DIRECTORY + "/vertical_archived"


def main():
    main_loop = True
    ytb.cli.cls()
    ytb.cli.header_print(f"YT_DLP YTB {ytb.LOCAL_VERSION}, VRT {LOCAL_VERSION}", 0, color="\033[92m")
    os.makedirs(ytb.TEMP_DIRECTORY, exist_ok=True)
    while main_loop:
        try:
            ret = ytb.run_ytdlp()
            time.sleep(5)
            if ret < 0:
                main_loop = False
        except KeyboardInterrupt:
            main_loop = False
            ytb.cli.status_line("KeyboardInterrupt in main")


if __name__ == "__main__":
    main()
