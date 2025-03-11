

config = {
    "Request": {
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
                "year": 2018,
                "conference": "ECCV",
                "output_directory": "outputs/ECCV/2018",
                "paper_online_date": "2024-09-30",
                "num_requested": None
            },
            "Translator": {
                "keywords_filter_plugin": "DefaultKeywordsFilter"
            },
            "ResultSaverByDefaultKeywordsFilter": {
                "output_directory": "outputs/ECCV/2018",
                "markdown_directory": "../../Notebook/journal/ECCV/2018"
            },
        }
    }
}
