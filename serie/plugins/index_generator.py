
import os.path as osp

from serie.utils.logging import create_logger
from serie.base.paper import Paper
from serie.base.plugin import BasePlugin, GlobalPluginData


logger = create_logger(__name__)


INDEX_CONTENT = """---
date: {year}-{month}-{day}
---

# <center>UnRead</center>

```dataview
TABLE WITHOUT ID
    file.link AS Title,
    file.tags AS tags
FROM "{folder}"
SORT file.link
WHERE Date.year = {year} AND Date.month = {month} AND Date.day = {day} AND DONE = false
```


# <center>Read</center>

```dataview
TABLE WITHOUT ID
    file.link AS Title,
    file.tags AS tags
FROM "{folder}"
SORT file.link
WHERE Date.year = {year} AND Date.month = {month} AND Date.day = {day} AND DONE = true
```

"""  # noqa


"""

        "论文笔记/NLP",
        "论文笔记/RL",
        "论文笔记/Self-Supervised Learning",
        "论文笔记/Text-to-Image",
        "论文笔记/Tricks",
"""


class DownloadedPaperIndexGenerator(BasePlugin):
    def __init__(self,
                 date: str,
                 index_directory: str,
                 papers_note_folders: list[str],
                 overwrite: bool = False,
                 version: str = "",
                 dependencies: list[str] | None = None,
                 **kwargs) -> None:
        super().__init__(overwrite, version, dependencies, **kwargs)
        self.date = date
        self.index_directory = osp.abspath(index_directory)
        self.papers_note_folders = papers_note_folders

    def process(self,
                papers: list[Paper] | None = None,
                global_plugin_data: GlobalPluginData | None = None):
        logger.info(f"Generating index files for date: {self.date}")
        year = self.date[:4]
        month = self.date[4:6]
        day = self.date[6:8]
        content = INDEX_CONTENT.format(
            folder="\" OR \"".join(self.papers_note_folders),
            year=year, month=month, day=day,
        )
        path_to_md = osp.join(
            self.index_directory, f"{year}-{month}-{day}.md"
        )
        logger.info(f"Writing index file to {path_to_md}")
        with open(path_to_md, 'w') as f:
            f.write(content)
        return papers
