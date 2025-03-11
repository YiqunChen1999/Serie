
from serie.config import Configs
from serie.core.run import forward_plugins
from serie.base.pipeline import BasePipeline


class DownloadByParsing(BasePipeline):
    def process(self, cfgs: Configs):
        return forward_plugins(cfgs, self.plugins, self.plugins_configs)

    @property
    def default_plugins(self):
        return [
            "ResultLoader", "MarkdownMetainfoParser", "Downloader"
        ]
