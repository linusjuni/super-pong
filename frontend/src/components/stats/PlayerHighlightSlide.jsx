const CUP_ROWS = [[1], [2, 3], [4, 5, 6], [7, 8, 9, 10]];

export default function PlayerHighlightSlide({ data, featuredPlayerId }) {
  const { player_leaderboard, cup_heatmap, punishment_counts, hot_hand, team_standings } = data;

  if (player_leaderboard.length === 0) return null;

  const idx = player_leaderboard.findIndex((p) => p.player_id === featuredPlayerId);
  const player = player_leaderboard[idx === -1 ? 0 : idx];

  // Build heatmap for this player: cup_position -> hits
  const heatmap = {};
  for (const entry of cup_heatmap) {
    if (entry.player_id === player.player_id) {
      heatmap[entry.cup_position] = entry.hits;
    }
  }

  const maxHits = Math.max(1, ...Object.values(heatmap));

  const punishments =
    punishment_counts.find((p) => p.player_id === player.player_id)?.count ?? 0;

  const streaks = hot_hand?.find((h) => h.player_id === player.player_id);
  const hitStreak = streaks?.longest_hit_streak ?? 0;
  const missStreak = streaks?.longest_miss_streak ?? 0;

  // --- 2B1C overlap factor ---
  // Find teammate
  const team = team_standings?.find(
    (t) => t.player1_id === player.player_id || t.player2_id === player.player_id
  );
  const teammateId = team
    ? team.player1_id === player.player_id
      ? team.player2_id
      : team.player1_id
    : null;
  const teammate = teammateId
    ? player_leaderboard.find((p) => p.player_id === teammateId)
    : null;

  // Compute 2B1C bonus: p_B * sum_c( q_A(c) * q_B(c) )
  let twoBOneCBonus = 0;
  if (teammate && teammate.hits > 0 && player.hits > 0) {
    // Teammate hit rate
    const pB = teammate.hits / teammate.total_shots;

    // Cup distributions: q(c) = hits_on_c / total_hits
    const buildCupDist = (playerId, totalHits) => {
      const dist = {};
      for (const entry of cup_heatmap) {
        if (entry.player_id === playerId) {
          dist[entry.cup_position] = entry.hits / totalHits;
        }
      }
      return dist;
    };

    const qA = buildCupDist(player.player_id, player.hits);
    const qB = buildCupDist(teammateId, teammate.hits);

    // Dot product of cup distributions
    let overlap = 0;
    for (const cup in qA) {
      if (qB[cup]) overlap += qA[cup] * qB[cup];
    }

    twoBOneCBonus = pB * overlap;
  }

  // EV = base cups/attempt * (1 + 2B1C bonus)
  const normalEv = player.normal_total > 0
    ? (player.normal_hits / player.normal_total) * (1 + twoBOneCBonus)
    : null;
  const bounceEv = player.bounce_shots > 0
    ? (player.bounce_cups_removed / player.bounce_shots) * (1 + twoBOneCBonus)
    : null;
  const trickshotEv = player.trickshot_total > 0
    ? (player.trickshot_hits / player.trickshot_total) * (1 + twoBOneCBonus)
    : null;

  return (
    <div className="w-full max-w-5xl">
      <div className="mb-2 text-center">
        <p className="text-sm uppercase tracking-widest text-muted-foreground">
          Player Spotlight
        </p>
        <h2 className="text-5xl font-bold tracking-tight">
          {player.player_name}
        </h2>
        <p className="mt-1 text-lg text-muted-foreground">
          Rank #{idx + 1} of {player_leaderboard.length}
        </p>
      </div>

      <div className="grid grid-cols-2 gap-12 mt-8">
        {/* Left: Cup heatmap */}
        <div className="flex flex-col items-center justify-center">
          <h3 className="mb-6 text-xl font-semibold text-muted-foreground">
            Cup Heatmap
          </h3>
          <div className="flex flex-col items-center gap-3">
            {CUP_ROWS.map((row, ri) => (
              <div key={ri} className="flex gap-3">
                {row.map((cup) => {
                  const hits = heatmap[cup] || 0;
                  const intensity = hits > 0 ? hits / maxHits : 0;
                  return (
                    <div
                      key={cup}
                      className="flex h-16 w-16 items-center justify-center rounded-full border border-border text-sm font-medium"
                      style={{
                        backgroundColor:
                          hits > 0
                            ? `oklch(0.65 0.2 145 / ${0.2 + intensity * 0.8})`
                            : undefined,
                        color: intensity > 0.5 ? "white" : undefined,
                      }}
                    >
                      {hits > 0 ? hits : cup}
                    </div>
                  );
                })}
              </div>
            ))}
          </div>
          <p className="mt-4 text-sm text-muted-foreground">
            {(() => { const n = Object.values(heatmap).reduce((a, b) => a + b, 0); return `${n} ${n === 1 ? "cup" : "cups"} hit`; })()}
          </p>
        </div>

        {/* Right: Stats */}
        <div className="flex flex-col justify-center space-y-6">
          {/* Core stats */}
          <div className="grid grid-cols-3 gap-4">
            <StatBox label="Cups" value={player.hits} />
            <StatBox label="Airballs" value={player.misses} />
            <StatBox label="Rims" value={player.rims} />
            <StatBox label="Total" value={player.total_shots} />
            <StatBox label="Hit%" value={`${player.hit_percentage}%`} />
            <StatBox label="Elbows" value={player.elbow_violations} />
          </div>

          {/* Shot type breakdown */}
          <div>
            <h3 className="mb-3 text-sm uppercase tracking-widest text-muted-foreground">
              Shot Types
            </h3>
            <div className="space-y-2">
              <ShotTypeBar
                label="Normal"
                hits={player.normal_hits}
                total={player.normal_total}
                ev={normalEv}
              />
              <ShotTypeBar
                label="Bounce"
                hits={player.bounce_hits}
                total={player.bounce_shots}
                ev={bounceEv}
              />
              <ShotTypeBar
                label="Trickshot"
                hits={player.trickshot_hits}
                total={player.trickshot_total}
                ev={trickshotEv}
              />
            </div>
          </div>

          {/* Bounces & punishments */}
          <div className="flex gap-6">
            <div className="flex-1 rounded-lg border border-border p-3 text-center">
              <p className="text-2xl font-bold">{player.bounce_total}</p>
              <p className="text-xs text-muted-foreground">Total Bounces</p>
            </div>
            <div className="flex-1 rounded-lg border border-border p-3 text-center">
              <p className="text-2xl font-bold">{punishments}</p>
              <p className="text-xs text-muted-foreground">Punishment Bongs</p>
            </div>
          </div>

          {/* Hot Hand Tracker */}
          <div>
            <h3 className="mb-3 text-sm uppercase tracking-widest text-muted-foreground">
              Hot Hand Tracker
            </h3>
            <div className="flex gap-6">
              <div className="flex-1 rounded-lg border border-border p-3 text-center">
                <p className="text-2xl font-bold">
                  🔥 {hitStreak}
                </p>
                <p className="text-xs text-muted-foreground">
                  Longest Hit Streak
                </p>
              </div>
              <div className="flex-1 rounded-lg border border-border p-3 text-center">
                <p className="text-2xl font-bold">
                  🧊 {missStreak}
                </p>
                <p className="text-xs text-muted-foreground">
                  Longest Miss Streak
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

function StatBox({ label, value }) {
  return (
    <div className="rounded-lg border border-border p-3 text-center">
      <p className="text-2xl font-bold">{value}</p>
      <p className="text-xs text-muted-foreground">{label}</p>
    </div>
  );
}

function ShotTypeBar({ label, hits, total, ev }) {
  const pct = total > 0 ? Math.round((hits / total) * 100) : 0;
  return (
    <div className="flex items-center gap-3">
      <span className="w-20 text-sm text-muted-foreground">{label}</span>
      <div className="flex-1 h-5 overflow-hidden rounded-full bg-muted">
        <div
          className="h-full rounded-full bg-primary transition-all duration-500"
          style={{ width: total > 0 ? `${pct}%` : "0%" }}
        />
      </div>
      <span className="w-24 text-right text-sm">
        {hits}/{total} ({pct}%)
      </span>
      <span className="w-16 text-right text-sm font-semibold text-muted-foreground">
        {ev !== null ? `${ev.toFixed(2)} EV` : "—"}
      </span>
    </div>
  );
}
