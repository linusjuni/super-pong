from sqlalchemy import text
from sqlmodel import Session

from .models import (
    CupHeatmapEntry,
    DashboardStats,
    HotHandEntry,
    PlayerEntry,
    PlayerStats,
    PunishmentCount,
    RecentPunishment,
    TeamStanding,
    TournamentStats,
)


# ---------------------------------------------------------------------------
# Private helpers — each runs a single focused query
# ---------------------------------------------------------------------------


def _game_counts(session: Session, tid: int) -> tuple[int, int, int]:
    """Returns (total, completed, in_progress) game counts."""
    row = session.execute(
        text("""
            SELECT
                COUNT(*) AS total,
                SUM(CASE WHEN status = 'COMPLETED' THEN 1 ELSE 0 END) AS completed,
                SUM(CASE WHEN status = 'IN_PROGRESS' THEN 1 ELSE 0 END) AS in_progress
            FROM game
            WHERE tournament_id = :tid
        """),
        {"tid": tid},
    ).one()
    return (row.total or 0, row.completed or 0, row.in_progress or 0)


def _player_leaderboard(session: Session, tid: int) -> list[PlayerEntry]:
    rows = session.execute(
        text("""
            SELECT
                p.id   AS player_id,
                p.name AS player_name,
                COUNT(s.id)                                         AS total_shots,
                SUM(CASE WHEN s.outcome = 'HIT' THEN 1 ELSE 0 END) AS hits,
                SUM(CASE WHEN s.outcome = 'MISS' THEN 1 ELSE 0 END) AS misses,
                SUM(CASE WHEN s.outcome = 'RIM' THEN 1 ELSE 0 END) AS rims,
                SUM(CASE WHEN s.elbow_violation = 1 THEN 1 ELSE 0 END) AS elbow_violations,
                SUM(CASE WHEN s.shot_type = 'BOUNCE' THEN 1 ELSE 0 END) AS bounce_shots,
                COALESCE(SUM(CASE WHEN s.shot_type = 'BOUNCE' THEN s.bounces ELSE 0 END), 0) AS bounce_total,
                SUM(CASE WHEN s.shot_type = 'NORMAL' AND s.outcome = 'HIT' THEN 1 ELSE 0 END) AS normal_hits,
                SUM(CASE WHEN s.shot_type = 'NORMAL' THEN 1 ELSE 0 END) AS normal_total,
                SUM(CASE WHEN s.shot_type = 'BOUNCE' AND s.outcome = 'HIT' THEN 1 ELSE 0 END) AS bounce_hits,
                SUM(CASE WHEN s.shot_type = 'TRICKSHOT' AND s.outcome = 'HIT' THEN 1 ELSE 0 END) AS trickshot_hits,
                SUM(CASE WHEN s.shot_type = 'TRICKSHOT' THEN 1 ELSE 0 END) AS trickshot_total,
                COALESCE(SUM(CASE WHEN s.shot_type = 'BOUNCE' AND s.outcome = 'HIT' THEN s.bounces + 1 ELSE 0 END), 0) AS bounce_cups_removed
            FROM (
                SELECT player1_id AS player_id FROM team WHERE tournament_id = :tid
                UNION
                SELECT player2_id FROM team WHERE tournament_id = :tid
            ) tp
            JOIN player p ON tp.player_id = p.id
            LEFT JOIN shot s ON s.player_id = p.id
                AND s.shot_type != 'RERACK'
                AND s.game_id IN (SELECT id FROM game WHERE tournament_id = :tid)
            GROUP BY p.id
            ORDER BY hits DESC, total_shots ASC, p.name ASC
        """),
        {"tid": tid},
    ).all()
    return [
        PlayerEntry(
            player_id=r.player_id,
            player_name=r.player_name,
            total_shots=r.total_shots,
            hits=r.hits,
            misses=r.misses or 0,
            rims=r.rims or 0,
            hit_percentage=round(r.hits / r.total_shots * 100, 1)
            if r.total_shots > 0
            else 0.0,
            elbow_violations=r.elbow_violations or 0,
            bounce_shots=r.bounce_shots or 0,
            bounce_total=r.bounce_total or 0,
            normal_hits=r.normal_hits or 0,
            normal_total=r.normal_total or 0,
            bounce_hits=r.bounce_hits or 0,
            trickshot_hits=r.trickshot_hits or 0,
            trickshot_total=r.trickshot_total or 0,
            bounce_cups_removed=r.bounce_cups_removed or 0,
        )
        for r in rows
    ]


