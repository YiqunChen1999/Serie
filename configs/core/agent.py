
config = {
    "noset": {},
    "siliconflow-deepseek-v3": {
        "base_url": "https://api.siliconflow.cn/v1/",
        "endpoint": "/v1/chat/completions",
        "model": "deepseek-ai/DeepSeek-V3",
        "api_key": "SILICONFLOW_APIKEY",
        "model_kwargs": {
            "max_tokens": 4096,
            "temperature": 0.7,
            "top_p": 0.7
        },
        "request_setting": {
            "requests_per_minute": 64
        }
    },
    "siliconflow-deepseek-r1": {
        "base_url": "https://api.siliconflow.cn/v1/",
        "endpoint": "/v1/chat/completions",
        "model": "deepseek-ai/DeepSeek-R1",
        "api_key": "SILICONFLOW_APIKEY",
        "model_kwargs": {
            "max_tokens": 4096,
            "temperature": 0.7,
            "top_p": 0.7
        },
        "request_setting": {
            "requests_per_minute": 64
        }
    },
    "siliconflow-deepseek-r1-distill-qwen-32b": {
        "base_url": "https://api.siliconflow.cn/v1/",
        "endpoint": "/v1/chat/completions",
        "model": "deepseek-ai/DeepSeek-R1-Distill-Qwen-32B",
        "api_key": "SILICONFLOW_APIKEY",
        "model_kwargs": {
            "max_tokens": 4096,
            "temperature": 0.7,
            "top_p": 0.7
        },
        "request_setting": {
            "requests_per_minute": 64
        }
    },
    "siliconflow-deepseek-r1-distill-qwen-14b": {
        "base_url": "https://api.siliconflow.cn/v1/",
        "endpoint": "/v1/chat/completions",
        "model": "deepseek-ai/DeepSeek-R1-Distill-Qwen-14B",
        "api_key": "SILICONFLOW_APIKEY",
        "model_kwargs": {
            "max_tokens": 4096,
            "temperature": 0.7,
            "top_p": 0.7
        },
        "request_setting": {
            "requests_per_minute": 64
        }
    },
    "siliconflow-deepseek-r1-distill-qwen-7b": {
        "base_url": "https://api.siliconflow.cn/v1/",
        "endpoint": "/v1/chat/completions",
        "model": "deepseek-ai/DeepSeek-R1-Distill-Qwen-7B",
        "api_key": "SILICONFLOW_APIKEY",
        "model_kwargs": {
            "max_tokens": 4096,
            "temperature": 0.7,
            "top_p": 0.7
        },
        "request_setting": {
            "requests_per_minute": 64
        }
    },
    "siliconflow-deepseek-r1-distill-llama-70b": {
        "base_url": "https://api.siliconflow.cn/v1/",
        "endpoint": "/v1/chat/completions",
        "model": "deepseek-ai/DeepSeek-R1-Distill-Llama-70B",
        "api_key": "SILICONFLOW_APIKEY",
        "model_kwargs": {
            "max_tokens": 4096,
            "temperature": 0.7,
            "top_p": 0.7
        },
        "request_setting": {
            "requests_per_minute": 64
        }
    },
    "siliconflow-deepseek-r1-distill-llama-8b": {
        "base_url": "https://api.siliconflow.cn/v1/",
        "endpoint": "/v1/chat/completions",
        "model": "deepseek-ai/DeepSeek-R1-Distill-Llama-8B",
        "api_key": "SILICONFLOW_APIKEY",
        "model_kwargs": {
            "max_tokens": 4096,
            "temperature": 0.7,
            "top_p": 0.7
        },
        "request_setting": {
            "requests_per_minute": 64
        }
    },
    "dashscope-qwen-max-latest": {
        "base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1",
        "endpoint": "/v1/chat/completions",
        "model": "qwen-max-latest",
        "api_key": "DASHSCOPE_APIKEY",
        "model_kwargs": {
            "max_tokens": 4096,
            "temperature": 0.7,
            "top_p": 0.7
        },
        "request_setting": {
            "requests_per_minute": 64
        }
    },
    "dashscope-qwen-plus-latest": {
        "base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1",
        "endpoint": "/v1/chat/completions",
        "model": "qwen-plus-latest",
        "api_key": "DASHSCOPE_APIKEY",
        "model_kwargs": {
            "max_tokens": 4096,
            "temperature": 0.7,
            "top_p": 0.7
        },
        "request_setting": {
            "requests_per_minute": 64
        }
    },
    "dashscope-qwen-turbo-latest": {
        "base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1",
        "endpoint": "/v1/chat/completions",
        "model": "qwen-turbo-latest",
        "api_key": "DASHSCOPE_APIKEY",
        "model_kwargs": {
            "max_tokens": 4096,
            "temperature": 0.7,
            "top_p": 0.7
        },
        "request_setting": {
            "requests_per_minute": 64
        }
    },
    "dashscope-deepseek-v3-latest": {
        "base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1",
        "endpoint": "/v1/chat/completions",
        "model": "deepseek-v3",
        "api_key": "DASHSCOPE_APIKEY",
        "model_kwargs": {
            "max_tokens": 4096,
            "temperature": 0.7,
            "top_p": 0.7
        },
        "request_setting": {
            "requests_per_minute": 64
        }
    },
    "dashscope-deepseek-r1-latest": {
        "base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1",
        "endpoint": "/v1/chat/completions",
        "model": "deepseek-r1",
        "api_key": "DASHSCOPE_APIKEY",
        "model_kwargs": {
            "max_tokens": 4096,
            "temperature": 0.7,
            "top_p": 0.7
        },
        "request_setting": {
            "requests_per_minute": 64
        }
    },
    "zhipuai-glm-4-flash": {
        "base_url": "https://open.bigmodel.cn/api/paas/v4/",
        "endpoint": "/v4/chat/completions",
        "model": "glm-4-flash",
        "api_key": "ZHIPUAI_APIKEY",
        "model_kwargs": {
            "max_tokens": 4000,
            "temperature": 0.5,
            "top_p": 0.9
        },
        "request_setting": {
            "requests_per_minute": 64
        }
    },
    "zhipuai-glm-4-plus": {
        "base_url": "https://open.bigmodel.cn/api/paas/v4/",
        "endpoint": "/v4/chat/completions",
        "model": "glm-4-plus",
        "api_key": "ZHIPUAI_APIKEY",
        "model_kwargs": {
            "max_tokens": 4000,
            "temperature": 0.5,
            "top_p": 0.9
        },
        "request_setting": {
            "requests_per_minute": 64
        }
    },
    "lingyi-yi-lightning": {
        "base_url": "https://api.lingyiwanwu.com/v1",
        "endpoint": "/v1/chat/completions",
        "model": "yi-lightning",
        "api_key": "LINGYI_APIKEY",
        "model_kwargs": {
            "max_tokens": 4000,
            "temperature": 0.5,
            "top_p": 0.9
        },
        "request_setting": {
            "requests_per_minute": 64
        }
    }
}
