const BEERS_PER_GAME = 4;

/*
 * Single-path beer glass with perfectly aligned liquid fill.
 * The glass shape is ONE path reused for both outline and clip,
 * so the liquid can never misalign with the glass walls.
 *
 * Geometry (viewBox 0 0 100 160):
 *   Rim:    x 15–85   (y 10)
 *   Base:   x 25–75   (y 145, rounded bottom)
 *   Handle: right side arc
 */
const GLASS = "M15,10 L85,10 L78,130 Q78,148 65,148 L35,148 Q22,148 22,130 Z";

// Liquid top Y   = 10  (full)
// Liquid bot Y   = 148 (empty)
// Fillable range = 138px
const FILL_TOP = 10;
const FILL_H = 138;

function BeerGlass({ pct }) {
  // Y coordinate where the liquid surface sits
  const surfaceY = FILL_TOP + FILL_H * (1 - pct / 100);

  return (
    <svg viewBox="0 0 110 160" className="h-40 w-auto drop-shadow-lg">
      <defs>
        {/* Clip liquid to the exact glass path */}
        <clipPath id="beer-clip">
          <path d={GLASS} />
        </clipPath>

        <linearGradient id="beer-grad" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%" stopColor="#FBBF24" />
          <stop offset="100%" stopColor="#D97706" />
        </linearGradient>

      </defs>

      {/* ── Liquid (clipped to glass) ── */}
      <g clipPath="url(#beer-clip)">
        {/* Solid fill */}
        <rect
          x="10" width="80"
          y={surfaceY}
          height={FILL_H - (surfaceY - FILL_TOP)}
          fill="url(#beer-grad)"
          opacity="0.9"
          className="transition-all duration-700"
        />

        {/* Foam — two staggered rows at the surface */}
        {pct > 0 && (
          <>
            {[20, 35, 50, 65, 80].map((cx) => (
              <ellipse
                key={cx}
                cx={cx} cy={surfaceY}
                rx="10" ry="5"
                fill="#FEF3C7"
                className="transition-all duration-700"
              />
            ))}
            {[27, 42, 57, 72].map((cx) => (
              <ellipse
                key={cx}
                cx={cx} cy={surfaceY - 3}
                rx="8" ry="4"
                fill="#FDE68A"
                className="transition-all duration-700"
              />
            ))}
          </>
        )}
      </g>

      {/* ── Glass outline (same path, drawn on top) ── */}
      <path
        d={GLASS}
        fill="none"
        stroke="currentColor"
        strokeWidth="2.5"
        strokeLinejoin="round"
        className="text-muted-foreground"
      />

      {/* ── Handle ── */}
      <path
        d="M85,35 Q105,35 105,65 Q105,95 85,95"
        fill="none"
        stroke="currentColor"
        strokeWidth="2.5"
        strokeLinecap="round"
        className="text-muted-foreground"
      />
    </svg>
  );
}

export default function ByTheNumbersSlide({ data }) {
  const { total_games, completed_games, player_leaderboard } = data;

  // Aggregate shot stats across all players
  const totals = { shots: 0, hits: 0, misses: 0, rims: 0, bounces: 0, elbows: 0 };
  for (const p of player_leaderboard) {
    totals.shots += p.total_shots;
    totals.hits += p.hits;
    totals.misses += p.misses;
    totals.rims += p.rims;
    totals.bounces += p.bounce_hits;
    totals.elbows += p.elbow_violations;
  }

  // Stacked bar segments
  const segments = [
    { label: "Hits", count: totals.hits, color: "bg-green-500" },
    { label: "Rims", count: totals.rims, color: "bg-yellow-500" },
    { label: "Airballs", count: totals.misses, color: "bg-red-500" },
  ];

  // Beer stats
  const totalBeers = total_games * BEERS_PER_GAME;
  const beersDrunk = completed_games * BEERS_PER_GAME;
  const beerPct = totalBeers > 0 ? (beersDrunk / totalBeers) * 100 : 0;

  return (
    <div className="w-full max-w-4xl">
      <div className="text-center">
        <p className="text-sm uppercase tracking-widest text-muted-foreground">
          By The Numbers
        </p>
        <p className="mt-2 text-5xl font-bold">{totals.shots}</p>
        <p className="mt-1 text-xl text-muted-foreground">
          total {totals.shots === 1 ? "shot" : "shots"} taken
        </p>
      </div>

      {/* Stacked shot bar */}
      {totals.shots > 0 && (
        <div className="mt-8">
          <div className="flex h-12 w-full overflow-hidden rounded-full">
            {segments.map((seg) => {
              const pct = (seg.count / totals.shots) * 100;
              if (pct === 0) return null;
              return (
                <div
                  key={seg.label}
                  className={`${seg.color} flex items-center justify-center transition-all duration-500`}
                  style={{ width: `${pct}%` }}
                >
                  {pct >= 8 && (
                    <span className="text-sm font-semibold text-black">
                      {Math.round(pct)}%
                    </span>
                  )}
                </div>
              );
            })}
          </div>
          <div className="mt-3 flex justify-center gap-6">
            {segments.map((seg) => (
              <div key={seg.label} className="flex items-center gap-2">
                <div className={`h-3 w-3 rounded-full ${seg.color}`} />
                <span className="text-sm text-muted-foreground">
                  {seg.label} ({seg.count})
                </span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Extra stats row */}
      <div className="mt-8 flex justify-center gap-8">
        {totals.bounces > 0 && (
          <div className="rounded-lg border border-border px-6 py-4 text-center">
            <p className="text-3xl font-bold">{totals.bounces}</p>
            <p className="mt-1 text-sm text-muted-foreground">
              {totals.bounces === 1 ? "bounce" : "bounces"}
            </p>
          </div>
        )}
        {totals.elbows > 0 && (
          <div className="rounded-lg border border-border px-6 py-4 text-center">
            <p className="text-3xl font-bold">{totals.elbows}</p>
            <p className="mt-1 text-sm text-muted-foreground">
              elbow {totals.elbows === 1 ? "violation" : "violations"}
            </p>
          </div>
        )}
      </div>

      {/* Beer glass fill */}
      <div className="mt-8 flex flex-col items-center">
        <BeerGlass pct={beerPct} />
        <p className="mt-3 text-lg text-muted-foreground">
          <span className="font-bold text-foreground">{beersDrunk}</span>
          {" / "}
          {totalBeers} beers
        </p>
      </div>
    </div>
  );
}
