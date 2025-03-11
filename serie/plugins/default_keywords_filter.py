
from dataclasses import dataclass
from serie.utils.logging import create_logger
from serie.base.plugin import (
    BasePlugin, BaseKeywordsFilterData, GlobalPluginData
)
from serie.base.paper import Paper


logger = create_logger(__name__)


def plugin_name():
    return "DefaultKeywordsFilter"


@dataclass
class DefaultKeywordsFilterData(BaseKeywordsFilterData):
    plugin_name: str = plugin_name()


class DefaultKeywordsFilter(BasePlugin):
    """
    This plugin is used to parse keywords from the papers.

    Args:
        keywords: A dictionary of keywords to be parsed with format:
            {keyword: [subkeyword1, subkeyword2, ...]}.
            The keys are the
            the real keyword for record and the values are the list of
            subkeywords that should be checked.
        ignorance: A dictionary of keywords to be ignored with format:
            {keyword: [subkeyword1, subkeyword2, ...]}.
            For a paper recognized with `keyword`, if any of the
            `subkeywords` is found, the paper will be ignored.
            The keys are the real keyword presented in the argument
            `keywords` and the values are the list of subkeywords that should
            be checked.

    Examples:
        # This plugin will check for the presence of "subkeyword1" and
        # "subkeyword2" in the papers and if found, it will add "keyword1"
        # to the keywords list.
        >>> keywords = {
        ...     "keyword1": ["subkeyword1", "subkeyword2"],
        ...     "keyword2": ["subkeyword3", "subkeyword4"]
        ... }
        # For keyword "keyword1", if "subkeyword5" or "subkeyword6" is found,
        # the paper will be ignored.
        >>> ignorance = {
        ...     "keyword1": ["subkeyword5", "subkeyword6"]
        ... }
        >>> plugin = DefaultKeywordsFilter(keywords, ignorance)
    """

    def __init__(self,
                 keywords: dict[str, list[str]] | None = None,
                 ignorance: dict[str, list[str]] | None = None,
                 version: str = "",
                 dependencies: list[str] | None = None,
                 **kwargs) -> None:
        super().__init__(version, dependencies, **kwargs)
        self.keywords = keywords or {}
        self.ignorance = ignorance or {}

    def process(self,
                papers: list[Paper],
                global_plugin_data: GlobalPluginData) -> list[Paper]:
        for paper in papers:
            paper.add_plugin_data(DefaultKeywordsFilterData())
        papers = self.process_keywords(papers)
        papers = self.process_ignorance(papers)
        return papers

    def process_keywords(self, papers: list[Paper]):
        for paper in papers:
            plugin_data = paper.get_plugin_data(plugin_name())
            assert isinstance(plugin_data, DefaultKeywordsFilterData)
            for keyword in self.keywords.keys():
                subkeywords = self.keywords[keyword]
                if any(check_paper_contains_keyword(paper, kw)
                       for kw in subkeywords):
                    if keyword not in plugin_data.keywords:
                        plugin_data.keywords.append(keyword)
        return papers

    def process_ignorance(self, papers: list[Paper]):
        for paper in papers:
            plugin_data = paper.get_plugin_data(plugin_name())
            assert isinstance(plugin_data, DefaultKeywordsFilterData)
            for keyword in self.ignorance.keys():
                subkeywords = self.ignorance[keyword]
                if any(check_paper_contains_keyword(paper, kw)
                       for kw in subkeywords):
                    if (
                            keyword not in plugin_data.ignorance
                            and keyword in plugin_data.keywords):
                        plugin_data.ignorance.append(keyword)
        return papers


def parse_keywords_for_papers(papers: list[Paper], keywords: list[str]):
    for paper in papers:
        paper.add_plugin_data(DefaultKeywordsFilterData())
        plugin_data = paper.get_plugin_data(plugin_name())
        assert isinstance(plugin_data, DefaultKeywordsFilterData)
        for keyword in keywords:
            if (
                    check_paper_contains_keyword(paper, keyword)
                    and (keyword not in plugin_data.keywords)):
                plugin_data.keywords.append(keyword)
    return papers


def check_paper_contains_keyword(paper: Paper, keyword: str):
    if "&" in keyword:
        keywords = keyword.split("&")
        keywords = [kw.strip() for kw in keywords]
        if all(check_paper_contains_keyword(paper, kw) for kw in keywords):
            return True
    else:
        if (
                keyword.lower() in paper.abstract.lower()
                or keyword.lower() in paper.title.lower()):
            return True
    return False


def filter_papers_by_keyword(papers: list[Paper], keyword: str):
    if '&' in keyword:
        return _filter_papers_by_and_logic(papers, keyword)
    return _filter_papers(papers, keyword)


def _filter_papers_by_and_logic(papers: list[Paper], keyword: str):
    assert '&' in keyword
    keywords = keyword.split('&')
    keywords = [kw.strip() for kw in keywords]
    filtered_papers = list(
        filter(
            lambda r: all(kw in r.abstract.lower() or kw in r.title.lower()
                          for kw in keywords),
            papers
        )
    )
    return filtered_papers


def _filter_papers(papers: list[Paper], keyword: str):
    filtered_papers = list(
        filter(
            lambda r: (keyword in r.abstract.lower()
                       or keyword in r.title.lower()),
            papers
        )
    )
    return filtered_papers


def ignore_by_keywords_list(papers: list[Paper], keywords: list[str]):
    logger.info(f"Ignoring {keywords}")
    for k in keywords:
        papers = _ignore_papers(papers, k)
    return papers


def _ignore_papers(papers: list[Paper], keyword: str):
    filtered_papers = list(
        filter(
            lambda r: (keyword not in r.abstract.lower()
                       and keyword not in r.title.lower()),
            papers
        )
    )
    return filtered_papers
