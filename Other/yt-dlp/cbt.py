from __future__ import annotations

import copy
import datetime
import multiprocessing
import os
import queue
import shutil
import signal
import time
from typing import TYPE_CHECKING, Any, Mapping, cast

from yt_dlp import YoutubeDL
from yt_dlp.utils import RejectedVideoReached

import util
from cli_print_v2 import ANSI, CLIPrint
from logger import Logger

LOCAL_VERSION = "2.17"
OUTPUT_DIRECTORY = "/Volumes/Delt/Prosjekter/yt-dlp/.cbtv2"
TEMP_DIRECTORY = "/Volumes/Ekstern/.cbttemp"
CLI_LOGGER = None

MINIMUM_RESOLUTION = 1000

CHANNELS_FILE = f"{OUTPUT_DIRECTORY}/channels"
CHANNELS_PREFIX = f"{OUTPUT_DIRECTORY}/channel_prefix"
YDL_OPTS = {
    "ignoreerrors": True,
    "live_from_start": False,
    "multistreams": True,
    "retries": 5,
    "sleep_interval": 10,
    "max_sleep_interval": 60,
    "sleep_interval_requests": 0.01,
    "paths": {
        "temp": f"{TEMP_DIRECTORY}/temp",
        "home": f"{OUTPUT_DIRECTORY}/home",
    },
    "cookiesfrombrowser": ("safari", None, None, None),
    "outtmpl": "%(epoch>%Y-%m)s/%(epoch>W%W)s/%(epoch>%a)s/%(id)s.%(ext)s",
    "writesubtitles": True,
    "writeautomaticsub": False,
    "subtitleslangs": ["all"],
    "writedescription": False,
    "writeinfojson": False,
    "hls_prefer_native": True,
    "external_downloader_args": {"ffmpeg": ["-loglevel", "quiet", "-hide_banner", "-nostats"]},
    "downloader_args": {
        "ffmpeg": ["-loglevel", "quiet", "-hide_banner", "-nostats"],
        "ffmpeg_i": ["-rw_timeout", "30000000"],
    },
    "postprocessor_args": {"ffmpeg": ["-loglevel", "error", "-hide_banner", "-nostats"]},
}
MIN_DURATION = 300
MAX_SLOTS = 4
MAX_HEADERS = 3
DEBUG = False
OFFLINE_WINDOW = 60

cli = CLIPrint(MAX_SLOTS, MAX_HEADERS, CLI_LOGGER, DEBUG)
cli_queue = multiprocessing.Queue()

if TYPE_CHECKING:
    from yt_dlp import _Params as YDLParams


class _Params(dict[str, Any]):
    """
    Dict-compatible params wrapper with dot-access and deep copy on init.
    Safe to pass to yt-dlp (behaves like a dict).
    """

    def __init__(self, data: Mapping[str, Any] | None = None, **kwargs: Any) -> None:
        base = copy.deepcopy(dict(data or {}))
        base.update(kwargs)
        super().__init__(base)
        # Recursively wrap nested dicts so dot-access works everywhere
        for k, v in list(self.items()):
            dict.__setitem__(self, k, self._wrap(v))

    @classmethod
    def _wrap(cls, v: Any) -> Any:
        if isinstance(v, dict) and not isinstance(v, _Params):
            return _Params(v)
        if isinstance(v, list):
            return [cls._wrap(x) for x in v]
        return v

    def __getattr__(self, name: str) -> Any:
        try:
            return self[name]
        except KeyError as e:
            raise AttributeError(name) from e

    def __setattr__(self, name: str, value: Any) -> None:
        # Keep normal attributes for internals
        if name.startswith("_"):
            # Use object.__setattr__ to avoid recursion
            object.__setattr__(self, name, value)
            return
        # Assign into dict and wrap nested dicts/lists
        dict.__setitem__(self, name, self._wrap(value))
        return  # Explicit None for type checkers

    def __delattr__(self, name: str) -> None:
        if name.startswith("_"):
            object.__delattr__(self, name)
            return
        del self[name]
        return

    def copy(self) -> "_Params":
        # Return the same type, deeply isolated from this instance
        return _Params(copy.deepcopy(dict(self)))


