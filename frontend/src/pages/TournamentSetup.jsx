import { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import { tournamentApi, teamApi, playerApi, gameApi } from "@/services/api";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import PlayerCombobox from "@/components/PlayerCombobox";

const emptyTeam = () => ({ name: "", player1: null, player2: null, group: "A" });

export default function TournamentSetup() {
  const navigate = useNavigate();
  const [tournamentName, setTournamentName] = useState("");
  const [teams, setTeams] = useState([emptyTeam(), emptyTeam()]);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState(null);

  const updateTeam = (index, field, value) => {
    setTeams((prev) => prev.map((t, i) => (i === index ? { ...t, [field]: value } : t)));
  };

  const removeTeam = (index) => {
    setTeams((prev) => prev.filter((_, i) => i !== index));
  };

  const validate = () => {
    if (!tournamentName.trim()) return "Tournament name is required.";
    if (teams.length < 2) return "At least 2 teams required.";
    for (let i = 0; i < teams.length; i++) {
      const t = teams[i];
      if (!t.name.trim()) return `Team ${i + 1} needs a name.`;
      if (!t.player1) return `Team ${i + 1} needs Player 1.`;
      if (!t.player2) return `Team ${i + 1} needs Player 2.`;
    }
    return null;
  };

  const handleSubmit = async () => {
    const validationError = validate();
    if (validationError) {
      setError(validationError);
      return;
    }

    setSubmitting(true);
    setError(null);

    try {
      // 1. Create tournament
      const tournament = await tournamentApi.create({ name: tournamentName.trim() });

      // 2. Collect unique new players (no id) and create them
      const newPlayerNames = new Set();
      for (const t of teams) {
        if (t.player1.id === null) newPlayerNames.add(t.player1.name);
        if (t.player2.id === null) newPlayerNames.add(t.player2.name);
      }

      const createdPlayers = {};
      for (const name of newPlayerNames) {
        const p = await playerApi.create({ name });
        createdPlayers[name] = p.id;
      }

      // Helper to resolve player id
      const resolvePlayerId = (player) =>
        player.id !== null ? player.id : createdPlayers[player.name];

      // 3. Create teams
      const createdTeams = [];
      for (const t of teams) {
        const created = await teamApi.create(tournament.id, {
          name: t.name.trim(),
          player1_id: resolvePlayerId(t.player1),
          player2_id: resolvePlayerId(t.player2),
          group: t.group,
        });
        createdTeams.push({ ...created, group: t.group });
      }

      // 4. Auto-generate round-robin games within each group
      const groups = {};
      for (const t of createdTeams) {
        const g = t.group || "A";
        if (!groups[g]) groups[g] = [];
        groups[g].push(t);
      }

      for (const groupTeams of Object.values(groups)) {
        for (let i = 0; i < groupTeams.length; i++) {
          for (let j = i + 1; j < groupTeams.length; j++) {
            await gameApi.create(tournament.id, {
              team1_id: groupTeams[i].id,
              team2_id: groupTeams[j].id,
              starting_cups_per_team: 6,
            });
          }
        }
      }

      navigate(`/tournaments/${tournament.id}/games`);
    } catch (e) {
      setError(e.response?.data?.detail || e.message);
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="mx-auto max-w-4xl p-6">
      <div className="mb-8 flex items-center gap-4">
        <Button variant="ghost" asChild>
          <Link to="/">Back</Link>
        </Button>
        <h1 className="text-3xl font-bold">New Tournament</h1>
      </div>

      <div className="mb-6">
        <Label htmlFor="tournament-name">Tournament Name</Label>
        <Input
          id="tournament-name"
          value={tournamentName}
          onChange={(e) => setTournamentName(e.target.value)}
          placeholder="e.g. Friday Night Pong"
          className="mt-1"
        />
      </div>

      <div className="mb-4">
        <h2 className="text-xl font-semibold">Teams</h2>
      </div>

      <div className="space-y-4">
        {teams.map((team, i) => (
          <div
            key={i}
            className="grid grid-cols-[1fr_1fr_1fr_80px_40px] items-end gap-3 rounded-lg border p-4"
          >
            <div>
              <Label>Team Name</Label>
              <Input
                value={team.name}
                onChange={(e) => updateTeam(i, "name", e.target.value)}
                placeholder={`Team ${i + 1}`}
                className="mt-1"
              />
            </div>
            <div>
              <Label>Player 1</Label>
              <div className="mt-1">
                <PlayerCombobox
                  value={team.player1}
                  onSelect={(p) => updateTeam(i, "player1", p)}
                  placeholder="Player 1..."
                />
              </div>
            </div>
            <div>
              <Label>Player 2</Label>
              <div className="mt-1">
                <PlayerCombobox
                  value={team.player2}
                  onSelect={(p) => updateTeam(i, "player2", p)}
                  placeholder="Player 2..."
                />
              </div>
            </div>
            <div>
              <Label>Group</Label>
              <Select
                value={team.group}
                onValueChange={(v) => updateTeam(i, "group", v)}
              >
                <SelectTrigger className="mt-1">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="A">A</SelectItem>
                  <SelectItem value="B">B</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <Button
              variant="ghost"
              size="icon"
              onClick={() => removeTeam(i)}
              disabled={teams.length <= 2}
              className="text-destructive"
            >
              X
            </Button>
          </div>
        ))}
      </div>

      <div className="mt-4 flex gap-4">
        <Button variant="outline" onClick={() => setTeams((prev) => [...prev, emptyTeam()])}>
          Add Team
        </Button>
      </div>

      {error && <p className="mt-4 text-destructive">{error}</p>}

      <div className="mt-8">
        <Button onClick={handleSubmit} disabled={submitting} size="lg">
          {submitting ? "Creating..." : "Create Tournament"}
        </Button>
      </div>
    </div>
  );
}
