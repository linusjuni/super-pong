export default function TournamentStandingsSlide({ data }) {
  const { team_standings, completed_games, total_games, tournament_name } =
    data;

  const groupA = team_standings.filter((t) => t.group === "A");
  const groupB = team_standings.filter((t) => t.group === "B");

  return (
    <div className="w-full max-w-6xl space-y-10">
      <div className="text-center">
        <h1 className="text-5xl font-bold tracking-tight">
          {tournament_name}
        </h1>
        <div className="mx-auto mt-4 max-w-md">
          <div className="mb-1 flex justify-between text-sm text-muted-foreground">
            <span>Group Stage</span>
            <span>
              {completed_games}/{total_games} games
            </span>
          </div>
          <div className="h-3 w-full overflow-hidden rounded-full bg-muted">
            <div
              className="h-full rounded-full bg-primary transition-all duration-500"
              style={{
                width: total_games > 0
                  ? `${(completed_games / total_games) * 100}%`
                  : "0%",
              }}
            />
          </div>
        </div>
      </div>

      <div className="grid grid-cols-2 gap-12">
        <StandingsTable title="Group A" standings={groupA} />
        <StandingsTable title="Group B" standings={groupB} />
      </div>
    </div>
  );
}

function StandingsTable({ title, standings }) {
  return (
    <div>
      <h2 className="mb-4 text-3xl font-semibold">{title}</h2>
      <table className="w-full text-xl">
        <thead>
          <tr className="border-b border-border text-muted-foreground">
            <th className="pb-3 text-left font-medium">Team</th>
            <th className="pb-3 text-center font-medium">W</th>
            <th className="pb-3 text-center font-medium">L</th>
            <th className="pb-3 text-center font-medium">GP</th>
          </tr>
        </thead>
        <tbody>
          {standings.map((team, i) => (
            <tr
              key={team.team_id}
              className={`border-b border-border/50 ${
                i === 0 && team.wins > 0 ? "text-primary" : ""
              }`}
            >
              <td className="py-4 font-medium">{team.team_name}</td>
              <td className="py-4 text-center">{team.wins}</td>
              <td className="py-4 text-center">{team.losses}</td>
              <td className="py-4 text-center">{team.games_played}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
