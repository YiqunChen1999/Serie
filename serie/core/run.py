
import os
import time
import inspect

from serie.config import Configs
from serie.utils.logging import create_logger
from serie.base.paper import Paper
from serie.base.plugin import BasePlugin, BasePluginData, GlobalPluginData
from serie.plugins import get_plugin_cls
from serie.utils.io import import_config
from serie.utils.misc import get_class_config_file_path


logger = create_logger(__name__)


def forward_plugins(cfgs: Configs,
                    plugin_names: list[str],
                    plugins_configs: dict[str, dict] | None = None):
    papers = forward_plugins_once(cfgs, plugin_names, plugins_configs)
    for idx in range(cfgs.max_retries_num):
        if len(papers):
            break
        logger.info(f"Retry {idx + 1}/{cfgs.max_retries_num}. "
                    f"Sleeping for {cfgs.sleep_seconds} seconds.")
        time.sleep(cfgs.sleep_seconds)
        papers = forward_plugins_once(cfgs, plugin_names, plugins_configs)
    return papers


def forward_plugins_once(
        cfgs: Configs,
        plugin_names: list[str],
        plugins_configs: dict[str, dict] | None = None) -> list[Paper]:
    papers: list[Paper] = []

    global_plugin_data = GlobalPluginData()
    plugins = [get_plugin_cls(name) for name in plugin_names]
    for cls, name in zip(plugins, plugin_names):
        # first, inspect the arguments of the plugin
        # find the argument from cfgs
        args = prepare_plugins_args_from_configs(cfgs, plugin_names, cls)
        if plugins_configs and name in plugins_configs:
            args.update(plugins_configs[name])
        str_args = "\n".join([f">>>> {k}: {v}" for k, v in args.items()])
        logger.info(
            f"Running plugin {cls.__name__} with following args:\n{str_args}"
        )
        plugin: BasePlugin = cls(**args)
        papers: list[Paper] = plugin(papers, global_plugin_data)
        papers = check_plugin_data_class(papers)
    return papers


def check_plugin_data_class(papers: list[Paper]):
    logger.info("Checking plugin data class...")
    for paper in papers:
        keys = paper.local_plugin_data.keys()
        for key in keys:
            data = paper.local_plugin_data[key]
            data_cls = get_plugin_cls(key + "Data")
            if isinstance(data, dict):
                data: BasePluginData = data_cls(key + "Data", **data)
            else:
                assert isinstance(data, data_cls)
            paper.local_plugin_data[key] = data
    return papers


def prepare_plugins_args_from_configs(
        cfgs: Configs, plugin_names: list[str], cls):
    signature = inspect.signature(cls)
    args = {}
    cfg_path = get_class_config_file_path(cls)
    plugin_config = {}
    if os.path.exists(cfg_path):
        plugin_config = import_config(cfg_path)
        plugin_config: dict = plugin_config.get(cls.__name__, {})
    for name, param in signature.parameters.items():
        if name in cfgs.__dict__:
            args[name] = cfgs.__dict__[name]
        elif name in plugin_config.keys():
            args[name] = plugin_config[name]
    verify_plugin_dependencies(plugin_names, cls, args)
    return args


def verify_plugin_dependencies(plugin_names: list[str], cls, args: dict):
    if "dependencies" in args:
        dependencies = args["dependencies"]
        # using set to check if all dependencies are in the list of plugins
        if not set(dependencies).issubset(plugin_names):
            logger.error(
                f"Plugin {cls.__name__} requires {dependencies} which "
                f"are not in the list of plugins."
            )
        # also check the order of dependencies
        ds = [plugin_names.index(d) for d in dependencies]
        if ds != sorted(ds):
            logger.error(
                f"Plugin {cls.__name__} requires dependencies in a "
                f"specific order."
            )
        for dependency in dependencies:
            if dependency not in plugin_names:
                logger.error(
                    f"Plugin {cls.__name__} requires {dependency} which "
                    f"is not in the list of plugins."
                )
