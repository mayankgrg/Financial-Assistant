from fastapi import APIRouter
from pydantic import parse_obj_as
from .schemas import AnalysisRequest, Suggestion, CardCompareRequest, CardOption
from .utils_categorizer import aggregate_by_category, suggest_cuts
from fastapi.responses import StreamingResponse
import io, matplotlib.pyplot as plt

router = APIRouter()

@router.post("/summary")
async def summary(req: AnalysisRequest):
    txs = [t.dict() if hasattr(t, 'dict') else t for t in req.transactions]
    agg = aggregate_by_category(txs)
    total = sum(agg.values()) or 0.0
    return {"aggregates": agg, "total": total}

@router.post("/suggestions")
async def suggestions(req: AnalysisRequest, strategy: str = 'conservative'):
    txs = [t.dict() if hasattr(t, 'dict') else t for t in req.transactions]
    agg = aggregate_by_category(txs)
    suggestions = suggest_cuts(agg, strategy=strategy)
    adjusted = agg.copy()
    for s in suggestions:
        cat = s['category']
        adjusted[cat] = max(0.0, adjusted[cat] - s['expected_savings'])
    total = sum(agg.values())
    adjusted_total = sum(adjusted.values())
    return {"original": {"aggregates": agg, "total": total},
            "suggestions": suggestions,
            "adjusted": {"aggregates": adjusted, "total": adjusted_total}}

@router.post("/pie_image")
async def pie_image(req: AnalysisRequest):
    txs = [t.dict() if hasattr(t, 'dict') else t for t in req.transactions]
    agg = aggregate_by_category(txs)
    labels = list(agg.keys())
    sizes = [v for v in agg.values()]
    fig, ax = plt.subplots()
    ax.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=140)
    ax.axis('equal')
    buf = io.BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight')
    plt.close(fig)
    buf.seek(0)
    return StreamingResponse(buf, media_type="image/png")

@router.post("/credit/compare")
async def credit_compare(req: CardCompareRequest):
    prefs = req.user_preferences
    results = []
    for card in req.card_options:
        score = 0.0
        rewards = card.reward_rate or {}
        for k, w in prefs.items():
            rate = rewards.get(k, 0.0)
            score += w * rate
        fee_penalty = (card.annual_fee or 0.0) * 0.01
        apr_penalty = (card.apr or 0.0) * 0.001
        final_score = score - fee_penalty - apr_penalty
        results.append({
            "card": card.name,
            "score": round(final_score, 4),
            "notes": card.notes
        })
    results = sorted(results, key=lambda x: x['score'], reverse=True)
    return {"results": results}
