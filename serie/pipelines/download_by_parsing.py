
from serie.base.pipeline import BasePipeline


class DownloadByParsing(BasePipeline):
    @property
    def default_plugins(self):
        return [
            "ResultLoader", "DownloaderGivenMarkdown", "Downloader"
        ]
