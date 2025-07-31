import common
import shutil
import time
import os

YTDLP_CBT_VERSION = "1.05"
common.YTDLP_OUTDIR = "/Volumes/Delt/Prosjekter/yt-dlp/.cbt"
common.VERBOSE = 0b001011
common.YTDLP_MB = True
common.YTDLP_LIVE = False
common.YTDLP_OUTTMPL = "%(epoch>%Y-%m)s/%(epoch>W%W)s/%(epoch>%a)s/%(id)s.%(ext)s"
common.YTDLP_HOMEDIR = f"{common.YTDLP_OUTDIR}/cbt"
common.YTDLP_TEMPDIR = f"/Volumes/Ekstern/.cbttemp"
common.YTDLP_ARCHIVEDIR = f"{common.YTDLP_OUTDIR}/archived"
common.YTDLP_CHANNELSDIR = f"{common.YTDLP_OUTDIR}/channels"
common.YTDLP_TEMP_ERRORS = f"{common.YTDLP_OUTDIR}/tmp_errors"


def main():
    main_loop = True
    archive_deletetime = 0
    common.yprint("I", f"YT-DLP CBT {YTDLP_CBT_VERSION}")
    if os.path.exists(common.YTDLP_TEMPDIR):
        common.yprint("D", f"YT-DLP CBT temporary directory {common.YTDLP_TEMPDIR} will be removed")
        shutil.rmtree(common.YTDLP_TEMPDIR)
    while main_loop:
        try:
            channel_count = sum(1 for _ in open(common.YTDLP_CHANNELSDIR))
            if os.path.exists(common.YTDLP_ARCHIVEDIR) and time.time() - archive_deletetime > 86400:
                common.yprint("D", f"YT-DLP CBT {common.YTDLP_ARCHIVEDIR} will be deleted")
                os.remove(common.YTDLP_ARCHIVEDIR)
                archive_deletetime = time.time()
            channel_loop = True
            while channel_loop:
                archived_count = sum(1 for _ in open(common.YTDLP_ARCHIVEDIR)) if os.path.isfile(common.YTDLP_ARCHIVEDIR) else 0
                common.yprint("I", f"YT-DLP CBT {archived_count}/{channel_count}")
                common.yprint("I", f"YT-DLP CBT {common.run_ytdlp()}")
                channel_loop = archived_count < (channel_count >> 1)
                common.sleep_now((archived_count + 1) * 300)
        except KeyboardInterrupt:
            common.yprint("E", f"YT-DLP CBT KeyboardInterrupt")
            main_loop = False

if __name__ == "__main__":
    main()
