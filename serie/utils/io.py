
import json
import importlib.util

from serie.utils.logging import create_logger, setup_format

setup_format()
logger = create_logger(__name__)


def import_config(path: str) -> dict:
    """
    Import sepcified variable from a .py file or .json file.
    """
    if path.endswith(".py"):
        spec = importlib.util.spec_from_file_location("configs", path)
        if spec is None:
            raise FileNotFoundError(f"File not found: {path}")
        module = importlib.util.module_from_spec(spec)
        assert spec.loader is not None
        spec.loader.exec_module(module)
        return module.config
    elif path.endswith(".json"):
        return load_json(path)
    else:
        raise ValueError(f"Unsupported file type: {path}")


def save_json(path: str, data: dict, **kwargs):
    logger.info(f"Saving data to {path}")
    with open(path, 'w') as fp:
        json.dump(data, fp, **kwargs)


def load_json(path: str):
    logger.info(f"Loading data from {path}")
    with open(path, 'r') as fp:
        data = json.load(fp)
    return data


def save_jsonl(path: str, data: list[dict]):
    logger.info(f"Saving data to {path}")
    with open(path, 'w') as fp:
        for line in data:
            fp.write(json.dumps(line))
            fp.write("\n")
    return path


def load_jsonl(path: str) -> list[dict]:
    logger.info(f"Loading data from {path}")
    lines = []
    with open(path, 'r') as fp:
        for line in fp:
            data = json.loads(line)
            lines.append(data)
    return lines
