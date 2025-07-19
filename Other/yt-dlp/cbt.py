import common
import os

YTDLP_CBT_VERSION = "1.00"
common.YTDLP_OUTDIR = ".cbt"
common.VERBOSE = 0b001011
common.YTDLP_MB = True
common.YTDLP_LIVE = False
common.YTDLP_OUTTMPL = "%(id)s/%(epoch>%Y-%m)s/%(epoch>W%W %a_%H)s.%(ext)s"
common.YTDLP_HOMEDIR = f"{common.YTDLP_OUTDIR}/cbt"
common.YTDLP_TEMPDIR = f"../temp"
common.YTDLP_ARCHIVEDIR = f"{common.YTDLP_OUTDIR}/archived"
common.YTDLP_CHANNELSDIR = f"{common.YTDLP_OUTDIR}/channels"
common.YTDLP_TEMP_ERRORS = f"{common.YTDLP_OUTDIR}/tmp_errors"


def main():
    main_loop = True
    common.yprint("I", f"YT-DLP CBT {YTDLP_CBT_VERSION}")
    while main_loop:
        try:
            channel_count = sum(1 for _ in open(f"{common.YTDLP_OUTDIR}/channels"))
            if os.path.exists(f"{common.YTDLP_OUTDIR}/archived"):
                os.remove(f"{common.YTDLP_OUTDIR}/archived")
            channel_loop = True
            while channel_loop:
                archived_count = sum(1 for _ in open(f"{common.YTDLP_OUTDIR}/archived")) if os.path.isfile(f"{common.YTDLP_OUTDIR}/archived") else 0
                common.yprint("I", f"YT-DLP CBT {common.run_ytdlp()}")
                channel_loop = archived_count < channel_count
                common.sleep_now(3600)
            common.sleep_now(43200)
        except KeyboardInterrupt:
            common.yprint("E", f"YT-DLP CBT Interrupted")
            main_loop = False

if __name__ == "__main__":
    main()
