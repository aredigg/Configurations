import traceback
import datetime
import random
import fcntl
import time
import re
import os
import yt_dlp
from yt_dlp.YoutubeDL import YoutubeDL

YTDLP_COMMON_VERSION = "1.22"
YTDLP_OUTDIR = ".ytdlp"
YTDLP_HOMEDIR = f"{YTDLP_OUTDIR}/home"
YTDLP_TEMPDIR = f"{YTDLP_OUTDIR}/temp"
YTDLP_ARCHIVEDIR = f"{YTDLP_OUTDIR}/archived"
YTDLP_CHANNELSDIR = f"{YTDLP_OUTDIR}/channels"
YTDLP_TEMP_ERRORS = f"{YTDLP_OUTDIR}/tmp_errors"
YTDLP_TIMETABLEDIR = f"{YTDLP_OUTDIR}/timetable"
VERBOSE = 0b001011
YTDLP_MB = True
YTDLP_LIVE = True
YTDPL_VERT = False
YTDLP_DESCRIPTION = False
YTDLP_OUTTMPL = "%(channel)s/%(timestamp>%Y-%m)s/%(id)s.%(ext)s"

def yprint(indicator, text):
    if indicator == "C" and (VERBOSE & 0b000001):
        print(f"{datetime.datetime.now()} \033[1mINF\033[0m {text}\033[0K")
    elif indicator == "I" and (VERBOSE & 0b000010):
        print(f"{datetime.datetime.now()} \033[32mINF\033[39m {text}\033[0K")
    elif indicator == "W" and (VERBOSE & 0b000100):
        print(f"{datetime.datetime.now()} \033[33mWRN\033[39m {text}\033[0K")
    elif indicator == "E" and (VERBOSE & 0b001000):
        print(f"{datetime.datetime.now()} \033[31mERR\033[39m {text}\033[0K")
    elif indicator == "D" and (VERBOSE & 0b010000):
        print(f"{datetime.datetime.now()} \033[34mDBG\033[39m {text}\033[0K")
    else:
        if VERBOSE & 0b100000:
            print(f"{datetime.datetime.now()} \033[36m---\033[39m {text}\033[0K")

def pprint(text):
    if VERBOSE > 0:
        print(f"{text}\033[0K\033[1F")

def run_ytdlp():
    # Common arguments
    ydl_opts = {
        "ignoreerrors": True,
        "live_from_start": YTDLP_LIVE,
        "multistreams": True,
        "retries": 5,
        "sleep_interval": 10,
        "max_sleep_interval": 20,
        "sleep_interval_requests": 0.75,
        "paths": {
            "temp": f"{YTDLP_TEMPDIR}",
            "home": f"{YTDLP_HOMEDIR}",
        },
        "cookiesfrombrowser": ('safari', None, None, None),
        "download_archive": f"{YTDLP_ARCHIVEDIR}",
        "outtmpl": f"{YTDLP_OUTTMPL}",
        "format": "bestvideo[ext=mp4]+bestaudio[ext=m4a]/bestvideo[height>=1600]+bestaudio/best",
        "writesubtitles": True,
        "writeautomaticsub": False,
        "subtitleslangs": ["all"],
        "keep_fragments": True,
        "writedescription": YTDLP_DESCRIPTION,
        "writeinfojson": YTDLP_DESCRIPTION,
        "extractor_args": {
            "youtube": {
                "player_client": ["default", "-tv", "web_safari", "web_embedded"]
            }
        },
        "external_downloader_args": {
            "ffmpeg": ["-loglevel", "quiet", "-hide_banner", "-nostats"]
        },
        "downloader_args": {
            "ffmpeg": ["-loglevel", "quiet", "-hide_banner", "-nostats"]
        },
        "postprocessor_args": {
            "ffmpeg": ["-loglevel", "error", "-hide_banner", "-nostats"]
        }
    }
    # Parse the channels
    try:
        with open(f"{YTDLP_CHANNELSDIR}", "r") as afile:
            channels = [line.strip() for line in afile if line.strip() and not line.startswith("#")]
    except FileNotFoundError:
        yprint("E", "Channel file not found")
        return "Error"
    # Create logger
    logger = Logger()
    ydl_opts["logger"] = logger
    # Hook up hooks
    ydl_opts["progress_hooks"] = [progress_hook]
    ydl_opts["postprocessor_hooks"] = [postprocessor_hook]
    # Process channels
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            for channel in channels:
                yprint("I", f"Channel {channel}")
                process_channel(ydl, channel)
                rotate_channel_file(f"{YTDLP_CHANNELSDIR}")
    except SystemExit as e:
        yprint("E", f"SystemExit {str(e)}")
    except KeyboardInterrupt:
        yprint("E", f"KeyboardInterrupt")
    except BaseException as e:
        yprint("E", f"BaseException {str(e)}")
    # save error messages
    with open(f"{YTDLP_TEMP_ERRORS}_ERR", "w", encoding="utf-8") as f:
        for msg in logger.error_messages:
            if msg and not msg.endswith("\n"):
                msg += "\n"
            f.write(msg)
    with open(f"{YTDLP_TEMP_ERRORS}_PRS", "w", encoding="utf-8") as f:
        for msg in logger.parse_messages:
            if msg and not msg.endswith("\n"):
                msg += "\n"
            f.write(msg)
    return "Complete"

