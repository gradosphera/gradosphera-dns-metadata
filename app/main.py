import json
from typing import Optional

import cachetools
from fastapi import FastAPI, HTTPException
from fastapi.responses import Response

from image_generator import generate_image
from utils import create_item_metadata

app = FastAPI(include_in_schema=False)
cache = cachetools.TTLCache(maxsize=1000, ttl=86400)


@cachetools.cached(cache)
def get_cached_image(domain: str, subdomain: Optional[str] = None) -> bytes:
    return generate_image(domain, subdomain)


@app.get("/api/ton/{domain}.png", include_in_schema=False)
async def create_qrcode(domain: str) -> Response:
    try:
        image = get_cached_image(domain)
        return Response(content=image, media_type="image/png")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/ton/{subdomain}/{domain}.png", include_in_schema=False)
async def create_qrcode(subdomain: str, domain: str) -> Response:
    try:
        image = get_cached_image(domain, subdomain)
        return Response(content=image, media_type="image/png")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/ton/{collection_addr_hash}/{subdomain}/{domain}.json", include_in_schema=False)
async def create_qrcode(collection_addr_hash, subdomain, domain: str) -> Response:
    try:
        data = create_item_metadata(collection_addr_hash, subdomain, domain)
        return Response(content=json.dumps(data, ensure_ascii=False, indent=2), media_type="application/json")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
