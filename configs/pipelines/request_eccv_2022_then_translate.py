
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
            "year": 2022,
            "conference": "ECCV",
            "output_directory": "outputs/ECCV/2022",
            "paper_online_date": "2022-07-20",
            "num_requested": None
        },
        "Translator": {
            "keywords_filter_plugin": "DefaultKeywordsFilter"
        },
        "ResultSaverByDefaultKeywordsFilter": {
            "output_directory": "outputs/ECCV/2022",
            "markdown_directory": "../../Notebook/journal/ECCV/2022"
        },
    }
}
