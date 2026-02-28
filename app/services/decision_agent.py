import json
import logging
from app.services.embeddings import client
from app.schemas.decision import DecisionRequest, DecisionResponse

logger = logging.getLogger(__name__)

# Fallback response in case OpenAI fails to return a valid JSON structure
FALLBACK_DECISION = DecisionResponse(
    overall_average=0.0,
    consistency_trend="Unknown",
    recurring_weaknesses=["Could not evaluate structure"],
    dominant_strengths=[],
    hallucination_risk_flag=True,
    overall_confidence="Low",
    hire_recommendation="No Hire",
    justification="System error: Could not complete decision aggregation."
)

async def make_hiring_decision(request: DecisionRequest) -> DecisionResponse:
    """
    Aggregates multiple interview question evaluations into a final structured hiring decision.
    """
    system_prompt = """You are a senior AI interview decision engine.
Your job is to aggregate multiple interview question evaluations into a final structured hiring decision.

You will receive:
- Interview role
- Multiple Q&A rounds
- Structured evaluation scores for each round
- Hallucination audit results for each evaluation

YOUR TASKS:
1. Compute overall performance trends based purely on the structured data provided.
2. Detect recurring weaknesses across the rounds.
3. Detect dominant strengths.
4. Penalize evaluations flagged as hallucinated or inconsistent.
   - If ANY round has `hallucination_detected == true`, you MUST set `hallucination_risk_flag = true` and lower the `overall_confidence`.
5. Assess consistency across answers (e.g. "Stable", "Variable", "Improving", "Declining").
6. Produce a final hiring recommendation.

CRITICAL INSTRUCTIONS:
- You must NOT generate new critique.
- You must ONLY aggregate and reason over the provided structured data.
- Output MUST be STRICT JSON matching the exact schema below.

JSON SCHEMA EXPECTED:
{
  "overall_average": <float 0.0-10.0>,
  "consistency_trend": "<string>",
  "recurring_weaknesses": ["<weakness 1>", "<weakness 2>"],
  "dominant_strengths": ["<strength 1>", "<strength 2>"],
  "hallucination_risk_flag": <true/false>,
  "overall_confidence": "<Low | Medium | High>",
  "hire_recommendation": "<Strong Hire | Hire | Leaning Hire | Leaning No Hire | No Hire>",
  "justification": "<A brief text justification>"
}"""

    # Format the input data cleanly
    rounds_data = [round_item.model_dump() for round_item in request.rounds]
    rounds_json_str = json.dumps(rounds_data, indent=2)

    user_prompt = f"""Role: {request.role}

Rounds Data:
{rounds_json_str}

Compute the final hiring recommendation based on the instructions."""

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
        
        # Pydantic will automatically validate the schema structure
        return DecisionResponse(**parsed_json)

    except json.JSONDecodeError as e:
        logger.error(f"Decision Engine LLM did not return valid JSON: {e}")
        return FALLBACK_DECISION
    except Exception as e:
        logger.error(f"Error executing decision engine aggregation: {e}")
        return FALLBACK_DECISION
