

config = {
    "Request": {
        "plugins": [
            "CVFParser",
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
            "CVFParser": {
                "year": 2024,
                "conference": "CVPR",
                "output_directory": "outputs/CVPR/2024",
                "num_requested": None
            },
            "ResultSaverByDefaultKeywordsFilter": {
                "output_directory": "outputs/CVPR/2024",
                "markdown_directory": "../../Notebook/journal/CVPR/2024"
            },
            "Translator": {
                "keywords_filter_plugin": "DefaultKeywordsFilter"
            },
        }
    }
}
