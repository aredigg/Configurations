#!/usr/bin/python3
import json
import struct
import sys
from pathlib import Path


class MPEGParser:
    def __init__(self, filename):
        self._path = Path(filename)
        self._exists = self._path.exists() and self._path.is_file()
        self._fp = None
        self._tree = None

    def _iterate_boxes(self, b, e):
        pos = b
        if self._fp:
            while pos + 8 <= e:
                self._fp.seek(pos)
                header = self._fp.read(8)
                if len(header) < 8:
                    break
                header_size = 8
                uuid_usertype = None
                size, type_bytes = struct.unpack(">I4s", header)
                typ = type_bytes.decode("latin-1")
                if size == 1:
                    if pos + 16 > e:
                        break
                    size = struct.unpack(">Q", self._fp.read(8))[0]
                    header_size = 16
                elif size == 0:
                    size = e - pos
                if typ == "uuid":
                    if pos + header_size + 16 > e:
                        break
                    uuid_usertype = self._fp.read(16).hex()
                    header_size += 16
                if size < header_size or pos + size > e:
                    break
                yield {
                    "type": typ,
                    "start": pos,
                    "size": size,
                    "header_size": header_size,
                    "data_start": pos + header_size,
                    "data_size": size - header_size,
                    "uuid": uuid_usertype,
                }
                pos += size

    def _iterate_tree(self, b, e, parent):
        nodes = []
        for box in self._iterate_boxes(b, e):
            node = {
                "type": box["type"],
                "start": box["start"],
                "size": box["size"],
                "header_size": box["header_size"],
                "data_size": box["data_size"],
            }
            if box["uuid"] is not None:
                node["uuid"] = box["uuid"]
            if box["type"] in (
                "moov",
                "udta",
                "ilst",
                "----",
                "trak",
                "mdia",
                "minf",
                "dinf",
                "dref",
                "stbl",
                "stsd",
                "sgpd",
                "sbgp",
                "mp4a",
                "esds",
                "avc1",
                "edts",
                "elst",
                "meta",
            ) or (parent and parent[-1] == "ilst"):
                child_start = box["data_start"]
                if box["type"] == "meta":
                    child_start += 4
                child_end = box["data_start"] + box["data_size"]
                if child_start < child_end:
                    children = self._iterate_tree(child_start, child_end, parent + [box["type"]])
                    if children:
                        node["children"] = children
            else:
                print("-" + box["type"])
            nodes.append(node)
        return nodes

    def exists(self):
        return self._exists

    def analyze(self):
        if not self._exists:
            return False
        if self._exists:
            _sz = self._path.stat().st_size
            with self._path.open(mode="rb") as self._fp:
                self._tree = self._iterate_tree(0, _sz, [])
            self._fp = None

    def output(self):
        print(json.dumps(self._tree, indent=2, ensure_ascii=False))


def main(argv):
    if len(argv) < 2:
        run_module = argv[0].split("/")[-1:][0]
        print(f"Usage: {run_module} <file1> [file2 …]")
        return 2
    for media_file_name in argv[1:]:
        print(media_file_name)
        parser = MPEGParser(media_file_name)
        parser.analyze()
        parser.output()
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
