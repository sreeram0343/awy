import json
import os
from typing import Dict, Any
from app.core.logging import logger


class FinancialConfigLoader:
    _config: Dict[str, Any] | None = None

    @classmethod
    def get_config_path(cls) -> str:
        return os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "config", "financial_rules.json")

    @classmethod
    def load_config(cls, force_reload: bool = False) -> Dict[str, Any]:
        if cls._config is None or force_reload:
            config_path = cls.get_config_path()
            if not os.path.exists(config_path):
                raise FileNotFoundError(f"Financial rules configuration not found at '{config_path}'")
            with open(config_path, "r", encoding="utf-8") as f:
                cls._config = json.load(f)
            logger.info(f"Loaded financial rules config version [{cls._config.get('version')}] effective from [{cls._config.get('effective_date')}]")
        return cls._config

    @classmethod
    def get_version_meta(cls) -> Dict[str, str]:
        cfg = cls.load_config()
        return {
            "financial_version": cfg.get("version", "unknown"),
            "effective_date": cfg.get("effective_date", "unknown"),
            "source": cfg.get("source", "unknown"),
        }


financial_config = FinancialConfigLoader.load_config()
