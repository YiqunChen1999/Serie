
# import platform
import os.path as osp
from dataclasses import field, dataclass
from glob import glob

from serie.utils.logging import create_logger
from serie.base.plugin import BasePlugin, BasePluginData, GlobalPluginData
from serie.base.paper import Link, LinkEnum, Paper, format_valid_title
from serie.base.constants import UNIQUE_PAPER_SIGNATURE


logger = create_logger(__name__)


OBSIDIAN_METAINFO = """---
DONE: false
Journal: {}
Paper: {}
Code: {}
Date: {}
tags: {}
---

"""

OBSIDIAN_NAVIGATION = """
```dataviewjs
let p = dv.pages(dv.current.file) // Retrieve pages with title "path/to/your/notes"
          .where(p => p.file.name == dv.current().file.name) // Filter out the current page
          .sort(p => p.file.ctime) //sort pages by creation time
          .forEach(p => { //for each page
            dv.header(2, "Table of Contents"); // Display page name as header
            const cache = this.app.metadataCache.getCache(p.file.path);//get metadata cache for the page

            if (cache) { // If cache exists
              const headings = cache.headings; // Get the headings from the cache

              if (headings) { //if headings exist
                const filteredHeadings = headings.slice(0) //Start from first heading
                  .filter(h => h.level <= 4) // Filter headings based on level (up to level 4)
                  .map(h => {
                    let indent = " ".repeat(2*(h.level - 1));// Determine indentation based on heading level
                   // let linkyHeading = "[[#" + h.heading + "]]";
    //Correct linking code
    let linkyHeading = "[[" + p.file.name + "#" + h.heading + "|" + h.heading + "]]";


               return indent + "- " + linkyHeading;
                  })
                  .join("\\n");// Join the formatted headings with newlines

                dv.el("div", filteredHeadings);// Display the formatted headings as a div
              }
            }
          });
```
"""  # noqa

PAPER_NOTE_TEMPLATE = """

# 1. 论文笔记
## 1.0. 本地文件
Windows: [{}]({})
MacOS: [{}]({})

## 1.1. 文章摘要

## 1.2. 研究动机

## 1.3. 方法简述

## 1.4. 实验结果

## 1.5. 论文评价

## 1.6. 要点摘要

# 2. 文章总结

## 文章标题

## 2.1 试图解决的问题



## 2.2 是否是新问题



## 2.3. 科学假设



## 2.4 相关研究与值得关注的研究员

### 2.4.1 相关研究



### 2.4.2 如何归类



### 2.4.3 值得关注的研究员



## 2.5 解决方案的关键



## 2.6 实验设计



## 2.7 数据集与代码



## 2.8 实验结果能否支持要验证的科学假设



## 2.9 主要贡献



## 2.10 下一步发展方向


"""


def downloader_information_collector_plugin_name():
    return "DownloaderInformationCollector"


def downloader_given_markdown_plugin_name():
    return "DownloaderGivenMarkdown"


def plugin_name():
    return "Downloader"


@dataclass
class BaseDownloaderData(BasePluginData):
    plugin_name: str = "BaseDownloaderData"
    download: bool = False
    pdf_url: str = ""
    tags: list[str] = field(default_factory=list)
    venue: str = ""
    save_as_item: bool = True
    subdir: str = ""


@dataclass
class DownloaderData(BaseDownloaderData):
    plugin_name: str = plugin_name()


@dataclass
class DownloaderGivenMarkdownData(BaseDownloaderData):
    plugin_name: str = downloader_given_markdown_plugin_name()


@dataclass
class DownloaderInformationCollectorData(BasePluginData):
    plugin_name: str = downloader_information_collector_plugin_name()
    save_as_item: bool = True
    unique_string: str = r"%% DownloaderFromMarkdownData %%"
    downloader_string_checkbox: str = "- [ ] [Downloader] Download"
    downloader_string_tags: str = "- [Downloader] Tags: "
    downloader_string_category: str = "- [Downloader] Category: "
    downloader_string_venue: str = "- [Downloader] Venue: "

    def __post_init__(self):
        self.downloader_string_category = (
            self.downloader_string_category + "\t\t" + self.unique_string
        )
        self.downloader_string_venue = (
            self.downloader_string_venue + "\t\t" + self.unique_string
        )
        self.downloader_string_tags = (
            self.downloader_string_tags + "\t\t" + self.unique_string
        )
        self.downloader_string_checkbox = (
            self.downloader_string_checkbox + "\t\t" + self.unique_string
        )

    def string_for_saving(self, *args, **kwargs) -> str:
        string = "\n".join([
            self.downloader_string_checkbox,
            self.downloader_string_tags,
            self.downloader_string_category,
            self.downloader_string_venue,
        ])
        return string


