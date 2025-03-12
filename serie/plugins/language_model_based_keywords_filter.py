
from dataclasses import dataclass

from serie.utils.logging import create_logger
from serie.base.plugin import (
    BasePlugin, BaseKeywordsFilterData, BasePluginData, PluginStatus,
    GlobalPluginData,
)
from serie.base.paper import Paper
from serie.core.agent import Agent, TaskMode


logger = create_logger(__name__)


def plugin_name():
    return "LanguageModelBasedKeywordsFilter"


def default_prompt_template():
    return (
        ""
        "# Task Description\n"
        "You are given a research paper's title and abstract as inputs. "
        "Your task is to determine whether the paper is falling into "
        "the interested topic.\n\n"

        # Requirements
        "# Task Requirements\n"
        "- Please first provide a clear analysis "
        "based on the title and abstract;\n"

        "- You shouldn't try to guess the content not appear in "
        "the provided text;\n"

        "- If the paper is related to the interested topic, "
        "return <-|RESULT: TRUE|->;\n"

        "- If the paper is related to the discarded topic, "
        "return <-|RESULT: FALSE|->, even if the paper is also related to "
        "the interested topic;\n"

        "- If the paper does not fall into the interested scope, return "
        "<-|RESULT: FALSE|->;\n\n"

        # Title and Abstract
        "# Task Input\n"
        "## Interested Topic\n{interested}\n\n"
        "## Discarded Topic\n{discarded}\n\n"
        "## Title\n{title}\n\n"
        "## Abstract\n{abstract}"
    )


@dataclass
class LanguageModelBasedKeywordsFilterData(BaseKeywordsFilterData):
    plugin_name: str = plugin_name()


