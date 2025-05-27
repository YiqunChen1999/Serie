
import os
from enum import Enum
from copy import deepcopy
from datetime import datetime
from dataclasses import asdict, dataclass
from urllib.request import urlretrieve

from serie.utils.logging import create_logger
from serie.base.plugin import BasePluginData


logger = create_logger(__name__)


@dataclass
class Author:
    """
    Representing a result's authors.
    """
    name: str

    def __str__(self) -> str:
        return self.name

    def __repr__(self) -> str:
        return "{}({})".format(self.__class__.__qualname__, repr(self.name))

    def __eq__(self, other) -> bool:
        if isinstance(other, Author):
            return self.name == other.name
        return False


class LinkEnum(Enum):
    """
    Enum for the link types.
    """
    APPENDIX = "appendix"
    ABSTRACT = "abstract"
    PDF = "pdf"
    HOME = "home"
    CODE = "code"
    BLOG = "blog"
    SLIDES = "slides"
    VIDEO = "video"
    OTHER = "other"


@dataclass
class Link:
    href: str
    title: str = ""
    tag: LinkEnum = LinkEnum.OTHER

    def __str__(self) -> str:
        return self.href

    def __post_init__(self):
        if isinstance(self.tag, str):
            self.tag = LinkEnum(self.tag.lower())

    def asdict(self):
        return {
            "href": self.href,
            "title": self.title,
            "tag": self.tag.value,
        }

    def __repr__(self) -> str:
        return "{}({}, title={}, tag={}".format(
            self.__class__.__qualname__,
            repr(self.href),
            repr(self.title),
            repr(self.tag),
        )

    def __eq__(self, other) -> bool:
        if isinstance(other, Link):
            return self.href == other.href
        return False


