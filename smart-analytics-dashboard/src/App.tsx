import { ThemeProvider } from "./contexts/ThemeContext";
import Results from "./pages/Results";

function App() {
  return (
    <ThemeProvider>
      <Results />
    </ThemeProvider>
  );
}

export default App;
