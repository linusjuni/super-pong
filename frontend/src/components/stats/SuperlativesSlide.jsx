export default function SuperlativesSlide({ data }) {
  const { player_leaderboard, punishment_counts } = data;

  const topBy = (fn) => {
    let best = null;
    for (const p of player_leaderboard) {
      const val = fn(p);
      if (val > 0 && (best === null || val > fn(best))) best = p;
    }
    return best;
  };

  const goldenWrist = topBy((p) => p.hits);
  const sniper = topBy((p) => p.hit_percentage);
  const bounceKing = topBy((p) => p.bounce_hits);
  const rimLord = topBy((p) => p.rims);
  const airballArtist = topBy((p) => p.misses);
  const elbowCriminal = topBy((p) => p.elbow_violations);
  const mostPunished =
    punishment_counts.length > 0 ? punishment_counts[0] : null;

  const awards = [
    sniper && {
      title: "Sniper",
      name: sniper.player_name,
      value: `${sniper.hit_percentage}% hit rate`,
    },
    bounceKing && {
      title: "Bounce King",
      name: bounceKing.player_name,
      value: `${bounceKing.bounce_hits} bounce ${bounceKing.bounce_hits === 1 ? "hit" : "hits"}`,
    },
    rimLord && {
      title: "Rim Lord",
      name: rimLord.player_name,
      value: `${rimLord.rims} ${rimLord.rims === 1 ? "rim" : "rims"}`,
    },
    airballArtist && {
      title: "Airball Artist",
      name: airballArtist.player_name,
      value: `${airballArtist.misses} ${airballArtist.misses === 1 ? "airball" : "airballs"}`,
    },
    elbowCriminal && {
      title: "Elbow Criminal",
      name: elbowCriminal.player_name,
      value: `${elbowCriminal.elbow_violations} ${elbowCriminal.elbow_violations === 1 ? "violation" : "violations"}`,
    },
    mostPunished && {
      title: "Most Punished",
      name: mostPunished.player_name,
      value: `${mostPunished.count} ${mostPunished.count === 1 ? "bong" : "bongs"}`,
    },
  ].filter(Boolean);

  return (
    <div className="w-full max-w-5xl">
      <div className="text-center">
        <p className="text-sm uppercase tracking-widest text-muted-foreground">
          Superlatives
        </p>
      </div>

      {/* Golden Wrist — hero card */}
      {goldenWrist && (
        <div className="mt-6 rounded-xl border-2 border-primary p-8 text-center">
          <p className="text-sm uppercase tracking-widest text-muted-foreground">
            Golden Wrist Contender
          </p>
          <p className="mt-3 text-5xl font-bold">{goldenWrist.player_name}</p>
          <p className="mt-2 text-2xl text-muted-foreground">
            {goldenWrist.hits} {goldenWrist.hits === 1 ? "cup" : "cups"}
          </p>
        </div>
      )}

      {/* Other awards */}
      {awards.length > 0 && (
        <div className="mt-8 grid grid-cols-3 gap-4">
          {awards.map((award) => (
            <div
              key={award.title}
              className="rounded-lg border border-border p-5 text-center"
            >
              <p className="text-xs uppercase tracking-widest text-muted-foreground">
                {award.title}
              </p>
              <p className="mt-2 text-xl font-bold">{award.name}</p>
              <p className="mt-1 text-sm text-muted-foreground">
                {award.value}
              </p>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
