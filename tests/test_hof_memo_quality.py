"""HOF memo wording and section-quality regression tests."""

from __future__ import annotations

import unittest

from hof_case_analysis import (
    _exclude_duplicate_bullets,
    _filter_position_peers,
    compose_hof_statistical_case,
    format_hof_case_memo_markdown,
)


def _freeman_style_packet() -> dict:
    return {
        "target_player": "Freddie Freeman",
        "primary_position": "1B",
        "sort_stat": "HR",
        "target_rank": 56,
        "total_players_returned": 87,
        "hall_of_famers_returned": 43,
        "hall_of_fame_rate_pct": 49.4,
        "cohort_strength_stats": ["2B", "H", "BA", "RBI", "OBP", "OPS"],
        "cohort_weakness_stats": ["HR"],
        "target_cohort_ranks": {
            "2B": {"rank": 8, "of": 87, "stat": "2B", "value": 520, "percentile_top": 92, "tier": "top 10%"},
            "H": {"rank": 12, "of": 87, "stat": "H", "value": 2100, "percentile_top": 88, "tier": "top 15%"},
            "BA": {"rank": 10, "of": 87, "stat": "BA", "value": 0.301, "percentile_top": 90, "tier": "top 10%"},
            "RBI": {"rank": 15, "of": 87, "stat": "RBI", "value": 1100, "percentile_top": 85, "tier": "top quartile"},
            "HR": {"rank": 56, "of": 87, "stat": "HR", "value": 350, "percentile_top": 40, "tier": "middle"},
        },
        "target_identity": {"career_span": {"debut_year": 2010, "final_year": 2025, "seasons": 16}},
        "target_awards_summary": {
            "data_available": True,
            "major_awards": 1,
            "mvp_summary": "NL MVP 2020",
            "total_awards": 4,
        },
        "position_percentiles": {
            "2B": {"percentile_top": 95, "tier": "top 5%"},
            "H": {"percentile_top": 92, "tier": "top 10%"},
            "BA": {"percentile_top": 90, "tier": "top 10%"},
        },
        "position_stat_ranks": {
            "2B": {"rank": 3, "of": 40},
            "H": {"rank": 5, "of": 40},
            "BA": {"rank": 4, "of": 40},
        },
        "comparable_players": {
            "hall_of_famers": [
                {"fullName": "Frank Thomas", "careerPrimaryPos": "1B", "HR": 521, "H": 2468, "2B": 495},
                {"fullName": "Jeff Kent", "careerPrimaryPos": "2B", "HR": 351, "H": 2461, "2B": 560},
                {"fullName": "Scott Rolen", "careerPrimaryPos": "3B", "HR": 316, "H": 2077, "2B": 485},
            ],
            "non_hall_of_famers": [
                {"fullName": "Jason Giambi", "careerPrimaryPos": "1B", "HR": 440, "H": 2010, "2B": 366},
            ],
        },
        "filters_used": {
            "sort_stat": "HR",
            "stat_minimums": {"R": 0, "OPS": 0.0, "OBP": 0.0, "BA": 0.0, "3B": 0, "RBI": 0, "AB": 0, "HR": 300},
        },
        "cohort_selectivity": {"selectivity": "selective", "confidence": "moderate"},
    }


class HofMemoQualityTests(unittest.TestCase):
    def test_compose_suppresses_trivial_stat_minimums(self) -> None:
        packet = _freeman_style_packet()
        analysis = compose_hof_statistical_case(packet)
        md = format_hof_case_memo_markdown(analysis).lower()
        self.assertNotIn("runs ≥ 0", md)
        self.assertNotIn("ops ≥ 0", md)
        self.assertNotIn("batting average ≥ 0", md)

    def test_position_peer_language_uses_same_primary_position_only(self) -> None:
        packet = _freeman_style_packet()
        analysis = compose_hof_statistical_case(packet)
        memo = analysis.get("case_memo") or {}
        position_text = " ".join(memo.get("position_era_context") or [])
        self.assertIn("Frank Thomas", position_text)
        self.assertNotIn("Jeff Kent", position_text)
        self.assertNotIn("Scott Rolen", position_text)
        comparison_text = " ".join(str(x) for x in (memo.get("comparison_notes") or []))
        self.assertIn("Jeff Kent", comparison_text)
        self.assertIn("broader comp", comparison_text.lower())

    def test_strongest_and_supporting_evidence_do_not_duplicate(self) -> None:
        packet = _freeman_style_packet()
        analysis = compose_hof_statistical_case(packet)
        memo = analysis.get("case_memo") or {}
        strongest = [str(x) for x in (memo.get("strongest_evidence") or [])]
        supporting = [str(x) for x in (memo.get("case_evidence") or [])]
        self.assertTrue(strongest)
        strongest_keys = {_normalize_key(x) for x in strongest}
        for line in supporting:
            key = _normalize_key(line)
            self.assertNotIn(key, strongest_keys, msg=f"Duplicate supporting line: {line}")
            self.assertFalse(
                any(key in sk or sk in key for sk in strongest_keys if len(sk) > 24),
                msg=f"Near-duplicate supporting line: {line}",
            )

    def test_era_note_uses_dataset_span_wording(self) -> None:
        packet = _freeman_style_packet()
        analysis = compose_hof_statistical_case(packet)
        memo = analysis.get("case_memo") or {}
        era_text = " ".join(memo.get("position_era_context") or [])
        self.assertIn("Career span in this dataset: 2010–2025", era_text)
        self.assertNotIn("Modern-era offense and roster usage can depress", era_text)
        self.assertIn("still active", era_text.lower())

    def test_final_takeaway_links_verdict_to_evidence(self) -> None:
        packet = _freeman_style_packet()
        analysis = compose_hof_statistical_case(packet)
        memo = analysis.get("case_memo") or {}
        takeaway = str(memo.get("final_takeaway") or "")
        self.assertIn("because", takeaway.lower())
        self.assertIn("home runs rank", takeaway.lower())
        self.assertIn("not induction odds", takeaway.lower())

    def test_disclaimer_is_concise(self) -> None:
        packet = _freeman_style_packet()
        analysis = compose_hof_statistical_case(packet)
        self.assertIn("not Hall of Fame induction odds", analysis.get("disclaimer") or "")

    def test_filter_position_peers(self) -> None:
        rows = [
            {"fullName": "Frank Thomas", "careerPrimaryPos": "1B"},
            {"fullName": "Jeff Kent", "careerPrimaryPos": "2B"},
        ]
        peers = _filter_position_peers(rows, "1B")
        self.assertEqual(len(peers), 1)
        self.assertEqual(peers[0]["fullName"], "Frank Thomas")

    def test_exclude_duplicate_bullets(self) -> None:
        strongest = ["Elite doubles (520) — #8 of 87 in this cohort."]
        supporting = [
            "Elite doubles (520) — #8 of 87 in this cohort.",
            "43/87 players in this cohort are Hall of Famers (49.4%) — the peer group itself is Hall-heavy.",
        ]
        out = _exclude_duplicate_bullets(supporting, strongest)
        self.assertEqual(len(out), 1)
        self.assertIn("Hall-heavy", out[0])


def _normalize_key(text: str) -> str:
    import re

    return re.sub(r"\s+", " ", str(text or "").lower()).strip().rstrip(".")


if __name__ == "__main__":
    unittest.main()