def run_ytdlp():
    ret_status = 0
    # Parse the channels
    channels = []
    channels_prefix = ""
    try:
        with open(f"{CHANNELS_FILE}", "r") as afile:
            channels = [line.strip() for line in afile if line.strip() and not line.startswith("#")]
        if len(channels) > len(set(channels)):
            # Remove duplicates
            temp_channels = []
            for channel in channels:
                if channel not in temp_channels:
                    temp_channels.append(channel)
            with open(f"{CHANNELS_FILE}", "w") as afile:
                for channel in temp_channels:
                    afile.write(f"{channel}\n")
            channels = temp_channels
        with open(f"{CHANNELS_PREFIX}", "r") as afile:
            channels_prefix = afile.readline().strip()
    except FileNotFoundError:
        cli.status_line("Channel files not found")
    # create a logger for yt-dlp
    logger = Logger()
    # set up yt-dlp
    ydl_opts = _Params(YDL_OPTS)
    ydl_opts["logger"] = logger
    ydl_opts["progress_hooks"] = [progress_hook]
    ydl_opts["postprocessor_hooks"] = [postprocessor_hook]
    # initialize slots
    slots = [{} for _ in range(MAX_SLOTS)]
    postprocess_lock = multiprocessing.RLock()
    # set up terminal
    for n in range(MAX_SLOTS):
        cli.slot_print((ANSI.Default + "○" + ANSI.Reset, "", ""), n)
    # try channels
    ydl_opts = cast("YDLParams", dict(ydl_opts))
    offline_channels = {}
    running = True
    try:
        with YoutubeDL(ydl_opts) as ydl:
            while running:
                # date limits
                previous_date = datetime.datetime.now(datetime.timezone.utc).date()
                finished_channels = []
                while previous_date == datetime.datetime.now(datetime.timezone.utc).date():
                    for minimum_resolution in [int(MINIMUM_RESOLUTION * 1.4)] + [MINIMUM_RESOLUTION] * 10:
                        while all(slot for slot in slots):
                            _wait_for_slot(slots)
                        for counter, channel in enumerate(channels, start=1):
                            color = ""
                            if counter < 25:
                                color = ANSI.color("D4AF37") + ANSI.Bold
                            elif counter < 50:
                                color = ANSI.color("8C8C96") + ANSI.Bold
                            elif counter < 100:
                                color = ANSI.color("F09CBB") + ANSI.Bold
                            elif counter < 200:
                                color = ANSI.color("89CFF0") + ANSI.Bold
                            cli.header_print(f"{previous_date} {color}{counter:>3}\033[0m/{len(channels)}", 1)
                            if channel in finished_channels:
                                cli.status_line(f"{ANSI.Bold}{channel}{ANSI.ResetBold} skipped")
                                continue
                            if channel in offline_channels:
                                if (remaining := (offline_channels[channel] - time.time()) / 60) > 0:
                                    cli.status_line(
                                        f"{ANSI.Bold}{channel}{ANSI.ResetBold} {remaining:.0f} minutes until retry"
                                    )
                                    continue
                            if all(slot for slot in slots):
                                # Skip all remaining channels while we wait for slot
                                continue
                            if info := ydl.extract_info(channels_prefix + channel, download=False, process=False):
                                slot_index = next(i for i, slot in enumerate(slots) if not slot)
                                if slot_index is not None:
                                    formats = info.get("formats") or []
                                    cli.status_line(
                                        f"{ANSI.Bold}{channel}{ANSI.ResetBold} {util.get_best_format(formats)}"
                                    )
                                    if check_slots(channel, slots):
                                        cli.status_line(f"{ANSI.Bold}{channel}{ANSI.ResetBold} active")
                                    elif not util.enumerate_is_low_resolution(formats, minimum_resolution):
                                        res = util.get_best_resolution(formats)
                                        if previous_date == datetime.datetime.now(datetime.timezone.utc).date():
                                            cli.slot_print(
                                                (ANSI.Blink + "●" + ANSI.ResetBlink, res, color + channel + ANSI.Reset),
                                                slot_index,
                                            )
                                        else:
                                            cli.slot_print(
                                                (
                                                    ANSI.BrBlue + "●" + ANSI.Reset,
                                                    res,
                                                    color + channel + ANSI.Reset,
                                                ),
                                                slot_index,
                                            )
                                        p, q = download_manager(channels_prefix, channel, slot_index, postprocess_lock)
                                        slots[slot_index] = {"process": p, "queue": q, "channel": channel}
                                        finished_channels.append(channel)
                                    elif util.enumerate_is_low_resolution(formats, MINIMUM_RESOLUTION):
                                        finished_channels.append(channel)
                                        cli.status_line(
                                            f"{ANSI.Bold}{channel}{ANSI.ResetBold} Resolution < {MINIMUM_RESOLUTION}"
                                        )
                                    else:
                                        cli.status_line(
                                            f"{ANSI.Bold}{channel}{ANSI.ResetBold} Resolution < {minimum_resolution}"
                                        )
                            else:
                                offline_channels[channel] = time.time() + OFFLINE_WINDOW * 60
                            while logger.if_error():
                                _, id, error_msg = logger.read_error()
                                if id == channel:
                                    cli.status_line(f"{ANSI.Bold}{channel}{ANSI.ResetBold} {error_msg}")
                                else:
                                    cli.status_line(f"{ANSI.Bold}{channel}{ANSI.ResetBold} | {id} {error_msg}")
                            if DEBUG:
                                dmsg = []
                                while logger.count() > 0:
                                    dmsg.append(logger.read())
                                # cli.debug_print(dmsg)
                            else:
                                logger.flush()
                            _poll_workers(slots)
                        time.sleep(5)
                        for i, slot in enumerate(slots):
                            if not slot:
                                cli.slot_print(
                                    (ANSI.Default + "○" + ANSI.Reset, "", ""),
                                    i,
                                )
                    cli.header_print(f"{previous_date}", 1)
    except SystemExit as e:
        cli.status_line(f"SystemExit {str(e)}")
        ret_status = -1
    except KeyboardInterrupt:
        cli.status_line("KeyboardInterrupt")
        _shutdown_slots(slots)
        ret_status = -1
    except BaseException as e:
        cli.status_line(f"BaseException {str(e)}")
        ret_status = -1
    _shutdown_slots(slots)
    while any(slot for slot in slots):
        time.sleep(5.0)
        try:
            if not _poll_workers(slots):
                cli.status_line("Waiting for slots to shutdown")
                time.sleep(5.0)
        except KeyboardInterrupt:
            return ret_status
    return ret_status


