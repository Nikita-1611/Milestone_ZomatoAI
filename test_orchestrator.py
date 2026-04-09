from backend.models.schemas import RecommendationRequest
from backend.services.retrieval import get_ranked_candidates
from backend.services.validators import normalize_request
from backend.services.prompt_builder import build_ranking_messages
from backend.services.llm_client import run_groq_chat
from backend.services.response_validator import parse_and_validate_ranking_response

req = RecommendationRequest(location="Delhi", budget=2000.0, cuisines=[], min_rating=0.0)
norm = normalize_request(req)
cands = get_ranked_candidates(norm)
messages = build_ranking_messages(norm, cands)
content = run_groq_chat(messages)
print("RAW LLM CONTENT:", content)
parsed = parse_and_validate_ranking_response(content)
print("PARSED:", parsed)
