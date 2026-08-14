"""
POST /api/complaint

Uses LangChain PromptTemplate → ChatGroq → StrOutputParser pipeline
to classify and route citizen complaints.
"""

import json
import os
import re
from typing import Optional

from fastapi import APIRouter
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_groq import ChatGroq
from pydantic import BaseModel

router = APIRouter()

GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")


class ComplaintRequest(BaseModel):
    complaint: str
    citizenName: Optional[str] = "Citizen"
    citizenWardId: Optional[str] = None
    citizenWard: Optional[str] = None


@router.post("/api/complaint")
async def process_complaint(body: ComplaintRequest):
    try:
        model = ChatGroq(
            api_key=GROQ_API_KEY,
            model="llama-3.1-8b-instant",
            temperature=0.1,
        )

        prompt = PromptTemplate.from_template(
            "You are the EcoFlow Complaint Intelligence AI for a Kerala Panchayat.\n"
            "Analyze the following complaint submitted by a citizen named {name}.\n"
            "The complaint might be in English or Malayalam.\n\n"
            'Complaint: "{complaint}"\n\n'
            "You MUST respond ONLY with a raw JSON object with the following exact keys:\n"
            '- "category": (string) e.g. "Illegal Dumping", "Missed Pickup", "Overflowing Bin"\n'
            '- "priority": (string) MUST BE EXACTLY "High", "Medium", or "Low"\n'
            '- "department": (string) e.g. "Health Department", "Haritha Karma Sena"\n'
            '- "ai_summary": (string) A 1-sentence summary of the issue translated to English.\n\n'
            "Return ONLY the JSON. Do not include markdown ```json blocks, and do not include any other text."
        )

        chain = prompt | model | StrOutputParser()

        result_string = await chain.ainvoke(
            {
                "name": body.citizenName or "Citizen",
                "complaint": body.complaint,
            }
        )

        # Clean up the string in case Llama adds backticks
        cleaned = result_string.strip()
        cleaned = re.sub(r"^```json\s*", "", cleaned)
        cleaned = re.sub(r"\s*```$", "", cleaned)
        cleaned = re.sub(r"^```\s*", "", cleaned)
        cleaned = re.sub(r"\s*```$", "", cleaned)

        result = json.loads(cleaned)

        return {"result": result}

    except Exception as e:
        print(f"Complaint API Error: {e}")
        return {"error": "Failed to process complaint", "details": str(e)}
