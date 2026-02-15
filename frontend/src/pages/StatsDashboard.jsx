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
const PROGRESS_TICK = 50;
const HIGHLIGHT_SLIDE_INDEX = 2;
const TOTAL_SLIDES = 6;

export default function StatsDashboard() {
  const { tournamentId } = useParams();
  const [data, setData] = useState(null);
  const [slideIndex, setSlideIndex] = useState(0);
  const [isPaused, setIsPaused] = useState(false);
  const [progress, setProgress] = useState(0);
  const [showPlayerPicker, setShowPlayerPicker] = useState(false);
  const [error, setError] = useState(null);
  const playerIdsRef = useRef(null);
  const playerCycleRef = useRef(0);
  const elapsedRef = useRef(0);

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

  // Helper: advance to next/prev slide, update player cycle, reset progress
  // NOTE: playerCycleRef must NOT be mutated inside the setSlideIndex updater
  // because React StrictMode calls updaters twice, which would double-increment.
  const goToSlide = useCallback(
    (direction) => {
      setSlideIndex((prev) => {
        const count = data ? TOTAL_SLIDES : 0;
        if (count <= 1) return 0;
        return direction === 1
          ? (prev + 1) % count
          : (prev - 1 + count) % count;
      });
      elapsedRef.current = 0;
      setProgress(0);
      fetchDashboard();
    },
    [data, fetchDashboard],
  );

  // Cycle the featured player whenever we leave the highlight slide
  const prevSlideRef = useRef(0);
  useEffect(() => {
    if (
      prevSlideRef.current === HIGHLIGHT_SLIDE_INDEX &&
      slideIndex !== HIGHLIGHT_SLIDE_INDEX &&
      playerIdsRef.current
    ) {
      playerCycleRef.current =
        (playerCycleRef.current + 1) % playerIdsRef.current.length;
    }
    prevSlideRef.current = slideIndex;
  }, [slideIndex]);

  // Progress bar tick + auto-advance
  useEffect(() => {
    if (isPaused) return;
    const id = setInterval(() => {
      elapsedRef.current += PROGRESS_TICK;
      if (elapsedRef.current >= SLIDE_INTERVAL) {
        goToSlide(1);
      } else {
        setProgress((elapsedRef.current / SLIDE_INTERVAL) * 100);
      }
    }, PROGRESS_TICK);
    return () => clearInterval(id);
  }, [isPaused, goToSlide]);

  // Select a specific player: jump to highlight slide and pause
  const selectPlayer = useCallback(
    (playerId) => {
      if (!playerIdsRef.current) return;
      const idx = playerIdsRef.current.indexOf(playerId);
      if (idx === -1) return;
      playerCycleRef.current = idx;
      setSlideIndex(HIGHLIGHT_SLIDE_INDEX);
      setIsPaused(true);
      elapsedRef.current = 0;
      setProgress(0);
      setShowPlayerPicker(false);
    },
    [],
  );

  // Keyboard controls: Space = pause, Arrows = navigate, P = player picker
  useEffect(() => {
    const handleKeyDown = (e) => {
      // Toggle player picker
      if (e.code === "KeyP") {
        e.preventDefault();
        setShowPlayerPicker((p) => !p);
        return;
      }
      // Close picker on Escape
      if (e.code === "Escape") {
        setShowPlayerPicker((prev) => {
          if (prev) {
            e.preventDefault();
            return false;
          }
          return prev;
        });
        return;
      }
      // Suppress other controls while picker is open
      if (showPlayerPicker) return;
      if (e.code === "Space") {
        e.preventDefault();
        setIsPaused((p) => !p);
      } else if (e.code === "ArrowRight") {
        e.preventDefault();
        goToSlide(1);
      } else if (e.code === "ArrowLeft") {
        e.preventDefault();
        goToSlide(-1);
      }
    };
    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [goToSlide, showPlayerPicker]);

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

  const playerList = data.player_leaderboard.map((p) => ({
    id: p.player_id,
    name: p.player_name,
  }));

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
    <SlideContainer
      slideIndex={slideIndex}
      totalSlides={slides.length}
      isPaused={isPaused}
      progress={progress}
      showPlayerPicker={showPlayerPicker}
      playerList={playerList}
      onSelectPlayer={selectPlayer}
      onClosePicker={() => setShowPlayerPicker(false)}
    >
      {slides[slideIndex]}
    </SlideContainer>
  );
}
