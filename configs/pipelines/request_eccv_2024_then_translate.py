
config = {
    "plugins": [
        "ECCVParser",
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
        "ECCVParser": {
            "year": 2024,
            "conference": "ECCV",
            "output_directory": "outputs/ECCV/2024",
            "paper_online_date": "2024-09-30",
            "num_requested": None
        },
        "Translator": {
            "keywords_filter_plugin": "DefaultKeywordsFilter"
        },
        "ResultSaverByDefaultKeywordsFilter": {
            "output_directory": "outputs/ECCV/2024",
            "markdown_directory": "../../Notebook/journal/ECCV/2024"
        },
    }
}
