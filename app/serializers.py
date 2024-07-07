import logging
from abc import abstractmethod
from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel

logger: logging.Logger = logging.getLogger(name=__name__.split(sep=".")[-1])


class RoadmapBaseModel(BaseModel):
    @abstractmethod
    def extract_topic_and_subtopics(self) -> dict[str, list[Any]]:
        pass


class RoadmapType(Enum):
    SUBROADMAP = "subroadmap"
    ROADMAP = "roadmap"


class Properties(BaseModel):
    controlName: Optional[str] = None


class Properties1(BaseModel):
    color: Optional[str] = None
    size: Optional[str] = None
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

    def extract_topic_and_subtopics(self) -> dict[str, list[Any]]:
        result: dict[str, list[Any]] = {}
        if self.mockup.controls is None or self.mockup.controls.control is None:
            return result

        nodes: list[ControlItem] = self.mockup.controls.control
        title_node: Optional[str] = None
        current_topic: Optional[str] = None
        current_subtopics: dict[str, list[str]] = {}
        for node in nodes:
            if node.typeID == "__group__":
                if node.properties is None:
                    continue
                control_name: str | None = node.properties.controlName
                # Exclude reference to other roadmaps
                if control_name is None or "roadmap.sh" in control_name:
                    continue

                control_name_parts: list[str] = control_name.split(sep=":")
                # Topic example: 100-python-basics
                if len(control_name_parts) == 1:
                    topic_parts: list[str] = control_name_parts[0].split(sep="-")
                    current_topic = topic_parts[2]
                    if current_topic == "roadmap":
                        continue
                    if title_node is None:
                        title_node = topic_parts[1]
                    if current_topic not in current_subtopics.keys():
                        current_subtopics[current_topic] = []
                    # Subtopic example: 100-python-package-managers:pypi
                elif len(control_name_parts) == 2:
                    current_topic = control_name_parts[0].split(sep="-")[2]
                    current_subtopic: str = control_name_parts[1]
                    if current_topic not in current_subtopics.keys():
                        current_subtopics[current_topic] = [current_subtopic]
                    else:
                        current_subtopics[current_topic].append(current_subtopic)
        if title_node is not None:
            logger.info(msg=f"Adding {title_node=}")
            result[title_node] = []

            for topic, subtopics in current_subtopics.items():
                logger.info(msg=f"Adding {topic=}")
                result[title_node].append({topic: subtopics})
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

    def extract_topic_and_subtopics(self) -> dict[str, list[Any]]:
        current_subtopics: list[str] = []
        current_topic: Optional[str] = None
        result: dict[str, list[Any]] = {}
        title_node: Optional[str] = None
        for node in self.nodes:
            if node.type == "title":
                title_node = node.data.label
                result[title_node] = []
            elif node.type == "topic":
                if isinstance(current_topic, str):
                    if isinstance(title_node, str):
                        result[title_node].append({current_topic: current_subtopics})

                current_topic = node.data.label
                current_subtopics = []
            elif node.type == "subtopic":
                current_subtopics.append(node.data.label)
        return result