def check_slots(channel, slots):
    for slot in slots:
        if slot and slot["channel"] == channel:
            return True
    return False


def download_manager(channels_prefix, channel, slot_index, lock):
    assert slot_index < MAX_SLOTS, f"Slots over limit {slot_index}"
    q = multiprocessing.Queue()
    p = multiprocessing.Process(
        target=_download_worker, args=(channels_prefix, channel, slot_index, q, lock), daemon=True
    )
    p.start()
    return p, q


def _download_worker(channels_prefix, channel, slot_index, queue, lock):
    try:
        ydl_opts = _Params(YDL_OPTS)
        ydl_opts["logger"] = Logger()
        slot_progress_hook, slot_postprocessor_hook = _make_slot_hooks(slot_index, lock, cli_queue)
        ydl_opts["progress_hooks"] = [slot_progress_hook]
        ydl_opts["postprocessor_hooks"] = [slot_postprocessor_hook]
        ydl_opts = cast("YDLParams", dict(ydl_opts))
        with YoutubeDL(ydl_opts) as ydl:
            result = ydl.download([channels_prefix + channel])
            queue.put(("done", result))
    except Exception as e:
        queue.put(("error", str(e)))
    finally:
        cli_queue.put(("status_line", (f"Slot {slot_index + 1} releasing lock",), {}))
        try:
            lock.release()
            cli_queue.put(("status_line", (f"Slot {slot_index + 1} lock released",), {}))
        except AssertionError:
            cli_queue.put(("status_line", (f"Slot {slot_index + 1} lock not owned",), {}))
        except ValueError:
            pass


