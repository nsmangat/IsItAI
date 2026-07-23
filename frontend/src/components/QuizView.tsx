import { useEffect, useState } from "react";
import {
  getNextImage,
  submitAnswer,
  type QuizAnswerResponse,
  type QuizImage,
} from "../api";
import AnswerReveal from "./AnswerReveal";

function QuizView() {
  const [image, setImage] = useState<QuizImage | null>(null);
  const [answer, setAnswer] = useState<QuizAnswerResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [seenImageIds, setSeenImageIds] = useState<string[]>([]);
  const [finished, setFinished] = useState(false); // All images seen in the quiz

  // Fetches a new image, excluding ones already seen this session
  async function loadNextImage() {
    setError(null);
    setAnswer(null);
    setImage(null);

    try {
      const nextImage = await getNextImage(seenImageIds);

      // Exhausted all images
      if (!nextImage) {
        setFinished(true);
        return;
      }

      setImage(nextImage);
      setSeenImageIds((prev) => [...prev, nextImage.image_id]);
    } catch {
      setError("Error: Image could not be loaded.");
    }
  }

  // Get an initial image on quiz load
  useEffect(() => {
    loadNextImage();
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

  if (finished) {
    return (
      <div className="flex min-h-screen flex-col items-center justify-center gap-2 text-center text-white">
        <p className="text-2xl font-semibold">You've seen every image!</p>
        <p className="text-gray-400">Check back later for more.</p>
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
    <div className="flex min-h-screen flex-col items-center justify-center gap-8 px-4 py-8">
      <h1 className="text-4xl font-bold text-white">Is It AI?</h1>

      {answer ? (
        <AnswerReveal image={image} answer={answer} onNext={loadNextImage} />
      ) : (
        <>
          <img
            src={image.public_url}
            alt="Guess whether this image is AI-generated or real"
            className="max-h-[60vh] max-w-full rounded-lg object-contain shadow-lg"
          />
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
        </>
      )}
    </div>
  );
}

export default QuizView;
