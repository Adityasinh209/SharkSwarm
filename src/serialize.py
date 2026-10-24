from src.schemas import Evaluation, Financials, Pitch


def to_response(pitch: Pitch, financials: Financials, evaluation: Evaluation) -> dict:
    return {
        "pitch": pitch.model_dump(),
        "financials": financials.model_dump(),
        "evaluation": evaluation.model_dump(),
    }
