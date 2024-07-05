import logging
from pathlib import Path
from typing import Any

import pytest
from pytest_insta.fixture import SnapshotFixture

from app.main import RoadmapExtractor


@pytest.mark.vcr()
def test_download_roadmap_page(
    roadmap_extractor_fixture: RoadmapExtractor, snapshot: SnapshotFixture
) -> None:
    name = "devops"
    result: bytes = roadmap_extractor_fixture.download_roadmap_page(name=name)
    assert snapshot() == str(object=result)


@pytest.mark.vcr()
def test_download_roadmap_json(
    roadmap_extractor_fixture: RoadmapExtractor, snapshot: SnapshotFixture
) -> None:
    name = "devops"
    result: dict[Any, Any] = roadmap_extractor_fixture.download_roadmap_json(name=name)
    assert snapshot("json") == result


@pytest.mark.vcr()
def test_extract_topic_and_subtopics(
    roadmap_extractor_fixture: RoadmapExtractor, snapshot: SnapshotFixture
) -> None:
    result: dict[str, list[list[str]]] = (
        roadmap_extractor_fixture.extract_topic_and_subtopics(name="devops")
    )
    assert snapshot("json") == result


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

    assert snapshot("json") == content


@pytest.mark.vcr()
def test_handle(
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
            roadmap_name="devops",
            output_path=base_path,
        )
    assert snapshot("json") == caplog.text
