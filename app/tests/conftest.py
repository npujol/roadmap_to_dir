import pytest

from app.main import RoadmapExtractor


@pytest.fixture()
def roadmap_extractor_fixture() -> RoadmapExtractor:
    return RoadmapExtractor()


@pytest.fixture()
def structure_fixture() -> dict[str, list[dict[str, list[str]]]]:
    return {
        "DevOps": [
            {
                "Learn a Programming Language": [
                    "Python",
                    "Ruby",
                    "Go",
                    "Rust",
                    "JavaScript / Node.js",
                ]
            }
        ]
    }
