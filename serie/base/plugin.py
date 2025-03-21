
from enum import Enum
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from serie.utils.logging import create_logger


logger = create_logger(__name__)


class PluginStatus(Enum):
    TODO = "todo"
    DONE = "done"
    ERROR = "error"
    RUNNING = "running"
    SKIPPED = "skipped"


@dataclass
class BasePluginData:
    plugin_name: str
    type: str = "local"
    save_as_item: bool = False
    save_as_text: bool = False

    def string_for_saving(self, *args, **kwargs) -> str:
        return ""


@dataclass
class GlobalPluginData:
    data = {}


class BasePlugin(ABC):
    def __init__(self,
                 overwrite: bool = False,
                 version: str = "",
                 dependencies: list[str] | None = None,
                 **kwargs) -> None:
        self.version = version
        self.dependencies = dependencies or []
        self.overwrite = overwrite
        self.status = PluginStatus.TODO

    @abstractmethod
    def process(self, papers, global_plugin_data: GlobalPluginData):
        raise NotImplementedError("process method is not implemented")

    def check_status(self, papers, global_plugin_data: GlobalPluginData):
        pass

    def __call__(self, papers, global_plugin_data: GlobalPluginData):
        self.check_status(papers, global_plugin_data)
        if self.status == PluginStatus.DONE:
            if not self.overwrite:
                logger.warning(
                    "Plugin status is DONE and overwrite is False. "
                    "Skipping processing."
                )
                return papers
            else:
                logger.warning(
                    "Plugin status is DONE and overwrite is True. "
                    "Processing again."
                )
        self.status = PluginStatus.RUNNING
        papers = self.process(papers, global_plugin_data)
        self.status = PluginStatus.DONE
        return papers


@dataclass
class BaseKeywordsFilterData(BasePluginData):
    plugin_name: str
    keywords: list[str] = field(default_factory=list)
    ignorance: list[str] = field(default_factory=list)

    def string_for_saving(self, *args, **kwargs) -> str:
        return f"- keywords: {', '.join(self.keywords)}"