def progress_hook(d):
    if d == None:
        yprint("E", f"Progress hook object is nothing")
        return
    if YTDLP_MB:
        divider = 20
        dnm = "MB"
    else:
        divider = 10
        dnm = "KB"
    if d.get("status") == "downloading":
        dl = int(d.get("downloaded_bytes") or 0) >> divider
        tl = int(d.get("total_bytes") or dl) >> divider
        if tl == 0:
            tl = int(d.get("total_bytes_estimate") or dl) >> divider
        if tl == 0:
            pct = float(d.get("_percent") or 0)
            dlt = float(d.get("downloaded_bytes") or 0)
            if pct > 0:
                tl = int((dlt * 100) / pct) >> divider
        sp = int(d.get("speed") or 0) >> divider
        sz = len(str(tl))
        eta = int(d.get("eta") or 0)
        elp = int(d.get("elapsed") or 0)
        hr = int(eta / 3600)
        mn = int((eta / 60) % 60)
        sc = int(eta % 60)
        ehr = int(elp / 3600)
        emn = int((elp / 60) % 60)
        esc = int(elp % 60)
        fri = int(d.get("fragment_index") or 0)
        frc = int(d.get("fragment_count") or 0)
        frl = len(str(frc))
        flsplit = d.get("filename").upper().split('.')
        if flsplit:
            fltyp = d.get("filename").upper().split('.')[-1]
        else:
            fltyp = "UNK"
        if len(fltyp) > 6:
            fltyp = "UNK"
        pprint(f"Downloading {fltyp} {d.get("_percent"):3.0f}% ({dl:{sz}}/{tl}{dnm}) ETA {hr:02}:{mn:02}:{sc:02} {sp:{int((60/divider))}} {dnm}/s FRAG[{fri:{frl}}/{frc}] AET {ehr:02}:{emn:02}:{esc:02}")
    elif d.get("status") == "finished":
        yprint("I", f"Downloaded {d.get("filename")}")
    else:
        yprint("+", f"{d.get("status")} {d.get("downloaded_bytes")}/{d.get("total_bytes")} {d.get("eta")} {d.get("speed")} {d.get("elapsed")} {d.get("_percent")}")
        yprint("+", f"{d.get("status")} {d.get("filename")} / {d.get("tmpfilename")}")

def postprocessor_hook(d):
    if d == None:
        yprint("E", f"Postprocessor hook object is nothing")
        return
    info = d.get("info_dict")
    if info:
        operation = ("None", "None")
        if d.get("postprocessor") == "Merger":
            operation = ("Merging", "Merged")
        elif d.get("postprocessor") == "MoveFiles":
            operation = ("Moving", "Moved")
        elif d.get("postprocessor") == "FixupM3u8":
            operation = ("Finalizing M3U8", "Completed M3U8")
        else:
            yprint("+", f"POSTPROCESSOR: {d.get("postprocessor")} {d.get("status")}")
            operation = (d.get("postprocessor"), d.get("postprocessor"))
        if d.get("status") == "started":
            pprint(f"{operation[0]} {info.get("filename")}")
        elif d.get("status") == "finished":
            codec_string = "UNK/UNK"
            vcodec = info.get("vcodec")
            acodec = info.get("acodec")
            if vcodec and acodec:
                codec_string = f"{vcodec[:4]}/{acodec[:4]}"
            yprint("I", f"{operation[1]} {info.get("filename")} [{info.get("resolution")}@{info.get("fps")} ({info.get("aspect_ratio")}) {info.get("dynamic_range")} {codec_string}] ({info.get("duration")})")
            # print("\033[38;5;8m" + str(info) + "\033[39m")
            if operation[1] == "Moved":
                sleep_time = random.randrange(min(max(info.get("duration") or 0, 1), 7200))
                sleep_now(sleep_time >> 2)
        else:
            yprint("+", f"{d.get("status")} {info.get("resolution")}/{info.get("fps")} {info.get("dynamic_range")} {info.get("vcodec")} {info.get("acodec")} {info.get("aspect_ratio")} {d.get("postprocessor")}")
            yprint("+", f"{d.get("status")} {info.get("filename")}")

