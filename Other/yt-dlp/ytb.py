import datetime
import os
import random
import shutil
import time
from collections import deque
from typing import TYPE_CHECKING, cast

import util
from cli_print import CLIPrint
from logger import Logger
from yt_dlp import YoutubeDL

if TYPE_CHECKING:
    from yt_dlp import _Params

LOCAL_VERSION = "2.08"
DEBUG = True

ACCEPT_VERTICAL = False
MINIMUM_RESOLUTION = 700

OUTPUT_DIRECTORY = "/Volumes/Delt/YouTube"
CONFIG_DIRECTORY = OUTPUT_DIRECTORY + "/.config"
CHANNELS_FILE = CONFIG_DIRECTORY + "/channels"
ARCHIVED_FILE = CONFIG_DIRECTORY + "/archived"
TEMP_DIRECTORY = "/Volumes/Ekstern/.temp"

MAX_HEADERS = 2
PROGRESS_LENGTH = 40
MEDIAN_LENGTH = 1000

YDL_OPTS = {
    "ignoreerrors": True,
    "live_from_start": True,
    "multistreams": True,
    "retries": 5,
    "sleep_interval": 10,
    "max_sleep_interval": 20,
    "sleep_interval_requests": 1,
    "paths": {
        "temp": f"{TEMP_DIRECTORY}",
        "home": f"{OUTPUT_DIRECTORY}",
    },
    "cookiesfrombrowser": ("safari", None, None, None),
    "download_archive": f"{ARCHIVED_FILE}",
    "outtmpl": "%(channel)s/%(timestamp>%Y-%m)s/%(id)s.%(ext)s",
    "format": "bestvideo[ext=mp4]+bestaudio[ext=m4a]/bestvideo[height>=1600]+bestaudio/best",
    "writesubtitles": True,
    "writeautomaticsub": False,
    "subtitleslangs": ["all"],
    "writedescription": False,
    "writeinfojson": False,
    "hls_prefer_native": True,
    "extractor_args": {"youtube": {"player_client": ["default", "-tv", "web_safari", "web_embedded"]}},
    "external_downloader_args": {"ffmpeg": ["-loglevel", "quiet", "-hide_banner", "-nostats"]},
    "downloader_args": {
        "ffmpeg": ["-loglevel", "quiet", "-hide_banner", "-nostats"],
        "ffmpeg_i": ["-rw_timeout", "30000000"],
    },
    "postprocessor_args": {"ffmpeg": ["-loglevel", "error", "-hide_banner", "-nostats"]},
}


cli = CLIPrint(0, MAX_HEADERS, TEMP_DIRECTORY + "/log", DEBUG)


