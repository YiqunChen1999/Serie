
from dataclasses import dataclass

from serie.utils.logging import create_logger
from serie.base.plugin import (
    BasePlugin, BasePluginData, BaseKeywordsFilterData, GlobalPluginData
)
from serie.base.paper import Paper
from serie.core.agent import Agent, TaskMode


logger = create_logger(__name__)


def plugin_name():
    return "Translator"


def translation_instruction():
    prompt = (
        "Directly translate the given text into Chinese. Don't output "
        "irrelevant contexts."
    )
    return prompt


@dataclass
class TranslatorData(BasePluginData):
    plugin_name: str = plugin_name()
    model: str = ""
    translated_summary: str = ""
    translated_title: str = ""
    save_as_text: bool = True

    def string_for_saving(self, *args, **kwargs) -> str:
        text = (
            f"### TRANSLATED\n\n"
            f"**{self.translated_title}**\n\n"
            f"{self.translated_summary}"
        )
        return text


class Translator(BasePlugin):
    def __init__(
            self,
            model: str,
            mode: str | TaskMode = TaskMode.CONCURRENT,
            prompt: str = "",
            translate_all_papers: bool = False,
            keywords_filter_plugin: str = "",
            max_workers: int = 16,
            max_tasks_per_minute: int = 16):
        self.agent = Agent(model)
        self.mode = TaskMode(mode) if isinstance(mode, str) else mode
        self.prompt = prompt or translation_instruction()
        self.translate_all_papers = translate_all_papers
        self.keywords_filter_plugin = keywords_filter_plugin
        self.max_workers = max_workers
        self.max_tasks_per_minute = max_tasks_per_minute

    def process(self,
                papers: list[Paper],
                global_plugin_data: GlobalPluginData) -> list[Paper]:
        if len(papers) == 0:
            logger.warning("No papers to translate.")
            return papers
        if self.mode in [TaskMode.BATCH, TaskMode.CONCURRENT]:
            return self.translate_batch(papers)
        else:
            return self.translate_single(papers)

    def translate_batch(self, papers: list[Paper]) -> list[Paper]:
        titles = [r.title for r in papers if self.requires_translation(r)]
        summaries = [
            r.abstract for r in papers if self.requires_translation(r)
        ]
        papers_to_translate = [
            r for r in papers if self.requires_translation(r)
        ]
        logger.info(f"Translating {len(titles)} titles...")
        prompts = [
            f"Given the following text:\n\n{t}\n\n{translation_instruction()}"
            for t in titles
        ]
        responses = self.agent(prompts, mode=self.mode)
        responses = [responses] if isinstance(responses, str) else responses
        translated_titles = responses

        logger.info(f"Translating {len(summaries)} summaries...")
        prompts = [
            f"Given the following text:\n\n{s}\n\n{translation_instruction()}"
            for s in summaries
        ]
        responses = self.agent(prompts, mode=self.mode)
        responses = [responses] if isinstance(responses, str) else responses
        translated_summaries = responses
        for result, title, translation in zip(papers_to_translate,
                                              translated_titles,
                                              translated_summaries):
            plugin = result.local_plugin_data.get(plugin_name(), None)
            if plugin is None:
                result.add_plugin_data(TranslatorData(model=self.agent.model))
            plugin = result.local_plugin_data[plugin_name()]
            assert isinstance(plugin, TranslatorData)
            plugin.translated_summary = translation
            plugin.translated_title = title
        return papers

    def translate_single(self, papers: list[Paper]) -> list[Paper]:
        papers_to_translate = [
            r for r in papers if self.requires_translation(r)
        ]
        logger.info(f"Translating {len(papers_to_translate)} summaries...")
        for idx, result in enumerate(papers_to_translate):
            abstract = result.abstract
            logger.info(
                f"Translating the abstract of "
                f"{idx+1}-th/{len(papers_to_translate)} paper: {result.title}"
            )
            translation = self.agent.complete_single(
                f"Given the following text:\n\n{abstract}\n\n"
                f"{translation_instruction()}"
            )
            plugin = result.local_plugin_data.get(plugin_name(), None)
            if plugin is None:
                result.add_plugin_data(TranslatorData(model=self.agent.model))
            plugin = result.local_plugin_data[plugin_name()]
            assert isinstance(plugin, TranslatorData)
            plugin.translated_summary = translation
        return papers

    def requires_translation(self, result: Paper) -> bool:
        if self.translate_all_papers:
            return True
        plugin_data = result.get_plugin_data(self.keywords_filter_plugin)
        assert isinstance(plugin_data, BaseKeywordsFilterData)
        translate = False
        if plugin_data and len(plugin_data.keywords) > 0:
            for keyword in plugin_data.keywords:
                if keyword in plugin_data.ignorance:
                    translate = False
                    break
            else:
                translate = True
        return translate
