import logging
from abc import abstractmethod
from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel

from app.string_processors import clean_url_strings

logger: logging.Logger = logging.getLogger(name=__name__.split(sep=".")[-1])


class RoadmapBaseModel(BaseModel):
    @abstractmethod
    def extract_topic_and_subtopics(self, roadmap_name: str) -> dict[str, list[Any]]:
        pass


class RoadmapType(Enum):
    SUBROADMAP = "subroadmap"
    ROADMAP = "roadmap"


class Properties(BaseModel):
    controlName: Optional[str] = None


class Properties1(BaseModel):
    text: Optional[str] = None


class ControlItem1(BaseModel):
    ID: Optional[str] = None
    typeID: Optional[str] = None
    properties: Optional[Properties1] = None


class Controls1(BaseModel):
    control: Optional[list[ControlItem1]] = None


class Children(BaseModel):
    controls: Optional[Controls1] = None


class ControlItem(BaseModel):
    ID: Optional[str] = None
    typeID: Optional[str] = None
    properties: Optional[Properties] = None
    children: Optional[Children] = None


class Controls(BaseModel):
    control: Optional[list[ControlItem]] = None


class Mockup(BaseModel):
    controls: Optional[Controls] = None


class SubRoadmap(BaseModel):
    mockup: Mockup

    def extract_topic_and_subtopics(
        self, roadmap_name: str
    ) -> dict[str, list[tuple[str, str]]]:
        result: dict[str, list[Any]] = {}
        if self.mockup.controls is None or self.mockup.controls.control is None:
            return result

        nodes: list[ControlItem] = self.mockup.controls.control
        current_topic: Optional[str] = None
        current_subtopics: dict[str, list[tuple[str, str]]] = {}
        for node in nodes:
            if node.typeID == "__group__":
                if node.properties is None:
                    continue
                control_name: str | None = node.properties.controlName
                # Exclude reference to other roadmaps
                if control_name is None or "roadmap.sh" in control_name:
                    continue

                control_name_parts: list[str] = control_name.split(sep=":")
                # Topic example: 100-python-package-managers
                # Subtopic example: 100-python-package-managers:pypi
                topic_parts = control_name_parts[0].split(sep="-")
                current_topic = topic_parts[-1]
                if current_topic == "roadmap":
                    continue
                if current_topic not in current_subtopics.keys():
                    current_subtopics[current_topic] = []
                if len(control_name_parts) == 2:
                    subtopic = control_name_parts[1]
                    complete_name_subtopic = "-".join(topic_parts[1:])
                    current_subtopics[current_topic].append(
                        (
                            subtopic,
                            f"https://roadmap.sh/{roadmap_name}/{clean_url_strings(complete_name_subtopic)}/{clean_url_strings(subtopic)}",
                        ),
                    )
        logger.info(msg=f"Adding {roadmap_name=}")
        result[roadmap_name] = []

        for topic, subtopics in current_subtopics.items():
            logger.info(msg=f"Adding {topic=}.")
            result[roadmap_name].append(
                {
                    topic: {
                        "subtopics": subtopics,
                        "content_url": f"https://roadmap.sh/{roadmap_name}/{clean_url_strings(topic)}",
                    }
                }
            )
        return result


class Data(BaseModel):
    label: str


class Node(BaseModel):
    id: str
    type: str
    selected: Optional[bool] = None
    data: Data


class Roadmap(BaseModel):
    nodes: list[Node]

    def extract_topic_and_subtopics(self, roadmap_name: str) -> dict[str, list[Any]]:
        current_subtopics: list[tuple[str, str]] = []
        current_topic: Optional[str] = None
        result: dict[str, list[Any]] = {roadmap_name: []}
        for node in self.nodes:
            if node.type == "title":
                title_node = node.data.label
                result[title_node] = []
            elif node.type == "topic":
                if isinstance(current_topic, str):
                    result[roadmap_name].append(
                        {
                            current_topic: {
                                "subtopics": current_subtopics,
                                "content_url": f"https://roadmap.sh/{clean_url_strings(roadmap_name)}/{clean_url_strings(current_topic)}@{node.id}",
                            }
                        }
                    )

                current_topic = node.data.label
                current_subtopics = []
            elif node.type == "subtopic":
                subtopic = node.data.label
                current_subtopics.append(
                    (
                        node.data.label,
                        f"https://roadmap.sh/{clean_url_strings(roadmap_name)}/{clean_url_strings(subtopic)}@{node.id}",
                    )
                )
        return result
