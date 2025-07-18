

config = {
    "Request": {
        "plugins": [
            "CVFParser",
            "GitHubLinkParser",
            "DefaultKeywordsFilter",
            "MarkdownTableMaker",
            "DownloaderInformationCollector",
            "ResultSaver",
            "Translator",
            "ResultSaver",
            "DownloadedPaperIndexGenerator"
        ],
        "configs": {
            "CVFParser": {
                "year": 2025,
                "conference": "CVPR",
                "output_directory": "outputs/CVPR/2025",
                "num_requested": None
            },
            "ResultSaver": {
                "keywords_filter_plugin": "DefaultKeywordsFilter",
                "output_directory": "outputs/CVPR/2025",
                "markdown_directory": "../../Notebook/journal/CVPR/2025",
            },
            "Translator": {
                "keywords_filter_plugin": "DefaultKeywordsFilter"
            },
        }
    }
}
