import type { QuizAnswerResponse, QuizImage } from "../api";

interface AnswerRevealProps {
  image: QuizImage;
  answer: QuizAnswerResponse;
}

// Dictionaries to look up severity colors to map severity of signals to appropriate color
const SEVERITY_BORDER_COLORS: Record<string, string> = {
  high: "border-red-500",
  medium: "border-orange-400",
  low: "border-yellow-300",
};

const SEVERITY_TEXT_COLORS: Record<string, string> = {
  high: "text-red-500",
  medium: "text-orange-400",
  low: "text-yellow-300",
};

const SEVERITY_BG_COLORS: Record<string, string> = {
  high: "bg-red-500",
  medium: "bg-orange-400",
  low: "bg-yellow-300",
};

const SEVERITY_LEGEND: { severity: string; label: string }[] = [
  { severity: "high", label: "High severity" },
  { severity: "medium", label: "Medium severity" },
  { severity: "low", label: "Low severity" },
];

function AnswerReveal({ image, answer }: AnswerRevealProps) {
  return (
    <div className="flex flex-col items-center gap-6 px-4 text-center">
      <p className="text-2xl font-semibold text-white">
        {answer.is_correct_answer ? "Correct!" : "Incorrect!"} This image is{" "}
        {answer.is_ai ? "AI-generated" : "real"}.
      </p>

      <div className="flex flex-col items-center gap-1">
        {answer.confidence !== null && (
          <p className="text-sm text-gray-400">
            {Math.round(answer.confidence * 100)}% confidence
          </p>
        )}
        <p className="text-sm text-gray-500">{answer.attribution}</p>
      </div>

      <div className="relative inline-block">
        <img
          src={image.public_url}
          alt="Revealed quiz image"
          className="max-h-[60vh] max-w-full rounded-lg object-contain shadow-lg"
        />

        {/* Gemini reports coordinates normalized to a 0-1000 scale, not raw pixels,
            so dividing by 10 converts them straight into percentages */}
        {answer.signals.map((signal, index) => (
          <div
            key={index}
            className={`absolute border-2 ${SEVERITY_BORDER_COLORS[signal.severity] ?? "border-red-500"}`}
            style={{
              left: `${signal.coordinates.x / 10}%`,
              top: `${signal.coordinates.y / 10}%`,
              width: `${signal.coordinates.width / 10}%`,
              height: `${signal.coordinates.height / 10}%`,
            }}
          />
        ))}
      </div>

      {answer.signals.length > 0 && (
        <>
          <h2 className="text-lg font-semibold text-white">
            Signals for AI Generated Content
          </h2>

          <div className="flex flex-wrap justify-center gap-4 text-xs text-gray-400">
            {SEVERITY_LEGEND.map(({ severity, label }) => (
              <span key={severity} className="flex items-center gap-1.5">
                <span
                  className={`h-2.5 w-2.5 rounded-full ${SEVERITY_BG_COLORS[severity]}`}
                />
                {label}
              </span>
            ))}
          </div>

          <ul className="flex w-full max-w-lg flex-col gap-3 text-left">
            {answer.signals.map((signal, index) => (
              <li key={index} className="rounded-lg bg-gray-800 p-3">
                <p
                  className={`font-semibold ${SEVERITY_TEXT_COLORS[signal.severity] ?? "text-red-500"}`}
                >
                  {signal.tell}
                </p>
                <p className="text-sm text-gray-300">{signal.explanation}</p>
              </li>
            ))}
          </ul>
        </>
      )}
    </div>
  );
}

export default AnswerReveal;
