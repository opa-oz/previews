from pathlib import Path

import yaml
from anime_pgen.constants import COLORS, SIZE
from pydantic import BaseModel, Field


class PreviewFonts(BaseModel):
    text: str | Path
    bold_text: str | Path
    numbers: str | Path
    japanese: str | Path


class PreviewLogo(BaseModel):
    glyph: str | Path
    text: str | Path


class PreviewImages(BaseModel):
    background_tile: str | Path
    star: str | Path
    logo: PreviewLogo


class PreviewContent(BaseModel):
    images: PreviewImages
    fonts: PreviewFonts


class PreviewRating(BaseModel):
    active: str
    regular: str


class PreviewColors(BaseModel):
    background: str
    text: str
    year: str

    rating: PreviewRating


class PreviewConfig(BaseModel):
    size: str = Field(default=SIZE)
    colors: PreviewColors = Field(defaults=COLORS)
    content: PreviewContent


async def get_preview_config(config_path: Path) -> PreviewConfig:
    with open(config_path, 'r') as config_f:
        config = yaml.load(config_f, Loader=yaml.FullLoader)

    config = PreviewConfig.parse_obj(config)

    return config
