import pathlib
import json


def write_cache(cache_path: pathlib.Path, data: dict, overwrite: bool = False) -> None:
    if cache_path.is_file() and not overwrite:
        print(f"Data has already been cached ({cache_path})")
        return

    with open(cache_path, "w") as f:
        json.dump(data, f)


def read_cache(cache_path: pathlib.Path) -> dict:
    if not cache_path.is_file():
        raise FileNotFoundError(f"Cannot find '{cache_path}'")

    with open(cache_path) as f:
        return json.load(f)
