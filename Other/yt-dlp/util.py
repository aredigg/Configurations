import datetime
import os
import random
import time
from statistics import mean, median


def dict_print(data, indent=0):
    if not data:
        return
    if isinstance(data, dict):
        for key, value in data.items():
            if isinstance(value, list) or isinstance(value, dict):
                print(" " * indent + f"\033[36m- {key} - \033[39m\033[0K")
                dict_print(value, indent + 4)
            else:
                print(" " * indent + f"\033[36m- {key} - \033[39m{value}\033[0K")
    elif isinstance(data, list):
        for i, value in enumerate(data):
            if isinstance(value, list) or isinstance(value, dict):
                print(" " * indent + f"\033[34m- {i}: - \033[39m\033[0K")
                dict_print(value, indent + 4)
            else:
                print(" " * indent + f"\033[34m - \033[39m{value}\033[0K")
    else:
        print(" " * indent + f"\033[33m - \033[39m{data}\033[0K")


def dict_save(data, saved_list, indent=0):
    if not data:
        return
    if isinstance(data, dict):
        for key, value in data.items():
            if isinstance(value, list) or isinstance(value, dict):
                saved_list.append(" " * indent + f"\033[36m- {key} - \033[39m\033[0K\n")
                dict_save(value, saved_list, indent + 4)
            else:
                saved_list.append(" " * indent + f"\033[36m- {key} - \033[39m{value}\033[0K\n")
    elif isinstance(data, list):
        for i, value in enumerate(data):
            if isinstance(value, list) or isinstance(value, dict):
                saved_list.append(" " * indent + f"\033[34m- {i}: - \033[39m\033[0K\n")
                dict_save(value, saved_list, indent + 4)
            else:
                saved_list.append(" " * indent + f"\033[34m - \033[39m{value}\033[0K\n")
    else:
        saved_list.append(" " * indent + f"\033[33m - \033[39m{data}\033[0K\n")


def save_list_to_file(prefix, save_list, output_directory):
    os.makedirs(output_directory + "/save", exist_ok=True)
    filename = output_directory + f"/save/{prefix}_" + datetime.datetime.now().strftime("%Y-%m-%d_%H_%M_%S")
    with open(filename, "w") as output:
        output.writelines(save_list)


def enumerate_best_format(formats, extension="mp4"):
    previous_height = previous_fps = previous_asr = previous_audio_channels = 0
    current_best_format = None
    for format in formats:
        height = format.get("height") or 0
        fps = format.get("fps") or 0
        asr = format.get("asr") or 0
        audio_channels = format.get("audio_channels") or 0
        dr = format.get("dynamic_range") or "SDR"
        if (format.get("ext") or "") == extension:
            if (
                height > previous_height
                or fps > previous_fps
                or asr > previous_asr
                or audio_channels > previous_audio_channels
                or dr != "SDR"
            ):
                current_best_format = format
                if height > previous_height:
                    previous_height = height
                if fps > previous_fps:
                    previous_fps = fps
                if asr > previous_asr:
                    previous_asr = asr
                if audio_channels > previous_audio_channels:
                    previous_audio_channels = audio_channels
    return current_best_format


def get_best_format(formats):
    if format := enumerate_best_format(formats):
        return get_format_string(format)
    return "Unknown"


def list_all_formats(formats):
    format_list = []
    for format in formats:
        format_list.append(get_format_string(format))
    return format_list


def get_format_string(format):
    width = format.get("width") or 0
    height = format.get("height") or 0
    fps = format.get("fps") or 0
    asr = format.get("asr") or 0
    audio_channels = format.get("audio_channels") or 0
    dr = format.get("dynamic_range") or "SDR"
    vcodec = (format.get("vcodec") or "----")[:4]
    acodec = (format.get("acodec") or "----")[:4]
    ext = format.get("ext") or "Unk"
    return f"{width}x{height}@{fps} ({dr}) - {asr}/{audio_channels} - {vcodec}/{acodec} {ext}"


def get_best_resolution(formats):
    if format := enumerate_best_format(formats):
        width = format.get("width") or 0
        height = format.get("height") or 0
        bitrate = format.get("tbr") or format.get("vbr") or 0
        return f"{width:>4}x{height:<4}", str(bitrate).split(".")[0]
    return "[Unknown]", ""


def enumerate_is_vertical(formats):
    if format := enumerate_best_format(formats):
        width = format.get("width") or 0
        height = format.get("height") or 0
        return height > width
    return False


def enumerate_is_low_resolution(formats, min_resolution):
    height = 0
    if format := enumerate_best_format(formats):
        height = format.get("height") or 0
    return height < min_resolution


def convert_seconds(seconds, incl_sec=True):
    seconds = max(0, seconds)
    hr = int(seconds / 3600)
    mn = int((seconds / 60) % 60)
    sc = int(seconds % 60)
    if incl_sec:
        return hr, mn, sc
    if sc > 0:
        mn += 1
    return hr, mn % 60, 0


def time_formatted(hr, mn, sc):
    return f"{hr:02}:{mn:02}:{sc:02}"


def time_formatted_short(hr, mn, sc=0):
    return f"{hr:02}:{mn:02}"


def convert_to_time(seconds=0):
    eta = datetime.datetime.now() + datetime.timedelta(seconds=seconds)
    return eta.hour, eta.minute, eta.second


def format_upload_date(upload_date):
    if len(upload_date) != 8:
        return f"{upload_date}"
    return f"{upload_date[:4]}-{upload_date[4:6]}-{upload_date[6:8]}"


def add_video_id(archive_file, video_id):
    with open(archive_file, "a", encoding="utf-8") as f:
        if video_id and not video_id.endswith("\n"):
            video_id += "\n"
        f.write(video_id)


def sleep_now(duration):
    time.sleep(duration)


def sleep_calc(duration):
    if duration <= 0:
        return "", 0
    duration += random.randrange(duration)
    sleep_time = time_formatted(*convert_seconds(duration))
    eta = datetime.datetime.now() + datetime.timedelta(seconds=duration)
    if duration < 1800:
        return f"Sleeping for {sleep_time}", duration
    return f"Sleeping for {sleep_time}, waking at {eta.strftime('%d %H:%M:%S (%A)')}", duration


def trim_mean(samples, trim=0.05):
    if not samples:
        return 0
    sorted_samples = sorted(samples)
    trim_count = int(len(samples) * trim)
    if trim_count > 0:
        trimmed = sorted_samples[trim_count:-trim_count]
        return mean(trimmed) if trimmed else mean(sorted_samples)
    return mean(sorted_samples)


def exp_mean(samples, factor=0.05):
    it = iter(samples)
    try:
        ema = next(it)
    except StopIteration:
        return 0
    a = factor
    b = 1 - a
    for x in it:
        ema = a * x + b * ema
    return ema


def mw_median(samples):
    samples_list = list(samples)
    windows = [
        mean(samples_list[-25:]),
        mean(samples_list[-50:]),
        mean(samples_list[-100:]),
        mean(samples_list[-200:]),
        mean(samples_list[-500:]),
        mean(samples_list),
    ]
    return median(windows)


def mw_mean(samples):
    samples_list = list(samples)
    windows = [
        median(samples_list[-25:]),
        median(samples_list[-50:]),
        median(samples_list[-100:]),
        median(samples_list[-200:]),
        median(samples_list[-500:]),
        median(samples_list),
    ]
    return mean(windows)


def normal_mean(samples):
    return mean(samples)