def progress_hook(data, rems, depth=0):
    status = data.get("status") or ""
    filepart = ""
    dl_bytes = int(data.get("downloaded_bytes") or 0)
    tl_bytes = int(data.get("total_bytes_estimate") or data.get("total_bytes") or 0)
    elapsed = util.time_formatted(*util.convert_seconds(int(data.get("elapsed") or 0)))
    progress = 0
    remaining = 0
    # fragments
    fri = int(data.get("fragment_index") or 0)
    frc = int(data.get("fragment_count") or 0)
    frl = len(str(frc))
    frs = ""
    if frc > 0:
        frs = f"[{fri:{frl}}/{frc}] "
    elif tl_bytes > 0:
        dl_sz = dl_bytes >> 20
        tl_sz = tl_bytes >> 20
        ln_sz = len(str(tl_sz))
        frs = f"{dl_sz:{ln_sz}}/{tl_sz} MB "
    filename = data.get("filename") or ""
    extsplit = filename.upper().split(".")
    ext = "UNK"
    if len(extsplit) > 1:
        ext = extsplit[-1]
    fnsplit = filename.split("/")
    if len(fnsplit) > 1:
        filepart = fnsplit[-1]
    if status == "downloading":
        if tl_bytes != 0:
            progress = int(dl_bytes * PROGRESS_LENGTH // tl_bytes)
        remaining = int(data.get("eta") or 0)
        # smooth remaining
        eta_timestamp = int(time.time()) + remaining
        now = int(time.time())
        # remove the past, embrace the future
        for i in range(len(rems)):
            if rems[i] < now:
                rems[i] = now + 5
        rems.append(eta_timestamp)
        eta_timestamp = int(util.mw_mean(rems))
        remaining = int(eta_timestamp - int(time.time()))
    elif status == "finished":
        progress = PROGRESS_LENGTH
        remaining = 0
    rem = util.time_formatted(*util.convert_seconds(remaining))
    eta = util.time_formatted(*util.convert_to_time(remaining))
    cli.tree_print(
        f"{elapsed}/{rem} {ext} {'◼' * progress}{'◻' * (PROGRESS_LENGTH - progress)} {frs}ETA {eta}",
        index=depth,
        line=1,
    )
    cli.tree_print(f"- {filepart} -", index=depth, line=2)


def postprocessor_hook(data, depth=0):
    status = data.get("status") or ""
    processes = {"Merger": "Merge", "MoveFiles": "Move", "FixupM3u8": "Fixup"}
    postprocess = data.get("postprocessor") or ""
    filepart = ""
    if info := data.get("info_dict"):
        dur = util.time_formatted(*util.convert_seconds(int(info.get("duration") or 0)))
        upload_date = util.format_upload_date(info.get("upload_date") or "")
        format = util.get_format_string(info)
        cli.tree_print(f"{dur} {format} ({info.get('id')}) {upload_date}", index=depth - 1, line=1)
        filename = info.get("filename") or ""
        fnsplit = filename.split("/")
        if len(fnsplit) > 1:
            filepart = fnsplit[-1]
    cli.tree_print(f"{processes[postprocess]} {status}", index=depth, line=1)
    cli.tree_print(f"- {filepart} -", index=depth, line=2)


def _make_hooks(depth, rems):
    def _ph(d):
        if d:
            progress_hook(d, rems, depth)

    def _pph(d):
        if d:
            postprocessor_hook(d, depth)

    return _ph, _pph


def process_download(url_list, availability, depth=0):
    if availability == "public":
        availability = "Public"
    elif availability == "needs_auth":
        availability = "Authorization"
    elif availability is None:
        availability = "Unknown"
    cli.tree_print(f"{availability}", index=depth, line=1)
    logger = Logger()
    ydl_opts = dict(YDL_OPTS)
    ydl_opts["download_archive"] = f"{ARCHIVED_FILE}"
    ydl_opts["logger"] = logger
    rems = deque([int(time.time())] * MEDIAN_LENGTH, maxlen=MEDIAN_LENGTH)
    virt_progress_hook, virt_postprocessor_hook = _make_hooks(depth, rems)
    ydl_opts["progress_hooks"] = [virt_progress_hook]
    ydl_opts["postprocessor_hooks"] = [virt_postprocessor_hook]
    ydl_opts = cast("_Params", dict(ydl_opts))
    with YoutubeDL(ydl_opts) as ydl:
        ydl.download(url_list)
    errors = 0
    while logger.if_error():
        extractor, id, error_msg = logger.read_error()
        cli.status_line(f"({extractor}) {id} \033[91m{error_msg}\033[0m")
        errors += 1
    sleep_header(errors * 60)


def process_channel(ydl, channel, depth=0, index=0):
    info = ydl.extract_info(channel, download=False, process=False)
    if info:
        info_type = info.get("_type") or ""
        if info_type == "playlist":
            cli.tree_print(f"{info.get('channel')}", index=depth)
            cli.tree_print(f"{info.get('title')}", index=depth)
            if entries := list(info.get("entries")):
                cli.tree_print(f"{info.get('title')} ({len(entries)})", index=depth)
                for i, entry in enumerate(entries, start=1):
                    if entry and (entry_url := (entry.get("webpage_url") or entry.get("url"))):
                        process_channel(ydl, entry_url, depth + 1, i)
        elif info_type == "url":
            cli.tree_print(f"URL TODO: {info.get('title')}", index=depth)
        else:
            video_url = channel
            cli.tree_print(
                f"|{index:>4}| \033[1m{info.get('title')}\033[0m ({info.get('live_status')})", index=depth, line=0
            )
            formats = info.get("formats") or []
            upload_date = util.format_upload_date(info.get("upload_date") or "")
            dur = util.time_formatted(*util.convert_seconds(int(info.get("duration") or 0)))
            cli.tree_print(
                f"{dur} {util.get_best_format(formats)} ({info.get('id')}) {upload_date}",
                index=depth,
                line=1,
            )
            util.save_list_to_file(f"{info.get('id')}_formats", util.list_all_formats(formats), TEMP_DIRECTORY)
            upload_date = datetime.datetime.strptime(upload_date, "%Y-%m-%d").date()
            if not ACCEPT_VERTICAL and util.enumerate_is_vertical(formats):
                cli.tree_print("Vertical", index=depth + 1, line=1)
                util.add_video_id(f"{ARCHIVED_FILE}", f"{info.get('extractor')} {info.get('id')}")
            elif util.enumerate_is_low_resolution(formats, MINIMUM_RESOLUTION):
                cli.tree_print("Low resolution", index=depth + 1, line=1)
            elif util.enumerate_is_low_resolution(
                formats, 1900
            ) and upload_date >= datetime.date.today() - datetime.timedelta(days=2):
                cli.tree_print("Held for later due resolution", index=depth + 1, line=1)
            else:
                availability = info.get("availability")
                process_download([video_url], availability, depth + 1)
                # sleep
                output, duration = util.sleep_calc(min(int(info.get("duration") or 0) >> 1, random.randint(0, 1800)))
                if output:
                    sleep_header(duration)


def sleep_header(duration):
    end_time = time.time() + duration
    while (remaining := end_time - time.time()) > 0:
        hr, mn, sc = util.convert_seconds(int(remaining))
        if hr > 24:
            cli.header_print(f"Sleeping for {hr // 24} days, {hr % 24} hours", 2, color=CLIPrint.DIM_GRAY)
            sleep_time = sc or (mn * 60 if mn else 3600)
        elif hr > 8:
            cli.header_print(f"Sleeping for {hr} hours", 2, color=CLIPrint.TEAL)
            sleep_time = sc or (mn * 60 if mn else 3600)
        elif hr > 0 or mn > 0:
            cli.header_print(f"Sleeping for {hr:02}:{mn:02}", 2, color=CLIPrint.TEAL)
            sleep_time = sc or 60
        else:
            cli.header_print(f"{sc:02} s remaining", 2, color=CLIPrint.RED)
            sleep_time = 1
        time.sleep(min(sleep_time, remaining))
    cli.header_print("", 2, color=CLIPrint.DEFAULT)


def old_sleep_header(duration):
    while duration > 0:
        hr, mn, sc = util.convert_seconds(duration)
        if hr > 24:
            cli.header_print(f"Sleeping for {hr // 24} days, {hr % 24} hours", 2, color=CLIPrint.TEAL)
            time.sleep(sc)
            duration -= sc + 1
            if mn > 0:
                time.sleep(mn * 60)
                duration -= mn * 60 + 1
            else:
                time.sleep(3600)
                duration -= 3600 + 1
        elif hr > 8:
            cli.header_print(f"Sleeping for {hr} hours", 2, color=CLIPrint.TEAL)
            time.sleep(sc)
            duration -= sc + 1
            if mn > 0:
                time.sleep(mn * 60)
                duration -= mn * 60 + 1
            else:
                time.sleep(3600)
                duration -= 3600 + 1
        elif hr > 0 or mn > 0:
            cli.header_print(f"Sleeping for {hr:02}:{mn:02}", 2, color=CLIPrint.TEAL)
            if sc > 0:
                time.sleep(sc)
                duration -= sc + 1
            else:
                time.sleep(60)
                duration -= 60 + 1
        else:
            cli.header_print(f"{sc:02} s remaining", 2, color=CLIPrint.RED)
            time.sleep(1)
            duration -= 1
    cli.header_print("", 2, color=CLIPrint.DEFAULT)


def run_ytdlp():
    ret_status = 0
    # Parse the channels
    channels = []
    try:
        with open(f"{CHANNELS_FILE}", "r") as cf:
            channels = [line.strip() for line in cf if line.strip() and not line.startswith("#")]
    except FileNotFoundError:
        cli.status_line(f"Channel file {CHANNELS_FILE} not found")
    random.shuffle(channels)
    logger = Logger()
    ydl_opts = dict(YDL_OPTS)
    ydl_opts["logger"] = logger
    ydl_opts["download_archive"] = f"{ARCHIVED_FILE}"
    ydl_opts = cast("_Params", dict(ydl_opts))
    try:
        with YoutubeDL(ydl_opts) as ydl:
            for channel in channels:
                process_channel(ydl, channel, depth=0, index=0)
                errors = 0
                while logger.if_error():
                    extractor, id, error_msg = logger.read_error()
                    if id == channel:
                        cli.status_line(f"({extractor}) {channel} \033[91m{error_msg}\033[0m")
                    else:
                        cli.status_line(f"({extractor}) {channel} | \033[37m{id}\033[0m -> \033[91m{error_msg}\033[0m")
                    sleep_header(15)
                    errors += 1
                sleep_header(errors * 600)
    except SystemExit as e:
        cli.status_line(f"SystemExit {str(e)}")
        ret_status = -1
    except KeyboardInterrupt:
        cli.status_line("KeyboardInterrupt in run_ytdlp")
        ret_status = -1
    except BaseException as e:
        cli.status_line(f"BaseException {str(e)}")
        ret_status = -1
    return ret_status


def main():
    main_loop = True
    cli.cls()
    cli.cursor_off()
    cli.header_print(f"YT_DLP YTB {LOCAL_VERSION}", 1, color=CLIPrint.GREEN)
    shutil.rmtree(TEMP_DIRECTORY, ignore_errors=True)
    os.makedirs(TEMP_DIRECTORY, exist_ok=True)
    while main_loop:
        try:
            ret = run_ytdlp()
            time.sleep(5)
            if ret < 0:
                main_loop = False
        except KeyboardInterrupt:
            main_loop = False
            cli.status_line("KeyboardInterrupt in main")
    cli.cursor_on()
    cli.pass_cursor()


if __name__ == "__main__":
    main()