class Paper:
    def __init__(
            self,
            url: str | Link,
            pdf_url: str | Link,
            title: str,
            authors: list[Author] | list[str],
            abstract: str,
            online_date: str | datetime,
            update_date: str | datetime,
            links: list[Link] | list[str],
            version: str = "v1",
            comment: str = "",
            venue: str = "",
            doi: str = "",
            primary_category: str = "",
            categories: list[str] | None = None,
            tags: list[str] | None = None,
            custom_fields: dict[str, str] | None = None,
            ) -> None:
        if isinstance(url, Link):
            self.url = url
            assert self.url.tag == LinkEnum.ABSTRACT
        else:
            self.url = Link(url, tag=LinkEnum.ABSTRACT)
        if isinstance(pdf_url, Link):
            self.pdf_url = pdf_url
            assert self.pdf_url.tag == LinkEnum.PDF
        else:
            self.pdf_url = Link(pdf_url, tag=LinkEnum.PDF)

        self.title = title
        self.abstract = abstract
        if isinstance(online_date, str):
            online_date = datetime.strptime(
                online_date, "%Y-%m-%d" if online_date else ""
            )
        self.online_date = online_date
        if isinstance(update_date, str):
            update_date = datetime.strptime(
                update_date, "%Y-%m-%d" if update_date else ""
            )
        self.update_date = update_date
        self.links = [
            Link(link) if isinstance(link, str) else link for link in links
        ]
        self.links = [self.url, self.pdf_url] + self.links
        self.version = version
        self.comment = comment
        self.venue = venue
        self.doi = doi
        self.primary_category = primary_category
        self.categories = categories or list()
        self.authors = [
            Author(a) if isinstance(a, str) else a for a in authors
        ]
        self.tags = tags or list()
        self.local_plugin_data: dict[str, BasePluginData] = {}
        self.custom_fields = custom_fields or dict()

    @property
    def code_link(self):
        for link in self.links:
            if link.tag == LinkEnum.CODE:
                return link
        return Link("", tag=LinkEnum.CODE)

    def reset_plugin_data(self, data: BasePluginData):
        self.local_plugin_data.pop(data.plugin_name, None)
        self.add_plugin_data(data)

    def add_plugin_data(self, data: BasePluginData):
        if data.plugin_name in self.local_plugin_data:
            logger.warning_once(
                f"Plugin {data.plugin_name} already exists, skip."
            )
            return
        self.local_plugin_data[data.plugin_name] = data

    def get_plugin_data(
            self,
            plugin_name: str,
            default: BasePluginData | None = None) -> BasePluginData | None:
        data = self.local_plugin_data.get(plugin_name, default)
        return data

    def download(self, link_type: LinkEnum, folder: str, filename: str = ""):
        if link_type == LinkEnum.CODE:
            raise NotImplementedError("Download code link is not implemented.")
        if link_type == LinkEnum.PDF:
            link = self.pdf_url
            filename = filename or f"{format_valid_title(self)}.pdf"
            path = os.path.join(folder, filename)
            if os.path.exists(path):
                path = path.replace(".pdf", f" @ {self.version}.pdf")
            if os.path.exists(path):
                logger.warning(
                    f"File {path} already exists, skip downloading."
                )
                return path
            logger.info(f"Downloading PDF from {link.href} to {path}")
            downloaded, _ = urlretrieve(link.href, path)
            return downloaded
        else:
            raise ValueError(f"Link type {link_type} is not supported.")

    def asdict(self):
        links = [
            link if isinstance(link, str) else link.asdict()
            for link in self.links
        ]
        data = {
            "url": self.url.asdict(),
            "pdf_url": self.pdf_url.asdict(),
            "title": self.title,
            "authors": [a.name for a in self.authors],
            "abstract": self.abstract,
            "online_date": self.online_date.strftime("%Y-%m-%d"),
            "update_date": self.update_date.strftime("%Y-%m-%d"),
            "links": links,
            "version": self.version,
            "local_plugin_data": {
                k: asdict(v) for k, v in self.local_plugin_data.items()
            },
            "comment": self.comment,
            "venue": self.venue,
            "doi": self.doi,
            "primary_category": self.primary_category,
            "categories": self.categories,
            "tags": self.tags,
            "custom_fields": self.custom_fields,
        }
        return deepcopy(data)

    def update_authors(self, authors: str | Author | list[Author] | list[str]):
        if isinstance(authors, list):
            self.authors = [
                Author(a) if isinstance(a, str) else a for a in authors
            ]
        elif isinstance(authors, Author):
            self.authors = [authors]
        elif isinstance(authors, str):
            self.authors = [Author(authors)]
        else:
            raise ValueError(
                f"Invalid authors type: {type(authors)}. "
                f"Expected list or Author."
            )

    def update_links(self, links: str | Link | list[Link] | list[str]):
        if isinstance(links, list):
            self.links = [
                Link(link) if isinstance(link, str) else link for link in links
            ]
        elif isinstance(links, Link):
            self.links = [links]
        elif isinstance(links, str):
            self.links = [Link(links)]
        else:
            raise ValueError(
                f"Invalid links type: {type(links)}. "
                f"Expected list or Link."
            )
        self.links = [self.url, self.pdf_url] + self.links
        self.links = list(set(self.links))

    def update_url(self, url: str | Link):
        if isinstance(url, Link):
            self.url = url
        elif isinstance(url, str):
            self.url = Link(url)
        else:
            raise ValueError(
                f"Invalid url type: {type(url)}. "
                f"Expected str or Link."
            )
        if self.url.tag != LinkEnum.ABSTRACT:
            self.url.tag = LinkEnum.ABSTRACT

    def update_pdf_url(self, pdf_url: str | Link):
        if isinstance(pdf_url, Link):
            self.pdf_url = pdf_url
        elif isinstance(pdf_url, str):
            self.pdf_url = Link(pdf_url)
        else:
            raise ValueError(
                f"Invalid pdf_url type: {type(pdf_url)}. "
                f"Expected str or Link."
            )
        if self.pdf_url.tag != LinkEnum.PDF:
            self.pdf_url.tag = LinkEnum.PDF

    def update(self, inputs: dict):
        keys: list[str] = list(self.asdict().keys())
        if isinstance(inputs, Paper):
            inputs = inputs.asdict()
        for key, val in inputs.items():
            if key == "authors":
                self.update_authors(val)
            elif key == "links":
                self.update_links(val)
            elif key == "url":
                self.update_url(val)
            elif key == "pdf_url":
                self.update_pdf_url(val)
            elif key in keys:
                if isinstance(val, list):
                    val = [v for v in val if v]
                if isinstance(val, str):
                    val = val.strip()
                if val:
                    setattr(self, key, val)
            else:
                logger.warning(f"Key {key} is invalid for Paper.")

    def __str__(self) -> str:
        return self.url.href

    def __repr__(self) -> str:
        return (
            "{}("
            "url={}, pdf_url={}, "
            "title={}, authors={}, abstract={}, "
            "online_date={}, update_date={}, "
            "links={}, comment={}, version={}, venue={}, doi={}, "
            "primary_category={}, categories={}, "
            "tags={}, custom_fields={} "
            ")"
        ).format(
            self.__class__.__qualname__,
            repr(self.url),
            repr(self.pdf_url),
            repr(self.title),
            repr(self.authors),
            repr(self.abstract),
            repr(self.online_date),
            repr(self.update_date),
            repr(self.links),
            repr(self.comment),
            repr(self.version),
            repr(self.venue),
            repr(self.doi),
            repr(self.primary_category),
            repr(self.categories),
            repr(self.tags),
            repr(self.custom_fields),
        )

    def __eq__(self, other) -> bool:
        if isinstance(other, Paper):
            return (
                self.url.href == other.url.href
                and self.version == other.version
            )
        return False


def format_valid_title(paper: Paper) -> str:
    title = (
        paper.title
        .replace(": ", " -- ").replace("? ", "？").replace("?", "？")
        .replace("<", "").replace(">", "")
        .replace('"', "'").replace("/", "").replace("\\", "")
        .replace("|", "or").replace("*", "Star")
    )
    if title != paper.title:
        logger.warning(f"Original title: {paper.title}. New title: {title}.")
    return title


def create_paper_from_dict(data: dict):
    url = data.get("url", "")
    if not isinstance(url, dict):
        url = {"href": url, "tag": LinkEnum.ABSTRACT}
    pdf_url = data.get("pdf_url", "")
    if not isinstance(pdf_url, dict):
        pdf_url = {"href": pdf_url, "tag": LinkEnum.PDF}
    paper = Paper(
        url=Link(**url),
        pdf_url=Link(**pdf_url),
        title=data.get("title", ""),
        authors=[Author(a) for a in data.get("authors", list())],
        abstract=data.get("abstract", ""),
        online_date=data.get("online_date", ""),
        update_date=data.get("update_date", ""),
        links=[Link(**link) for link in data.get("links", list())],
        comment=data.get("comment", ""),
        version=data.get("version", "v1"),
        tags=data.get("tags", list()),
        venue=data.get("venue", ""),
        doi=data.get("doi", ""),
        primary_category=data.get("primary_category", ""),
        categories=data.get("categories", list()),
        custom_fields=data.get("custom_fields", dict()),
    )
    paper.local_plugin_data.update(data.get("local_plugin_data", {}))
    return paper
