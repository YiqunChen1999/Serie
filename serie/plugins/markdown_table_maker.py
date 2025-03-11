
from dataclasses import dataclass
from serie.base.plugin import BasePlugin, BasePluginData, GlobalPluginData
from serie.base.paper import Paper


TABLE_HEADER = [
    'title', 'primary category', 'paper abstract link', 'code link'
]


def table_header():
    global TABLE_HEADER
    return TABLE_HEADER[:]


def plugin_name():
    return "MarkdownTableMaker"


@dataclass
class MarkdownTableMakerData(BasePluginData):
    type: str = "global"
    plugin_name: str = "MarkdownTableMaker"
    table = ""


class MarkdownTableMaker(BasePlugin):
    def process(self,
                papers: list[Paper],
                global_plugin_data: GlobalPluginData):
        table = self.make_table(papers)
        global_plugin_data.data[MarkdownTableMakerData.plugin_name] = table
        return papers

    def make_table(self,
                   papers: list[Paper],
                   headers: list[str] | None = None) -> str:
        if headers is None:
            headers = table_header()

        table = f"| Index | {' | '.join(headers)} |\n"
        table += f"| --- | {' | '.join(['---' for _ in headers])} |\n"

        for idx, paper in enumerate(papers):
            code_link: str = paper.code_link.href
            row = [
                str(idx + 1),
                f"[[#{paper.title}]]",
                paper.primary_category,
                paper.url.href,
                code_link
            ]
            table += f"| {' | '.join(row)} |\n"

        return table
