from pydantic import BaseModel
from typing import List, Dict, Optional

class Transaction(BaseModel):
    date: Optional[str]
    description: str
    amount: float
    type: Optional[str] = None  
    category: Optional[str] = None

class AnalysisRequest(BaseModel):
    transactions: List[Transaction]

class Suggestion(BaseModel):
    suggestion: str
    expected_savings: float

class CardOption(BaseModel):
    name: str
    apr: Optional[float] = None
    annual_fee: Optional[float] = 0.0
    reward_rate: Optional[Dict[str, float]] = None
    notes: Optional[str] = None

class CardCompareRequest(BaseModel):
    user_preferences: Dict[str, float] 
    card_options: List[CardOption]
