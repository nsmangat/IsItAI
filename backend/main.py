"""
Quiz API that the frontend will communicate with to serve images, take users' answers
and let them know if their guess is correct
Will also provide the confidence and AI tells information needed to highlight on the frontend 

To run:

    uvicorn main:app --reload

"""

import random
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from schemas import QuizAnswerRequest, QuizAnswerResponse, QuizImage
from supabase_client import get_client

app = FastAPI(title="IsItAI Quiz API")
client = get_client()

# Adjust CORS settings to be able to communicate with frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)

# Serving an image
# Potential TODO: Change from client-side image tracking to server side using session based methods
@app.get("/quiz/next", response_model=QuizImage)
def get_next_image(exclude: str = ""):

    # Frontend passes image_ids already seen this quiz session so that it doesn't repeat images
    excluded_image_ids = [image_id for image_id in exclude.split(",") if image_id]

    # Only need the total row count here, not the rows themselves
    count_query = client.table("images").select("id", count="exact")

    if excluded_image_ids:
        # .not.in - exclude the rows with these ids
        count_query = count_query.not_.in_("id", excluded_image_ids)
    
    # limit(1) for a bit of efficiency - pull just 1 row, since only need count
    total_images = count_query.limit(1).execute().count

    if not total_images:
        raise HTTPException(status_code=404, detail="No images available")

    random_row_number = random.randint(0, total_images - 1)

    row_query = client.table("images").select("id, public_url")

    if excluded_image_ids:        
        row_query = row_query.not_.in_("id", excluded_image_ids)

    row = row_query.range(random_row_number, random_row_number).execute().data[0]

    return QuizImage(image_id=row["id"], public_url=row["public_url"])

# Flow of user submitting answer, then backend returning response of if they're correct and
# if it was an AI image, the info needed to highlight the AI tells on the frontend
@app.post("/quiz/answer", response_model=QuizAnswerResponse)
def submit_answer(answer: QuizAnswerRequest):

    image_response = client.table("images").select("*").eq("id", answer.image_id).execute()

    if not image_response.data:
        raise HTTPException(status_code=404, detail="Image not found")

    image = image_response.data[0]
    is_correct_answer = answer.guess_is_ai == image["is_ai"]

    confidence = None
    signals = []

    # Real images have no corresponding analyses row, so AI analyses related attributes
    # like confidence and signals will be empty, only AI images get analyzed
    if image["is_ai"]:

        analysis_response = client.table("analyses").select("*").eq("image_id", answer.image_id).execute()

        if analysis_response.data:
            analysis = analysis_response.data[0]
            confidence = analysis["confidence"]
            signals = analysis["signals"]

    return QuizAnswerResponse(
        is_correct_answer=is_correct_answer,
        is_ai=image["is_ai"],
        attribution=image["attribution"],
        confidence=confidence,
        signals=signals,
    )
