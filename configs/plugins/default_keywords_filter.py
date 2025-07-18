
from copy import deepcopy


keywords = {
    "detect": ["detect", "detection"],
    "diffusion": ["diffusion"],
    "segment": ["segment", "segmentation"],
    "vision": ["vision", "visual"],
    "vision-language": ["vision-language", "vision language"],
    "multimodal": [
        "multimodal", "multi-modal", "multi modal", "vlm", "mllm",
        "vision language", "vision-language"
    ],
    "segment & vision": ["segment & vision", "segment & visual"],
    "segment & multimodal": [
        "segment & multimodal", "segment & multi-modal",
        "segment & multi modal", "segment & vlm", "segment & mllm",
        "segment & vision language", "segment & vision-language"
    ]
}


common_ignore_keywords = [
    " disease ", " cancer ", " medical ", " polyp ", " lesion ",
    " mri ", " tumor ", " lidar ", " remote sens", " audio ", " video ",
    " tracking ", " video ", " 3d ", " point cloud", " covid-19 ",
    " vehicle", " Bird's Eye View ", " BEV ", " surgery ", " Cardiac ",
    " deepfake ", " out-of-distribution ", " toxicity ", " speech ",
    " fraud ", " traffic ", " salient object ", " self-driving ",
    " emotion ", " anomaly ", " Meningeal ", " Lymphatic ", " Vessel ",
    " music ", " clinical ", " economist", " Jailbreak ", " Vessel ",
    " Clinical ", " Spatiotemporal ", "Crack Segmentation"
]


config = {
    "DefaultKeywordsFilter": {
        "keywords": keywords,
        "ignorance": {
            "detect": deepcopy(common_ignore_keywords),
            "diffusion": deepcopy(common_ignore_keywords),
            "segment": deepcopy(common_ignore_keywords),
            "vision": deepcopy(common_ignore_keywords),
            "vision-language": deepcopy(common_ignore_keywords),
            "multimodal": deepcopy(common_ignore_keywords),
            "segment & vision": deepcopy(common_ignore_keywords),
            "segment & multimodal": deepcopy(common_ignore_keywords),
        }
    }
}
