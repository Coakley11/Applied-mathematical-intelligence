"""Backward-compatible re-exports — primary structure is practical_labs."""

from content.practical_labs import (
    ACTION_LABELS,
    ACTION_TO_LAB,
    NUM_PRACTICAL_LABS,
    PRACTICAL_LABS,
    PRACTICAL_LAB_NAMES,
)

# Legacy names used by older components/tests
LAB_NAMES = PRACTICAL_LAB_NAMES
INTERACTIVE_LABS = PRACTICAL_LABS
NUM_LABS = NUM_PRACTICAL_LABS
