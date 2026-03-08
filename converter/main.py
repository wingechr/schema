import argparse
import json
from pathlib import Path
from typing import Callable

import networkx as nx

with (Path(__file__).parent.parent / "schema" / "base.schema.json").open("rb") as f:
    schema_base_id = json.load(f)["$id"]


class MetadataConverter:
    """import subclasses of this class to register them in the converter graph."""

    version_from = schema_base_id
    version_to = schema_base_id

    def __call__(self, metadata) -> dict:
        """convert metadata from version_from to version_to."""
        return metadata


class MetadataConverterGraph:
    @classmethod
    def get_all_subclasses(cls) -> set[type[MetadataConverter]]:
        """get all subclasses of this class."""
        subclasses = set()
        work = [MetadataConverter]
        while work:
            parent = work.pop()
            for child in parent.__subclasses__():
                if child not in subclasses:
                    subclasses.add(child)
                    work.append(child)
        return subclasses

    @classmethod
    def get_converter_graph(cls) -> nx.DiGraph:
        """get a graph of all converters."""
        graph = nx.DiGraph()
        for converter_class in cls.get_all_subclasses():
            graph.add_edge(
                converter_class.version_from,
                converter_class.version_to,
                converter=converter_class,
            )

        return graph

    def __init__(self) -> None:
        self.converter_graph = self.get_converter_graph()

    def get_converter_path(
        self, version_from: str, version_to: str
    ) -> list[type[MetadataConverter]]:
        """get a path of converters from version_from to version_to."""
        try:
            path = nx.shortest_path(self.converter_graph, version_from, version_to)
            return [
                self.converter_graph.edges[path[i], path[i + 1]]["converter"]
                for i in range(len(path) - 1)
            ]
        except nx.NetworkXNoPath:
            raise ValueError(f"No converter path from {version_from} to {version_to}")

    def get_converter(
        self, version_from: str, version_to: str
    ) -> Callable[[dict], dict]:
        """get a converter function from version_from to version_to."""
        converter_classes = self.get_converter_path(version_from, version_to)

        def converter(metadata: dict) -> dict:
            for converter_class in converter_classes:
                metadata = converter_class()(metadata)
            return metadata

        return converter


def convert_metadata(metadata: dict, version_to: str) -> dict:
    """convert metadata to version_to."""
    version_from = metadata["$schema"]
    converter_graph = MetadataConverterGraph()
    converter = converter_graph.get_converter(version_from, version_to)
    return converter(metadata)


def convert_metadata_inplace(metadata_filepath: str | Path, version_to: str) -> None:
    """convert metadata in place."""
    metadata_filepath = Path(metadata_filepath)
    with metadata_filepath.open("r") as f:
        metadata = json.load(f)

    converted_metadata = convert_metadata(metadata, version_to=version_to)

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

    # parse args
    kwargs = vars(ap.parse_args())

    convert_metadata_inplace(**kwargs)