def _cup_heatmap(session: Session, tid: int) -> list[CupHeatmapEntry]:
    rows = session.execute(
        text("""
            SELECT
                s.player_id,
                s.cup_position,
                COUNT(*) AS hits
            FROM shot s
            JOIN game g ON s.game_id = g.id
            WHERE g.tournament_id = :tid
                AND s.outcome = 'HIT'
                AND s.cup_position IS NOT NULL
            GROUP BY s.player_id, s.cup_position
        """),
        {"tid": tid},
    ).all()
    return [
        CupHeatmapEntry(
            player_id=r.player_id,
            cup_position=r.cup_position,
            hits=r.hits,
        )
        for r in rows
    ]


def _total_punishments(session: Session, tid: int) -> int:
    row = session.execute(
        text("SELECT COUNT(*) AS total FROM punishmentbong WHERE tournament_id = :tid"),
        {"tid": tid},
    ).one()
    return row.total or 0


def _punishment_counts(session: Session, tid: int) -> list[PunishmentCount]:
    rows = session.execute(
        text("""
            SELECT pb.player_id, p.name AS player_name, COUNT(*) AS count
            FROM punishmentbong pb
            JOIN player p ON pb.player_id = p.id
            WHERE pb.tournament_id = :tid
            GROUP BY pb.player_id
            ORDER BY count DESC, p.name ASC
            LIMIT 10
        """),
        {"tid": tid},
    ).all()
    return [
        PunishmentCount(player_id=r.player_id, player_name=r.player_name, count=r.count)
        for r in rows
    ]


def _recent_punishments(session: Session, tid: int) -> list[RecentPunishment]:
    rows = session.execute(
        text("""
            SELECT p.name AS player_name, pb.note, pb.timestamp
            FROM punishmentbong pb
            JOIN player p ON pb.player_id = p.id
            WHERE pb.tournament_id = :tid
            ORDER BY pb.timestamp DESC
            LIMIT 6
        """),
        {"tid": tid},
    ).all()
    return [
        RecentPunishment(
            player_name=r.player_name,
            note=r.note,
            timestamp=r.timestamp,
        )
        for r in rows
    ]


def _team_standings(session: Session, tid: int) -> list[TeamStanding]:
    rows = session.execute(
        text("""
            SELECT
                t.id    AS team_id,
                t.name  AS team_name,
                t."group" AS "group",
                t.player1_id AS player1_id,
                t.player2_id AS player2_id,
                p1.name AS player1_name,
                p2.name AS player2_name,
                SUM(CASE WHEN g.winner_id = t.id THEN 1 ELSE 0 END) AS wins,
                SUM(CASE WHEN g.winner_id IS NOT NULL
                     AND g.winner_id != t.id THEN 1 ELSE 0 END) AS losses,
                COUNT(g.id) AS games_played
            FROM team t
            JOIN player p1 ON t.player1_id = p1.id
            JOIN player p2 ON t.player2_id = p2.id
            LEFT JOIN game g ON (g.team1_id = t.id OR g.team2_id = t.id)
                AND g.status = 'COMPLETED'
            WHERE t.tournament_id = :tid
            GROUP BY t.id
            ORDER BY wins DESC, losses ASC
        """),
        {"tid": tid},
    ).all()
    return [
        TeamStanding(
            team_id=r.team_id,
            team_name=r.team_name,
            player1_id=r.player1_id,
            player2_id=r.player2_id,
            player1_name=r.player1_name,
            player2_name=r.player2_name,
            group=r.group,
            wins=r.wins or 0,
            losses=r.losses or 0,
            games_played=r.games_played or 0,
        )
        for r in rows
    ]


def _hot_hand_streaks(session: Session, tid: int) -> list[HotHandEntry]:
    """Longest consecutive hit streak and miss streak per player.

    Uses the gaps-and-islands technique on shots ordered by timestamp.
    RIM outcomes count as misses.  RERACK shots are excluded.
    """
    rows = session.execute(
        text("""
            WITH ordered_shots AS (
                SELECT
                    s.player_id,
                    CASE WHEN s.outcome = 'HIT' THEN 1 ELSE 0 END AS is_hit,
                    ROW_NUMBER() OVER (
                        PARTITION BY s.player_id
                        ORDER BY s.timestamp, s.id
                    ) AS rn,
                    ROW_NUMBER() OVER (
                        PARTITION BY s.player_id,
                            CASE WHEN s.outcome = 'HIT' THEN 1 ELSE 0 END
                        ORDER BY s.timestamp, s.id
                    ) AS grp_rn
                FROM shot s
                JOIN game g ON s.game_id = g.id
                WHERE g.tournament_id = :tid
                    AND s.shot_type != 'RERACK'
            ),
            streaks AS (
                SELECT
                    player_id,
                    is_hit,
                    COUNT(*) AS streak_len
                FROM ordered_shots
                GROUP BY player_id, is_hit, rn - grp_rn
            )
            SELECT
                player_id,
                MAX(CASE WHEN is_hit = 1 THEN streak_len ELSE 0 END) AS longest_hit_streak,
                MAX(CASE WHEN is_hit = 0 THEN streak_len ELSE 0 END) AS longest_miss_streak
            FROM streaks
            GROUP BY player_id
        """),
        {"tid": tid},
    ).all()
    return [
        HotHandEntry(
            player_id=r.player_id,
            longest_hit_streak=r.longest_hit_streak,
            longest_miss_streak=r.longest_miss_streak,
        )
        for r in rows
    ]


