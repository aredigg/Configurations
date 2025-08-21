import common
import atexit
import shutil
import fcntl
import time
import os

YTDLP_CBT_VERSION = "1.16"
YTDLP_MAX_LOCKS = 8
common.YTDLP_OUTDIR = "/Volumes/Delt/Prosjekter/yt-dlp/.cbt"
YTDLP_LOCK = f"{common.YTDLP_OUTDIR}/cbt"
common.VERBOSE = 0b001011
common.YTDLP_MB = True
common.YTDLP_LIVE = False
common.YTDLP_OUTTMPL = "%(epoch>%Y-%m)s/%(epoch>W%W)s/%(epoch>%a)s/%(id)s.%(ext)s"
common.YTDLP_HOMEDIR = f"{common.YTDLP_OUTDIR}/cbt"
common.YTDLP_TEMPDIR = f"/Volumes/Ekstern/.cbttemp"
common.YTDLP_ARCHIVEDIR = f"{common.YTDLP_OUTDIR}/archived"
common.YTDLP_CHANNELSDIR = f"{common.YTDLP_OUTDIR}/channels"
common.YTDLP_TEMP_ERRORS = f"{common.YTDLP_OUTDIR}/tmp_errors"
common.YTDLP_TIMETABLEDIR = f"{common.YTDLP_OUTDIR}/timetable"

def acquire_lock(lock_file):
    common.yprint("D", f"YT-DLP CBT acquiring lock {lock_file}")
    fd = os.open(lock_file, os.O_RDWR | os.O_CREAT, 0o644)
    try:
        fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        common.yprint("D", f"YT-DLP CBT lock acquired")                    
        return fd
    except BlockingIOError:
        common.yprint("D", f"YT-DLP CBT lock not acquired")
        return None

def release_lock(lock_fd):
    common.yprint("D", f"YT-DLP CBT releasing lock")                    
    if lock_fd is not None:
        try:
            fcntl.flock(lock_fd, fcntl.LOCK_UN)
        finally:
            os.close(lock_fd)

def get_lockname(id):
    if id is None:
        return f"{YTDLP_LOCK}.lock"
    else:
        return f"{YTDLP_LOCK}-{id}.lock"

def acquire_slot():
    fd = acquire_lock(get_lockname(None))
    if fd is not None:
        return None, fd
    for id in range(1, YTDLP_MAX_LOCKS + 1):
        fd = acquire_lock(get_lockname(id))
        if fd is not None:
            return id, fd
    common.yprint("E", "No more locks available")
    return None, None

def main():
    main_loop = True
    common.yprint("I", f"YT-DLP CBT {YTDLP_CBT_VERSION}")
    os.makedirs(common.YTDLP_OUTDIR, exist_ok=True)
    slot_id, lock_fd = acquire_slot()
    if lock_fd == None:
        return
    atexit.register(release_lock, lock_fd)
    if slot_id is None:
        common.yprint("I", f"YT-DLP CBT Main Slot")
        common.yprint("D",f"YT-DLP CBT temporary directory will be removed")
        shutil.rmtree(common.YTDLP_TEMPDIR, ignore_errors=True)
    else:
        common.YTDLP_CHANNELSDIR = f"{common.YTDLP_CHANNELSDIR}_{slot_id}"
        common.YTDLP_ARCHIVEDIR = f"{common.YTDLP_ARCHIVEDIR}_{slot_id}"
        common.yprint("I", f"YT-DLP CBT Slot {slot_id}")                    
    archive_deletetime = 0
    while main_loop:
        try:
            channel_count = sum(1 for _ in open(common.YTDLP_CHANNELSDIR))
            if time.time() - archive_deletetime > 86400:
                if os.path.exists(common.YTDLP_ARCHIVEDIR):
                    common.yprint("D", f"YT-DLP CBT {common.YTDLP_ARCHIVEDIR} will be deleted")
                    os.remove(common.YTDLP_ARCHIVEDIR)
                archive_deletetime = time.time()
            channel_loop = True
            channel_loop_counter = 8
            while channel_loop:
                archived_count = sum(1 for _ in open(common.YTDLP_ARCHIVEDIR)) if os.path.isfile(common.YTDLP_ARCHIVEDIR) else 0
                common.yprint("I", f"YT-DLP CBT {archived_count}/{channel_count} LOOP {channel_loop_counter}")
                common.yprint("I", f"YT-DLP CBT {common.run_ytdlp()}")
                channel_loop = (archived_count < channel_count) and (archived_count < 12) and (channel_loop_counter > 0)
                common.sleep_now(1800)
                channel_loop_counter -= 1
        except KeyboardInterrupt:
            common.yprint("E", f"YT-DLP CBT KeyboardInterrupt")
            main_loop = False

if __name__ == "__main__":
    main()
