

config = {
    "Translator": {
        "model": "zhipuai-glm-4-flash",
        "batch_mode": False,
        "concurrent_mode": True,
        "translate_all_results": False,
        "prompt": "Directly translate the given text into Chinese. Don't output irrelevant contexts."  # noqa
    }
}
