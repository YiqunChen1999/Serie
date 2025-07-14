
"""
This script is designed to parse the papers from CVF Open Access.
"""

import os
import re
import time
import requests
import datetime
import os.path as osp

import bs4
import bibtexparser
from tqdm import tqdm
from bs4 import BeautifulSoup
from bibtexparser.bibdatabase import BibDatabase

from serie.utils.logging import create_logger
from serie.base.paper import Paper, Link, LinkEnum
from serie.base.plugin import (
    BasePlugin, GlobalPluginData
)


logger = create_logger(__name__)
BASE_URL = "https://openaccess.thecvf.com"


class CVFParser(BasePlugin):
    def __init__(
            self,
            year: int,
            conference: str,
            output_directory: str,
            max_retries: int = 3,
            num_requested: int | None = None,
            overwrite: bool = False,
            version: str = "",
            dependencies: list[str] | None = None,
            **kwargs) -> None:
        super().__init__(overwrite, version, dependencies, **kwargs)
        self.year = year
        self.conference = conference
        self.output_directory = output_directory
        self.max_retries = max_retries
        self.num_requested = num_requested
        self.url = osp.join(BASE_URL, f"{conference}{year}?day=all")
        os.makedirs(self.output_directory, exist_ok=True)

    def process(self,
                papers: list[Paper],
                global_plugin_data: GlobalPluginData):
        date = self.get_conference_date()
        date = datetime.datetime.strptime(date, "%Y-%m-%d")
        soup = request_html_content(
            self.url,
            cache_file=osp.join(self.output_directory, "paper_list.html"),
            max_retries=self.max_retries,
        )
        paper_folder = osp.join(self.output_directory, "papers")
        os.makedirs(paper_folder, exist_ok=True)
        pbar = tqdm(soup.find_all("dt", class_="ptitle"))
        for count, dt in enumerate(pbar):
            if self.num_requested and count >= self.num_requested:
                break
            a: bs4.element.Tag = dt.find("a")  # type: ignore
            if a:
                url: str = a["href"]  # type: ignore
                url = osp.join(BASE_URL, url.lstrip("/"))
                cache_path = osp.join(paper_folder, osp.basename(url))
                info = parse_paper_info(url, cache_file=cache_path)
                if not info:
                    logger.warning_once(
                        f"Failed to parse paper info from {url}. "
                        f"Skipping this paper."
                    )
                    continue
                info["title"] = info["title"] or a.text
                info["url"] = url
                paper = create_paper_from_cvf_data(info, date)
                papers.append(paper)
        return papers

    def get_conference_date(self):
        url = osp.join(BASE_URL, f"{self.conference}{self.year}")
        soup = request_html_content(url, max_retries=self.max_retries)
        date_text: bs4.element.Tag = soup.find(
            "a", string=lambda x: x and x.startswith("Day")  # type: ignore
        )
        default_date = f"{self.year}-01-01"
        if date_text:
            # find the date from the text with the format using regex:
            # 'Day 1: 2024-06-19'
            date = re.search(r"\d{4}-\d{2}-\d{2}", date_text.text)
            if date:
                return date.group()
        return default_date


def create_paper_from_cvf_data(
        info: dict[str, str], date: datetime.datetime) -> Paper:
    paper = Paper(
        url=info["url"],
        pdf_url=info["pdfurl"],
        title=info["title"],
        online_date=date,
        update_date=date,
        authors=[
            author for author in info["authors"].split(" and ")
        ],
        abstract=info["abstract"],
        venue=info["booktitle"],
        links=[
            Link(href=info["pdfurl"], title="pdf", tag=LinkEnum.PDF),
            Link(href=info["url"], title="html", tag=LinkEnum.ABSTRACT),
        ],
        comment=info["bibtex"],
    )
    return paper


def parse_paper_info(
        url: str,
        cache_file: str | None = None,
        max_retries: int = 3,
        sleep_time: int = 1) -> dict[str, str]:
    soup = request_html_content(url, cache_file, max_retries, sleep_time)
    if soup is None:
        return {}
    abstract = soup.find(id="abstract")
    if abstract:
        abstract = abstract.text.strip()
    else:
        abstract = ""
        logger.warning_once(
            f"Abstract not found for {url}, abstract: {abstract}"
        )
    pdf = soup.find("a", string=lambda x: x and "pdf" in x.lower())  # type: ignore # noqa
    if pdf:
        pdfurl: str = pdf["href"].lstrip("/")  # type: ignore # noqa
    else:
        pdfurl = ""
        logger.warning_once(
            f"PDF link not found for {url}, pdf url: {pdfurl}"
        )
    if pdfurl:
        if pdfurl.startswith("/"):
            pdfurl: str = osp.join(BASE_URL, pdfurl.lstrip("/"))
        else:
            pdfurl = osp.join(osp.dirname(url), pdfurl)
    else:
        pdfurl = ""
        logger.warning_once(
            f"PDF url not found for {url}, pdf url: {pdfurl}"
        )
    bibtex = soup.find(class_="bibref pre-white-space")
    if bibtex:
        bib_data: BibDatabase = bibtexparser.loads(
            bibtex.text.replace("<br>", "")
        )
        bibtex = bibtex.text
        entries: dict[str, str] = bib_data.entries[0]
    else:
        bibtex = ""
        entries = {}
    return {
        "title": entries.get("title", ""),
        "authors": entries.get("author", ""),
        "abstract": abstract,
        "pdfurl": pdfurl,
        "year": entries.get("year", ""),
        "month": entries.get("month", ""),
        "bibtex": bibtex,
        "booktitle": entries.get("booktitle", ""),
    }


def request_html_content(
        url: str,
        cache_file: str | None = None,
        max_retries: int = 3,
        sleep_time: int = 1):
    if cache_file and osp.exists(cache_file):
        with open(cache_file, "r") as f:
            txt = f.read()
    else:
        response = None
        for _ in range(max_retries):
            try:
                response = requests.get(url, timeout=10, allow_redirects=True)
                response.raise_for_status()
            except Exception as e:
                logger.error(f"Failed to get {url}. Error message: {e}.\n"
                             f"Retry after {sleep_time} seconds.")
                time.sleep(sleep_time)
                continue
            break
        if response is None:
            logger.error(f"Failed to get {url}")
            return None
        txt = response.text
        if cache_file:
            with open(cache_file, "w") as f:
                f.write(txt)
        if sleep_time:
            time.sleep(sleep_time)
    return BeautifulSoup(txt, "html5lib")


if __name__ == "__main__":
    request_html_content(
        osp.join(BASE_URL, "CVPR2024?day=2024-06-21"),
        "tmp/result.txt",
    )
    parser = CVFParser(
        year=2024, conference="CVPR", output_directory="tmp"
    )
    global_plugin_data = GlobalPluginData()
    parser([], global_plugin_data)
