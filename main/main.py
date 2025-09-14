# main.py
from fastapi import FastAPI, HTTPException
import httpx
from models.models import KundliResponse   # ✅ Sirf Response import karenge
from functions.functions import generate_pdf, send_email, get_coordinates_str
from token_generator.refresh_token import get_current_token, start_token_refresher
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from models.models import KundliRequest
app = FastAPI()

API_BASE = "https://api.prokerala.com/v2"
# Start the background token refresher
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # dev only
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
start_token_refresher()

@app.post("/kundli", response_model=KundliResponse)
async def get_kundli(req: KundliRequest):
    token = get_current_token()
    if not token:
        raise HTTPException(status_code=503, detail="Access token not yet available")

    url = f"{API_BASE}/astrology/kundli"
    headers = {"Authorization": f"Bearer {token}"}

    params = {
        "ayanamsa": (req.ayanamsa)//2 + 1,
        "coordinates": get_coordinates_str(req.coordinates),
        "datetime": req.datetime,
    }

    async with httpx.AsyncClient() as client:
        resp = await client.get(url, headers=headers, params=params)

    if resp.status_code != 200:
        raise HTTPException(status_code=resp.status_code, detail=resp.json())

    data = resp.json()

    # Generate PDF
    pdf_bytes = generate_pdf(data)

    # Send email
    await send_email(req.email, pdf_bytes)

    return {"message": f"Report sent to {req.email}"}