class DownloaderInformationCollector(BasePlugin):
    def process(
            self, papers: list[Paper], global_plugin_data: GlobalPluginData):
        for paper in papers:
            paper.add_plugin_data(DownloaderInformationCollectorData())
        return papers


class Downloader(BasePlugin):
    def __init__(self,
                 dir_pdf: str = "",
                 dir_code: str = "",
                 dir_markdown_note: str = "",
                 overwrite: bool = False,
                 *args, **kwargs) -> None:
        super().__init__(overwrite, *args, **kwargs)
        self.dir_pdf = dir_pdf
        self.dir_code = dir_code
        self.dir_markdown_note = dir_markdown_note

    def process(
            self, papers: list[Paper], global_plugin_data: GlobalPluginData):
        for paper in papers:
            data = paper.get_plugin_data(DownloaderData.plugin_name)
            assert isinstance(data, DownloaderData)
            if not data.download:
                continue
            pdf_url = paper.pdf_url.href or data.pdf_url
            paper.pdf_url.href = pdf_url
            paper.tags = list(set(data.tags + paper.tags))
            paper.venue = data.venue or paper.venue
            if not pdf_url:
                logger.warning(f"Paper {paper.title} has no pdf url.")
                continue
            if self.dir_pdf:
                paper.download(LinkEnum.PDF, folder=self.dir_pdf)
            if self.dir_code:
                paper.download(LinkEnum.CODE, folder=self.dir_code)
            if not self.dir_markdown_note:
                continue
            save_markdown_note(
                osp.join(self.dir_markdown_note, data.subdir),
                paper.title,
                prepare_markdown_content(paper, self.dir_pdf),
            )
        return papers


class DownloaderGivenMarkdown(BasePlugin):
    def __init__(self,
                 dir_markdown_src: str = "",
                 dir_pdf: str = "",
                 dir_code: str = "",
                 dir_markdown_note: str = "",
                 overwrite: bool = False,
                 *args, **kwargs) -> None:
        super().__init__(overwrite, *args, **kwargs)
        self.dir_markdown_src = dir_markdown_src
        self.dir_pdf = dir_pdf
        self.dir_code = dir_code
        self.dir_markdown_note = dir_markdown_note

    def process(
            self, papers: list[Paper], global_plugin_data: GlobalPluginData):
        for paper in papers:
            data = paper.get_plugin_data(
                DownloaderGivenMarkdownData.plugin_name
            )
            if data is None:
                data = DownloaderGivenMarkdownData()
                paper.add_plugin_data(data)
            assert isinstance(data, DownloaderGivenMarkdownData)
            if not data.download:
                continue
            pdf_url = paper.pdf_url.href or data.pdf_url
            if not pdf_url:
                logger.warning(f"Paper {paper.title} has no pdf url.")
                continue
            if self.dir_pdf:
                paper.download(LinkEnum.PDF, folder=self.dir_pdf)
        return papers

    def parse_file_then_download(self, path: str, papers: list[Paper]):
        with open(path, "r") as f:
            markdown = f.read()
        papers_string = parse_paper(markdown)
        for string in papers_string:
            if download_checkbox_checked(string):
                tags = parse_tags_from_paper(string)
                category = parse_category_from_paper(string)
                venue = parse_venue_from_paper(string)
                code_link = parse_code_link_from_paper(string)
                pdf_link = parse_pdf_url_from_paper(string)
                paper = match_paper(pdf_link, papers)
                paper.tags = list(set(tags + paper.tags))
                paper.primary_category = category
                paper.venue = venue
                paper.links.append(Link(code_link, tag=LinkEnum.CODE))
                data = DownloaderGivenMarkdownData(
                    download=True, pdf_url=pdf_link, tags=tags, venue=venue
                )
                paper.add_plugin_data(data)
                pdf_url = paper.pdf_url.href or pdf_link
                if not pdf_url:
                    logger.warning(f"Paper {paper.title} has no pdf url.")
                    continue
                if self.dir_pdf:
                    paper.download(LinkEnum.PDF, folder=self.dir_pdf)
                if self.dir_code:
                    paper.download(LinkEnum.CODE, folder=self.dir_code)
                save_markdown_note(
                    self.dir_markdown_note, format_valid_title(paper),
                    prepare_markdown_content(paper, self.dir_pdf)
                )
        return papers

    def find_from_local_file(self):
        paths = glob(f"{self.dir_markdown_src}/*.md")
        return paths


