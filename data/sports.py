"""Sports analytics data placeholders."""

import pandas as pd

INTEGRATION_STATUS = "placeholder"


def load_player_season_stats(season: int, league: str = "MLB") -> pd.DataFrame:
    """Schema: player_id, games, rate_stats, playing_time."""
    return pd.DataFrame(
        columns=["player_id", "games", "pa", "woba", "war"],
        data=[],
    )


def load_team_results(season: int, league: str = "NBA") -> pd.DataFrame:
    """Schema: game_id, date, home, away, home_pts, away_pts."""
    return pd.DataFrame(columns=["game_id", "date", "home", "away", "home_pts", "away_pts"])
