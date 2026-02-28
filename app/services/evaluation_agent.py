import json
import logging
from app.services.embeddings import client
from app.schemas.evaluation import EvaluationRequest, EvaluationResponse, Scores

logger = logging.getLogger(__name__)

# Fallback response in case OpenAI completely fails to return a valid JSON structure or errors out
FALLBACK_EVALUATION = EvaluationResponse(
    scores=Scores(
        conceptual_clarity=0,
        technical_depth=0,
        real_world_application=0,
        communication_precision=0
    ),
    confidence_level="Low",
    strengths=["None identified due to processing error"],
    weaknesses=["The answer could not be properly evaluated"],
    improvement_suggestions=["Please try answering the question again or providing more context."],
    final_score=0
)

async def evaluate_candidate_answer(request: EvaluationRequest) -> EvaluationResponse:
    """
    Evaluates a candidate's answer using GPT-4o against the provided question and their resume context.
    Enforces a strict deterministic JSON output scale.
    """
    system_prompt = """You are an expert technical interviewer and senior engineering manager evaluating a candidate's answer.
You will be provided with:
1. The Question asked
2. The Candidate's Resume Context
3. The Candidate's Answer

Your task is to critically evaluate the answer and return a STRICT JSON object matching the schema below.

EVALUATION CRITERIA:
- Penalize vague, buzzword-heavy, or non-technical answers heavily.
- Reward deep technical discussions, especially regarding trade-offs, scaling, and architectural decisions.
- Detect if the candidate missed the core technical depth required for the question.
- Compare their answer to what is expected given their resume context (e.g., a senior engineer should give a senior-level answer).

RETURN FORMAT (STRICT JSON):
{
  "scores": {
    "conceptual_clarity": <int 0-10>,
    "technical_depth": <int 0-10>,
    "real_world_application": <int 0-10>,
    "communication_precision": <int 0-10>
  },
  "confidence_level": "<Low | Medium | High>",
  "strengths": ["<strength 1>", "<strength 2>"],
  "weaknesses": ["<weakness 1>", "<weakness 2>"],
  "improvement_suggestions": ["<suggestion 1>", "<suggestion 2>"],
  "final_score": <int 0-100>
}
"""

    user_prompt = f"""Question:
{request.question}

Candidate Resume Context:
{request.resume_context}

Candidate Answer:
{request.answer}

Evaluate the candidate's answer based on the criteria."""

    try:
        response = await client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.0,  # Deterministic output
            response_format={"type": "json_object"}
        )
        
        content = response.choices[0].message.content
        parsed_json = json.loads(content)
        
        # Pydantic will automatically validate the schema structure, raising ValueError if malformed
        return EvaluationResponse(**parsed_json)

    except json.JSONDecodeError as e:
        logger.error(f"LLM did not return valid JSON: {e}")
        return FALLBACK_EVALUATION
    except Exception as e:
        logger.error(f"Error evaluating answer: {e}")
        # Return fallback to avoid crashing the endpoint and dropping the interview state
        return FALLBACK_EVALUATION
