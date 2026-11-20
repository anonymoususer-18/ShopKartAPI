"""Loads settings: base YAML -> environment YAML -> environment variables,
then validates everything with Pydantic so the app fails fast on bad config."""
import copy
import os
from pathlib import Path
from typing import List

import yaml
from pydantic import BaseModel, Field

CONFIG_DIR = Path(__file__).parent.parent / "config"


class AppSettings(BaseModel):
    name: str
    environment: str
    debug: bool
    log_level: str = "INFO"


class StoreSettings(BaseModel):
    currency: str = Field(min_length=3, max_length=3)
    gst_percent: float = Field(ge=0, le=28)
    free_shipping_above: float = Field(ge=0)
    shipping_fee: float = Field(ge=0)
    max_qty_per_item: int = Field(gt=0)


class CouponSettings(BaseModel):
    code: str
    discount_percent: float = Field(gt=0, le=90)
    min_cart_value: float = Field(default=0, ge=0)


class Settings(BaseModel):
    app: AppSettings
    store: StoreSettings
    coupons: List[CouponSettings] = []


def _deep_merge(base, override):
    result = copy.deepcopy(base)
    for key, value in override.items():
        if isinstance(value, dict) and isinstance(result.get(key), dict):
            result[key] = _deep_merge(result[key], value)
        else:
            result[key] = value
    return result


def load_settings(env=None) -> Settings:
    env = env or os.getenv("SHOPKART_ENV", "development")
    with open(CONFIG_DIR / "settings.yaml", encoding="utf-8") as f:
        raw = yaml.safe_load(f)

    env_file = CONFIG_DIR / f"settings.{env}.yaml"
    if env_file.exists():
        with open(env_file, encoding="utf-8") as f:
            raw = _deep_merge(raw, yaml.safe_load(f))

    if os.getenv("SHOPKART_GST_PERCENT"):
        raw["store"]["gst_percent"] = os.getenv("SHOPKART_GST_PERCENT")   # Pydantic converts it

    return Settings.model_validate(raw)
