

config = {
    "DownloadByParsing": {
        "plugins": [
            "ResultLoader", "DownloaderGivenMarkdown", "Downloader"
        ],
        "configs": {
            "ResultLoader": {},
            "DownloaderGivenMarkdown": {
                "dir_markdown_src": ""
            },
            "Downloader": {}
        }
    }
}
