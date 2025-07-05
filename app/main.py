import json
from typing import Optional

import cachetools
from fastapi import FastAPI, HTTPException
from fastapi.responses import Response

from image_generator import generate_image
from utils import SUPPORTED_TLD, create_item_metadata

app = FastAPI(include_in_schema=False)
cache = cachetools.TTLCache(maxsize=1000, ttl=86400)


@cachetools.cached(cache)
def get_cached_image(domain: str, tld: str, subdomain: Optional[str] = None) -> bytes:
    return generate_image(domain, subdomain, tld)


@app.get("/api/{tld}/{domain}.png", include_in_schema=False)
async def handler(tld: str, domain: str) -> Response:
    if tld not in SUPPORTED_TLD:
        raise HTTPException(status_code=400, detail="Unsupported TLD")

    try:
        image = get_cached_image(domain, tld)
        return Response(content=image, media_type="image/png")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/{tld}/{subdomain}/{domain}.png", include_in_schema=False)
async def handler(tld: str, subdomain: str, domain: str) -> Response:
    if tld not in SUPPORTED_TLD:
        raise HTTPException(status_code=400, detail="Unsupported TLD")

    try:
        image = get_cached_image(domain, tld, subdomain)
        return Response(content=image, media_type="image/png")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/{tld}/{subdomain}/{domain}.json", include_in_schema=False)
async def metadata_handler(
        tld: str,
        subdomain: str,
        domain: str
) -> Response:
    if tld not in SUPPORTED_TLD:
        raise HTTPException(status_code=400, detail="Unsupported TLD")

    try:
        metadata = {
            "description": (
                f"Субдомен .{domain}.{tld} для блокчейн-доменов Градосферы. "
                f"DNS это сервис, который отображает человекочитаемые имена "
                f"для адресов мультикошельков, кошельков, умных контрактов, ДАО, субДАО и вебсайтов."
            ),
            "attributes": [
                {
                    "trait_type": "длина субдомена",
                    "value": str(len(subdomain)),
                }
            ]
        }
        return Response(
            content=json.dumps(metadata, ensure_ascii=False, indent=2),
            media_type="application/json"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/{tld}/{collection_addr_hash}/{subdomain}/{domain}.json", include_in_schema=False)
async def handler(tld: str, collection_addr_hash, subdomain, domain: str) -> Response:
    if tld not in SUPPORTED_TLD:
        raise HTTPException(status_code=400, detail="Unsupported TLD")

    try:
        data = create_item_metadata(collection_addr_hash, subdomain, domain, tld)
        return Response(content=json.dumps(data, ensure_ascii=False, indent=2), media_type="application/json")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
