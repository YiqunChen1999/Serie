

config = {
    "LanguageModelBasedKeywordsFilter": {
        "model": "dashscope-deepseek-v3-latest",
        "batch_mode": False,
        "concurrent_mode": True,
        "interested_topics": {
            "detect": "object detection task of 2D images",
            "segment": "image segmentation task of 2D images"
        },
        "discarded_topics": {
            "detect": "3D related topics, medical related topics",
            "segment": "3D related topics, medical related topics"
        }
    }
}
