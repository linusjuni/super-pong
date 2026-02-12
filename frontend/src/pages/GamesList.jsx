import { useEffect, useState } from "react";
import { useParams, Link } from "react-router-dom";
import { tournamentApi, gameApi } from "@/services/api";
import { Button } from "@/components/ui/button";
import { Card, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import { Label } from "@/components/ui/label";
import { Input } from "@/components/ui/input";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";

const statusVariant = {
  not_started: "secondary",
  in_progress: "default",
  completed: "outline",
};

const statusLabel = {
  not_started: "Not Started",
  in_progress: "In Progress",
  completed: "Completed",
};

export default function GamesList() {
  const { tournamentId } = useParams();
  const [tournament, setTournament] = useState(null);
  const [teams, setTeams] = useState([]);
  const [games, setGames] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Delete game
  const [deletingId, setDeletingId] = useState(null);

  const handleDeleteGame = async (e, gameId) => {
    e.preventDefault();
    e.stopPropagation();
    if (!window.confirm("Delete this game? This cannot be undone.")) return;
    setDeletingId(gameId);
    try {
      await gameApi.delete(gameId);
      setGames((prev) => prev.filter((g) => g.id !== gameId));
    } catch (e) {
      setError(e.response?.data?.detail || e.message);
    } finally {
      setDeletingId(null);
    }
  };

  // Create game dialog
  const [dialogOpen, setDialogOpen] = useState(false);
  const [newTeam1, setNewTeam1] = useState("");
  const [newTeam2, setNewTeam2] = useState("");
  const [newCups, setNewCups] = useState(6);
  const [creating, setCreating] = useState(false);

  const fetchData = async () => {
    try {
      const [t, tm, g] = await Promise.all([
        tournamentApi.get(tournamentId),
        tournamentApi.getTeams(tournamentId),
        tournamentApi.getGames(tournamentId),
      ]);
      setTournament(t);
      setTeams(tm);
      setGames(g);
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, [tournamentId]);

  const teamMap = {};
  for (const t of teams) {
    teamMap[t.id] = t;
  }

  // Group games by inferred group
  const groupedGames = {};
  for (const g of games) {
    const t1 = teamMap[g.team1_id];
    const t2 = teamMap[g.team2_id];
    const group = t1?.group && t2?.group && t1.group === t2.group ? `Group ${t1.group}` : "Other";
    if (!groupedGames[group]) groupedGames[group] = [];
    groupedGames[group].push(g);
  }

  // Sort group keys so Group A, Group B come first
  const sortedGroups = Object.keys(groupedGames).sort((a, b) => {
    if (a === "Other") return 1;
    if (b === "Other") return -1;
    return a.localeCompare(b);
  });

  const handleCreateGame = async () => {
    if (!newTeam1 || !newTeam2 || newTeam1 === newTeam2) return;
    setCreating(true);
    try {
      await gameApi.create(tournamentId, {
        team1_id: parseInt(newTeam1),
        team2_id: parseInt(newTeam2),
        starting_cups_per_team: newCups,
      });
      setDialogOpen(false);
      setNewTeam1("");
      setNewTeam2("");
      setNewCups(6);
      setLoading(true);
      fetchData();
    } catch (e) {
      setError(e.response?.data?.detail || e.message);
    } finally {
      setCreating(false);
    }
  };

  if (loading) return <div className="p-6 text-muted-foreground">Loading...</div>;
  if (error) return <div className="p-6 text-destructive">Error: {error}</div>;

  return (
    <div className="mx-auto max-w-4xl p-6">
      <div className="mb-8 flex items-center justify-between">
        <div className="flex items-center gap-4">
          <Button variant="ghost" asChild>
            <Link to="/">Back</Link>
          </Button>
          <h1 className="text-3xl font-bold">{tournament?.name}</h1>
        </div>
        <Dialog open={dialogOpen} onOpenChange={setDialogOpen}>
          <DialogTrigger asChild>
            <Button>Add Game</Button>
          </DialogTrigger>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>Create Game</DialogTitle>
            </DialogHeader>
            <div className="space-y-4">
              <div>
                <Label>Team 1</Label>
                <Select value={newTeam1} onValueChange={setNewTeam1}>
                  <SelectTrigger className="mt-1">
                    <SelectValue placeholder="Select team..." />
                  </SelectTrigger>
                  <SelectContent>
                    {teams.map((t) => (
                      <SelectItem key={t.id} value={String(t.id)}>
                        {t.name}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
              <div>
                <Label>Team 2</Label>
                <Select value={newTeam2} onValueChange={setNewTeam2}>
                  <SelectTrigger className="mt-1">
                    <SelectValue placeholder="Select team..." />
                  </SelectTrigger>
                  <SelectContent>
                    {teams.map((t) => (
                      <SelectItem key={t.id} value={String(t.id)}>
                        {t.name}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
              <div>
                <Label>Starting Cups</Label>
                <Input
                  type="number"
                  value={newCups}
                  onChange={(e) => setNewCups(parseInt(e.target.value) || 6)}
                  className="mt-1"
                />
              </div>
              <Button onClick={handleCreateGame} disabled={creating || !newTeam1 || !newTeam2 || newTeam1 === newTeam2}>
                {creating ? "Creating..." : "Create Game"}
              </Button>
            </div>
          </DialogContent>
        </Dialog>
      </div>

      {games.length === 0 && (
        <p className="text-muted-foreground">No games yet. Add one to get started!</p>
      )}

      {sortedGroups.map((group) => (
        <div key={group} className="mb-8">
          <h2 className="mb-4 text-xl font-semibold">{group}</h2>
          <div className="grid gap-4 sm:grid-cols-2">
            {groupedGames[group].map((g) => {
              const t1 = teamMap[g.team1_id];
              const t2 = teamMap[g.team2_id];
              const winner = g.winner_id ? teamMap[g.winner_id] : null;
              return (
                <Link key={g.id} to={`/tournaments/${tournamentId}/games/${g.id}`}>
                  <Card className="transition-colors hover:bg-accent">
                    <CardHeader>
                      <div className="flex items-center justify-between">
                        <CardTitle className="text-base">
                          {t1?.name || "?"} vs {t2?.name || "?"}
                        </CardTitle>
                        <div className="flex items-center gap-2">
                          <Badge variant={statusVariant[g.status]}>
                            {statusLabel[g.status]}
                          </Badge>
                          <Button
                            variant="ghost"
                            size="sm"
                            className="h-7 w-7 p-0 text-muted-foreground hover:text-destructive"
                            disabled={deletingId === g.id}
                            onClick={(e) => handleDeleteGame(e, g.id)}
                          >
                            {deletingId === g.id ? "…" : "✕"}
                          </Button>
                        </div>
                      </div>
                      {winner && (
                        <CardDescription>Winner: {winner.name}</CardDescription>
                      )}
                    </CardHeader>
                  </Card>
                </Link>
              );
            })}
          </div>
        </div>
      ))}
    </div>
  );
}
