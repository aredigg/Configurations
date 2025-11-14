import os
import time
from importlib.metadata import version

import yt_dlp.version as YDLV  # noqa

import ytb
from cli_print_v2 import ANSI

LOCAL_VERSION = "2.02"

ytb.OUTPUT_DIRECTORY = "/Volumes/Delt/Prosjekter/yt-dlp/.cbtv2"
ytb.TEMP_DIRECTORY = "/Volumes/Ekstern/.cbttemp"
ytb.CONFIG_DIRECTORY = ytb.OUTPUT_DIRECTORY

ytb.DEBUG = False
ytb.ACCEPT_VERTICAL = True
ytb.CHANNELS_FILE = ytb.OUTPUT_DIRECTORY + "/other_channels"
ytb.ARCHIVED_FILE = ytb.OUTPUT_DIRECTORY + "/other_archived"
ytb.YDL_OPTS["writesubtitles"] = False


def main():
    main_loop = True
    ytb.cli.cls()
    ytb.cli.header_print(
        f"{YDLV.ORIGIN.split('/')[0].upper()} {version('yt_dlp')} {YDLV.CHANNEL}/{YDLV.VARIANT} YTB {ytb.LOCAL_VERSION}, OTH {LOCAL_VERSION}",
        0,
        color=ANSI.BGBrGreen + ANSI.Black,
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
