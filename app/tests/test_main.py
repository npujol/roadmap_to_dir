import logging
from pathlib import Path
from typing import Any

import pytest
from pytest_insta.fixture import SnapshotFixture

from app.main import RoadmapExtractor
from app.serializers import Roadmap, SubRoadmap


@pytest.mark.vcr()
def test_download_roadmap_page(
    roadmap_extractor_fixture: RoadmapExtractor, snapshot: SnapshotFixture
) -> None:
    name = "devops"
    result: bytes = roadmap_extractor_fixture.download_roadmap_page(name=name)
    assert snapshot() == str(object=result)


@pytest.mark.vcr()
@pytest.mark.parametrize("roadmap_name", ["devops", "python", "docker"])
def test_get_roadmap(
    roadmap_name: str,
    roadmap_extractor_fixture: RoadmapExtractor,
    snapshot: SnapshotFixture,
) -> None:
    result: Roadmap | SubRoadmap = roadmap_extractor_fixture.get_roadmap(
        name=roadmap_name
    )
    assert snapshot(f"{roadmap_name}.json") == result.model_dump(mode="json")


def test_directory_structure(
    roadmap_extractor_fixture: RoadmapExtractor,
    structure_fixture: dict[str, list[dict[str, list[str]]]],
    tmp_path: Path,
    snapshot: SnapshotFixture,
) -> None:
    """Test if directories are created correctly."""
    base_path: Path = tmp_path / "test_directory_structure"
    base_path.mkdir(exist_ok=True)
    assert base_path.exists()

    roadmap_extractor_fixture.create_structure(
        data=structure_fixture, base_path=base_path
    )
    assert (base_path / "DevOps").is_dir()
    assert (base_path / "DevOps" / "Learn-a-Programming-Language").is_dir()
    md_file_path: Path = (
        base_path
        / "DevOps"
        / "Learn-a-Programming-Language"
        / "Learn-a-Programming-Language.md"
    )

    assert md_file_path.is_file()

    with open(file=md_file_path, mode="r") as file:
        content: str = file.read()

    assert snapshot() == content


@pytest.mark.vcr()
@pytest.mark.parametrize("roadmap_name", ["devops", "python", "docker"])
def test_handle(
    roadmap_name: str,
    roadmap_extractor_fixture: RoadmapExtractor,
    tmp_path: Path,
    snapshot: SnapshotFixture,
    caplog: Any,
) -> None:
    base_path: Path = tmp_path / "test_handle"
    base_path.mkdir(exist_ok=True)
    assert base_path.exists()
    with caplog.at_level(logging.INFO):
        roadmap_extractor_fixture.handle(
            roadmap_name=roadmap_name,
            output_path=base_path,
        )
    assert snapshot(f"{roadmap_name}.txt") == caplog.text
