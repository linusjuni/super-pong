import { useEffect, useCallback, useRef, useState } from "react";
import { useParams } from "react-router-dom";
import { tournamentApi } from "@/services/api";
import SlideContainer from "@/components/stats/SlideContainer";
import TournamentStandingsSlide from "@/components/stats/TournamentStandingsSlide";
import PlayerOverviewSlide from "@/components/stats/PlayerOverviewSlide";
import PlayerHighlightSlide from "@/components/stats/PlayerHighlightSlide";
import PunishmentBongsSlide from "@/components/stats/PunishmentBongsSlide";
import ByTheNumbersSlide from "@/components/stats/ByTheNumbersSlide";
import SuperlativesSlide from "@/components/stats/SuperlativesSlide";

const SLIDE_INTERVAL = 8_000;
const HIGHLIGHT_SLIDE_INDEX = 2;

export default function StatsDashboard() {
  const { tournamentId } = useParams();
  const [data, setData] = useState(null);
  const [slideIndex, setSlideIndex] = useState(0);
  const [error, setError] = useState(null);
  const playerIdsRef = useRef(null);
  const playerCycleRef = useRef(0);

  const fetchDashboard = useCallback(async () => {
    try {
      const d = await tournamentApi.getDashboard(tournamentId);
      setData(d);
      // Lock in player order on first fetch
      if (playerIdsRef.current === null && d.player_leaderboard.length > 0) {
        playerIdsRef.current = d.player_leaderboard.map((p) => p.player_id);
      }
    } catch (e) {
      setError(e.message);
    }
  }, [tournamentId]);

  // Initial fetch
  useEffect(() => {
    fetchDashboard();
  }, [fetchDashboard]);

  // Advance slide + refresh data each time
  useEffect(() => {
    const id = setInterval(() => {
      setSlideIndex((prev) => {
        const count = data ? 6 : 0;
        const next = count > 1 ? (prev + 1) % count : 0;
        if (prev === HIGHLIGHT_SLIDE_INDEX && playerIdsRef.current) {
          playerCycleRef.current =
            (playerCycleRef.current + 1) % playerIdsRef.current.length;
        }
        return next;
      });
      fetchDashboard();
    }, SLIDE_INTERVAL);
    return () => clearInterval(id);
  }, [data, fetchDashboard]);

  if (error) {
    return (
      <div className="flex h-screen items-center justify-center text-destructive">
        Error: {error}
      </div>
    );
  }

  if (!data) {
    return (
      <div className="flex h-screen items-center justify-center text-muted-foreground">
        Loading...
      </div>
    );
  }

  const featuredPlayerId = playerIdsRef.current?.[playerCycleRef.current] ?? null;

  const slides = [
    <TournamentStandingsSlide key="standings" data={data} />,
    <PlayerOverviewSlide key="players" data={data} />,
    <PlayerHighlightSlide
      key="highlight"
      data={data}
      featuredPlayerId={featuredPlayerId}
    />,
    <PunishmentBongsSlide key="punishments" data={data} />,
    <ByTheNumbersSlide key="numbers" data={data} />,
    <SuperlativesSlide key="superlatives" data={data} />,
  ];

  return (
    <SlideContainer slideIndex={slideIndex} totalSlides={slides.length}>
      {slides[slideIndex]}
    </SlideContainer>
  );
}
