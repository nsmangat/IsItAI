const BACKEND_API_URL = import.meta.env.VITE_BACKEND_API_URL as string;

// Copies backend's Pydantic schema
export interface QuizImage {
  image_id: string;
  public_url: string;
}

export interface Signal {
  tell: string;
  explanation: string;
  coordinates: { x: number; y: number; width: number; height: number };
  severity: string;
}

export interface QuizAnswerResponse {
  is_correct_answer: boolean;
  is_ai: boolean;
  attribution: string;
  confidence: number | null;
  signals: Signal[];
}

// Getting the next image to display for the quiz
// excludeIds are images already seen this session
// Returns null to signify all images in DB currently being seen
// Future consideration: This will need to be adjusted when cycling through images daily if hosted online
export async function getNextImage(
  excludeIds: string[] = [],
): Promise<QuizImage | null> {
  const query = excludeIds.length > 0 ? `?exclude=${excludeIds.join(",")}` : "";
  const response = await fetch(`${BACKEND_API_URL}/quiz/next${query}`);

  // In current context, means quiz is done
  if (response.status === 404) {
    return null;
  }

  if (!response.ok) {
    throw new Error(`Failed to fetch next image: ${response.status}`);
  }

  return response.json();
}

// User submits their answer on if image is AI or not, then respond with QuizAnswerResponse ie
// details on the image along with correct answer
export async function submitAnswer(
  imageId: string,
  guessIsAi: boolean,
): Promise<QuizAnswerResponse> {
  const response = await fetch(`${BACKEND_API_URL}/quiz/answer`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ image_id: imageId, guess_is_ai: guessIsAi }),
  });

  if (!response.ok) {
    throw new Error(`Failed to submit answer: ${response.status}`);
  }

  return response.json();
}
