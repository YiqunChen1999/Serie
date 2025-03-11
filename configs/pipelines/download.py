
import os.path as osp
from serie.base.constants import ROOT_PATH

config = {
    "Download": {
        "plugins": [
            "ArxivParser", "GitHubLinkParser", "Downloader"
        ],
        "configs": {
            "ArxivParser": {
                "json_file": osp.join(ROOT_PATH, "configs/misc/download.json"),
            },
            "Downloader": {
                "dir_pdf": osp.join(ROOT_PATH, "../../Papers"),
                "download_file": osp.join(
                    ROOT_PATH, "configs/misc/download.json"
                ),
                "dir_markdown_note": osp.join(
                    ROOT_PATH, "../../Notebook/论文笔记"
                ),
            },
        }
    },
}
