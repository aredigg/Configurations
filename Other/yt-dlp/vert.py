import common
import shutil
import os

YTDLP_RUN_VERSION = "1.02"
common.YTDLP_OUTDIR = "/Volumes/Delt/Prosjekter/yt-dlp/vert"
common.VERBOSE = 0b001011
# common.VERBOSE = 0b111111
common.YTDLP_MB = True
common.YTDPL_VERT = True
common.YTDLP_LIVE = True
common.YTDLP_OUTTMPL = "%(channel)s/%(timestamp>%Y-%m)s/%(id)s.%(ext)s"
common.YTDLP_HOMEDIR = f"/Volumes/Delt/YouTube"
common.YTDLP_TEMPDIR = f"/Volumes/Ekstern/.temp"
common.YTDLP_ARCHIVEDIR = f"{common.YTDLP_OUTDIR}/archived"
common.YTDLP_CHANNELSDIR = f"{common.YTDLP_OUTDIR}/channels"
common.YTDLP_TEMP_ERRORS = f"{common.YTDLP_OUTDIR}/tmp_errors"

def main():
    main_loop = True
    common.yprint("I", f"YT-DLP RUN {YTDLP_RUN_VERSION}")
    if os.path.exists(common.YTDLP_TEMPDIR):
        shutil.rmtree(common.YTDLP_TEMPDIR)
    while main_loop:
        try:
            common.yprint("I", f"YT-DLP RUN {common.run_ytdlp()}")
            common.sleep_now(43200)
        except KeyboardInterrupt:
            common.yprint("E", f"YT-DLP RUN KeyboardInterrupt")
            main_loop = False


if __name__ == "__main__":
    main()