class PLCounter:
    def __init__(self, counter, total):
        self.total = total
        self.counter = counter

def process_channel(ydl: YoutubeDL, url: str, progress=None):
    if url == None:
        yprint("E", f"Given process channel URL does not exist")
        return
    try:
        info = ydl.extract_info(url, download=False, process=False)
        if info:
            url_type = info.get("_type")
            if url_type == "playlist":
                entries = info.get("entries")
                if entries:
                    entries = list(entries)
                    yprint("I", f"Playlist {info.get("title")} with {len(entries)} entries")
                    for i, entry in enumerate(entries):
                        if entry:
                            entry_url = entry.get("webpage_url") or entry.get("url")
                            if entry_url:
                                pl = PLCounter(i+1, len(entries))
                                process_channel(ydl, entry_url, pl)
            elif url_type == "url":
                availability = info.get("availability")
                if availability == "subscriber_only":
                    yprint("+", f"url: subscriber_only")
                else:
                    yprint("+", f"url: {availability}")
            else:
                pl_string = "N/A"
                if progress:
                    pl_string = f"{progress.counter}/{progress.total}"
                yprint("C", f"[{info.get("extractor")}] ({pl_string}) {info.get("upload_date")} ({info.get("id")}) \033[1m\"{info.get("title")}\"\033[0m")
                formats = info.get("formats")
                if formats:
                    # 1716 is Cinemascope (2160), 1644 is Cinemawide (21:9), 2160, 4320
                    # Technically just heights, but we don't use it to anything practical now
                    resolution = "LR"
                    has_720 = any(fmt.get("height", 0) >= 720 for fmt in formats if fmt.get('height') is not None)
                    has_1080 = any(fmt.get("height", 0) >= 1080 for fmt in formats if fmt.get('height') is not None)
                    has_1440 = any(fmt.get("height", 0) >= 1440 for fmt in formats if fmt.get('height') is not None)
                    has_cinemascope = any(fmt.get("height", 0) >= 1644 for fmt in formats if fmt.get('height') is not None)
                    has_cinemawide = any(fmt.get("height", 0) >= 1716 for fmt in formats if fmt.get('height') is not None)
                    has_4k = any(fmt.get("height", 0) >= 2160 for fmt in formats if fmt.get('height') is not None)
                    has_4k_mp4 = any(fmt.get("height", 0) >= 2160 and fmt.get("ext") == "mp4" for fmt in formats if fmt.get('height') is not None)
                    has_8k = any(fmt.get("height", 0) >= 4320 for fmt in formats if fmt.get('height') is not None)
                    has_8k_mp4 = any(fmt.get("height", 0) >= 4320 and fmt.get("ext") == "mp4" for fmt in formats if fmt.get('height') is not None)
                    is_vertical = any(fmt['height'] > fmt['width'] for fmt in formats if fmt.get('height') is not None and fmt.get('width') is not None and fmt.get('height', 0) != 0 and fmt.get('width', 0) != 0)
                    is_lowres = False
                    if has_8k_mp4:
                        resolution = "8K (MP4)"
                    elif has_8k:
                        resolution = "8K"
                    elif has_4k_mp4:
                        resolution = "4K (MP4)"
                    elif has_4k:
                        resolution = "4K"
                    elif has_cinemawide:
                        resolution = "Cinemawide"
                    elif has_cinemascope:
                        resolution = "Cinemascope"
                    elif has_1440:
                        resolution = "2.5K"
                    elif has_1080:
                        resolution = "HD 2K"
                    elif has_720:
                        resolution = "HD"
                    else:
                        is_lowres = True
                    duration = int(info.get("duration") or 0)
                    hr = int(duration / 3600)
                    mn = int((duration / 60) % 60)
                    sc = int(duration % 60)
                    category = info.get("categories")
                    retcode = None
                    if category:
                        category = category[0]
                    else:
                        category = "Unknown"
                    if not is_vertical and not is_lowres:
                        yprint("I", f"CHANNEL: {info.get("channel")} UPLOADER: {info.get("uploader")} UPLOADER_ID: {info.get("uploader_id")}")
                        yprint("I", f"{resolution} DURATION: {hr:02}:{mn:02}:{sc:02} LIVE: {info.get("live_status")} AGE_LIMIT: {info.get("age_limit")} CATEGORY: {category}")
                        availability = info.get("availability")
                        if availability == "public":
                            pprint("\033[5mDownloading (Availability: Public)…\033[0m")
                            retcode = ydl.download([url])
                        elif availability == "needs_auth":
                            pprint("\033[5mDownloading (Availability: Needs authorization)…\033[0m")
                            retcode = ydl.download([url])
                        elif availability == None:
                            pprint("\033[5mDownloading…\033[0m")
                            retcode = ydl.download([url])
                        else:
                            yprint("+", f"AVAILABILITY: {availability}")
                    else:
                        if YTDPL_VERT and not is_lowres:
                            yprint("I", f"Vertical DURATION: {hr:02}:{mn:02}:{sc:02} CATEGORY: {category}")
                            pprint(f"\033[5mDownloading (Availability: {info.get("availability")})…\033[0m")
                            retcode = ydl.download([url])
                        else:
                            yprint("E", f"Skipping {info.get("id")} because it is vertical or low resolution")
                            if is_vertical:
                                add_video_id(f"{YTDLP_ARCHIVEDIR}", f"{info.get("extractor")} {info.get("id")}")
                    yprint("D", f"Return code {retcode}")
    except Exception as e:
        current_traceback = traceback.format_exc()
        yprint("E", f"EXCEPTION {url} {str(e)}")
        print("\033[38;5;8m" + current_traceback + "\033[39m")
        sleep_now(600)

