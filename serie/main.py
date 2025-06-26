"""

"""
from serie.config import parse_cfgs
from serie.utils.io import import_config
from serie.utils.logging import create_logger
from serie.utils.misc import get_class_config_file_path, apply_patch
from serie.pipelines import get_pipeline_cls

logger = create_logger(__name__)


def main():
    apply_patch()
    cfgs = parse_cfgs()
    global logger
    logger = create_logger(__name__, cfgs.output_directory)
    logger.info(f"{cfgs}")
    pipeline_cls = get_pipeline_cls(cfgs.pipeline)
    pipe_json_path = get_class_config_file_path(
        pipeline_cls, cfgs.pipeline_config)
    pipe_cfgs = import_config(pipe_json_path)
    if pipeline_cls.__name__ not in pipe_cfgs.keys():
        raise ValueError(
            f"You are specifying a pipeline that is not in the config file. "
            f"Required: {pipeline_cls.__name__}, "
            f"but got {list(pipe_cfgs.keys())}.\n"
            f"If you want to use the default config, please unset "
            f"`--pipeline`, otherwise, please check the config file: \n"
            f"{pipe_json_path}.\n"
        )
    pipeline = pipeline_cls(pipe_json_path)
    pipeline(cfgs)


if __name__ == '__main__':
    main()
