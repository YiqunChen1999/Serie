
import os
import os.path as osp
from dataclasses import dataclass
from serie.utils.logging import create_logger
from serie.base.plugin import (
    BaseKeywordsFilterData, BasePlugin, BasePluginData, PluginStatus,
    GlobalPluginData
)
from serie.base.paper import Paper
from serie.base.constants import UNIQUE_PAPER_SIGNATURE
from serie.plugins.markdown_table_maker import (
    MarkdownTableMaker, MarkdownTableMakerData
)
from serie.utils.io import save_jsonl


logger = create_logger(__name__)


def plugin_name():
    return "ResultSaver"


OBSIDIAN_NAVIGATION = """
```dataviewjs
const folder = dv.current().file.folder;

let files = (
    dv.pages(`"${folder}"`)
    .where(p => !p.file.name.includes("_Navigation"))
    .sort(p => p.file.name)
    .map(p => [
        p.file.link + " (" + p.counts.toString() + ")"
    ]))

let num_cols = 3
let num_items = files.length
let reshaped = []

for (let i=0; i < num_items; i += num_cols){
    reshaped.push(files.slice(i, i+num_cols));
}

dv.table(["#_hide_header ", "#_hide_header ", "#_hide_header "],
    reshaped
);
```

"""

METAINFO_TEMPLATE = (
    "---\n"
    "DONE: false\n"
    "counts: {counts}\n"
    "---\n\n"
)

PAPER_INFO_STRING = """
{UNIQUE_PAPER_SIGNATURE}
## {title}
- authors: {authors}
- venue: {venue}
- url: {url}
- pdf url: {pdf_url}
- publish date: {online_date}
- updated date: {update_date}
- primary category: {primary_category}
- categories: {categories}
- comment: {comment}
- doi: {doi}
{save_as_item}

### ABSTRACT
{abstract}

{save_as_text}

"""


@dataclass
class ResultSaverData(BasePluginData):
    plugin_name: str = "ResultSaver"
    output_directory: str = ""
    markdown_directory: str = ""


