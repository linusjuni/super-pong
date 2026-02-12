import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import TournamentList from "./pages/TournamentList";
import TournamentSetup from "./pages/TournamentSetup";
import GamesList from "./pages/GamesList";
import GamePlay from "./pages/GamePlay";

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<TournamentList />} />
        <Route path="/tournaments/new" element={<TournamentSetup />} />
        <Route path="/tournaments/:tournamentId/games" element={<GamesList />} />
        <Route path="/tournaments/:tournamentId/games/:gameId" element={<GamePlay />} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
