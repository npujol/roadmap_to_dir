import argparse
import json
import logging
import re
from pathlib import Path
from typing import Any, Optional

import requests
from markdownify import markdownify
from pydantic_core import ValidationError

from app.serializers import Roadmap, SubRoadmap
from app.string_processors import clean_url_strings

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

logger: logging.Logger = logging.getLogger(name=__name__)


class RoadmapExtractor:
    base_url: str = "https://roadmap.sh/"

    def handle(self, roadmap_name: str, output_path: Path) -> None:
        logger.info(msg=f"Extracting roadmap {roadmap_name}.")
        roadmap: Roadmap | SubRoadmap = self.get_roadmap(name=roadmap_name)

        data: dict[Any, Any] = roadmap.extract_topic_and_subtopics(
            roadmap_name=roadmap_name
        )
        json.dump(data, open(output_path / f"{roadmap_name}.json", "w"))

        self.create_structure(data=data, base_path=output_path)
        logger.info(msg=f"Roadmap {roadmap_name} extracted.")

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
        except ValidationError as e:
            logger.error(e)
            logger.info(msg="Checking if the content is a subroadmap.")
            roadmap: Roadmap | SubRoadmap = SubRoadmap.model_validate(
                obj=content_dict, strict=False
            )
            logger.info(msg="The content is a subroadmap.")
        return roadmap

    def create_structure(self, data: dict[str, Any], base_path: Path) -> None:
        for title, topics in data.items():
            logger.info(
                msg=f"Creating {title=} structure and {len(topics)} related files."
            )

            related_filenames: list[str] = []
            title_path: Path = self._create_directory(
                dirname=title, base_path=base_path
            )

            for content in topics:
                for name in content.keys():
                    related_filenames.append(clean_url_strings(f"{title}-{name}"))

                self._create_topic_structure(
                    data=content, base_path=title_path, title=title
                )

            self._create_markdown_file(
                filename=f"{title}-content",
                related_filenames=related_filenames,
                base_path=title_path,
            )

    def _create_topic_structure(
        self, data: dict[str, Any], base_path: Path, title: str
    ) -> None:
        for raw_topic, subtopics_info in data.items():
            topic = clean_url_strings(f"{title}-{raw_topic}")
            logger.info(msg=f"Creating {topic=} structure.")
            subtopics = subtopics_info.get("subtopics", [])
            topic_content_url = subtopics_info.get("content_url", None)

            topic_path = base_path / clean_url_strings(topic)
            subtopic_path = self._create_directory(
                dirname="content", base_path=topic_path
            )

            for subtopic_info in subtopics:
                raw_subtopic = subtopic_info[0]
                subtopic = clean_url_strings(f"{topic}-{raw_subtopic}")
                content_url = subtopic_info[1]

                logger.info(msg=f"Creating {raw_subtopic=} structure.")
                self._create_markdown_file(
                    filename=subtopic,
                    related_filenames=[],
                    base_path=subtopic_path,
                    content_url=content_url,
                )
            self._create_markdown_file(
                filename=clean_url_strings(topic),
                related_filenames=[value[0] for value in subtopics],
                base_path=topic_path,
                content_url=topic_content_url,
            )

    def _create_markdown_file(
        self,
        filename: str,
        related_filenames: list[str],
        base_path: Path,
        content_url: Optional[str] = None,
    ) -> Path:
        logger.info(
            msg=f"Creating {filename=} markdown file with content {related_filenames}."
        )
        markdown_file_path: Path = base_path / f"{clean_url_strings(filename)}.md"
        shall_add_initial_content = not markdown_file_path.exists()

        with open(file=markdown_file_path, mode="a") as md_file:
            logger.debug(msg=f"Creating {markdown_file_path=} file.")
            parents = "\n- ".join(str(markdown_file_path).split(sep="/")[-4:-2])
            if shall_add_initial_content:
                md_file.write(
                    f"---\ntags:\n- roadmap\n- {parents}\n- ready\n---\n\n# {filename}\n\n## Contents\n\n"
                )
                for item in related_filenames:
                    cleaned_filename = clean_url_strings(f"{filename}-{item}")
                    md_file.write(f"- [[{cleaned_filename}]]\n")

            if content_url:
                md_file.write(
                    f"\n__Roadmap info from [roadmap website]({content_url})__\n"
                )
                try:
                    content = self._get_topic_content(content_url)
                    md_file.write(f"\n{content}\n")
                except Exception:
                    logger.exception(msg=f"Failed to get content from {content_url}.")

        return markdown_file_path

    def _get_topic_content(self, content_url: str) -> str:
        response: requests.Response = requests.get(url=content_url)
        response.raise_for_status()
        decoded_content = response.content.decode("utf-8")
        markdownify_content = markdownify(
            html=decoded_content,
            heading_style="ATX",
            extensions=["fenced-code", "tables"],
        )
        # workaround for set the right heading level
        return f"#{markdownify_content.strip()}"

    def _create_directory(self, dirname: str, base_path: Path) -> Path:
        new_path: Path = base_path / clean_url_strings(dirname)
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
