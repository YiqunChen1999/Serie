
import re
from dataclasses import dataclass

from serie.base.plugin import BasePlugin, BasePluginData, GlobalPluginData
from serie.base.paper import LinkEnum, Paper, Link


def plugin_name():
    return "GitHubLinkParser"


@dataclass
class GitHubLinkParserData(BasePluginData):
    plugin_name: str = "GitHubLinkParser"
    code_link: str = ""
    save_as_item: bool = True

    def string_for_saving(self, *args, **kwargs) -> str:
        return f"- code link: {self.code_link}"


class GitHubLinkParser(BasePlugin):
    def process(self,
                papers: list[Paper],
                global_plugin_data: GlobalPluginData) -> list[Paper]:
        for paper in papers:
            plugin_name = GitHubLinkParserData.plugin_name
            data = GitHubLinkParserData()
            if plugin_name not in paper.local_plugin_data:
                paper.add_plugin_data(data)
            data.code_link = (
                self.parse_github_link(paper.abstract)
                or self.parse_github_link(paper.comment)
            )
            paper.links.append(Link(data.code_link, tag=LinkEnum.CODE))
        return papers

    def parse_github_link(self, text: str | None) -> str:
        if text is None:
            return ""
        pattern = r'https?:\/\/(?:www\.)?github\.com\/[\w-]+\/[\w-]+|(?:www\.)?github\.com\/[\w-]+\/[\w-]+|(?:www\.)?.*github\.io\/[\w-]+\/[\w-]+|https?:\/\/(?:www\.)?.*github\.io\/[\w-]+\/[\w-]+'  # noqa
        matches: list[str] = re.findall(pattern, text)
        if len(matches) == 0:
            return ""
        link = matches[0]
        if link.startswith('github.com'):
            link = 'https://' + link
        return link
