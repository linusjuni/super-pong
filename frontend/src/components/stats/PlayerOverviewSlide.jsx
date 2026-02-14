export default function PlayerOverviewSlide({ data }) {
  const { player_leaderboard } = data;

  const mid = Math.ceil(player_leaderboard.length / 2);
  const left = player_leaderboard.slice(0, mid);
  const right = player_leaderboard.slice(mid);

  return (
    <div className="w-full max-w-7xl">
      <h2 className="mb-6 text-center text-4xl font-bold tracking-tight">
        Player Overview
      </h2>
      <div className="grid grid-cols-2 gap-10">
        <PlayerTable players={left} startRank={1} />
        <PlayerTable players={right} startRank={mid + 1} />
      </div>
    </div>
  );
}

function PlayerTable({ players, startRank }) {
  return (
    <table className="w-full text-base">
      <thead>
        <tr className="text-muted-foreground">
          <th />
          <th />
          <th />
          <th />
          <th />
          <th />
          <th />
          <th
            colSpan={2}
            className="border-b border-border pb-1 text-center text-xs font-medium"
          >
            Bounces
          </th>
          <th />
        </tr>
        <tr className="border-b border-border text-muted-foreground">
          <th className="pb-2 text-left text-sm font-medium">#</th>
          <th className="pb-2 text-left text-sm font-medium">Player</th>
          <th className="pb-2 text-center text-sm font-medium">Cups</th>
          <th className="pb-2 text-center text-sm font-medium">Air</th>
          <th className="pb-2 text-center text-sm font-medium">Rim</th>
          <th className="pb-2 text-center text-sm font-medium">Tot</th>
          <th className="pb-2 text-center text-sm font-medium">Hit%</th>
          <th className="pb-2 text-center text-sm font-medium">Sh</th>
          <th className="pb-2 text-center text-sm font-medium">Tot</th>
          <th className="pb-2 text-center text-sm font-medium">Elb</th>
        </tr>
      </thead>
      <tbody>
        {players.map((p, i) => (
          <tr key={p.player_id} className="border-b border-border/50">
            <td className="py-2 text-muted-foreground">{startRank + i}</td>
            <td className="py-2 font-medium">{p.player_name}</td>
            <td className="py-2 text-center">{p.hits}</td>
            <td className="py-2 text-center">{p.misses}</td>
            <td className="py-2 text-center">{p.rims}</td>
            <td className="py-2 text-center text-muted-foreground">
              {p.total_shots}
            </td>
            <td className="py-2 text-center">{p.hit_percentage}%</td>
            <td className="py-2 text-center">
              {p.bounce_shots > 0 ? p.bounce_shots : ""}
            </td>
            <td className="py-2 text-center">
              {p.bounce_total > 0 ? p.bounce_total : ""}
            </td>
            <td className="py-2 text-center">
              {p.elbow_violations > 0 ? p.elbow_violations : ""}
            </td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}