class LanguageModelBasedKeywordsFilter(BasePlugin):
    """
    This plugin is used to parse keywords from the papers.

    Args:
        model: The model used to tell if a paper is related to a specific task.
        batch_mode: If True, the plugin will process the papers in batch.
        topics: A dictionary of topics, the key of the dict is the specified
            keyword, and the value is the related topic to be analyzed.

    Examples:
        >>> topics = {
        ...     "detect": "object detection task of 2D images",
        ...     "segment": "segmentation task of 2D images",
        ... }
    """

    def __init__(
            self,
            model: str,
            batch_mode: bool,
            concurrent_mode: bool,
            interested_topics: dict[str, str],
            discarded_topics: dict[str, str],
            max_workers: int = 16,
            max_tasks_per_minute: int = 16,
            overwrite: bool = False,
            version: str = "",
            dependencies: list[str] | None = None,
            **kwargs) -> None:
        super().__init__(overwrite, version, dependencies, **kwargs)
        self.agent = Agent(model)
        self.batch_mode = batch_mode
        self.concurrent_mode = concurrent_mode
        self.interested_topics = interested_topics
        self.discarded_topics = discarded_topics
        self.max_workers = max_workers
        self.max_tasks_per_minute = max_tasks_per_minute

    def check_status(
            self, papers: list[Paper], global_plugin_data: GlobalPluginData):
        datas = [p.get_plugin_data(plugin_name()) for p in papers]
        keywords = []
        for d in datas:
            if isinstance(d, LanguageModelBasedKeywordsFilterData):
                if len(d.keywords) > 0:
                    keywords.extend(d.keywords)
        if len(keywords) > 0:
            self.status = PluginStatus.DONE
            return

    def process(
            self, papers: list[Paper], global_plugin_data: GlobalPluginData):
        for paper in papers:
            paper.add_plugin_data(LanguageModelBasedKeywordsFilterData())
        if self.batch_mode or self.concurrent_mode:
            return self.process_batch(papers, global_plugin_data)
        else:
            return self.process_single(papers, global_plugin_data)

    def process_batch(
            self, papers: list[Paper], global_plugin_data: GlobalPluginData):
        prompts: list[str] = []
        papers_to_process = [
            r for r in papers if self.requires_processing(r)
        ]
        if len(papers_to_process) == 0:
            return papers
        N = len(papers_to_process)
        logger.info(f"Processing {N} papers in batch...")
        for keyword, interested in self.interested_topics.items():
            logger.info(f"Creating prompts related to {interested}...")
            discarded = self.discarded_topics.get(keyword, "")
            prompts.extend(
                prepare_prompts(papers_to_process, interested, discarded)
            )
        logger.info("Sending prompts to the agent...")
        mode = TaskMode.BATCH if self.batch_mode else TaskMode.CONCURRENT
        responses = self.agent(prompts, mode=mode)
        responses = [responses] if isinstance(responses, str) else responses
        logger.info("Processing responses...")
        keywords = list(self.interested_topics.keys())
        for i, r in enumerate(responses):
            if "<-|RESULT: TRUE|->" in r or "<-|RESULT: FALSE|->" not in r:
                paper = papers_to_process[i % N]
                if "<-|RESULT: TRUE|->" not in r:
                    logger.warning(
                        f"The model doesn't output valid result, the paper "
                        f"will be marked as related.\n\n"
                        f"Model Prompt: {prompts[i]}\n\n"
                        f"Model Response: {r}\n\n"
                        f"Model: {self.agent.model}\n"
                    )
                plugin = paper.get_plugin_data(plugin_name())
                assert isinstance(plugin, LanguageModelBasedKeywordsFilterData)
                plugin.keywords.append(keywords[i // N])
            elif "<-|RESULT: FALSE|->" in r:
                pass
        return papers

    def process_single(
            self, papers: list[Paper], global_plugin_data: GlobalPluginData):
        papers_to_process = [
            r for r in papers if self.requires_processing(r)
        ]
        if len(papers_to_process) == 0:
            return papers
        N = len(papers_to_process)
        logger.info(f"Processing {N} papers in single...")
        for keyword, interested in self.interested_topics.items():
            logger.info(f"Processing {interested}...")
            discarded = self.discarded_topics.get(keyword, "")
            for i, paper in enumerate(papers_to_process):
                prompt = prepare_prompts([paper], interested, discarded)[0]
                logger.info(
                    f"Processing {i+1}-th of {N} paper of keyword {keyword}..."
                )
                r = self.agent.complete_single(prompt)
                if "<-|RESULT: TRUE|->" in r or "<-|RESULT: FALSE|->" not in r:
                    if "<-|RESULT: TRUE|->" not in r:
                        logger.warning(
                            f"The model doesn't output valid result, "
                            f"the paper will be marked as related.\n\n"
                            f"Model Prompt: {prompt}\n\n"
                            f"Model Response: {r}\n\n"
                            f"Model: {self.agent.model}\n"
                        )
                    plugin = paper.get_plugin_data(plugin_name())
                    assert isinstance(
                        plugin, LanguageModelBasedKeywordsFilterData
                    )
                    plugin.keywords.append(keyword)
                    logger.info(f"TRUE: Keyword {keyword} in {paper.title}")
                else:
                    logger.info(f"FALSE: Keyword {keyword} in {paper.title}")
        return papers

    def requires_processing(self, paper: Paper):
        plugin_datas: dict[str, BasePluginData] = paper.local_plugin_data
        for data in plugin_datas.values():
            if isinstance(data, BaseKeywordsFilterData):
                if data.plugin_name == plugin_name():
                    continue
                interested = set(self.interested_topics.keys())
                ignorance = set(data.ignorance)
                detected = set(data.keywords)
                if len(interested & ignorance) > 0:
                    # If the paper should be ignored even if it is classified
                    # as interested, then it should be ignored.
                    return False
                if len(interested & detected) > 0:
                    # If the paper has been classified as interested and
                    # it is not ignored, then it should be processed later.
                    return True
                # If there exists a keyword filter but the paper is not
                # classified as interested, then it should be ignored.
                return False
        # If there is no keyword filter before, then the paper should be
        # processed.
        return True


def prepare_prompts(
        papers: list[Paper], interested_topic: str, discarded_topic: str):
    total_prompts: list[str] = []
    for paper in papers:
        prompt = default_prompt_template()
        prompt = prompt.format(
            interested=interested_topic, discarded=discarded_topic,
            title=paper.title, abstract=paper.abstract)
        total_prompts.append(prompt)
    return total_prompts
