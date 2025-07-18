
import os.path as osp
from serie.base.constants import ROOT_PATH


config = {
    "DownloadedPaperIndexGenerator": {
        "index_directory": osp.join(ROOT_PATH, "../../Notebook/论文笔记/Index"),
        "papers_note_folders": [
            "论文笔记/NLP",
            "论文笔记/RL",
            "论文笔记/Self-Supervised Learning",
            "论文笔记/Text-to-Image",
            "论文笔记/Tricks",
            "论文笔记/Vision",
            "论文笔记/Vision-Language"
        ]
    }
}
