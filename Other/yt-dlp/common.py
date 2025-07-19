import datetime
import random
import time
import re
import yt_dlp
from yt_dlp.YoutubeDL import YoutubeDL

YTDLP_COMMON_VERSION = "1.00"
YTDLP_OUTDIR = ".ytdlp"
YTDLP_HOMEDIR = f"{YTDLP_OUTDIR}/home"
YTDLP_TEMPDIR = f"{YTDLP_OUTDIR}/temp"
YTDLP_ARCHIVEDIR = f"{YTDLP_OUTDIR}/archived"
YTDLP_CHANNELSDIR = f"{YTDLP_OUTDIR}/channels"
YTDLP_TEMP_ERRORS = f"{YTDLP_OUTDIR}/tmp_errors"
VERBOSE = 0b001011
YTDLP_MB = True
YTDLP_LIVE = True
YTDLP_OUTTMPL = "%(channel)s/%(timestamp>%Y-%m)s/%(id)s.%(ext)s"

def yprint(indicator, text):
    if indicator == "C" and (VERBOSE & 0b000001):
        print(f"{datetime.datetime.now()} \033[1mINF\033[0m {text}")
    elif indicator == "I" and (VERBOSE & 0b000010):
        print(f"{datetime.datetime.now()} \033[32mINF\033[39m {text}")
    elif indicator == "W" and (VERBOSE & 0b000100):
        print(f"{datetime.datetime.now()} \033[33mWRN\033[39m {text}")
    elif indicator == "E" and (VERBOSE & 0b001000):
        print(f"{datetime.datetime.now()} \033[31mERR\033[39m {text}")
    elif indicator == "D" and (VERBOSE & 0b010000):
        print(f"{datetime.datetime.now()} \033[34mDBG\033[39m {text}")
    else:
        if VERBOSE & 0b100000:
            print(f"{datetime.datetime.now()} \033[36m---\033[39m {text}")

def pprint(text):
    if VERBOSE > 0:
        print(f"{text}\033[1F")

