interface LandingPageProps {
  onStart: () => void;
}

function LandingPage({ onStart }: LandingPageProps) {
  return (
    <div className="flex min-h-screen flex-col items-center justify-center gap-6 px-4 text-center">
      <h1 className="text-5xl font-bold text-white">Is It AI?</h1>
      <p className="max-w-md text-lg text-gray-400">
        Can you tell a real photo from an AI-generated one? Try this quiz to
        test your eye and learn about the common signs of AI images that
        scammers hope you'll miss.
      </p>
      <button
        onClick={onStart}
        className="rounded-lg bg-violet-600 px-6 py-3 text-lg font-semibold text-white transition hover:bg-violet-500"
      >
        Start Quiz
      </button>
    </div>
  );
}

export default LandingPage;