def _make_slot_hooks(slot_index, lock, cli_q):
    def _ph(d):
        if d:
            common_hook("progress", d, slot_index=slot_index, cli_queue=cli_q)
            if d.get("status") == "finished":
                cli_q.put(("status_line", (f"Slot {slot_index + 1} acquiring lock",), {}))
                lock.acquire()
                cli_q.put(("status_line", (f"Slot {slot_index + 1} lock acquired",), {}))

    def _pph(d):
        if d:
            common_hook("postprocessor", d, slot_index=slot_index, cli_queue=cli_q)

    return _ph, _pph


def _poll_workers(slots):
    cli.header_print(datetime.datetime.now().strftime("%H:%M"), 2)
    process_cli_messages()
    state_changed = False
    for i, slot in enumerate(list(slots)):
        if slot:
            p, q, c = slot["process"], slot["queue"], slot["channel"]
            draining = True
            while draining:
                try:
                    msg = q.get(timeout=0.1)
                    if isinstance(msg, tuple) and msg and msg[0] in ("done", "error"):
                        key, value = msg
                        if key == "done":
                            cli.slot_print((ANSI.Default + "○" + ANSI.Reset, "", c), i)
                            cli.status_line(f"{c} Done: {value}")
                        else:
                            cli.slot_print(
                                (ANSI.Default + "○" + ANSI.Reset, "", f"{c} Error: {ANSI.Red}{value}{ANSI.Reset}"), i
                            )
                            cli.status_line(f"{c} Error: {value}")
                        state_changed = True
                except Exception:
                    draining = False
            if not p.is_alive():
                p.join(timeout=1.0)
                if q:
                    try:
                        q.close()
                        q.join_thread()
                    except Exception:
                        pass
                slots[i] = {}
    return state_changed


def _wait_for_slot(slots):
    cli.status_line("Waiting for free slots")
    interval = 0.1
    while all(slot for slot in slots):
        if _poll_workers(slots):
            return
        time.sleep(interval)
        interval = min(5.0, interval * 1.5)


def _shutdown_slots(slots):
    for slot in slots:
        if slot:
            cli.status_line(f"Slot(s) shutdown: {slot['channel']}")
            p = slot.get("process")
            q = slot.get("queue")
            if p and p.is_alive():
                cli.status_line("Slot process")
                try:
                    pgid = os.getpgid(p.pid)
                    cli.status_line(f"Slot process send SIGINT -> {pgid}")
                    os.killpg(pgid, signal.SIGINT)
                except ProcessLookupError:
                    cli.status_line("ProcessLookupError")
                except Exception as e:
                    cli.status_line(f"Exception {str(e)}")
            if q:
                try:
                    while not q.empty():
                        try:
                            q.get_nowait()
                        except Exception:
                            break
                    q.close()
                    q.join_thread()
                except Exception as e:
                    cli.status_line(f"Error closing queue: {e}")


def process_cli_messages(timeout=0.01):
    try:
        while True:
            msg = cli_queue.get(timeout=timeout)
            if msg is None:  # Shutdown signal
                break
            cmd, args, kwargs = msg
            if cmd == "slot_print":
                cli.slot_print(*args, **kwargs)
            elif cmd == "status_line":
                cli.status_line(*args, **kwargs)
            elif cmd == "header_print":
                cli.header_print(*args, **kwargs)
            elif cmd == "tree_print":
                cli.tree_print(*args, **kwargs)
    except queue.Empty:
        pass


def progress_hook(data):
    if not data:
        cli.status_line("Empty progress_hook data")
    else:
        common_hook("progress", data)


def postprocessor_hook(data):
    if not data:
        cli.status_line("Empty postprocessor_hook data")
    else:
        common_hook("postprocessor", data)


