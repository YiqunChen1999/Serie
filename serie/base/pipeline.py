
import os.path as osp
from dataclasses import dataclass

from serie.utils.io import import_config
from serie.utils.logging import create_logger
from serie.config import Configs
from serie.core.run import forward_plugins


logger = create_logger(__name__)


@dataclass
class BasePipelineData:
    pipeline_name: str
    type: str = "local"


class BasePipeline:
    def __init__(self,
                 config_path: str,
                 version: str = "",
                 dependencies: list[str] | None = None,
                 **kwargs) -> None:
        config_path = osp.abspath(config_path)
        self.config_path = config_path
        self.version = version
        self.dependencies = dependencies or []
        if osp.exists(config_path):
            cfg = import_config(self.config_path)
            if self.__class__.__name__ in cfg.keys():
                cfg: dict = cfg[self.__class__.__name__]
            else:
                logger.warning(
                    f"{self.__class__.__name__} is not in the config file."
                )
                cfg = {}
        else:
            logger.warning(f"{config_path} does not exist.")
            cfg = {}
        self.plugins: list[str] = cfg.get("plugins", self.default_plugins)
        self.plugins_configs: dict[str, dict] = cfg.get("configs", dict())
        plugins_string = ''.join(
            [f'  - {plugin}\n' for plugin in self.plugins]
        )
        logger.info(
            f"Pipeline {self.__class__.__name__} is initialized. Running with "
            f"plugins: \n{plugins_string}"
        )

    def process(self, cfgs: Configs):
        return forward_plugins(cfgs, self.plugins, self.plugins_configs)

    def __call__(self, cfgs: Configs):
        return self.process(cfgs)

    @property
    def default_plugins(self):
        raise NotImplementedError("`default_plugins` is not implemented")
