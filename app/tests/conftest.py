from typing import Any

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
                    ("Python", "https://roadmap.sh/python/python-basics/basic-syntax"),
                    ("Ruby", "https://roadmap.sh/python/python-basics/basic-syntax"),
                    ("Go", "https://roadmap.sh/python/python-basics/basic-syntax"),
                    ("Rust", "https://roadmap.sh/python/python-basics/basic-syntax"),
                    (
                        "JavaScript / Node.js",
                        "https://roadmap.sh/python/python-basics/basic-syntax",
                    ),
                ]
            }
        ]
    }


@pytest.fixture()
def roadmap_extract_content_url() -> tuple[dict[str, Any], str]:
    return {
        "id": "npnMwSDEK2aLGgnuZZ4dO",
        "type": "subtopic",
        "position": {"x": 2039.941514522558, "y": 229.3007298193524},
        "selected": False,
        "data": {
            "label": "Go",
            "style": {
                "fontSize": 17,
                "justifyContent": "flex-start",
                "textAlign": "center",
            },
            "oldId": "QCdemtWa2mE78poNXeqzr",
            "legend": {
                "id": "RkcQf9vafpvjAVpo02XhQ",
                "color": "#2b78e4",
                "label": "Personal Recommendation / Opinion",
                "position": "left-center",
            },
        },
        "zIndex": 999,
        "width": 107,
        "height": 49,
        "positionAbsolute": {"x": 2039.941514522558, "y": 229.3007298193524},
        "dragging": False,
        "style": {"width": 107, "height": 49},
        "resizing": False,
        "selectable": True,
        "focusable": True,
    }, "https://roadmap.sh/devops/go@npnMwSDEK2aLGgnuZZ4dO"


@pytest.fixture()
def subroadmap_extract_content_url() -> tuple[dict[str, Any], str]:
    return {
        "ID": "917",
        "typeID": "__group__",
        "zOrder": "36",
        "measuredW": "222",
        "measuredH": "42",
        "w": "222",
        "h": "42",
        "x": "359",
        "y": "422",
        "properties": {"controlName": "100-python-basics:basic-syntax"},
    }, "https://roadmap.sh/python/python-basics/typecasting-exceptions"
