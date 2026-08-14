"""
POST /api/chat

RAG-backed chat endpoint. Performs semantic search on the policy
vector DB for context, then invokes ChatGroq via LangChain.
"""

import os
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, File, UploadFile, Form
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_groq import ChatGroq
from pydantic import BaseModel

from rag import semantic_search

router = APIRouter()

GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")


class ChatMessage(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    messages: List[ChatMessage]
    language: Optional[str] = None


@router.post("/api/chat")
async def chat(body: ChatRequest):
    try:
        model = ChatGroq(
            api_key=GROQ_API_KEY,
            model="llama-3.3-70b-versatile",
            temperature=0.5,
            max_tokens=1024,
        )

        # Extract the latest user question for semantic search
        user_messages = [m for m in body.messages if m.role == "user"]
        last_user_message = user_messages[-1] if user_messages else None
        context_string = ""

        if last_user_message:
            try:
                # --- Query Expansion for Cross-Lingual RAG ---
                query_prompt = (
                    "You are a search query generator. Extract the main keywords from the user message. "
                    "Translate the keywords into Malayalam (written in Manglish) AND English, and return BOTH. "
                    "For example, if user asks 'What is the fee?', return 'fee amount monthly collection panam masappadi roopa'. "
                    "Output ONLY the keywords separated by spaces, nothing else.\n\n"
                    f"User message: {last_user_message.content}"
                )
                search_query_msg = await model.ainvoke([HumanMessage(content=query_prompt)])
                search_query = search_query_msg.content.strip(' "\n')
                print(f"Original Query: {last_user_message.content}")
                print(f"Expanded Query: {search_query}")
                
                relevant_chunks = await semantic_search(search_query, 3)
                if relevant_chunks:
                    context_string = (
                        "\n\nGOVERNMENT POLICY CONTEXT (Use this to answer the question):\n"
                    )
                    for index, chunk in enumerate(relevant_chunks):
                        context_string += (
                            f'[Source {index + 1}: {chunk["source"]}]\n'
                            f'"{chunk["text"]}"\n\n'
                        )
            except Exception as err:
                print(f"Semantic search failed: {err}")

        # Determine strict language rule
        language = body.language
        if language == "ml-IN":
            lang_rule = "CRITICAL RULE: The user prefers Manglish. You MUST reply ONLY in Manglish (Malayalam language written using English alphabets a-z). NEVER use native Malayalam characters like അ, ആ, ക, ച. EXAMPLES OF MANGLISH: 'Ward 1 il Saturday aanu waste edukkunney.', 'Plastic waste blue binil iduka.' ALWAYS format your answer exactly like these examples using only English letters."
        elif language == "en-US":
            lang_rule = "- YOU MUST REPLY IN PURE ENGLISH. Do NOT use any Malayalam script or Manglish."
        else:
            lang_rule = "- If the user asks in Malayalam, YOU MUST REPLY IN MANGLISH (using English alphabets)."

        # Construct the message history for LangChain
        system_prompt = (
            "You are EcoMitra, a friendly and helpful AI assistant for the EcoFlow Waste Management Platform in Kerala.\n"
            "You answer citizens' questions about waste disposal rules, recycling, collection schedules, and environmental tips.\n\n"
            "IMPORTANT RULES:\n"
            f"{lang_rule}\n"
            "- Keep answers concise, friendly, and practical.\n"
            "- If you find relevant information in the GOVERNMENT POLICY CONTEXT provided below, "
            'ALWAYS base your answer on it and explicitly mention the Source (e.g., "According to [Source 1]...").\n'
            "- If the context doesn't contain the answer, clearly state that the information is not available in the uploaded documents. Do NOT invent policies or use general knowledge for policy questions.\n"
            "- If they ask where to throw old medicines, say: "
            '"Old medicines should NOT be thrown in normal bins. Please wrap them securely and hand them over directly '
            'to the Haritha Karma Sena or drop them at the nearest PHC (Public Health Center)."\n'
            f"{context_string}"
        )

        langchain_messages: List[Any] = [SystemMessage(content=system_prompt)]
        for m in body.messages:
            if m.role == "user":
                langchain_messages.append(HumanMessage(content=m.content))
            else:
                langchain_messages.append(AIMessage(content=m.content))

        response = await model.ainvoke(langchain_messages)

        return {"reply": response.content}

    except Exception as e:
        print(f"Chat API Error: {e}")
        return {"error": "Failed to generate response", "details": str(e)}


@router.post("/api/transcribe")
async def transcribe(
    file: UploadFile = File(...),
    language: Optional[str] = Form(None)
):
    try:
        contents = await file.read()
        
        from groq import Groq
        client = Groq(api_key=GROQ_API_KEY)
        
        whisper_lang = None
        if language:
            if "ml" in language:
                whisper_lang = "ml"
            elif "en" in language:
                whisper_lang = "en"
                
        transcription = client.audio.transcriptions.create(
            file=(file.filename, contents, file.content_type),
            model="whisper-large-v3",
            response_format="json",
            language=whisper_lang
        )
        
        return {"text": transcription.text}
    except Exception as e:
        print(f"Transcription Error: {e}")
        return {"error": "Failed to transcribe audio", "details": str(e)}
