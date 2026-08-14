"""
POST /api/analyze-waste

Accepts a base64-encoded image and uses the Groq API with
Llama 4 Scout vision model to classify the waste.
"""

import json
import os
import re

import httpx
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter()

GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")


class AnalyzeWasteRequest(BaseModel):
    imageBase64: str


@router.post("/api/analyze-waste")
async def analyze_waste(body: AnalyzeWasteRequest):
    image_base64 = body.imageBase64

    if not image_base64:
        raise HTTPException(status_code=400, detail="No image provided")

    # If it doesn't have the data prefix, assume jpeg
    full_data_url = image_base64
    if not image_base64.startswith("data:"):
        full_data_url = f"data:image/jpeg;base64,{image_base64}"

    if not GROQ_API_KEY:
        raise HTTPException(status_code=500, detail="Groq API Key not configured")

    url = "https://api.groq.com/openai/v1/chat/completions"

    request_body = {
        "model": "meta-llama/llama-4-scout-17b-16e-instruct",
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": (
                            "You are an expert Intelligent Waste Management AI for the EcoFlow AI platform.\n"
                            "Analyze this image and identify the waste.\n"
                            "IMPORTANT: Inspect if the waste is properly prepared for disposal. "
                            "(e.g., a plastic bottle containing water is bad, food waste inside a plastic cover is bad, "
                            "batteries mixed with household waste is hazardous).\n"
                            'If the image does NOT contain waste (e.g. it is a person\'s face, a dog, a landscape), '
                            'you MUST respond with category "Not Waste".\n\n'
                            "Respond ONLY with a valid JSON object matching this structure exactly:\n"
                            "{\n"
                            '  "category": "Plastic Waste" | "Paper" | "Cardboard" | "Glass" | "Metal" | '
                            '"Bio Waste" | "Food Waste" | "Garden Waste" | "E-Waste" | "Hazardous Waste" | '
                            '"Medical Waste" | "Mixed Waste" | "Not Waste",\n'
                            '  "confidence": 98,\n'
                            '  "binColor": "Blue Bin" | "Green Bin" | "Red Bin" | "Yellow Bin" | "Black Bin" | "None",\n'
                            '  "recyclable": true | false,\n'
                            '  "instructions": "Remove bottle cap. Empty remaining liquid. Flatten bottle before disposal.",\n'
                            '  "warning": "Liquid detected inside the bottle. Please empty it." '
                            "// Include this ONLY if there is a segregation issue or hazard. Otherwise omit.\n"
                            "}\n"
                            "Do not use markdown code blocks like ```json, just return the raw JSON text."
                        ),
                    },
                    {
                        "type": "image_url",
                        "image_url": {"url": full_data_url},
                    },
                ],
            }
        ],
        "temperature": 0.2,
        "response_format": {"type": "json_object"},
    }

    async with httpx.AsyncClient(timeout=60.0) as client:
        response = await client.post(
            url,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {GROQ_API_KEY}",
            },
            json=request_body,
        )

    if response.status_code != 200:
        print(f"Groq API Error Response: {response.text}")
        raise HTTPException(
            status_code=500,
            detail=f"API returned {response.status_code}: {response.text}",
        )

    data = response.json()
    ai_text = data.get("choices", [{}])[0].get("message", {}).get("content", "{}")

    try:
        clean_json = re.sub(r"```json\n?|\n?```", "", ai_text).strip()
        result = json.loads(clean_json)
    except (json.JSONDecodeError, Exception):
        print(f"Failed to parse Groq response: {ai_text}")
        raise HTTPException(
            status_code=500, detail="AI failed to analyze the image correctly"
        )

    return result