class Logger:
    def __init__(self):
        self.error_messages = []
        self.parse_messages = []

    def debug(self, msg):
        yprint("D", f"{msg}")

    def info(self, msg):
        yprint("I", f"{msg}")

    def warning(self, msg):
        yprint("W", f"{msg}")

    def error(self, msg):
        parts = msg.split()
        extractor = "Unk"
        id = "N/A"
        err_msg = msg
        if not msg:
            err_msg = "Empty"
        if len(parts) >= 2:
            extractor = parts[1]
            id = parts[2]
            err_msg = " ".join(parts[1:])
        if id.endswith(":"):
            err_msg = " ".join(parts[3:])
            id = id[:-1]
            short, sleep_time, add_archive = self.parse_error(err_msg, id)
            yprint("E", f"{extractor} {id} {short}")
            extractor = extractor[1:-1]
            if sleep_time > 0:
                sleep_now(sleep_time)
            if add_archive:
                add_video_id(f"{YTDLP_ARCHIVEDIR}", f"{extractor} {id}")
        elif err_msg == "unable to download video data: HTTP Error 403: Forbidden":
            yprint("E", "403 Forbidden")
            sleep_now(7200)
        elif err_msg.startswith("[download] Got error: HTTP Error 403: Forbidden"):
            yprint("E", "403 Forbidden")
            sleep_now(7200)
        elif err_msg.startswith("[download] Got error: HTTP Error 503: Service Unavailable"):
            yprint("E", "503 Service Unavailable")
            sleep_now(120)
        elif err_msg.startswith("[download] Got error: timed out"):
            yprint("E", "Timed out")
            sleep_now(120)
        elif err_msg.startswith("[download] Got error: The read operation timed out"):
            yprint("E", "Read timed out")
            sleep_now(120)
        elif err_msg.startswith("fragment 1 not found, unable to continue"):
            yprint("E", "Fragments missing")
            sleep_now(120)
        elif err_msg.startswith("[Errno 60] Operation timed out: "):
            yprint("E", "Timed out")
            sleep_now(120)
        elif err_msg.startswith("unable to create directory [Errno 60]"):
            yprint("E", "Timed out")
            sleep_now(7200)
        elif err_msg.startswith("unable to create directory [Errno 13]"):
            yprint("E", "Permission denied")
            sleep_now(7200)
        elif err_msg.startswith("unable to open for writing: [Errno 2] No such file or directory: "):
            yprint("E", "No such file or directory")
            sleep_now(1)
        elif err_msg.startswith("Unable to download video: [Errno 2] No such file or directory: "):
            yprint("E", "No such file or directory")
            sleep_now(1)
        elif err_msg.startswith("Unable to rename file: [Errno 2] No such file or directory: "):
            yprint("E", "No such file or directory")
            sleep_now(1)
        elif err_msg.startswith("[Errno 2] No such file or directory: "):
            yprint("E", "No such file or directory")
            sleep_now(1)
        elif err_msg.startswith("ffmpeg exited with code 254"):
            yprint("E", "ffmpeg: File not found")
            sleep_now(1)
        else:
            pattern = re.compile(
                r"\[download\]\s+Got error:\s+HTTPS?ConnectionPool\(host=(['\"]).*?\1,\s*"
                r"port=\d+\):\s*Read timed out\.\s*\(read timeout=\d+(?:\.\d+)?\)"
            )
            if pattern.search(err_msg):
                yprint("E", "Pool read timeout")
                sleep_now(120)
                return

            pattern = re.compile(
                r"\[download\]\s+Got error:\s*"
                r"\(<urllib3\.connection\.HTTPS?Connection object at 0x[0-9A-Fa-f]+>,\s*"
                r"(['\"])Connection to \S+ timed out\. "
                r"\(connect timeout=\d+(?:\.\d+)?\)\1\)"
                r"(?:\.\s*Giving up after \d+\s+retries)?"
            )
            if pattern.search(err_msg):
                yprint("E", "Connection timeout")
                sleep_now(120)
                return

            pattern = re.compile(
                r"\[download\]\s+Got error:\s*"
                r"\(\s*(['\"])Connection aborted\.\1,\s*"
                r"(?:[\w.]*\.)?RemoteDisconnected\(\1Remote end closed connection without response\1\)"
                r"\s*\)"
                r"(?:\.\s*Giving up after \d+\s+retries)?"
            )
            if pattern.search(err_msg):
                yprint("E", "Remote disconnect")
                sleep_now(120)
                return

            pattern = re.compile(
                r"\[download\]\s+Got error:\s*"
                r"(?:\d{1,3}(?:,\d{3})*|\d+)\s+bytes read,\s*"
                r"(?:\d{1,3}(?:,\d{3})*|\d+)\s+more expected\."
                r"(?:\s*Giving up after \d+\s+retries)?"
            )
            if pattern.search(err_msg):
                yprint("E", "Partial read error")
                sleep_now(120)
                return

            yprint("E", f" \033[33m**\033[39m {err_msg}")
            if err_msg not in self.error_messages:
                self.error_messages.append(err_msg)

    def parse_error(self, msg, id=None):
        if msg == "This video is available to this channel's members on level: Tier 2 (or any higher level). Join this channel to get access to members-only content and other exclusive perks.":
            return "Member level: Tier 2 or higher", 0, True
        elif msg.startswith("This video is available to this channel's members on level: "):
            return "Member level", 0, True
        elif msg == "Join this channel to get access to members-only content like this video, and other exclusive perks.":
            return "Members only", 0, True
        elif msg == "Video unavailable. Playback on other websites has been disabled by the video owner":
            return "Video disabled by owner", 0, True
        elif msg == "Video unavailable":
            return "Video unavailable", 0, False
        elif msg == "Video unavailable. This content isn’t available.":
            return "This content isn’t available.", 43200, False
        elif msg == "--live-from-start is passed, but there are no formats that can be downloaded from the start. If you want to download from the current time, use --no-live-from-start":
            return "Unable to live from start", 0, False
        elif msg == "Sign in to confirm you’re not a bot. Use --cookies-from-browser or --cookies for the authentication. See https://github.com/yt-dlp/yt-dlp/wiki/FAQ#how-do-i-pass-cookies-to-yt-dlp for how to manually pass cookies. Also see https://github.com/yt-dlp/yt-dlp/wiki/Extractors#exporting-youtube-cookies for tips on effectively exporting YouTube cookies":
            return "Authentication required (Cookies)", 3600, False
        elif msg == "Video unavailable. This content isn't available, try again later. Your account has been rate-limited by YouTube for up to an hour. It is recommended to use `-t sleep` to add a delay between video requests to avoid exceeding the rate limit. For more information, refer to https://github.com/yt-dlp/yt-dlp/wiki/Extractors#this-content-isnt-available-try-again-later":
            return "Video unavailable due rate limitation", 43200, False
        elif msg == "unable to download video data: HTTP Error 403: Forbidden":
            return "Forbidden", 43200, False
        elif msg == "Hidden session in progress":
            return "Hidden", 0, False
        elif msg == "Room is currently in a private show":
            return "Private", 0, False
        elif msg == "Room is password protected":
            return "Protected", 0, False
        elif msg == "Room is currently offline":
            add_hour_id(f"{YTDLP_TIMETABLEDIR}", id)
            return "Offline", 3, False
        elif msg == "Performer is currently away":
            return "Performer away", 0, False
        elif msg == "Unable to download webpage: [SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: unable to get local issuer certificate (_ssl.c:1028) (caused by CertificateVerifyError('[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: unable to get local issuer certificate (_ssl.c:1028)')); please report this issue on https://github.com/yt-dlp/yt-dlp/issues?q= , filling out the appropriate issue template. Confirm you are on the latest version using yt-dlp -U":
            return "Certificate verify fail", 0, False
        elif msg == "Unable to download JSON metadata: HTTP Error 403: Forbidden (caused by <HTTPError 403: Forbidden>)":
            return "JSON forbidden", 60, False
        elif msg == "Did not get any data blocks":
            return "No data blocks", 0, False
        elif msg == "Failed to download m3u8 information: HTTP Error 404: Not Found (caused by <HTTPError 404: Not Found>)":
            return "Not Found", 120, False
        elif msg == "Failed to download m3u8 information: HTTP Error 502: Bad Gateway (caused by <HTTPError 502: Bad Gateway>)":
            return "Bad Gateway", 120, False
        elif msg == "Unable to download webpage: HTTP Error 429: Too Many Requests (caused by <HTTPError 429: Too Many Requests>)":
            return "Too many requests", 120, False
        elif msg.startswith("This live event will begin in"):
            return "Future live event", 0, False
        if msg not in self.parse_messages:
            self.parse_messages.append(msg)
        return "\033[33mUnknown\033[39m", 43200, False

