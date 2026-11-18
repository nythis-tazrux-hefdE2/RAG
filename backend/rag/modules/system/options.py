"""系统配置定义；跨域汇总由 bootstrap 组合根拥有。"""

from rag.modules.system.services.options import Option

system_options = Option(
    key="system_options",
    name="系统配置",
    description="API 与 worker 共用的管理员配置。",
    params={
        "internal": True,
        "fields": [
            {
                "key": "default_model",
                "label": "默认对话模型",
                "type": "model",
                "default": "deepseek:deepseek-flash",
            },
            {
                "key": "fast_model",
                "label": "快速响应模型",
                "type": "model",
                "default": "deepseek:deepseek-flash",
            },
            {
                "key": "reference_model",
                "label": "来源标注模型",
                "type": "model",
                "default": "",
            },
            {
                "key": "embed_model",
                "label": "默认 Embedding 模型",
                "type": "model",
                "default": "siliconflow-cn:Pro/BAAI/bge-m3",
            },
            {
                "key": "reranker",
                "label": "默认 Re-Ranker 模型",
                "type": "model",
                "default": "siliconflow-cn:Pro/BAAI/bge-reranker-v2-m3",
            },
            {
                "key": "default_ocr_engine",
                "label": "默认 OCR 解析引擎",
                "type": "ocr_engine",
                "default": "mineru_official",
            },
        ],
    },
)