class ResultSaver(BasePlugin):
    def __init__(self,
                 output_directory: str,
                 markdown_directory: str,
                 keywords_filter_plugin: str = "",
                 overwrite: bool = False,
                 version: str = "",
                 dependencies: list[str] | None = None,
                 **kwargs) -> None:
        super().__init__(overwrite, version, dependencies, **kwargs)
        self.output_directory = output_directory
        self.markdown_directory = markdown_directory
        self.keywords_filter_plugin = keywords_filter_plugin
        os.makedirs(self.output_directory, exist_ok=True)
        os.makedirs(self.markdown_directory, exist_ok=True)

    def check_status(
            self, papers: list[Paper], global_plugin_data: GlobalPluginData):
        dates = [
            p.update_date.strftime("%Y-%m-%d") for p in papers
        ]
        dates = list(set(dates))
        for date in dates:
            folder = osp.join(self.markdown_directory, date)
            if not osp.exists(folder):
                os.makedirs(folder, exist_ok=True)
            elif len(os.listdir(folder)) > 0:
                self.status = PluginStatus.DONE
                return
            else:
                self.status = PluginStatus.TODO

    def process(self,
                papers: list[Paper],
                global_plugin_data: GlobalPluginData):
        if len(papers) == 0:
            return papers
        markdown_table = global_plugin_data.data.get("MarkdownTableMaker", "")
        logger.info(f"Saving {len(papers)} papers ...")
        self.save_papers(papers, markdown_table)
        return papers

    def save_papers(self, papers: list[Paper], markdown_table: str):
        self.save_jsonl(papers)
        self.save_markdown_file(papers, markdown_table)
        self.save_text(papers)
        self.save_by_keywords(papers)
        self.make_navigation_list(papers)

    def save_jsonl(self, papers: list[Paper]):
        path = os.path.join(self.output_directory, 'papers.jsonl')
        save_jsonl(path, [r.asdict() for r in papers])

    def save_markdown_file(self, papers: list[Paper], markdown_table: str):
        if not markdown_table:
            return
        path = os.path.join(self.markdown_directory, 'papers.md')
        logger.info(f"Saving markdown table to {path}")
        with open(path, 'w') as fp:
            fp.write(METAINFO_TEMPLATE.format(counts=len(papers)))
            fp.write(markdown_table)

    def save_text(self, papers: list[Paper]):
        path = os.path.join(self.output_directory, 'papers.txt')
        logger.info(f"Saving text to {path}")
        with open(path, 'w') as fp:
            for i, result in enumerate(papers):
                fp.write(self.format_text_result(result, i))

    def save_by_keywords(self, papers: list[Paper]):
        plugin_name = self.keywords_filter_plugin
        keywords: list[str] = list()
        for result in papers:
            plugin_data = result.get_plugin_data(plugin_name)
            assert isinstance(plugin_data, BaseKeywordsFilterData)
            keywords.extend(plugin_data.keywords)
        keywords = list(set(keywords))
        for keyword in keywords:
            dates = [
                p.update_date.strftime("%Y-%m-%d") for p in papers
            ]
            dates = list(set(dates))
            for date in dates:
                papers_this_date = [
                    p for p in papers
                    if p.update_date.strftime("%Y-%m-%d") == date
                ]
                self.save_by_keyword(papers_this_date, keyword)

    def save_by_keyword(self, papers: list[Paper], keyword: str):
        plugin_name = self.keywords_filter_plugin
        filtered_papers: list[Paper] = []
        for result in papers:
            plugin_data = result.get_plugin_data(plugin_name)
            assert isinstance(plugin_data, BaseKeywordsFilterData)
            if keyword in plugin_data.ignorance:
                continue
            if keyword in plugin_data.keywords:
                filtered_papers.append(result)
        if not filtered_papers:
            logger.info(f"No papers found for keyword: {keyword}")
            return
        logger.info(
            f"Saving {len(filtered_papers)} papers for keyword: {keyword}"
        )
        paper_infos = [self.format_text_result(r) for r in filtered_papers]
        paper_infos = "\n\n# Abstract\n" + "".join(paper_infos)
        markdown_plugin = MarkdownTableMaker()
        global_plugin = GlobalPluginData()
        markdown_plugin(filtered_papers, global_plugin)
        table: str = global_plugin.data[MarkdownTableMakerData.plugin_name]
        content: str = (
            METAINFO_TEMPLATE.format(counts=len(filtered_papers))
            + table
            + "\n\n"
            + paper_infos
        )
        dates = [p.update_date.strftime("%Y-%m-%d") for p in filtered_papers]
        dates = list(set(dates))
        assert len(dates) == 1
        folder = osp.join(self.markdown_directory, dates[0])
        os.makedirs(folder, exist_ok=True)
        path = osp.join(folder, f'papers @ {keyword}.md')
        logger.info(f"Saving markdown file to {path}")
        with open(path, 'w') as fp:
            fp.write(content)

    def make_navigation_list(self, papers: list[Paper]):
        path = osp.join(self.markdown_directory, "_Navigation.md")
        osp.basename(self.markdown_directory)
        dates = [p.update_date.strftime("%Y-%m-%d") for p in papers]
        dates = list(set(dates))
        date = dates[0]
        logger.info(f"Making navigation list at {path}")
        with open(path, 'w') as fp:
            fp.write('---\n')
            fp.write(f'date: {date}\n')
            fp.write('---\n\n')
            fp.write(OBSIDIAN_NAVIGATION)
        return path

    def format_text_result(
            self, result: Paper, index: int | None = None) -> str:
        authors = [r.name for r in result.authors]
        save_as_item = "\n".join([
            r.string_for_saving() for r in result.local_plugin_data.values()
            if r.save_as_item
        ])
        save_as_text = "\n\n".join([
            r.string_for_saving() for r in result.local_plugin_data.values()
            if r.save_as_text
        ])
        string = PAPER_INFO_STRING.format(
            UNIQUE_PAPER_SIGNATURE=UNIQUE_PAPER_SIGNATURE,
            title=result.title,
            authors=', '.join(authors),
            venue=result.venue,
            url=result.url.href,
            pdf_url=result.pdf_url.href,
            online_date=result.online_date,
            update_date=result.update_date,
            primary_category=result.primary_category,
            categories=result.categories,
            comment=result.comment,
            doi=result.doi,
            abstract=result.abstract,
            save_as_item=save_as_item,
            save_as_text=save_as_text,
        )
        if index is not None:
            string = f"Index: {index}\n" + string
        return string
