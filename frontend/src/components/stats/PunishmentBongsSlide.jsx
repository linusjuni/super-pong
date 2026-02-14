export default function PunishmentBongsSlide({ data }) {
  const { total_punishments, punishment_counts, recent_punishments } = data;

  const total = total_punishments;

  return (
    <div className="w-full max-w-5xl">
      <div className="mb-8 text-center">
        <p className="text-sm uppercase tracking-widest text-muted-foreground">
          Hall of Shame
        </p>
        <p className="mt-2 text-6xl font-bold tracking-tight">{total}</p>
        <p className="mt-1 text-xl text-muted-foreground">
          punishment {total === 1 ? "bong" : "bongs"}
        </p>
      </div>

      {total > 0 && (
        <div className="grid grid-cols-2 gap-12">
          {/* Left: Ranked list */}
          <div>
            <h3 className="mb-4 text-sm uppercase tracking-widest text-muted-foreground">
              Leaderboard
            </h3>
            <div className="space-y-3">
              {punishment_counts.map((p, i) => (
                <div key={p.player_id} className="flex items-center gap-3">
                  <span className="w-6 text-right text-muted-foreground">
                    {i + 1}
                  </span>
                  <div className="flex-1">
                    <div className="flex items-center justify-between">
                      <span className="text-lg font-medium">
                        {p.player_name}
                      </span>
                      <span className="text-lg font-bold">{p.count}</span>
                    </div>
                    <div className="mt-1 h-2 overflow-hidden rounded-full bg-muted">
                      <div
                        className="h-full rounded-full bg-destructive transition-all duration-500"
                        style={{
                          width: `${(p.count / punishment_counts[0].count) * 100}%`,
                        }}
                      />
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Right: Recent log */}
          <div>
            <h3 className="mb-4 text-sm uppercase tracking-widest text-muted-foreground">
              Recent
            </h3>
            <div className="space-y-4">
              {recent_punishments.map((pb, i) => (
                <div key={i} className="border-b border-border/50 pb-3">
                  <div className="flex items-center justify-between">
                    <span className="font-medium">{pb.player_name}</span>
                    <span className="text-sm text-muted-foreground">
                      {new Date(pb.timestamp).toLocaleTimeString([], {
                        hour: "2-digit",
                        minute: "2-digit",
                      })}
                    </span>
                  </div>
                  {pb.note && (
                    <p className="mt-1 text-sm text-muted-foreground italic">
                      &ldquo;{pb.note}&rdquo;
                    </p>
                  )}
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
