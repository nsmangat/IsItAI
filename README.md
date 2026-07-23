# IsItAI

A quiz based web app that tests how well you can tell AI-generated images apart from real photos. This was built to help people (especially those less familiar with AI-generated content, like elderly users) recognize common tell-tale signs of AI images and avoid falling for scams that rely on them.

You're shown an image, guess whether it's real or AI-generated, and the app then reveals the answer.
For AI images, it also highlights the specific regions Gemini Vision flagged as suspicious, along
with an explanation of why each one is a common sign of AI-generated content.

![AI image example - no answer ](/Screenshots/AI_Image_Example_No_Answer.png)
![AI image example - answer ](/Screenshots/AI_Image_Example_Answer.png)

## Tech stack

- **Backend**: Python, FastAPI, Supabase (Postgres + Storage), Google Gemini Vision
- **Frontend**: React, TypeScript, Vite, Tailwind CSS
- **Image sources**:
  - [Pollinations.ai](https://pollinations.ai) (AI-generated images),
  - [Unsplash](https://unsplash.com/developers) (real images)

## Prerequisites

- Python 3.11+
- Node.js 18+
- [Supabase](https://supabase.com) project (free tier) or alternatives for image storage and Postgres
- A [Google Gemini API key](https://aistudio.google.com/apikey) (free tier)
- [Unsplash API key](https://unsplash.com/developers) (free tier)
- \*Pollinations.ai doesn't require an API key, but they do have plans to utilize more premium models

## Setup

### 1. Backend Setup

From the project root:

```bash
python -m venv venv
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate

pip install -r backend/requirements.txt
```

### 2. Environment variables

Copy `backend/.env.example` to `backend/.env` and fill in:

```
UNSPLASH_ACCESS_KEY=       # unsplash.com/developers
GEMINI_API_KEY=            # aistudio.google.com/apikey
SUPABASE_URL=              # Supabase project URL
SUPABASE_KEY=              # Supabase SECRET key

```

### 3. Supabase Setup

1. Create a new Supabase project.
2. In the SQL editor, run `backend/sql/schema.sql` to create the `images`/`analyses` tables
   (with RLS policies for public read access).
3. Create a Storage bucket named `images` (must be lowercase), marked **public**.

### 4. Frontend Setup

```bash
cd frontend
npm install
```

`frontend/.env` for the frontend to communicate with the backend API include:  
`VITE_BACKEND_API_URL=http://127.0.0.1:8000`

## Running the app

```bash
# Terminal 1 - backend (from backend/, with venv activated)
uvicorn main:app --reload

# Terminal 2 - frontend (from frontend/)
npm run dev
```

This opens the backend and frontend dev servers in separate windows.

- Frontend: http://localhost:5173
- Backend + interactive API docs: http://127.0.0.1:8000/docs

## Fetching, Analyzing and Storing Images

The processes of fetching real and AI-generated images, analyzing the AI images, and storing them to the cloud are all separate scripts. The scripts themselves such as the analyzer script follow the **Strategy Pattern** of having an abstract base class with common functionality like rate-limiting, then a specific analyzer such as Google Gemini Vision implements it and incorporates the code to communicate with its API. I developed in this modular approach to ensure loose coupling so that I could fetch a bunch of images without having to be worried about instantly having to store them for example, as well as in the future trying out different sources for getting images or analyzing the AI ones without having to change much code.

These scripts are in `backend/` and can be ran individually. The flow to setup the images to be ready for the quiz look like this:

1. Fetch x amount of AI and real images
2. Analyze the AI-generated images for AI tells
3. Upload the images to storage

```bash
# Fetch AI-generated and real images (saved locally to backend/images/)
python fetch_images.py --ai 5 --real 5

# Analyze AI images with Gemini Vision
python analyze_images.py

# Upload the images and analysis results of the AI ones to Supabase
python upload_images.py
```

Useful flags:

- `--limit N` (analyze_images.py, upload_images.py) - cap how many get processed in
  one run
- `--no-rate-limit` (fetch_images.py, analyze_images.py) - skip the delay between
  requests (Caution with this to not go over rate limits, mainly used if I needed to fetch or analyze something quickly after a request for testing)
- `--force` (analyze_images.py) - re-analyze images that already have a result

## API

- `GET /quiz/next?exclude=id1,id2,...` - returns a random image (`image_id`, `public_url`) not
  in the excluded list, without revealing the answer
- `POST /quiz/answer` - `{ "image_id": "...", "guess_is_ai": true }` - returns whether the guess
  was correct, the real answer, confidence, and for AI images, the list of flagged signals with
  bounding box coordinates

Full interactive docs at `/docs` once the backend is running.

## Future Considerations

- Deploying the project and gamifying it by having hi-scores for users for how many images they got correct for the day
- Background task to add and remove new images daily
- Trying out different models for AI-image analysis and generation

## Credits

Thanks to [Pollinations.ai](https://pollinations.ai) for free, keyless AI image generation,
[Unsplash](https://unsplash.com) and its photographers for free real photos, and Google Gemini
Vision for making the AI image analysis possible.
