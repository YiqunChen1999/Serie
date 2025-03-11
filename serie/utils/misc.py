
import sys
import inspect
import os.path as osp
from time import sleep
import openai
from openai import OpenAI

from serie.utils.logging import create_logger


logger = create_logger(__name__)


def get_class_config_file_path(cls, file_name: str = ""):
    json_path = get_class_file_path(cls)
    json_path = json_path.replace("serie/serie", "serie/configs")
    if not osp.exists(json_path):
        json_path = json_path.replace(".py", ".json")
    if file_name:
        json_path = osp.join(osp.dirname(json_path), file_name)
    return json_path


def get_class_file_path(cls):
    module = sys.modules[cls.__module__]
    file_path = inspect.getfile(module)
    return file_path


def wait_batch_task(client: OpenAI,
                    batch: openai.types.Batch,
                    interval: float = 10):
    while True:
        sleep(interval)
        job = client.batches.retrieve(batch.id)
        if job.status in ("validating", "in_progress", "finalizing"):
            logger.info(f"Completion status: {job.status}, "
                        f"batch id: {batch.id}")
            continue
        else:
            logger.info(
                f"Complete batches task exists with status: {job.status}.\n"
                f"Details: {job}")
            break
    return client.batches.retrieve(batch.id)


def batch_task_success(batch: openai.types.Batch):
    return batch.status in ("completed",)
