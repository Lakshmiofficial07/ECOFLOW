"""
POST /api/admin-report

Uses LangChain PromptTemplate → ChatGroq → StrOutputParser pipeline
to generate AI performance reports for Panchayat admins.
"""

import os
from typing import Any, Dict, List

from fastapi import APIRouter
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_groq import ChatGroq
from pydantic import BaseModel

router = APIRouter()

GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")


class Stats(BaseModel):
    totalPickups: int = 0
    completedPickups: int = 0
    pendingPickups: int = 0
    totalCitizens: int = 0


class CategoryItem(BaseModel):
    name: str
    value: int


class AdminReportRequest(BaseModel):
    stats: Stats
    categories: List[CategoryItem]


@router.post("/api/admin-report")
async def generate_admin_report(body: AdminReportRequest):
    try:
        model = ChatGroq(
            api_key=GROQ_API_KEY,
            model="llama-3.1-8b-instant",
            temperature=0.5,
            max_tokens=150,
        )

        prompt = PromptTemplate.from_template(
            "You are the Chief AI Data Analyst for EcoFlow AI, a waste management platform "
            "used by Panchayats in Kerala.\n"
            "You have been asked to generate a quick, predictive \"AI Report\" for the "
            "Panchayat Admin based on today's real-time data.\n\n"
            "Current Data:\n"
            "- Total Pickup Requests: {totalPickups}\n"
            "- Completed Pickups: {completedPickups}\n"
            "- Pending Pickups: {pendingPickups}\n"
            "- Registered Citizens: {totalCitizens}\n"
            "- Waste Distribution: {wasteDistribution}\n\n"
            "Provide a very concise, professional 2-3 sentence analysis.\n"
            "Highlight the most prominent waste type and give a short recommendation.\n"
            "Do not use markdown formatting like bold or asterisks. "
            "Make it read like a direct alert."
        )

        chain = prompt | model | StrOutputParser()

        waste_distribution = ", ".join(
            f"{c.name} ({c.value})" for c in body.categories
        )

        report = await chain.ainvoke(
            {
                "totalPickups": str(body.stats.totalPickups),
                "completedPickups": str(body.stats.completedPickups),
                "pendingPickups": str(body.stats.pendingPickups),
                "totalCitizens": str(body.stats.totalCitizens),
                "wasteDistribution": waste_distribution,
            }
        )

        return {"report": report}

    except Exception as e:
        print(f"Admin Report Error (LangChain): {e}")
        return {
            "error": "Failed to generate admin report via LangChain",
            "details": str(e),
        }
