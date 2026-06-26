#!/usr/bin/env bash
# Run the Telos goal-understanding benchmark for each available model family as the
# agent-under-test. Each family is judged by the OTHER families (self-judging excluded),
# so the scores are genuine cross-family verdicts.
#
# Usage: bash scripts/run_baselines.sh
set -u
cd "$(dirname "$0")/.."

for fam in claude gemini openai; do
  echo "=================================================================="
  echo "  baseline: $fam"
  echo "=================================================================="
  python -m telos.bench --adapter generic --family "$fam" \
      --out "results/generic-$fam.json" --verbose
done

echo "All baselines complete. Building leaderboard..."
python -m telos.report 2>/dev/null || true
