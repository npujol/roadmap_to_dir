import argparse
import json
import logging
import re
from pathlib import Path
from typing import Any, Optional

import requests

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

logger: logging.Logger = logging.getLogger(name=__name__)


class RoadmapExtractor:
    base_url: str = "https://roadmap.sh/"

    def handle(self, roadmap_name: str, output_path: Path) -> None:
        logger.info(msg=f"Extracting roadmap {roadmap_name}.")
        data: dict[Any, Any] = self.extract_topic_and_subtopics(name=roadmap_name)
        self.create_structure(data=data, base_path=output_path)

    def download_roadmap_page(self, name: str) -> bytes:
        url: str = self.base_url + name
        logger.info(msg=f"Downloading roadmap page for {name} using {url} url.")
        response: requests.Response = requests.get(url=url)
        response.raise_for_status()
        logger.debug(msg=f"The response status code is {response.status_code}.")
        return response.content

    def download_roadmap_json(self, name: str) -> dict[Any, Any]:
        url: str = self.base_url + name + ".json"
        logger.info(msg=f"Downloading roadmap json for {name} using {url} url.")
        response: requests.Response = requests.get(url=url)
        response.raise_for_status()
        logger.debug(msg=f"The response status code is {response.status_code}.")
        content_dict: dict[Any, Any] = json.loads(s=response.content)
        return content_dict

    def extract_topic_and_subtopics(self, name: str) -> dict[str, list[list[str]]]:
        """
        Extracts the topics and subtopics from the roadmap JSON.

        Args:
            name (str): The name of the roadmap.

        Returns:
            dict[str, list[list[str]]]: A dictionary where the keys are topic names
            and the values are lists of subtopics.
        """
        roadmap_dict: dict[str, Any] = self.download_roadmap_json(name=name)
        current_subtopics: list[str] = []
        current_topic: Optional[str] = None
        result: dict[str, list[Any]] = {}
        title_node: Optional[str] = None
        for node in roadmap_dict.get("nodes", []):
            if node.get("type") == "title":
                title_node = node["data"]["label"]
                logger.info(msg=f"Adding title {node['data']['label']} to the result.")
                if isinstance(title_node, str):
                    result[title_node] = []
            elif node["type"] == "topic":
                if isinstance(current_topic, str):
                    logger.info(
                        msg=f"Adding {current_topic=} with {current_subtopics=} to result."
                    )
                    if isinstance(title_node, str):
                        result[title_node].append({current_topic: current_subtopics})

                current_topic = node["data"]["label"]
                current_subtopics = []
            elif node["type"] == "subtopic":
                current_subtopics.append(node["data"]["label"])
        return result

    def create_structure(self, data: dict[str, Any], base_path: Path) -> None:
        for title, topics in data.items():
            title_path: Path = self._create_directory(
                filename=title, base_path=base_path
            )
            for content in topics:
                self._create_topic_structure(data=content, base_path=title_path)

    def _create_topic_structure(self, data: dict[str, Any], base_path: Path) -> None:
        for topic, subtopics in data.items():
            topic_path = self._create_directory(filename=topic, base_path=base_path)
            for subtopic in subtopics:
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
