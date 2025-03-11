
config = {
    "plugins": [
        "OpenReviewParser",
        "GitHubLinkParser",
        "DefaultKeywordsFilter",
        "MarkdownTableMaker",
        "DownloaderInformationCollector",
        "ResultSaverByDefaultKeywordsFilter",
        "Translator",
        "ResultSaverByDefaultKeywordsFilter",
        "DownloadedPaperIndexGenerator"
    ],
    "configs": {
        "OpenReviewParser": {
            "year": 2024,
            "conference": "ICML",
            "output_directory": "outputs/ICML/2024",
            "num_requested": None
        },
        "Translator": {
            "keywords_filter_plugin": "DefaultKeywordsFilter"
        },
        "ResultSaverByDefaultKeywordsFilter": {
            "output_directory": "outputs/ICML/2024",
            "markdown_directory": "../../Notebook/journal/ICML/2024"
        },
    }
}
