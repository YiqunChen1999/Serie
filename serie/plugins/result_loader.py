
import os
from dataclasses import dataclass

from serie.utils.logging import create_logger
from serie.utils.io import load_jsonl
from serie.base.paper import Paper, create_paper_from_dict
from serie.base.plugin import BasePlugin, BasePluginData, GlobalPluginData


logger = create_logger(__name__)


def plugin_name():
    return "ResultLoader"


@dataclass
class ResultLoaderData(BasePluginData):
    plugin_name: str = plugin_name()
    papers: list[Paper] | None = None


class ResultLoader(BasePlugin):
    def __init__(self, output_directory: str):
        self.output_directory = output_directory

    def process(self,
                papers: list[Paper],
                global_plugin_data: GlobalPluginData) -> list[Paper]:
        return papers or self.load_papers()

    def load_papers(self) -> list[Paper]:
        path = os.path.join(self.output_directory, 'papers.jsonl')
        logger.info(f"Loading results from {path}")
        results = load_jsonl(path)
        return [create_paper_from_dict(r) for r in results]