def save_markdown_note(dir_markdown_note: str, title: str, content: str):
    path = osp.join(dir_markdown_note, f"{title}.md")
    if not osp.exists(path):
        with open(path, 'w') as fp:
            fp.write(content)
        logger.info(f"Markdown file saved to {path}")
    else:
        logger.warning(f"Markdown file exists, I won't overwrite it:\n{path}")


def prepare_markdown_content(paper: Paper, dir_pdf: str):
    def win_path(dir_pdf: str, filename: str):
        return (osp.abspath(osp.join(dir_pdf, filename))
            .replace('/', "\\")  # bad way, need refactor.
            .replace("\\mnt\\c", "file:///C:")
            .replace("\\mnt\\d", "file:///D:")
            .replace("\\mnt\\e", "file:///E:")
            .replace("\\mnt\\f", "file:///F:")
            .replace("\\mnt\\g", "file:///G:")
            .replace("\\mnt\\h", "file:///H:")
            .replace("\\mnt\\i", "file:///I:")
        )

    def mac_path(dir_pdf: str, filename: str):
        return "file://" + osp.join(osp.abspath(dir_pdf), filename).replace(" ", "%20")

    filename = paper.title + ".pdf"
    meta = OBSIDIAN_METAINFO.format(
        paper.venue, paper.url.href, paper.code_link.href,
        paper.online_date.strftime("%Y-%m-%d")[:10],
        "\n"+"\n".join([" - "+t for t in paper.tags])
    )
    temp = PAPER_NOTE_TEMPLATE.format(
        filename, win_path(dir_pdf, filename),
        filename, mac_path(dir_pdf, filename)
    )
    # content = meta + OBSIDIAN_NAVIGATION + temp
    content = meta + temp
    return content


def match_paper(link: str, papers: list[Paper]) -> Paper:
    paperid = link.split("/")[-1].split("v")[0]
    for paper in papers:
        if paper.url is None:
            continue
        if paperid in paper.url.href:
            return paper
    raise ValueError(f"Paper not found for link: {link}")


def download_checkbox_checked(result: str) -> bool:
    return "- [x] [downloader] download" in result.lower()


def parse_tags_from_paper(result: str):
    tags = ""
    pattern = DownloaderInformationCollectorData.downloader_string_tags
    for line in result.split("\n"):
        if pattern in line:
            tags = line.replace(pattern, "").strip().split(",")
    tags = [tag.strip() for tag in tags]
    return tags


def parse_category_from_paper(result: str):
    category = ""
    pattern = (
        DownloaderInformationCollectorData.downloader_string_category
    )
    for line in result.split("\n"):
        if pattern in line:
            category = line.replace(pattern, "").strip()
    return category


def parse_venue_from_paper(result: str):
    venue = ""
    pattern = (
        DownloaderInformationCollectorData.downloader_string_venue
    )
    for line in result.split("\n"):
        if pattern in line:
            venue = line.replace(pattern, "").strip()
    return venue


def parse_pdf_url_from_paper(result: str):
    pdf_link = ""
    pattern = "paper pdf link"
    for line in result.split("\n"):
        if pattern in line.lower():
            pdf_link = line.split(pattern)[-1].strip(":").strip()
    return pdf_link


def parse_code_link_from_paper(result: str):
    code_link = ""
    pattern = "code link"
    for line in result.split("\n"):
        if pattern in line.lower():
            code_link = line.split(pattern)[-1].strip(":").strip()
    return code_link


def parse_paper(markdown: str):
    papers = markdown.split(UNIQUE_PAPER_SIGNATURE)
    return papers[1:]
