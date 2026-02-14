import { useEffect, useState, useRef, useCallback } from "react";
import { useParams, Link } from "react-router-dom";
import { gameApi, tournamentApi, playerApi, shotApi } from "@/services/api";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardHeader,
  CardTitle,
  CardContent,
} from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
} from "@/components/ui/dialog";

const statusLabel = {
  not_started: "Not Started",
  in_progress: "In Progress",
  completed: "Completed",
};

const statusVariant = {
  not_started: "secondary",
  in_progress: "default",
  completed: "outline",
};

const SHOT_TYPES = ["normal", "bounce", "trickshot"];
const OUTCOMES = ["miss", "hit", "rim"];
const outcomeLabel = { miss: "Airball", hit: "Hit", rim: "Rim", none: "" };
const shotTypeLabel = { normal: "Normal", bounce: "Bounce", trickshot: "Trickshot", rerack: "Rerack" };

function formatTime(seconds) {
  const m = Math.floor(seconds / 60);
  const s = seconds % 60;
  return `${String(m).padStart(2, "0")}:${String(s).padStart(2, "0")}`;
}

function formatTimestamp(ts) {
  const d = new Date(ts);
  return d.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit", second: "2-digit" });
}

export default function GamePlay() {
  const { tournamentId, gameId } = useParams();

  // --- Data state ---
  const [game, setGame] = useState(null);
  const [teamMap, setTeamMap] = useState({});
  const [playerMap, setPlayerMap] = useState({});
  const [shots, setShots] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // --- Shot form state ---
  const [selectedPlayerId, setSelectedPlayerId] = useState(null);
  const [selectedTeamId, setSelectedTeamId] = useState(null);
  const [shotType, setShotType] = useState(null);
  const [outcome, setOutcome] = useState(null);
  const [bounces, setBounces] = useState(null);
  const [elbowViolation, setElbowViolation] = useState(false);
  const [cupPosition, setCupPosition] = useState(null);
  const [submitting, setSubmitting] = useState(false);

  // --- Timer state ---
  const GAME_DURATION = 20 * 60; // 20 minutes in seconds
  const [timerSeconds, setTimerSeconds] = useState(GAME_DURATION);
  const timerRef = useRef(null);

  // --- Dialog state ---
  const [endGameOpen, setEndGameOpen] = useState(false);

  // --- Data fetching ---
  const fetchGame = useCallback(async () => {
    return gameApi.get(gameId);
  }, [gameId]);

  const fetchShots = useCallback(async () => {
    const s = await shotApi.list(gameId);
    setShots(s);
  }, [gameId]);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [g, teamsList] = await Promise.all([
          fetchGame(),
          tournamentApi.getTeams(tournamentId),
        ]);
        setGame(g);

        const tMap = {};
        for (const t of teamsList) tMap[t.id] = t;
        setTeamMap(tMap);

        // Collect unique player IDs from the two teams in this game
        const team1 = tMap[g.team1_id];
        const team2 = tMap[g.team2_id];
        const playerIds = [
          ...new Set([
            team1?.player1_id,
            team1?.player2_id,
            team2?.player1_id,
            team2?.player2_id,
          ].filter(Boolean)),
        ];

        const players = await Promise.all(playerIds.map((id) => playerApi.get(id)));
        const pMap = {};
        for (const p of players) pMap[p.id] = p;
        setPlayerMap(pMap);

        await fetchShots();
      } catch (e) {
        setError(e.message);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, [tournamentId, gameId, fetchGame, fetchShots]);

  // --- Timer logic: derive from game.started_at ---
  useEffect(() => {
    clearInterval(timerRef.current);

    if (!game?.started_at || game.status !== "in_progress") return;

    const calcRemaining = () => {
      // Ensure the timestamp is treated as UTC (SQLite drops timezone info)
      const startedAtUtc = game.started_at.endsWith("Z")
        ? game.started_at
        : game.started_at + "Z";
      const elapsed = Math.floor(
        (Date.now() - new Date(startedAtUtc).getTime()) / 1000
      );
      return Math.max(0, GAME_DURATION - elapsed);
    };

    setTimerSeconds(calcRemaining());

    timerRef.current = setInterval(() => {
      const remaining = calcRemaining();
      setTimerSeconds(remaining);
      if (remaining <= 0) clearInterval(timerRef.current);
    }, 1000);

    return () => clearInterval(timerRef.current);
  }, [game?.started_at, game?.status]);

  // --- Handlers ---
  const handleStartGame = async () => {
    try {
      const updated = await gameApi.update(gameId, { status: "in_progress" });
      setGame(updated);
    } catch (e) {
      setError(e.message);
    }
  };

  const handleResetTimer = async () => {
    try {
      const updated = await gameApi.update(gameId, {
        started_at: new Date().toISOString(),
      });
      setGame(updated);
    } catch (e) {
      setError(e.message);
    }
  };

  const handleEndGame = async (winnerTeamId) => {
    try {
      const updated = await gameApi.update(gameId, {
        winner_id: winnerTeamId,
        status: "completed",
      });
      setGame(updated);
      clearInterval(timerRef.current);
      setEndGameOpen(false);
    } catch (e) {
      setError(e.message);
    }
  };

  const resetForm = () => {
    setSelectedPlayerId(null);
    setSelectedTeamId(null);
    setShotType(null);
    setOutcome(null);
    setBounces(null);
    setElbowViolation(false);
    setCupPosition(null);
  };

  const handleLogShot = async () => {
    if (!selectedPlayerId || !selectedTeamId || !shotType || !outcome) return;
    if (shotType === "bounce" && !bounces) return;

    setSubmitting(true);
    try {
      await shotApi.create(gameId, {
        player_id: selectedPlayerId,
        team_id: selectedTeamId,
        shot_type: shotType,
        outcome,
        bounces: shotType === "bounce" ? bounces : null,
        elbow_violation: elbowViolation,
        cup_position: outcome === "hit" ? cupPosition : null,
      });
      await fetchShots();
      resetForm();
    } catch (e) {
      setError(e.message);
    } finally {
      setSubmitting(false);
    }
  };

  const handleDeleteShot = async (shotId) => {
    try {
      await shotApi.delete(shotId);
      await fetchShots();
    } catch (e) {
      setError(e.message);
    }
  };

  const handleRerack = async (team) => {
    try {
      await shotApi.create(gameId, {
        player_id: team.player1_id,
        team_id: team.id,
        shot_type: "rerack",
        outcome: "none",
      });
      await fetchShots();
    } catch (e) {
      setError(e.message);
    }
  };

  const selectPlayer = (playerId, teamId) => {
    setSelectedPlayerId(playerId);
    setSelectedTeamId(teamId);
  };

  // --- Render helpers ---
  if (loading) return <div className="p-6 text-muted-foreground">Loading...</div>;
  if (error) return <div className="p-6 text-destructive">Error: {error}</div>;

  const team1 = teamMap[game.team1_id];
  const team2 = teamMap[game.team2_id];
  const isPlaying = game.status === "in_progress";
  const isCompleted = game.status === "completed";
  const isNotStarted = game.status === "not_started";

  const canLogShot =
    selectedPlayerId && selectedTeamId && shotType && outcome &&
    (shotType !== "bounce" || bounces);

  return (
    <div className="mx-auto max-w-2xl p-6">
      {/* Header */}
      <div className="mb-6 flex items-center gap-4">
        <Button variant="ghost" asChild>
          <Link to={`/tournaments/${tournamentId}/games`}>← Back</Link>
        </Button>
      </div>

      {/* Game info bar */}
      <Card className="mb-6">
        <CardHeader>
          <div className="flex items-center justify-between">
            <CardTitle className="text-2xl">
              {team1?.name ?? "?"} vs {team2?.name ?? "?"}
            </CardTitle>
            <Badge variant={statusVariant[game.status]}>
              {statusLabel[game.status]}
            </Badge>
          </div>
        </CardHeader>
        <CardContent>
          <div className="flex items-center justify-between">
            {/* Timer */}
            <div className="text-3xl font-mono font-bold tabular-nums">
              {isNotStarted ? "20:00" : formatTime(timerSeconds)}
            </div>

            {/* Actions */}
            <div className="flex gap-2">
              {isNotStarted && (
                <Button onClick={handleStartGame}>Start Game</Button>
              )}
              {isPlaying && (
                <Button variant="outline" onClick={handleResetTimer}>
                  Reset Timer
                </Button>
              )}
              {isPlaying && (
                <Button variant="destructive" onClick={() => setEndGameOpen(true)}>
                  End Game
                </Button>
              )}
            </div>
          </div>

          {isCompleted && game.winner_id && (
            <div className="mt-4 rounded-lg bg-muted p-3 text-center">
              <span className="text-muted-foreground">Winner: </span>
              <span className="font-semibold">
                {teamMap[game.winner_id]?.name ?? "?"}
              </span>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Rerack — only when in progress */}
      {isPlaying && (
        <div className="mb-6 flex gap-3">
          <Button
            variant="outline"
            className="flex-1"
            onClick={() => handleRerack(team1)}
          >
            {team1?.name ?? "?"} Rerack
          </Button>
          <Button
            variant="outline"
            className="flex-1"
            onClick={() => handleRerack(team2)}
          >
            {team2?.name ?? "?"} Rerack
          </Button>
        </div>
      )}

      {/* Shot form — only when in progress */}
      {isPlaying && (
        <Card className="mb-6">
          <CardHeader>
            <CardTitle className="text-lg">Log Shot</CardTitle>
          </CardHeader>
          <CardContent className="space-y-5">
            {/* Player selection — quick-tap buttons grouped by team */}
            <div className="space-y-3">
              {[team1, team2].map((team) => {
                if (!team) return null;
                const players = [
                  playerMap[team.player1_id],
                  playerMap[team.player2_id],
                ].filter(Boolean);
                return (
                  <div key={team.id}>
                    <p className="mb-1.5 text-sm font-medium text-muted-foreground">
                      {team.name}
                    </p>
                    <div className="flex gap-2">
                      {players.map((p) => (
                        <Button
                          key={p.id}
                          variant={
                            selectedPlayerId === p.id ? "default" : "outline"
                          }
                          className="flex-1"
                          onClick={() => selectPlayer(p.id, team.id)}
                        >
                          {p.name}
                        </Button>
                      ))}
                    </div>
                  </div>
                );
              })}
            </div>

            {/* Shot type */}
            <div>
              <p className="mb-1.5 text-sm font-medium text-muted-foreground">
                Shot Type
              </p>
              <div className="flex gap-2">
                {SHOT_TYPES.map((t) => (
                  <Button
                    key={t}
                    variant={shotType === t ? "default" : "outline"}
                    className="flex-1"
                    onClick={() => {
                      setShotType(t);
                      if (t !== "bounce") setBounces(null);
                    }}
                  >
                    {shotTypeLabel[t]}
                  </Button>
                ))}
              </div>
            </div>

            {/* Bounces — only for bounce shots */}
            {shotType === "bounce" && (
              <div>
                <p className="mb-1.5 text-sm font-medium text-muted-foreground">
                  Bounces
                </p>
                <div className="flex gap-2">
                  {[1, 2, 3, 4, 5].map((n) => (
                    <Button
                      key={n}
                      variant={bounces === n ? "default" : "outline"}
                      size="sm"
                      onClick={() => setBounces(n)}
                    >
                      {n}
                    </Button>
                  ))}
                </div>
              </div>
            )}

            {/* Outcome */}
            <div>
              <p className="mb-1.5 text-sm font-medium text-muted-foreground">
                Outcome
              </p>
              <div className="flex gap-2">
                {OUTCOMES.map((o) => (
                  <Button
                    key={o}
                    variant={outcome === o ? "default" : "outline"}
                    className="flex-1"
                    onClick={() => {
                      setOutcome(o);
                      if (o !== "hit") setCupPosition(null);
                    }}
                  >
                    {outcomeLabel[o]}
                  </Button>
                ))}
              </div>
            </div>

            {/* Cup position — only for hits */}
            {outcome === "hit" && (() => {
              const rows =
                game.starting_cups_per_team === 10
                  ? [[1], [2, 3], [4, 5, 6], [7, 8, 9, 10]]
                  : [[1], [2, 3], [4, 5, 6]];
              return (
                <div>
                  <p className="mb-1.5 text-sm font-medium text-muted-foreground">
                    Cup Position <span className="text-xs font-normal">(optional)</span>
                  </p>
                  <div className="flex flex-col items-center gap-1.5">
                    {rows.map((row, ri) => (
                      <div key={ri} className="flex gap-1.5">
                        {row.map((n) => (
                          <button
                            key={n}
                            type="button"
                            onClick={() =>
                              setCupPosition(cupPosition === n ? null : n)
                            }
                            className={`flex h-9 w-9 items-center justify-center rounded-full border text-sm font-medium transition-colors ${
                              cupPosition === n
                                ? "bg-primary text-primary-foreground border-primary"
                                : "bg-background hover:bg-accent border-input"
                            }`}
                          >
                            {n}
                          </button>
                        ))}
                      </div>
                    ))}
                  </div>
                </div>
              );
            })()}

            {/* Elbow violation */}
            <label className="flex items-center gap-2 cursor-pointer">
              <input
                type="checkbox"
                checked={elbowViolation}
                onChange={(e) => setElbowViolation(e.target.checked)}
                className="h-4 w-4 rounded border-input"
              />
              <span className="text-sm">Elbow violation</span>
            </label>

            {/* Submit */}
            <Button
              className="w-full"
              disabled={!canLogShot || submitting}
              onClick={handleLogShot}
            >
              {submitting ? "Logging..." : "Log Shot"}
            </Button>
          </CardContent>
        </Card>
      )}

      {/* Shot history */}
      {shots.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="text-lg">Shot History</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              {shots.map((shot) => (
                <div
                  key={shot.id}
                  className="flex items-center justify-between rounded-lg border px-3 py-2 text-sm"
                >
                  <div className="flex flex-wrap items-center gap-2">
                    <span className="text-muted-foreground">
                      {formatTimestamp(shot.timestamp)}
                    </span>
                    {shot.shot_type === "rerack" ? (
                      <>
                        <Badge variant="secondary" className="text-xs">
                          Rerack
                        </Badge>
                        <Badge variant="outline" className="text-xs">
                          {teamMap[shot.team_id]?.name ?? "?"}
                        </Badge>
                      </>
                    ) : (
                      <>
                        <span className="font-medium">
                          {playerMap[shot.player_id]?.name ?? "?"}
                        </span>
                        <Badge variant="outline" className="text-xs">
                          {teamMap[shot.team_id]?.name ?? "?"}
                        </Badge>
                        <Badge variant="secondary" className="text-xs">
                          {shotTypeLabel[shot.shot_type]}
                        </Badge>
                        {shot.shot_type === "bounce" && shot.bounces && (
                          <span className="text-xs text-muted-foreground">
                            ({shot.bounces}x)
                          </span>
                        )}
                        <Badge
                          variant={shot.outcome === "hit" ? "default" : "outline"}
                          className="text-xs"
                        >
                          {outcomeLabel[shot.outcome]}
                        </Badge>
                        {shot.outcome === "hit" && shot.cup_position && (
                          <span className="text-xs text-muted-foreground">
                            Cup {shot.cup_position}
                          </span>
                        )}
                        {shot.elbow_violation && (
                          <Badge variant="destructive" className="text-xs">
                            Elbow
                          </Badge>
                        )}
                      </>
                    )}
                  </div>
                  {!isCompleted && (
                    <Button
                      variant="ghost"
                      size="icon-xs"
                      className="text-muted-foreground hover:text-destructive"
                      onClick={() => handleDeleteShot(shot.id)}
                    >
                      ✕
                    </Button>
                  )}
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* End Game Dialog */}
      <Dialog open={endGameOpen} onOpenChange={setEndGameOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>End Game</DialogTitle>
            <DialogDescription>Select the winning team.</DialogDescription>
          </DialogHeader>
          <div className="flex flex-col gap-3 pt-2">
            <Button
              className="w-full"
              onClick={() => handleEndGame(team1.id)}
            >
              {team1?.name ?? "?"} Wins
            </Button>
            <Button
              className="w-full"
              variant="outline"
              onClick={() => handleEndGame(team2.id)}
            >
              {team2?.name ?? "?"} Wins
            </Button>
          </div>
        </DialogContent>
      </Dialog>
    </div>
  );
}
