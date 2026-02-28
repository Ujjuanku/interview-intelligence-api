import json
import logging
from typing import List, Dict, Any
from app.services.embeddings import get_embeddings, client
from app.services.faiss_store import faiss_store
from app.schemas.question import QuestionResponse

logger = logging.getLogger(__name__)

async def generate_interview_questions(role: str) -> QuestionResponse:
    """
    Generates resume-aware interview questions based on the complete context or top chunks.
    Since we don't have a specific query, we retrieve the top chunks that generally 
    match the 'role' to provide context to the LLM.
    """
    try:
        # Step 1: Retrieve relevant resume chunks
        # We embed the role itself to find the most relevant experiences in the resume
        query_embedding = (await get_embeddings([role]))[0]
        results = faiss_store.search(query_embedding, top_k=5)
        
        context_texts = [metadata.get("text", "") for metadata, score in results if metadata.get("text")]
        resume_context = "\n\n".join(context_texts)
        
        if not resume_context:
            resume_context = "No relevant resume data found in the index for this role."

        # Step 2: Build the prompt
        system_prompt = """You are an expert technical interviewer and senior engineering manager.
Your task is to generate exactly 5 advanced, highly technical interview questions for a candidate.

CRITICAL REQUIREMENTS:
1. Questions MUST be directly based on the provided resume context.
2. Focus heavily on trade-offs, system design, scaling, and architectural decisions.
3. DO NOT ask generic questions like "What are your strengths?" or basic definition questions.
4. Adapt the difficulty to assume a senior/experienced candidate if the resume reflects it.
5. You MUST return the output STRICTLY as a JSON object matching this schema exactly:
{
  "questions": [
    "Question 1...",
    "Question 2...",
    "Question 3...",
    "Question 4...",
    "Question 5..."
  ]
}
"""
        
        user_prompt = f"""Role: {role}
        
Candidate Resume Context:
{resume_context}

Generate the 5 interview questions based on the requirements."""

        # Step 3: Call OpenAI API
        response = await client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.0,
            response_format={"type": "json_object"}
        )
        
        # Step 4: Parse and validate JSON
        content = response.choices[0].message.content
        parsed_json = json.loads(content)
        
        # Ensure we have the right structure
        if "questions" not in parsed_json or not isinstance(parsed_json["questions"], list):
            raise ValueError("LLM returned malformed JSON structure.")
            
        return QuestionResponse(questions=parsed_json["questions"][:5])
        
    except Exception as e:
        logger.error(f"Error generating questions: {e}")
        raise
