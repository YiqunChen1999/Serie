
"""
This script is designed to parse the papers from OpenReview.
"""

import os
from datetime import datetime

import openreview
from tqdm import tqdm
from openreview.api import OpenReviewClient, Note

from serie.utils.logging import create_logger
from serie.base.paper import Paper, Link, LinkEnum
from serie.base.plugin import (
    BasePlugin, GlobalPluginData
)


logger = create_logger(__name__)
BASE_URL = "https://api2.openreview.net"


class OpenReviewParser(BasePlugin):
    def __init__(
            self,
            year: int,
            conference: str,
            output_directory: str,
            max_retries: int = 3,
            num_requested: int | None = None,
            version: str = "",
            dependencies: list[str] | None = None,
            **kwargs) -> None:
        super().__init__(version, dependencies, **kwargs)
        self.year = year
        self.conference = conference
        self.output_directory = output_directory
        self.max_retries = max_retries
        self.num_requested = num_requested
        os.makedirs(self.output_directory, exist_ok=True)
        self.client = OpenReviewClient(baseurl=BASE_URL)

    def process(self,
                papers: list[Paper],
                global_plugin_data: GlobalPluginData):
        if use_v1_api(self.conference, self.year):
            return self.process_openreview_v1(papers, global_plugin_data)
        return self.process_openreview_v2(papers, global_plugin_data)

    def process_openreview_v2(
            self, papers: list[Paper], global_plugin_data: GlobalPluginData):
        submissions: list[Note] = self.client.get_all_notes(
            invitation=get_invitation_id(self.conference, self.year),
            content={"venueid": get_venue_id(self.conference, self.year)}
        )
        if self.num_requested:
            submissions = submissions[:self.num_requested]
        logger.info(f"Found {len(submissions)} submissions.")
        pbar = tqdm(submissions)
        for s in pbar:
            pbar.set_description(s.id)
            assert s.pdate and s.tmdate and s.content, (
                f"Submission {s} does not have odate."
            )
            paper = create_paper_from_openreview(note=s)
            papers.append(paper)
        return papers

    def process_openreview_v1(
            self, papers: list[Paper], global_plugin_data: GlobalPluginData):
        client = openreview.Client(baseurl="https://api.openreview.net")
        submissions: list[openreview.Note] = client.get_all_notes(
            invitation=get_invitation_id(self.conference, self.year),
            content={"venueid": get_venue_id(self.conference, self.year)}
        )
        submissions = list(filter(
            lambda s: (
                "submitted" not in s.content["venue"].lower()
                and "submit" not in s.content["venue"].lower()
            ),
            submissions
        ))
        if self.num_requested:
            submissions = submissions[:self.num_requested]
        if len(submissions) == 0:
            logger.warning("No submissions found.")
        logger.info(f"Found {len(submissions)} submissions.")
        pbar = tqdm(submissions)
        for s in pbar:
            pbar.set_description(s.id)
            paper = create_paper_from_openreview(s)
            papers.append(paper)
        return papers

    def check_content(self, content: dict[str, dict]):
        keys = (
            "title", "authors", "abstract", "venue", "TLDR", "keywords"
        )
        for key in keys:
            if key not in content:
                content[key] = {"value": ""}
        return content


def create_paper_from_openreview(note: Note | openreview.Note) -> Paper:
    assert note.pdate and note.tmdate and note.content, (
        f"Submission {note} does not have odate."
    )
    content = check_content(note.content)
    paper_link = f"https://openreview.net/forum?id={note.id}"
    pdf_link = f"https://openreview.net/pdf?id={note.id}"
    appendix_link = (
        f"https://openreview.net/attachment?id={note.id}"
        f"&name=supplementary_material"
    )
    authors = content["authors"]["value"]
    links = [
        Link(href=paper_link, title="html", tag=LinkEnum.ABSTRACT),
        Link(href=pdf_link, title="pdf", tag=LinkEnum.PDF),
        Link(href=appendix_link, title="appendix", tag=LinkEnum.APPENDIX),
    ]
    online_date = datetime.fromtimestamp(note.pdate / 1000)
    modified_date = datetime.fromtimestamp(note.tmdate / 1000)
    paper = Paper(
        url=paper_link,
        pdf_url=pdf_link,
        title=content["title"]["value"],
        authors=authors,
        abstract=content["abstract"]["value"],
        online_date=online_date,
        update_date=modified_date,
        venue=content["venue"]["value"],
        links=links,
        comment=content["TLDR"]["value"],
    )
    return paper


def check_content(content: dict):
    keys = (
        "title", "authors", "abstract", "venue", "TLDR", "keywords"
    )
    for key in keys:
        if key not in content:
            content[key] = {"value": ""}
        elif not isinstance(content[key], dict):
            # handle openreview v1 API
            content[key] = {"value": content[key]}
    return content


def use_v1_api(conference: str, year: int):
    if conference.lower() == "iclr" and year < 2024:
        return True
    return False


def get_invitation_id(conference: str, year: int):
    venueid = get_venue_id(conference, year)
    conference = conference.lower()
    if conference == "iclr":
        if 2017 < year < 2024:
            return f"{venueid}/-/Blind_Submission"
        elif year <= 2017:
            return f"{venueid}/-/submission"
        else:
            return f"{venueid}/-/Submission"
    if conference == "icml":
        return f"{venueid}/-/Submission"
    if conference == "neurips" or conference == "nips":
        return f"{venueid}/-/Submission"
    raise ValueError(f"Unknown conference: {conference}")


def get_venue_id(venue: str, year: int):
    venue = venue.lower()
    if venue == "iclr":
        return f"ICLR.cc/{year}/Conference"
    if venue == "icml":
        return f"ICML.cc/{year}/Conference"
    if venue == "neurips" or venue == "nips":
        return f"NeurIPS.cc/{year}/Conference"
    raise ValueError(f"Unknown venue: {venue}")


if __name__ == "__main__":
    parser = OpenReviewParser(
        year=2024, conference="neurips", output_directory="tmp",
        num_requested=10
    )
    global_plugin_data = GlobalPluginData()
    results = parser.process([], global_plugin_data)
