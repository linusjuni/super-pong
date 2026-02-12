import { useEffect, useState } from "react";
import { useParams, Link } from "react-router-dom";
import { gameApi, tournamentApi } from "@/services/api";
import { Button } from "@/components/ui/button";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";

const statusLabel = {
  not_started: "Not Started",
  in_progress: "In Progress",
  completed: "Completed",
};

export default function GamePlay() {
  const { tournamentId, gameId } = useParams();
  const [game, setGame] = useState(null);
  const [teams, setTeams] = useState({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [g, teamsList] = await Promise.all([
          gameApi.get(gameId),
          tournamentApi.getTeams(tournamentId),
        ]);
        setGame(g);
        const map = {};
        for (const t of teamsList) map[t.id] = t;
        setTeams(map);
      } catch (e) {
        setError(e.message);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, [tournamentId, gameId]);

  if (loading) return <div className="p-6 text-muted-foreground">Loading...</div>;
  if (error) return <div className="p-6 text-destructive">Error: {error}</div>;

  const team1 = teams[game.team1_id];
  const team2 = teams[game.team2_id];

  return (
    <div className="mx-auto max-w-4xl p-6">
      <div className="mb-8 flex items-center gap-4">
        <Button variant="ghost" asChild>
          <Link to={`/tournaments/${tournamentId}/games`}>Back</Link>
        </Button>
        <h1 className="text-3xl font-bold">Game</h1>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>
            {team1?.name || "?"} vs {team2?.name || "?"}
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-3">
          <div className="flex items-center gap-2">
            <span className="text-muted-foreground">Status:</span>
            <Badge>{statusLabel[game.status]}</Badge>
          </div>
          <div>
            <span className="text-muted-foreground">Starting cups per team:</span>{" "}
            {game.starting_cups_per_team}
          </div>
          {game.winner_id && (
            <div>
              <span className="text-muted-foreground">Winner:</span>{" "}
              {teams[game.winner_id]?.name || "?"}
            </div>
          )}
          <div className="mt-6 rounded-lg border border-dashed p-8 text-center">
            <p className="text-lg text-muted-foreground">GamePlay coming soon</p>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
