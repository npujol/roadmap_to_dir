import json
import logging

import requests

logger = logging.getLogger(__name__)


class Downloader:
    base_url = "https://roadmap.sh/"

    def download_roadmap_page(self, name: str):
        url = self.base_url + name
        logger.info(f"Downloading roadmap page for {name} using {url} url.")
        response = requests.get(url)
        response.raise_for_status()
        logger.debug(f"The response status code is {response.status_code}.")
        return response.content
    
    def download_roadmap_json(self, name: str):
        url = self.base_url + name + ".json"
        logger.info(f"Downloading roadmap json for {name} using {url} url.")
        response = requests.get(url)
        response.raise_for_status()
        logger.debug(f"The response status code is {response.status_code}.")
        content_dict = json.loads(response.content)
        return content_dict
    
    def extract_topic_and_subtopics(self, name: str):
        roadmap_dict = self.download_roadmap_json(name)
        result = {}
        title = None
        current_topic = None
        current_subtopics = []
        for node in roadmap_dict["nodes"]:
            if node["type"] == "title":
                nname = node["data"]["label"]
                title = nname
                if nname is not None and nname not in result.keys():
                    result[nname] = []
                elif title is not None and current_topic not in result.keys(): 
                    result[title].append({current_topic: current_subtopics})
            
            if node["type"] == "topic":
                if current_topic is not None:
                    result[title].append({current_topic: current_subtopics})
                current_topic = node["data"]["label"]
                current_subtopics = []
            elif node["type"] == "subtopic":
                current_subtopics.append(node["data"]["label"])
        return result