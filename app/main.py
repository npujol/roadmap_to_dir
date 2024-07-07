import argparse
import json
import logging
import re
from pathlib import Path
from typing import Any, Optional

import requests
from pydantic_core import ValidationError

from app.serializers import Roadmap, SubRoadmap

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

logger: logging.Logger = logging.getLogger(name=__name__.split(sep=".")[-1])


class RoadmapExtractor:
    base_url: str = "https://roadmap.sh/"

    def handle(self, roadmap_name: str, output_path: Path) -> None:
        logger.info(msg=f"Extracting roadmap {roadmap_name}.")
        roadmap: Roadmap | SubRoadmap = self.get_roadmap(name=roadmap_name)
        data: dict[Any, Any] = roadmap.extract_topic_and_subtopics()
        self.create_structure(data=data, base_path=output_path)
        logger.info(msg=f"Roadmap {roadmap_name} extracted.")

    def download_roadmap_page(self, name: str) -> bytes:
        url: str = self.base_url + name
        logger.info(msg=f"Downloading roadmap page for {name} using {url} url.")
        response: requests.Response = requests.get(url=url)
        response.raise_for_status()
        logger.debug(msg=f"The response status code is {response.status_code}.")
        return response.content

    def get_roadmap(self, name: str) -> Roadmap | SubRoadmap:
        url: str = self.base_url + name + ".json"
        logger.info(msg=f"Downloading roadmap json for {name} using {url} url.")
        response: requests.Response = requests.get(url=url)
        response.raise_for_status()
        logger.debug(msg=f"The response status code is {response.status_code}.")
        content_dict: dict[Any, Any] = json.loads(s=response.content)
        return self._validate_roadmap_type(content_dict=content_dict)

    def _validate_roadmap_type(
        self, content_dict: dict[Any, Any]
    ) -> Roadmap | SubRoadmap:
        try:
            logger.info(msg="Checking if the content is a roadmap")
            roadmap: Roadmap | SubRoadmap = Roadmap.model_validate(
                obj=content_dict, strict=False
            )
            logger.info(msg="The content is a roadmap.")
        except ValidationError:
            logger.info(msg="Checking if the content is a subroadmap.")
            roadmap: Roadmap | SubRoadmap = SubRoadmap.model_validate(
                obj=content_dict, strict=False
            )
            logger.info(msg="The content is a subroadmap.")
        return roadmap

    def create_structure(self, data: dict[str, Any], base_path: Path) -> None:
        for title, topics in data.items():
            logger.info(msg=f"Creating {title=} structure.")
            title_path: Path = self._create_directory(
                filename=title, base_path=base_path
            )
            for content in topics:
                self._create_topic_structure(data=content, base_path=title_path)

    def _create_topic_structure(self, data: dict[str, Any], base_path: Path) -> None:
        for topic, subtopics in data.items():
            logger.info(msg=f"Creating {topic=} structure.")
            topic_path = self._create_directory(filename=topic, base_path=base_path)
            for subtopic in subtopics:
                logger.info(msg=f"Creating {subtopic=} structure.")
                topic_path: Path = base_path / self._clean_pathname(pathname=topic)
                self._create_directory(filename=subtopic, base_path=topic_path)
                self._create_markdown_file(
                    filename=subtopic, related_filenames=[], base_path=topic_path
                )
            self._create_markdown_file(
                filename=topic, related_filenames=subtopics, base_path=topic_path.parent
            )

    def _create_markdown_file(
        self,
        filename: str,
        related_filenames: list[str],
        base_path: Path,
    ) -> Path:
        logger.info(msg=f"Creating {filename=} markdown file.")
        subtopic_path: Path = base_path / self._clean_pathname(pathname=filename)
        subtopic_path.mkdir(exist_ok=True)
        markdown_file_path: Path = (
            subtopic_path / f"{self._clean_pathname(pathname=filename)}.md"
        )
        markdown_file_path.touch(exist_ok=True)
        with open(file=markdown_file_path, mode="w") as md_file:
            logger.debug(msg=f"Creating {markdown_file_path=} file.")
            md_file.write(f"# {filename}\n\n## Contents\n\n")
            for item in related_filenames:
                cleaned_filename = self._clean_pathname(pathname=item)
                md_file.write(f"- [{item}](./{cleaned_filename}/{cleaned_filename})\n")
        return markdown_file_path

    def _create_directory(self, filename: str, base_path: Path) -> Path:
        new_path: Path = base_path / self._clean_pathname(pathname=filename)
        logger.debug(msg=f"Creating {new_path=} directory.")
        new_path.mkdir(exist_ok=True, parents=True)
        return new_path

    def _clean_pathname(self, pathname: str) -> str:
        cleaned_name: str = re.sub(pattern=r"[^a-zA-Z0-9\s-]", repl="", string=pathname)
        cleaned_name: str = re.sub(
            pattern=r"\s+", repl="-", string=cleaned_name
        ).strip()
        return cleaned_name


def main():
    description_msg = (
        "Extract topics and subtopics from a roadmap and create a folder structure."
    )
    logger.info(description_msg)
    parser = argparse.ArgumentParser(description=description_msg)
    parser.add_argument(
        "name",
        type=str,
        help="The name of the roadmap to extract",
    )
    parser.add_argument(
        "--output",
        type=str,
        default="output",
        help="The base path for the output folder structure",
    )
    args: argparse.Namespace = parser.parse_args()

    roadmap_name: Optional[str] = args.name
    if roadmap_name is None:
        name_error_msg = "The name of the roadmap is required."
        logger.error(msg=name_error_msg)
        raise ValueError(name_error_msg)

    output: Optional[str] = args.output
    if output is None:
        output_error_msg = "The base path for the output folder structure is required."
        logger.error(msg=output_error_msg)
        raise ValueError(output_error_msg)

    RoadmapExtractor().handle(roadmap_name=roadmap_name, output_path=Path(output))


if __name__ == "__main__":
    main()
