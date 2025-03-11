

config = {
    "Request": {
        "plugins": [
            "ArxivParser",
            "GitHubLinkParser",
            "DefaultKeywordsFilter",
            "LanguageModelBasedKeywordsFilter",
            "MarkdownTableMaker",
            "DownloaderInformationCollector",
            "ResultSaver",
            "Translator",
            "ResultSaver",
            "DownloadedPaperIndexGenerator"
        ],
        "configs": {
            "ResultSaver": {
                "keywords_filter_plugin": "LanguageModelBasedKeywordsFilter"
            },
            "Translator": {
                "keywords_filter_plugin": "LanguageModelBasedKeywordsFilter"
            }
        }
    }
}
