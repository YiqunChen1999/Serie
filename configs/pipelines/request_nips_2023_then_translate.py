
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
            "year": 2023,
            "conference": "NeurIPS",
            "output_directory": "outputs/NeurIPS/2023",
            "num_requested": None
        },
        "Translator": {
            "keywords_filter_plugin": "DefaultKeywordsFilter"
        },
        "ResultSaverByDefaultKeywordsFilter": {
            "output_directory": "outputs/NeurIPS/2023",
            "markdown_directory": "../../Notebook/journal/NeurIPS/2023"
        },
    }
}
