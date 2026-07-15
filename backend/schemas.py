from pydantic import BaseModel

# Image handed to the quiz frontend before the user has answered - no is_ai, attribution, or analysis needed
class QuizImage(BaseModel):
    image_id: str
    public_url: str


class QuizAnswerRequest(BaseModel):
    image_id: str
    guess_is_ai: bool


# Same as analyzers.base.Signal, indicate information on why it is likely AI generated
class Signal(BaseModel):
    tell: str
    explanation: str
    coordinates: dict
    severity: str


class QuizAnswerResponse(BaseModel):
    is_correct_answer: bool
    is_ai: bool
    attribution: str
    confidence: float | None = None
    signals: list[Signal] = []
