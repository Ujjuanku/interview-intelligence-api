import json
import logging
from app.services.embeddings import client
from app.schemas.auditor import AuditRequest, AuditResponse

logger = logging.getLogger(__name__)

# Fallback response in case OpenAI fails to return a valid JSON structure
FALLBACK_AUDIT = AuditResponse(
    grounded=False,
    hallucination_detected=True,
    unsupported_claims=["System error: Could not complete audit"],
    reasoning_alignment_score=1,
    score_consistency="Inconsistent",
    verdict="Potential Hallucination"
)

async def audit_evaluation(request: AuditRequest) -> AuditResponse:
    """
    Validates whether an AI-generated interview evaluation is logically grounded 
    in the candidate's actual answer and resume context.
    """
    system_prompt = """You are a strict AI evaluation auditor.
Your job is to verify whether an AI-generated interview evaluation is logically grounded in:
1) The candidate's actual answer
2) The resume context
3) The interview question

You must detect:
- Fabricated criticism or unmentioned technologies
- Unsupported assumptions
- Claims not present in the answer
- Misinterpretation of technical content
- Over-penalization without justification

You must NOT re-evaluate the answer. You must ONLY validate whether the evaluation is justified and grounded.

AUDIT INSTRUCTIONS:
1. Check whether weaknesses mentioned are actually supported by the answer.
2. Check whether strengths are justified by the answer.
3. Ensure no fabricated claims appear (e.g. criticizing a lack of a skill the question didn't ask for, or inventing claims the candidate made).
4. Verify scoring consistency with reasoning.
5. Detect exaggerated criticism.

Return STRICT JSON only matching this format:
{
  "grounded": <true/false>,
  "hallucination_detected": <true/false>,
  "unsupported_claims": ["<claim 1>", "<claim 2>"],
  "reasoning_alignment_score": <int 1-10>,
  "score_consistency": "<Consistent | Inconsistent>",
  "verdict": "<Valid Evaluation | Potential Hallucination>"
}"""

    # We need to present the JSON evaluation as a formatted string to the LLM
    eval_json_str = json.dumps(request.evaluation_json, indent=2)

    user_prompt = f"""Question:
{request.question}

Candidate Answer:
{request.candidate_answer}

Resume Context:
{request.resume_context}

Evaluation Output:
{eval_json_str}

Evaluate the integrity of the evaluation based on the instructions."""

    try:
        response = await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.0,  # Deterministic output
            response_format={"type": "json_object"}
        )
        
        content = response.choices[0].message.content
        parsed_json = json.loads(content)
        
        # Pydantic will automatically validate the schema structure
        return AuditResponse(**parsed_json)

    except json.JSONDecodeError as e:
        logger.error(f"Audit LLM did not return valid JSON: {e}")
        return FALLBACK_AUDIT
    except Exception as e:
        logger.error(f"Error executing evaluation audit: {e}")
        return FALLBACK_AUDIT
