from functools import cache
from pathlib import Path
from typing import Iterable

from src.pgm import PGMImage


@cache
def get_project_dir() -> Path:
    current_dir = Path(__file__)
    return current_dir.parent.parent


@cache
def get_data_dir() -> Path:
    return get_project_dir() / 'data'


def read_pgm_images() -> Iterable[PGMImage]:
    for path in get_data_dir().iterdir():
        if path.is_file() and path.suffix.endswith('pgm'):
            yield PGMImage.read(file_path=path)


def calculate_compression_rate(path_original: Path, path_modified: Path) -> float:
    original_size = path_original.stat().st_size
    modified_size = path_modified.stat().st_size
    compression_rate = modified_size / original_size
    return compression_rate
