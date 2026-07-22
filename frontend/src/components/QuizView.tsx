import { useEffect, useState } from "react";
import {
  getNextImage,
  submitAnswer,
  type QuizAnswerResponse,
  type QuizImage,
} from "../api";

function QuizView() {
  const [image, setImage] = useState<QuizImage | null>(null);
  const [answer, setAnswer] = useState<QuizAnswerResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  // Get an initial image on quiz load
  useEffect(() => {
    async function loadImage() {
      try {
        const nextImage = await getNextImage();
        setImage(nextImage);
      } catch {
        setError("Error: Image could not be loaded.");
      }
    }

    loadImage();
  }, []);

  async function handleGuess(guessIsAi: boolean) {
    if (!image) return;

    try {
      const result = await submitAnswer(image.image_id, guessIsAi);
      setAnswer(result);
    } catch {
      setError("Error: Answer could not be submitted");
    }
  }

  if (error) {
    return (
      <div className="flex min-h-screen items-center justify-center text-red-400">
        {error}
      </div>
    );
  }

  if (!image) {
    return (
      <div className="flex min-h-screen items-center justify-center text-gray-400">
        Loading...
      </div>
    );
  }

  return (
    <div className="flex min-h-screen flex-col items-center justify-center gap-8 px-4">
      <h1 className="text-4xl font-bold text-white">Is It AI?</h1>

      <img
        src={image.public_url}
        alt="Guess whether this image is AI-generated or real"
        className="max-h-[60vh] max-w-full rounded-lg object-contain shadow-lg"
      />

      {answer ? (
        // TODO: fill with actual info
        <p className="text-2xl font-semibold text-white">
          {answer.is_correct_answer ? "Correct!" : "Incorrect!"} This image is{" "}
          {answer.is_ai ? "AI-generated" : "real"}.
        </p>
      ) : (
        <div className="flex gap-4">
          <button
            onClick={() => handleGuess(true)}
            className="rounded-lg bg-violet-600 px-6 py-3 text-lg font-semibold text-white transition hover:bg-violet-500"
          >
            Yes
          </button>
          <button
            onClick={() => handleGuess(false)}
            className="rounded-lg bg-gray-700 px-6 py-3 text-lg font-semibold text-white transition hover:bg-gray-600"
          >
            No
          </button>
        </div>
      )}
    </div>
  );
}

export default QuizView;
