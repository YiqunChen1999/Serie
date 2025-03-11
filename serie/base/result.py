
from enum import Enum
from copy import deepcopy
from datetime import datetime
from dataclasses import asdict, dataclass, field
import os
from urllib.request import urlretrieve

import arxiv
from serie.utils.logging import create_logger
from serie.base.plugin import BasePluginData


logger = create_logger(__name__)


@dataclass
class Metainfo:
    code_link: str = ""
    category: str = ""
    journal: str = ""
    download: bool = False
    tags: list[str] = field(default_factory=list)
    id: str = ""


class Author:
    """
    Representing a result's authors.
    """
    def __init__(self, name: str):
        """
        Constructs an `Author` with the specified name.
        """
        self.name = name

    def __str__(self) -> str:
        return self.name

    def __repr__(self) -> str:
        return "{}({})".format(self.__class__.__qualname__, repr(self.name))

    def __eq__(self, other) -> bool:
        if isinstance(other, Result.Author):
            return self.name == other.name
        return False


class LinkEnum(Enum):
    """
    Enum for the link types.
    """
    ABSTRACT = "abstract"
    PDF = "pdf"
    HOME = "home"
    CODE = "code"
    BLOG = "blog"
    SLIDES = "slides"
    VIDEO = "video"
    OTHER = "other"


class Link:
    """
    Representing a paper's links.
    """
    def __init__(
        self,
        href: str,
        title: str = "",
        tag: LinkEnum = LinkEnum.OTHER,
    ):
        """
        Constructs a `Link` with the specified link metadata.
        """
        self.href = href
        self.title = title
        self.tag = tag

    def __str__(self) -> str:
        return self.href

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
            online_date: datetime,
            update_date: datetime,
            links: list[Link] | list[str],
            comment: str = "",
            venue: str = "",
            doi: str = "",
            primary_category: str = "",
            categories: list[str] = [],  # later process # noqa
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
        self.online_date = online_date
        self.update_date = update_date
        self.links = [
            Link(link) if isinstance(link, str) else link for link in links
        ]
        self.links = [self.url, self.pdf_url] + self.links
        self.comment = comment
        self.venue = venue
        self.doi = doi
        self.primary_category = primary_category
        self.categories = categories or list()
        self.authors = [
            Author(a) if isinstance(a, str) else a for a in authors
        ]

    @property
    def code_link(self):
        for link in self.links:
            if link.tag == LinkEnum.CODE:
                return link
        return Link("", tag=LinkEnum.CODE)

    def download(self, link_type: LinkEnum, folder: str, filename: str = ""):
        if link_type == LinkEnum.CODE:
            raise NotImplementedError("Download code link is not implemented.")
        if link_type == LinkEnum.PDF:
            link = self.pdf_url
            filename = filename or f"{format_valid_title(self)}.pdf"
            path = os.path.join(folder, filename)
            downloaded, _ = urlretrieve(link.href, path)
            return downloaded
        else:
            raise ValueError(f"Link type {link_type} is not supported.")

    def __str__(self) -> str:
        return self.url.href

    def __repr__(self) -> str:
        return (
            "{}("
            "url={}, pdf_url={}, "
            "title={}, authors={}, abstract={}, "
            "online_date={}, update_date={}, "
            "links={}, comment={}, venue={}, doi={}, "
            "primary_category={}, categories={}"
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
            repr(self.venue),
            repr(self.doi),
            repr(self.primary_category),
            repr(self.categories),
        )

    def __eq__(self, other) -> bool:
        if isinstance(other, Paper):
            return self.url.href == other.url.href
        return False


def format_valid_title(paper: Paper) -> str:
    title = (
        paper.title
        .replace(": ", "：").replace("? ", "？").replace("?", "？")
        .replace("<", "").replace(">", "")
        .replace('"', "'").replace("/", "").replace("\\", "")
        .replace("|", "or").replace("*", "Star")
    )
    if title != paper.title:
        logger.warning(f"Original title: {paper.title}. New title: {title}.")
    return title


class Result(arxiv.Result):
    fields = (
        "entry_id", "updated", "published", "title", "authors", "summary",
        "comment", "journal_ref", "doi", "primary_category", "categories",
        "links", "pdf_url",
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.metainfo = Metainfo()
        self.local_plugin_data = {}

    def update_metainfo(self, metainfo: Metainfo | dict):
        if isinstance(metainfo, Metainfo):
            self.metainfo = deepcopy(metainfo)
        if isinstance(metainfo, dict):
            orig_dict = asdict(self.metainfo)
            for key, val in orig_dict.items():
                orig_dict[key] = metainfo.get(key, val)
            self.metainfo = Metainfo(**orig_dict)

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

    @classmethod
    def create_from_arxiv_result(cls, arxiv_result: arxiv.Result):
        result = cls(
            entry_id=arxiv_result.entry_id,
            updated=arxiv_result.updated,
            published=arxiv_result.published,
            title=arxiv_result.title,
            authors=arxiv_result.authors,
            summary=arxiv_result.summary,
            comment=arxiv_result.comment,
            journal_ref=arxiv_result.journal_ref,
            doi=arxiv_result.doi,
            primary_category=arxiv_result.primary_category,
            categories=arxiv_result.categories,
            links=arxiv_result.links,
        )
        return result

    def todict(self):
        links = [
            {
                "href": ln.href,
                "title": ln.title,
                "rel": ln.rel,
                "content_type": ln.content_type,
            } for ln in self.links
        ]
        return {
            "entry_id": self.entry_id,
            "pdf_url": self.pdf_url,
            "updated": self.updated.strftime("%Y-%m-%d, %H:%M:%S"),
            "published": self.published.strftime("%Y-%m-%d, %H:%M:%S"),
            "title": self.title,
            "authors": [a.name for a in self.authors],
            "summary": self.summary,
            "comment": self.comment,
            "journal_ref": self.journal_ref,
            "doi": self.doi,
            "primary_category": self.primary_category,
            "categories": self.categories,
            "links": links,
            "local_plugin_data": {
                plugin_name: asdict(plugin_data)
                for plugin_name, plugin_data in self.local_plugin_data.items()
            },
            "metainfo": asdict(self.metainfo),
        }

    def check_plugin_class(self, plugin_name: str, plugin_class: type):
        if plugin_name not in self.local_plugin_data:
            logger.warning(f"Plugin {plugin_name} not found, init one.")
            self.add_plugin_data(plugin_class())
        plugin_data = self.local_plugin_data[plugin_name]
        if isinstance(plugin_data, dict):
            plugin_data = plugin_class(**plugin_data)
            self.local_plugin_data[plugin_name] = plugin_data


def init_results_plugin_datas(results: list[Result],
                              plugin_class: type):
    for result in results:
        result.add_plugin_data(plugin_class())
    results = check_results_plugin_class(results, plugin_class)
    return results


def reset_results_plugin_datas(results: list[Result],
                               plugin_datas: list[BasePluginData]):
    for result, data in zip(results, plugin_datas):
        result.reset_plugin_data(data)
    return results


def check_results_plugin_class(results: list[Result],
                               plugin_class: type):
    plugin_name: str = plugin_class.plugin_name
    for result in results:
        result.check_plugin_class(plugin_name, plugin_class)
    return results
