import { useState } from "react";
import LandingPage from "./components/LandingPage";
import QuizView from "./components/QuizView";

function App() {
  const [started, setStarted] = useState(false);

  if (!started) {
    return <LandingPage onStart={() => setStarted(true)} />;
  }

  return <QuizView />;
}

export default App;