def run_ytdlp():
    # Common arguments
    ydl_opts = {
        "ignoreerrors": True,
        "live_from_start": YTDLP_LIVE,
        "multistreams": True,
        "retries": 2,
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
        "format": "bestvideo[ext=mp4]+bestaudio[ext=m4a]/bestvideo[height>=2160]+bestaudio/best",
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
    with open(f"{YTDLP_TEMP_ERRORS}", "w", encoding="utf-8") as f:
        for msg in logger.error_messages:
            if msg and not msg.endswith("\n"):
                msg += "\n"
            f.write(msg)
    return "Complete"

def progress_hook(d):
    if YTDLP_MB:
        divider = 20
        denominator = "MB"
    else:
        divider = 10
        denominator = "KB"
    if d.get("status") == "downloading":
        dl = (d.get("downloaded_bytes") or 0) >> divider
        tl = (d.get("total_bytes") or dl) >> divider
        sp = int(d.get("speed") or 0) >> divider
        sz = len(str(tl))
        eta = int(d.get("eta") or 0)
        hr = int(eta / 3600)
        mn = int((eta / 60) % 60)
        sc = int(eta % 60)
        pprint(f"Downloading {d.get("_percent"):3.0f}% ({dl:{sz}}/{tl}{denominator}) ETA {hr:02}:{mn:02}:{sc:02} {sp:{int((60/divider))}} {denominator}/s")
    elif d.get("status") == "finished":
        yprint("I", f"Downloaded {d.get("filename")}")
    else:
        yprint("+", f"{d.get("status")} {d.get("downloaded_bytes")}/{d.get("total_bytes")} {d.get("eta")} {d.get("speed")} {d.get("elapsed")} {d.get("_percent")}")
        yprint("+", f"{d.get("status")} {d.get("filename")} / {d.get("tmpfilename")}")

def postprocessor_hook(d):
    info = d.get("info_dict")
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
        yprint("I", f"{operation[1]} {info.get("filename")} [{info.get("resolution")}@{info.get("fps")} ({info.get("aspect_ratio")}) {info.get("dynamic_range")} {info.get("vcodec")[:4]}/{info.get("acodec")[:4]}]")
    else:
        yprint("+", f"{d.get("status")} {info.get("resolution")}/{info.get("fps")} {info.get("dynamic_range")} {info.get("vcodec")} {info.get("acodec")} {info.get("aspect_ratio")} {d.get("postprocessor")}")
        yprint("+", f"{d.get("status")} {info.get("filename")}")

class PLCounter:
    def __init__(self, counter, total):
        self.total = total
        self.counter = counter

def process_channel(ydl: YoutubeDL, url: str, progress=None):
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
                                pl = PLCounter(i, len(entries))
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
                    has_cinemascope = any(fmt.get("height", 0) >= 1644 for fmt in formats if fmt.get('height') is not None)
                    has_cinemawide = any(fmt.get("height", 0) >= 1716 for fmt in formats if fmt.get('height') is not None)
                    has_4k = any(fmt.get("height", 0) >= 2160 for fmt in formats if fmt.get('height') is not None)
                    has_4k_mp4 = any(fmt.get("height", 0) >= 2160 and fmt.get("ext") == "mp4" for fmt in formats if fmt.get('height') is not None)
                    has_8k = any(fmt.get("height", 0) >= 4320 for fmt in formats if fmt.get('height') is not None)
                    has_8k_mp4 = any(fmt.get("height", 0) >= 4320 and fmt.get("ext") == "mp4" for fmt in formats if fmt.get('height') is not None)
                    is_vertical = any(fmt['height'] > fmt['width'] for fmt in formats if fmt.get('height') is not None and fmt.get('width') is not None and fmt.get('height', 0) != 0 and fmt.get('width', 0) != 0)
                    duration = int(info.get("duration") or 0)
                    hr = int(duration / 3600)
                    mn = int((duration / 60) % 60)
                    sc = int(duration % 60)
                    category = info.get("categories")
                    if category:
                        category = category[0]
                    else:
                        category = "Unknown"
                    if not is_vertical:
                        yprint("I", f"8K: {has_8k} 8K-MP4: {has_8k_mp4} 4K: {has_4k} 4K-MP4: {has_4k_mp4} Cinemascope: {has_cinemascope} Cinemawide: {has_cinemawide} VERTICAL: {is_vertical}")
                        yprint("I", f"CHANNEL: {info.get("channel")} UPLOADER: {info.get("uploader")} UPLOADER_ID: {info.get("uploader_id")}")
                        yprint("I", f"DURATION: {hr:02}:{mn:02}:{sc:02} LIVE: {info.get("live_status")} AGE_LIMIT: {info.get("age_limit")} CATEGORY: {category}")
                        availability = info.get("availability")
                        if availability == "public":
                            pprint("\033[5mDownloading (Availability: Public)…\033[0m")
                            retcode = ydl.download([url])
                        elif availability == None:
                            pprint("\033[5mDownloading…\033[0m")
                            retcode = ydl.download([url])
                        else:
                            yprint("+", f"AVAILABILITY: {availability}")
                    else:
                        yprint("E", f"Skipping {info.get("id")} because it is vertical")
                        add_video_id(f"{YTDLP_ARCHIVEDIR}", f"{info.get("extractor")} {info.get("id")}")

    except Exception as e:
        if e and e.__traceback__:
            yprint("E", f"EXCEPTION {url} {str(e)}:{e.__traceback__.tb_lineno}")
        else:
            yprint("E", f"EXCEPTION {url} {str(e)}")

class Logger:
    def __init__(self):
        self.error_messages = []

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
            short, sleep_time, add_archive = parse_error(err_msg)
            yprint("E", f"{extractor} {id} {short}")
            id = id[:-1]
            extractor = extractor[1:-1]
            if sleep_time > 0:
                sleep_now(sleep_time)
            if add_archive:
                add_video_id(f"{YTDLP_ARCHIVEDIR}", f"{extractor} {id}")
        elif err_msg == "unable to download video data: HTTP Error 403: Forbidden":
            yprint("E", "403 Forbidden")
            sleep_now(7200)
        elif err_msg == "[download] Got error: HTTP Error 503: Service Unavailable. Giving up after 2 retries":
            yprint("E", "503 Service Unavailable")
            sleep_now(120)
        else:
            yprint("E", f"{err_msg}")
        if err_msg not in self.error_messages:
            self.error_messages.append(err_msg)

def parse_error(msg):
    if msg == "This video is available to this channel's members on level: Tier 2 (or any higher level). Join this channel to get access to members-only content and other exclusive perks.":
        return "Member level: Tier 2 or higher", 0, True
    elif msg == "Join this channel to get access to members-only content like this video, and other exclusive perks.":
        return "Members only", 0, True
    elif msg == "Video unavailable. Playback on other websites has been disabled by the video owner":
        return "Video disabled by owner", 0, True
    elif msg == "--live-from-start is passed, but there are no formats that can be downloaded from the start. If you want to download from the current time, use --no-live-from-start":
        return "Unable to live from start", 0, False
    elif msg == "Sign in to confirm you’re not a bot. Use --cookies-from-browser or --cookies for the authentication. See https://github.com/yt-dlp/yt-dlp/wiki/FAQ#how-do-i-pass-cookies-to-yt-dlp for how to manually pass cookies. Also see https://github.com/yt-dlp/yt-dlp/wiki/Extractors#exporting-youtube-cookies for tips on effectively exporting YouTube cookies":
        return "Authentication required (Cookies)", 3600, False
    elif msg == "Video unavailable. This content isn't available, try again later. Your account has been rate-limited by YouTube for up to an hour. It is recommended to use `-t sleep` to add a delay between video requests to avoid exceeding the rate limit. For more information, refer to https://github.com/yt-dlp/yt-dlp/wiki/Extractors#this-content-isnt-available-try-again-later":
        return "Video unavailable due rate limitation", 14400, False
    elif msg == "unable to download video data: HTTP Error 403: Forbidden":
        return "Forbidden", 14400, False
    elif msg == "Hidden session in progress":
        return "Hidden", 0, False
    elif msg == "Room is currently in a private show":
        return "Private", 0, False
    elif msg == "Room is password protected":
        return "Protected", 0, False
    elif msg == "Room is currently offline":
        return "Offline", 0, False
    elif msg == "Performer is currently away":
        return "Performer away", 0, False
    else:
        pattern = re.compile(r"\[download\] Got error: \d+ bytes read, \d+ more expected\. Giving up after \d+ retries")
        if pattern.fullmatch(msg):
            return "Download timed out", 0, False
    return "Unknown", 0, False

# unable to download video data: HTTP Error 403: Forbidden

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

def sleep_now(duration):
    duration += random.randrange(duration)
    hr = int(duration/3600)
    mn = int((duration%3600)/60)
    sc = int((duration%3600)%60)
    eta = datetime.datetime.now() + datetime.timedelta(seconds=duration)
    if duration < 3600:
        yprint("I", f"Sleeping for {hr:02}:{mn:02}:{sc:02}")
    else:
        yprint("I", f"Sleeping for {hr:02}:{mn:02}:{sc:02}, waking at {eta.strftime('%d %H:%M:%S (%A)')}")
    time.sleep(duration)

yprint("I", f"YT-DLP COMMON {YTDLP_COMMON_VERSION}")
if __name__ == "__main__":
    pass