def common_hook(hook, data, slot_index=None, cli_queue=None):
    processes = {"Merger": "merging", "MoveFiles": "moving", "FixupM3u8": "adjusting", "": "Unknown"}
    output = ""
    slot_output = (ANSI.Default + "●" + ANSI.Reset, "", "")
    # save data struct to a file
    if DEBUG:
        save_list = []
        util.dict_save(data, save_list)
        util.save_list_to_file(hook, save_list, TEMP_DIRECTORY)
    #
    status = data.get("status")
    if not status:
        return
    title = ""
    id = ""
    resolution = ""
    elapsed = int(data.get("elapsed") or 0)
    total_bytes = int(data.get("total_bytes") or 0)
    if info := data.get("info_dict"):
        id = info.get("id") or ""
        title = info.get("title") or id
        width = int(info.get("width") or 0)
        height = int(info.get("height") or 0)
        fps = info.get("fps") or 0
        tbr = info.get("tbr") or 0
        ar = info.get("aspect_ratio") or 0.0
        dr = info.get("dynamic_range") or "SDR"
        vcodec = (info.get("vcodec") or "----")[:4]
        acodec = (info.get("acodec") or "----")[:4]
        if width > 0 and height > 0:
            resolution = f"{width:4}x{height:4}"
        ext = info.get("ext") or ""
        filename = info.get("filename") or ""
        from_filepath = info.get("filepath") or ""
        finaldir = info.get("__finaldir") or ""
        output += f"{title} {fps} {tbr} {ar} {dr} {vcodec} {acodec} {ext} {filename} {from_filepath} {finaldir}"
    if hook == "progress":
        if status == "finished":
            if 0 < elapsed < MIN_DURATION:
                # fixme, need to find the proper filenames before move
                filename = info.get("filename") or data.get("filename")
                if filename and os.path.exists(filename):
                    try:
                        os.remove(filename)
                    except Exception:
                        cli.status_line(f"Error during remove: {filename}")
                else:
                    cli.status_line(f"Error with file: {filename}")
                cli.status_line(f"{title} rejected: {elapsed} s < {MIN_DURATION} s")
                if slot_index:
                    cli.slot_print((ANSI.Default + "●" + ANSI.Reset, resolution, f"{id} rejected"), slot_index)
                raise RejectedVideoReached(f"Duration {elapsed} s too short")
        tf = util.time_formatted(*util.convert_seconds(elapsed))
        output = (
            f"{resolution:9} {ANSI.Bold}{id:20}{ANSI.ResetBold} | {status} download, {int(total_bytes >> 20)} MB {tf}"
        )
        slot_output = (
            ANSI.Default + "●" + ANSI.Reset,
            resolution,
            f"{id}, {status} download, {int(total_bytes >> 20)} MB {tf}",
        )
    elif hook == "postprocessor":
        post_status = data.get("postprocessor") or ""
        output = f"{resolution:9} {id:20} | {processes[post_status]} {status}"
        slot_output = ANSI.Default + "●" + ANSI.Reset, resolution, f"{id}, {processes[post_status]} {status}"
    if slot_index is not None and cli_queue is not None:
        cli_queue.put(("slot_print", (slot_output, slot_index), {}))
    elif cli_queue is not None:
        cli_queue.put(("status_line", (output,), {}))
    elif slot_index is not None:
        cli.slot_print(slot_output, slot_index)
    else:
        cli.status_line(output)


def main():
    main_loop = True
    cli.cls()
    cli.header_print(f"YT_DLP CBT {LOCAL_VERSION}", 0, color=ANSI.Green)
    os.makedirs(OUTPUT_DIRECTORY, exist_ok=True)
    shutil.rmtree(TEMP_DIRECTORY, ignore_errors=True)
    os.makedirs(TEMP_DIRECTORY, exist_ok=True)
    while main_loop:
        try:
            ret = run_ytdlp()
            if ret < 0:
                main_loop = False
        except KeyboardInterrupt:
            main_loop = False
            cli.status_line("KeyboardInterrupt")


if __name__ == "__main__":
    main()
