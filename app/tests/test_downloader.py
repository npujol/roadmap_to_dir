import pytest

from app.downloader import Downloader


@pytest.mark.vcr()
def test_download_roadmap_page(snapshot):
    name = "devops"
    result = Downloader().download_roadmap_page(name)
    assert snapshot() == str(result)

@pytest.mark.vcr()
def test_download_roadmap_json(snapshot):
    name = "devops"
    result = Downloader().download_roadmap_json(name)
    assert snapshot("json") == result

@pytest.mark.vcr()
def test_extract_topic_and_subtopics(snapshot):
    result = Downloader().extract_topic_and_subtopics("devops")
    assert snapshot("json") == result