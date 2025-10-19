import os
import time

import ytb

LOCAL_VERSION = "2.00"

ytb.ACCEPT_LOW_RESOLUTION = True
ytb.CHANNELS_FILE = ytb.CONFIG_DIRECTORY + "/low_resolution_channels"


def main():
    main_loop = True
    ytb.cli.cls()
    ytb.cli.cursor_off()
    ytb.cli.header_print(f"YT_DLP YTB {ytb.LOCAL_VERSION}, LOW {LOCAL_VERSION}", 1, color="\033[5;94m")
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
    ytb.cli.cursor_on()
    ytb.cli.pass_cursor()


if __name__ == "__main__":
    main()