def rotate_channel_file(channel_file):
    with open(channel_file, "r+", encoding="utf-8") as f:
        lines = f.readlines()
        if lines:
            rotated = lines[1:] + [lines[0]]
            f.seek(0)
            f.writelines(rotated)
            f.truncate()

def add_video_id(archive_file, video_id):
    with open(archive_file, "a", encoding="utf-8") as f:
        if video_id and not video_id.endswith("\n"):
            video_id += "\n"
        f.write(video_id)

def id_parse_lines(lines):
    data = {}
    order = []
    for line in lines:
        parts = line.strip().split()
        if not parts:
            continue
        k = parts[0]
        hours = [h for h in parts[1:] if h.isdigit()]
        if k not in data:
            data[k] = set(hours)
            order.append(k)
        else:
            data[k].update(hours)
    return data, order

def add_hour_id(hour_file, video_id):
    now = datetime.datetime.now().strftime("%w%H")
    with open(hour_file, "a+", encoding="utf-8") as f:
        fcntl.flock(f.fileno(), fcntl.LOCK_EX)
        try:
            f.seek(0)
            lines = f.read().splitlines()
            data, order = id_parse_lines(lines)
            if video_id not in data:
                data[video_id] = {now}
                order.append(video_id)
            else:
                data[video_id].add(now)
            out_lines = []
            seen = set()
            for k in order:
                if k in seen:
                    continue
                seen.add(k)
                hours = sorted(data.get(k, []))
                out_lines.append(f"{k} " + " ".join(hours) if hours else k)
            f.seek(0)
            f.truncate()
            f.write("\n".join(out_lines) + "\n")
            f.flush()
            os.fsync(f.fileno())
        finally:
            fcntl.flock(f.fileno(), fcntl.LOCK_UN)

def sleep_now(duration):
    if duration <= 0:
        return
    duration += random.randrange(duration)
    hr = int(duration/3600)
    mn = int((duration%3600)/60)
    sc = int((duration%3600)%60)
    eta = datetime.datetime.now() + datetime.timedelta(seconds=duration)
    if duration < 1800:
        yprint("I", f"Sleeping for {hr:02}:{mn:02}:{sc:02}")
    else:
        yprint("I", f"Sleeping for {hr:02}:{mn:02}:{sc:02}, waking at {eta.strftime('%d %H:%M:%S (%A)')}")
    time.sleep(duration)

yprint("I", f"YT-DLP COMMON {YTDLP_COMMON_VERSION}")
if __name__ == "__main__":
    pass
