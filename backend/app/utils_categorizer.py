from typing import List, Dict
import re

CATEGORY_KEYWORDS = {
    "housing": ["rent", "mortgage", "landlord", "apartment", "lease"],
    "utilities": ["electric", "water", "gas bill", "internet", "wifi", "utility"],
    "food": ["grocery", "supermarket", "whole foods", "trader joe", "aldi", "food", "restaurant", "dining"],
    "transport": ["uber", "lyft", "taxi", "gas", "shell", "chevron", "train", "bus", "transport"],
    "entertainment": ["netflix", "spotify", "hulu", "movie", "concert", "ticket", "play"],
    "travel": ["airline", "delta", "united", "hotel", "booking", "airbnb", "expedia"],
    "health": ["pharmacy", "walgreens", "cvs", "clinic", "doctor", "hospital"],
    "education": ["university", "college", "tuition", "course", "udemy", "coursera"],
    "others": []
}

def categorize_transaction(description: str) -> str:
    desc = description.lower()
    for cat, keys in CATEGORY_KEYWORDS.items():
        for k in keys:
            if k in desc:
                return cat
    if re.search(r'\b(gift|donation)\b', desc):
        return 'others'
    return 'others'

def categorize_transactions(transactions: List[Dict]) -> List[Dict]:
    for t in transactions:
        t['category'] = categorize_transaction(t.get('description', ''))
    return transactions

def aggregate_by_category(transactions: List[Dict]):
    result = {}
    for t in transactions:
        amt = float(t.get('amount') or 0.0)
        if amt < 0:
            amt = abs(amt)
        cat = t.get('category') or 'others'
        result[cat] = result.get(cat, 0.0) + amt
    return result

def suggest_cuts(aggregates: Dict[str, float], strategy: str = 'conservative'):
    suggestions = []
    discretionary = ['entertainment', 'travel', 'others']
    total = sum(aggregates.values()) or 1.0
    for cat in aggregates:
        if cat in discretionary:
            if strategy == 'conservative':
                pct = 0.10
            elif strategy == 'aggressive':
                pct = 0.25
            else:
                pct = 0.15
            savings = aggregates[cat] * pct
            suggestions.append({
                "category": cat,
                "suggestion": f"Reduce {cat} spending by {int(pct*100)}% (e.g. cancel subscriptions, reduce dining out).",
                "expected_savings": round(savings, 2)
            })
    return suggestions
