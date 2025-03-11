
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
            "year": 2020,
            "conference": "ECCV",
            "output_directory": "outputs/ECCV/2020",
            "paper_online_date": "2020-09-30",
            "num_requested": None,
        },
        "Translator": {
            "keywords_filter_plugin": "DefaultKeywordsFilter"
        },
        "ResultSaverByDefaultKeywordsFilter": {
            "output_directory": "outputs/ECCV/2020",
            "markdown_directory": "../../Notebook/journal/ECCV/2020"
        },
    }
}
