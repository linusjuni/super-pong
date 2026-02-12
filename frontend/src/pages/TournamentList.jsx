import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { tournamentApi } from "@/services/api";
import { Button } from "@/components/ui/button";
import { Card, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";

export default function TournamentList() {
  const [tournaments, setTournaments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    tournamentApi
      .list()
      .then(setTournaments)
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false));
  }, []);

  return (
    <div className="mx-auto max-w-4xl p-6">
      <div className="mb-8 flex items-center justify-between">
        <h1 className="text-3xl font-bold">Super Pong</h1>
        <Button asChild>
          <Link to="/tournaments/new">New Tournament</Link>
        </Button>
      </div>

      {loading && <p className="text-muted-foreground">Loading...</p>}
      {error && <p className="text-destructive">Error: {error}</p>}

      {!loading && !error && tournaments.length === 0 && (
        <div className="py-12 text-center">
          <p className="text-muted-foreground">
            No tournaments yet. Create your first one!
          </p>
        </div>
      )}

      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {tournaments.map((t) => (
          <Link key={t.id} to={`/tournaments/${t.id}/games`}>
            <Card className="transition-colors hover:bg-accent">
              <CardHeader>
                <CardTitle>{t.name}</CardTitle>
                <CardDescription>
                  {new Date(t.created_at).toLocaleDateString()}
                </CardDescription>
              </CardHeader>
            </Card>
          </Link>
        ))}
      </div>
    </div>
  );
}
