
config = {
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
            "year": 2023,
            "conference": "WACV",
            "output_directory": "outputs/WACV/2023",
            "num_requested": None
        },
        "Translator": {
            "keywords_filter_plugin": "DefaultKeywordsFilter"
        },
        "ResultSaverByDefaultKeywordsFilter": {
            "output_directory": "outputs/WACV/2023",
            "markdown_directory": "../../Notebook/journal/WACV/2023"
        },
    }
}