# ---------------------------------------------------------------------------
# Public functions — compose helpers into response models
# ---------------------------------------------------------------------------


def get_player_stats(session: Session, player_id: int, player_name: str) -> PlayerStats:
    row = session.execute(
        text("""
            SELECT
                COUNT(*)                                             AS total_shots,
                SUM(CASE WHEN outcome = 'HIT' THEN 1 ELSE 0 END)   AS hits,
                SUM(CASE WHEN outcome = 'MISS' THEN 1 ELSE 0 END)  AS misses,
                SUM(CASE WHEN outcome = 'RIM' THEN 1 ELSE 0 END)   AS rims,
                SUM(CASE WHEN shot_type = 'NORMAL' AND outcome = 'HIT' THEN 1 ELSE 0 END)    AS normal_hits,
                SUM(CASE WHEN shot_type = 'NORMAL' THEN 1 ELSE 0 END)                        AS normal_total,
                SUM(CASE WHEN shot_type = 'BOUNCE' AND outcome = 'HIT' THEN 1 ELSE 0 END)    AS bounce_hits,
                SUM(CASE WHEN shot_type = 'BOUNCE' THEN 1 ELSE 0 END)                        AS bounce_total,
                SUM(CASE WHEN shot_type = 'TRICKSHOT' AND outcome = 'HIT' THEN 1 ELSE 0 END) AS trickshot_hits,
                SUM(CASE WHEN shot_type = 'TRICKSHOT' THEN 1 ELSE 0 END)                     AS trickshot_total,
                SUM(CASE WHEN elbow_violation = 1 THEN 1 ELSE 0 END) AS elbow_violations
            FROM shot
            WHERE player_id = :pid AND shot_type != 'RERACK'
        """),
        {"pid": player_id},
    ).one()

    total = row.total_shots or 0
    hits = row.hits or 0

    return PlayerStats(
        player_id=player_id,
        player_name=player_name,
        total_shots=total,
        hits=hits,
        misses=row.misses or 0,
        rims=row.rims or 0,
        hit_percentage=round(hits / total * 100, 1) if total > 0 else 0.0,
        normal_hits=row.normal_hits or 0,
        normal_total=row.normal_total or 0,
        bounce_hits=row.bounce_hits or 0,
        bounce_total=row.bounce_total or 0,
        trickshot_hits=row.trickshot_hits or 0,
        trickshot_total=row.trickshot_total or 0,
        elbow_violations=row.elbow_violations or 0,
    )


def get_tournament_stats(
    session: Session, tournament_id: int, tournament_name: str
) -> TournamentStats:
    total, completed, _ = _game_counts(session, tournament_id)
    return TournamentStats(
        tournament_id=tournament_id,
        tournament_name=tournament_name,
        total_games=total,
        completed_games=completed,
        player_leaderboard=_player_leaderboard(session, tournament_id),
        team_standings=_team_standings(session, tournament_id),
    )


def get_dashboard(
    session: Session, tournament_id: int, tournament_name: str
) -> DashboardStats:
    total, completed, in_progress = _game_counts(session, tournament_id)
    return DashboardStats(
        tournament_id=tournament_id,
        tournament_name=tournament_name,
        total_games=total,
        completed_games=completed,
        in_progress_games=in_progress,
        team_standings=_team_standings(session, tournament_id),
        player_leaderboard=_player_leaderboard(session, tournament_id),
        cup_heatmap=_cup_heatmap(session, tournament_id),
        total_punishments=_total_punishments(session, tournament_id),
        punishment_counts=_punishment_counts(session, tournament_id),
        recent_punishments=_recent_punishments(session, tournament_id),
        hot_hand=_hot_hand_streaks(session, tournament_id),
    )
