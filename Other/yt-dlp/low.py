import os
import time
from importlib.metadata import version

import yt_dlp.version as YDLV  # noqa  # noqa

import ytb

LOCAL_VERSION = "2.01"

ytb.ACCEPT_LOW_RESOLUTION = True
ytb.CHANNELS_FILE = ytb.CONFIG_DIRECTORY + "/low_resolution_channels"


def main():
    main_loop = True
    ytb.cli.cls()
    ytb.cli.header_print(
        f"{YDLV.ORIGIN.split('/')[0].upper()} {version('yt_dlp')} {YDLV.CHANNEL}/{YDLV.VARIANT} YTB {ytb.LOCAL_VERSION}, LOW {LOCAL_VERSION}",
        0,
        color="\033[92m",
    )
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
