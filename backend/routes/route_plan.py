"""
POST /api/route-plan

Generates an AI route strategy for Haritha Karma Sena drivers
based on their list of pending waste pickups.
"""

import os
from datetime import datetime
from typing import Any, Dict, List, Optional

import httpx
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter()

GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")


class Pickup(BaseModel):
    id: Optional[str] = None
    citizenName: Optional[str] = "Unknown"
    category: Optional[str] = "Unknown"
    binColor: Optional[str] = "Unknown"
    timestamp: Optional[str] = None
    # Allow extra fields from the frontend
    model_config = {"extra": "allow"}


class RoutePlanRequest(BaseModel):
    pickups: List[Pickup]


@router.post("/api/route-plan")
async def generate_route_plan(body: RoutePlanRequest):
    try:
        pickups = body.pickups

        if not pickups:
            return {"strategy": "No pending pickups. Your route is clear!"}

        # Format pickups for the prompt
        pickup_list = "\n".join(
            f"{i + 1}. Location: {p.citizenName}'s house, Waste: {p.category}, "
            f"Bin: {p.binColor}, Requested at: {p.timestamp or 'N/A'}"
            for i, p in enumerate(pickups)
        )

        prompt = (
            "You are an AI Route Strategist for the Haritha Karma Sena "
            "(Kerala's green army for waste management).\n"
            "Your job is to look at the list of pending waste pickups and provide "
            "a short, actionable strategy for the driver in 2-3 sentences, and sort them into the most efficient route.\n"
            "Focus on safety (e.g. hazardous or E-waste first), grouping similar items, "
            "or time efficiency.\n\n"
            f"Current Pickups:\n{pickup_list}\n\n"
            "You MUST output exactly a JSON object in this format (and nothing else):\n"
            '{\n  "strategy": "Your short strategy text here",\n  "orderedIds": ["id1", "id2"]\n}'
        )

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {GROQ_API_KEY}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": "llama-3.1-8b-instant",
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.3,
                    "response_format": {"type": "json_object"}
                },
            )

        if response.status_code != 200:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to generate strategy from Groq: {response.text}",
            )

        data = response.json()
        content = data["choices"][0]["message"]["content"].strip()
        
        import json
        try:
            result_json = json.loads(content)
        except json.JSONDecodeError:
            result_json = {"strategy": content, "orderedIds": [p.id for p in pickups]}

        return result_json

    except HTTPException:
        raise
    except Exception as e:
        print(f"Route Plan Error: {e}")
        return {"error": "Failed to generate route plan", "details": str(e)}
