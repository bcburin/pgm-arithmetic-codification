from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import TextIO


@dataclass
class PGMImage:
    max_value: int
    pixels: list[list[int]]
    size: tuple[int, int]
    path: Path | None = None

    @staticmethod
    def _read_line(f: TextIO):
        line = f.readline().strip()
        while line.startswith('#'):
            line = f.readline().strip()
        return line

    @classmethod
    def read(cls, file_path: Path) -> PGMImage:
        with open(file_path, 'r') as f:
            # assert file type
            file_type = cls._read_line(f)
            assert file_type == 'P2'
            # read header
            width, height, *max_val = map(int, cls._read_line(f).split())
            if len(max_val) >= 1:
                max_val = int(max_val[0])
            else:
                max_val = int(cls._read_line(f))
            assert 0 <= max_val < 65536
            # read pixels
            pixels = []
            for _ in range(height):
                row = [int(n) for n in cls._read_line(f).split()]
                while len(row) < width:
                    row.append(0)
                pixels.append(row)
            return PGMImage(max_val, pixels, (width, height), file_path)

    def write(self, file_path: Path):
        with open(file_path, 'w') as f:
            # Write the header
            f.write("P2\n")
            f.write(f"{self.size[0]} {self.size[1]}\n")
            f.write(f"{self.max_value}\n")
            # Write the pixel data
            for row in self.pixels:
                row_str = ' '.join(map(str, row))
                f.write(row_str + '\n')
