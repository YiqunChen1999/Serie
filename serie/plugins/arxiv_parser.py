
import os.path as osp
from dataclasses import dataclass

import arxiv
from serie.base.paper import Link, LinkEnum, Paper
from serie.base.plugin import BasePluginData, GlobalPluginData, BasePlugin
from serie.utils.io import load_json
from serie.utils.logging import create_logger


logger = create_logger(__name__)


@dataclass
class ArxivParserData(BasePluginData):
    plugin_name: str = "ArxivParser"


@dataclass
class ArxivParserFromJsonFileData(BasePluginData):
    plugin_name: str = "ArxivParserFromJsonFile"
    metainfo: dict | None = None


class ArxivParser(BasePlugin):
    def __init__(
            self,
            datetime: str,
            categories: str = "(cat:cs.CV OR cat:cs.AI OR cat:cs.LG)",
            query: str = "",
            json_file: str = "",
            overwrite: bool = False,
            version: str = "",
            dependencies: list[str] | None = None,
            **kwargs):
        super().__init__(overwrite, version, dependencies, **kwargs)
        self.categories = categories
        self.datetime = datetime

        self.json_file = osp.abspath(json_file) if json_file else ""
        if json_file and not osp.exists(json_file):
            raise FileNotFoundError(f"{json_file} does not exist.")
        if not self.json_file and not query:
            query = f"{self.categories} AND {self.datetime}"
        self.query = query

    def process(self,
                papers: list[Paper],
                global_plugin_data: GlobalPluginData) -> list[Paper]:
        if self.query:
            papers.extend(search(self.query))
        if self.json_file:
            items: list[dict] = load_json(self.json_file)
            self.check_metas(items)
            queries = [f"id:{item['id']}" for item in items]
            results = search(" OR ".join(queries))
            for result in results:
                item_of_result = None
                for item in items:
                    if item["id"] in result.url.href:
                        item_of_result = item
                        break
                if item_of_result is None:
                    logger.warning(f"Item not found for {result.url}")
                    continue
                result.version = item_of_result["version"]
                for key, val in item_of_result["local_plugin_data"].items():
                    if key not in result.local_plugin_data.keys():
                        result.local_plugin_data[key] = val
                    else:
                        data = result.get_plugin_data(key)
                        assert data is not None
                        for k, v in val.items():
                            setattr(data, k, v)
            papers.extend(results)
        papers = self.deduplicate(papers)
        return papers

    def deduplicate(self, papers: list[Paper]):
        logger.info(f"Deduplicating papers for {len(papers)} items papers...")
        if len(papers) == 0:
            return papers
        if len(papers) == 1:
            logger.info("Only one paper found. No deduplication needed.")
            return papers
        # Deduplicate papers based on URL
        # Use a dictionary to track unique URLs
        # and keep the first occurrence of each URL
        # This will remove duplicates while preserving the order
        # of the original list
        mapping = {}
        for p in papers:
            if p.url.href not in mapping.keys():
                mapping[p.url.href] = p
        papers = list(mapping.values())
        logger.info(f"Deduplication complete. {len(papers)} unique papers.")
        return papers

    def check_metas(self, metainfos: list[dict]):
        for item in metainfos:
            if "venue" not in item:
                raise ValueError(f"Venue not found in {item}.")
            if "url" not in item:
                raise ValueError(f"URL not found in {item}.")
            if "tags" not in item:
                raise ValueError(f"Tags not found in {item}.")
            link: str = item["url"]
            item["id"] = link.split("/")[-1].split("v")[0]
            ver = link.split("/")[-1]
            ver = ver.split("v")[-1] if "v" in ver else "1"
            item["version"] = f"v{ver}"
            logger.debug(f"Check item: {item}")


def search(query: str) -> list[Paper]:
    results = []
    client = arxiv.Client(num_retries=10, delay_seconds=3)
    for i in range(10):
        search = arxiv.Search(query=query,
                              sort_by=arxiv.SortCriterion.LastUpdatedDate,
                              max_results=10000)
        results = list(client.results(search))
        logger.info(f"Get {len(results)} items.")
        if len(results):
            logger.info(f"Range: {results[-1].updated} {results[0].updated}")
            break
    results = [create_paper_from_arxiv(r) for r in results]
    return results


def create_paper_from_arxiv(result: arxiv.Result):
    links = []
    for L in result.links:
        link = Link(href=L.href, title=L.title or "")
        if "pdf" in L.rel:
            link.tag = LinkEnum.PDF
        links.append(link)
    return Paper(
        url=result.entry_id,
        online_date=result.published,
        update_date=result.updated,
        title=result.title,
        authors=[a.name for a in result.authors],
        abstract=result.summary,
        comment=result.comment or "",
        venue=result.journal_ref or "arxiv",
        doi=result.doi or "",
        primary_category=result.primary_category,
        categories=result.categories,
        links=links,
        pdf_url=result.pdf_url or "",
    )
