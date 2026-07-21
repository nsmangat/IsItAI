import { useState } from "react";
import LandingPage from "./components/LandingPage";

function App() {
  const [started, setStarted] = useState(false);

  if (!started) {
    return <LandingPage onStart={() => setStarted(true)} />;
  }

  return (
    <div className="flex min-h-screen items-center justify-center text-white">
      <p>Quiz placeholder</p>
    </div>
  );
}

export default App;
