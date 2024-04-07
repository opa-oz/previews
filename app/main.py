from typing import Optional, Any, Tuple

import boto3
from colour import Color
from pathlib import Path

from anime_pgen.make import make_preview
from anime_pgen.Item import Item
from anime_pgen.constants import SIZES
from fastapi import FastAPI

from contextlib import asynccontextmanager

from pydantic import BaseModel

from .config import get_config, Config
from .preview_config import get_preview_config, PreviewConfig

global_stores = {}

base_dir = Path.cwd() / 'tmp'
out_dir = base_dir / 'output'
config_path = Path.cwd() / 'config.yaml'

headers = {"content-type": "application/json"}


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Load the config
    cfg = get_config()

    s3_client = boto3.client(
        's3',
        aws_access_key_id=cfg.s3_key_id,
        aws_secret_access_key=cfg.s3_access_key,
        endpoint_url=cfg.s3_endpoint,
    )

    global_stores["cfg"] = cfg
    global_stores["s3"] = s3_client
    global_stores["config"] = await get_preview_config(config_path)

    out_dir.mkdir(exist_ok=True, parents=True)

    yield
    # Clean up the clients and release the resources
    global_stores.clear()


app = FastAPI(lifespan=lifespan)


class GeneratePayload(BaseModel):
    id: int
    name: str
    russian: str
    image: Optional[Any] = None
    url: str
    kind: str
    score: str
    status: str
    episodes: int
    episodes_aired: int
    aired_on: str
    released_on: str
    rating: str
    english: Optional[list[Any]] = None
    japanese: Optional[list[Any]] = None
    synonyms: Optional[list[Any]] = None
    license_name_ru: str
    duration: int
    description: str
    description_html: str
    description_source: Optional[Any] = None
    franchise: str
    favoured: bool
    anons: bool
    ongoing: bool
    thread_id: int
    topic_id: int
    myanimelist_id: int
    rates_scores_stats: Optional[list[Any]] = None
    rates_statuses_stats: Optional[list[Any]] = None
    updated_at: str
    next_episode_at: Optional[Any] = None
    fansubbers: Optional[list[Any]] = None
    fandubbers: Optional[list[Any]] = None
    licensors: Optional[list[Any]] = None
    genres: Optional[list[Any]] = None
    studios: Optional[list[Any]] = None
    videos: Optional[list[Any]] = None
    screenshots: Optional[list[Any]] = None
    user_rate: Optional[Any] = None


class GenerateBody(BaseModel):
    payload: Any  # ex `GeneratePayload`
    cover: str


@app.post("/generate")
async def generate(data: GenerateBody):
    payload = data.payload
    cover = data.cover
    cfg: Config = global_stores["cfg"]
    client = global_stores["s3"]
    pconfig: PreviewConfig = global_stores["config"]

    item = Item(payload)
    item_type = "manga" if item.is_manga else "anime"
    filename = base_dir / f'{item_type}-{item.id}.jpg'
    client.download_file(cfg.covers_bucket_name, cover, filename)

    if not cfg.prod:
        item_type = "dev_" + item_type

    item.image = filename

    proportion: float = 1 if pconfig.size == 'big' else 0.5
    size: Tuple[int, int] = SIZES[pconfig.size]

    result = make_preview(
        input_item=item,
        output_file=out_dir,
        size=size,
        bg_tile=Path(pconfig.content.images.background_tile),
        star_path=Path(pconfig.content.images.star),
        japan_font=pconfig.content.fonts.japanese,
        number_font=pconfig.content.fonts.numbers,
        text_font=pconfig.content.fonts.text,
        bold_text_font=pconfig.content.fonts.bold_text,
        logo_path=Path(pconfig.content.images.logo.text),
        glyph_path=Path(pconfig.content.images.logo.glyph),
        proportion=proportion,
        bg_color=Color(pconfig.colors.background),
        text_color=Color(pconfig.colors.text),
        year_color=Color(pconfig.colors.year),
        active_star_color=Color(pconfig.colors.rating.active),
        star_color=Color(pconfig.colors.rating.regular),
    )

    key = f"{cfg.file_prefix}/{item_type}/{item.id}.jpg"
    client.upload_file(Bucket=cfg.bucket_name, Key=key, Filename=str(result))
    filename.unlink(missing_ok=True)
    Path(result).unlink(missing_ok=True)

    return {"id": item.id, "result": key, "type": item_type.replace('dev_', '')}


@app.get("/healz")
async def healz():
    return {"message": "OK"}


@app.get("/ready")
async def ready():
    return {"message": "Ready"}
