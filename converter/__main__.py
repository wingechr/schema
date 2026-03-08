import argparse
import json
from pathlib import Path

from . import MetadataConverterGraph


def convert_metadata_inplace(metadata_filepath: str | Path, version_to: str) -> None:
    """convert metadata in place."""
    graph = MetadataConverterGraph()

    metadata_filepath = Path(metadata_filepath)
    with metadata_filepath.open("r") as f:
        metadata = json.load(f)

    converted_metadata = graph.convert_metadata(metadata, version_to=version_to)

    with metadata_filepath.open("w") as f:
        json.dump(converted_metadata, f, indent=2)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "metadata_filepath", type=str, help="path to the metadata file to convert"
    )
    ap.add_argument(
        "version_to", type=str, help="the version to convert the metadata to"
    )
    kwargs = vars(ap.parse_args())

    convert_metadata_inplace(**kwargs)
