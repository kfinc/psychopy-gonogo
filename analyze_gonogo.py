#!/usr/bin/env python3
"""Compute accuracy and reaction-time metrics from Go/No-Go task data.

Reads all CSVs from a data directory (output of gonogo_task.py), computes
per-participant × session:
  - trial counts (go, nogo, total)
  - signal-detection counts (hits, misses, false alarms, correct rejections)
  - hit rate, false-alarm rate, overall accuracy
  - d′  (log-linear floor/ceiling correction before z-transform)
  - mean, median, and SD of correct-Go RT in milliseconds

Prints a summary table to the terminal and saves a CSV to --output.

Usage:
    python analyze_gonogo.py
    python analyze_gonogo.py --data data/ --output results/gonogo_summary.csv
"""

import argparse
import logging
import sys
from pathlib import Path

import pandas as pd
from scipy.stats import norm
from tabulate import tabulate

logging.basicConfig(level=logging.INFO, format="%(levelname)s  %(message)s")
log = logging.getLogger(__name__)

# Columns expected in every raw CSV
REQUIRED_COLS = {"participant", "session", "trial_type", "outcome", "rt_ms"}


def load_data(data_dir: Path) -> pd.DataFrame:
    """Load and concatenate all CSVs from *data_dir*.

    Parameters
    ----------
    data_dir : Path
        Directory containing raw gonogo_task.py output files.

    Returns
    -------
    pd.DataFrame
        Concatenated trial-level data.
    """
    csv_files = sorted(data_dir.glob("*.csv"))
    if not csv_files:
        log.error("No CSV files found in %s", data_dir)
        sys.exit(1)

    log.info("Found %d CSV file(s) in %s", len(csv_files), data_dir)
    frames = []
    for path in csv_files:
        df = pd.read_csv(path)
        missing = REQUIRED_COLS - set(df.columns)
        if missing:
            log.warning("Skipping %s — missing columns: %s", path.name, missing)
            continue
        frames.append(df)

    if not frames:
        log.error("No valid CSV files could be loaded.")
        sys.exit(1)

    data = pd.concat(frames, ignore_index=True)
    log.info("Loaded %d trials total", len(data))
    return data


def _dprime(hit_rate: float, fa_rate: float, n_go: int, n_nogo: int) -> float:
    """Compute d′ with log-linear floor/ceiling correction.

    Log-linear rule (Hautus 1995): replace raw proportions with
    (count + 0.5) / (n + 1) before z-transforming.  This is preferable
    to the simpler 0.5/n correction for small n because it shrinks extreme
    rates toward 0.5 rather than toward 0 or 1.

    Parameters
    ----------
    hit_rate, fa_rate : float
        Raw hit and false-alarm rates (may be 0 or 1).
    n_go, n_nogo : int
        Number of Go and No-Go trials (denominators for correction).
    """
    hits_raw = round(hit_rate * n_go)
    fa_raw = round(fa_rate * n_nogo)

    hr_adj = (hits_raw + 0.5) / (n_go + 1)
    fa_adj = (fa_raw + 0.5) / (n_nogo + 1)

    return float(norm.ppf(hr_adj) - norm.ppf(fa_adj))


def compute_metrics(group: pd.DataFrame) -> pd.Series:
    """Compute all accuracy and RT metrics for one participant × session.

    Parameters
    ----------
    group : pd.DataFrame
        Subset of the full trial table for a single participant/session.

    Returns
    -------
    pd.Series
        One row of summary statistics.
    """
    counts = group["outcome"].value_counts()
    hits = int(counts.get("hit", 0))
    misses = int(counts.get("miss", 0))
    fa = int(counts.get("false_alarm", 0))
    cr = int(counts.get("correct_rejection", 0))

    n_go = hits + misses
    n_nogo = fa + cr
    n_trials = len(group)

    hit_rate = hits / n_go if n_go > 0 else float("nan")
    fa_rate = fa / n_nogo if n_nogo > 0 else float("nan")
    overall_acc = (hits + cr) / n_trials if n_trials > 0 else float("nan")

    if n_go > 0 and n_nogo > 0:
        dp = _dprime(hit_rate, fa_rate, n_go, n_nogo)
    else:
        dp = float("nan")

    # RT only on hits (correct Go responses)
    hit_rts = pd.to_numeric(
        group.loc[group["outcome"] == "hit", "rt_ms"], errors="coerce"
    ).dropna()

    return pd.Series(
        {
            "n_trials": n_trials,
            "n_go": n_go,
            "n_nogo": n_nogo,
            "hits": hits,
            "misses": misses,
            "false_alarms": fa,
            "correct_rejections": cr,
            "hit_rate": round(hit_rate, 4) if not pd.isna(hit_rate) else float("nan"),
            "fa_rate": round(fa_rate, 4) if not pd.isna(fa_rate) else float("nan"),
            "overall_acc": round(overall_acc, 4) if not pd.isna(overall_acc) else float("nan"),
            "d_prime": round(dp, 3) if not pd.isna(dp) else float("nan"),
            "mean_rt_ms": round(hit_rts.mean(), 1) if len(hit_rts) > 0 else float("nan"),
            "median_rt_ms": round(hit_rts.median(), 1) if len(hit_rts) > 0 else float("nan"),
            "sd_rt_ms": round(hit_rts.std(ddof=1), 1) if len(hit_rts) > 1 else float("nan"),
        }
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--data",
        type=Path,
        default=Path("data"),
        help="Directory containing raw CSV files (default: data/)",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("results/gonogo_summary.csv"),
        help="Path for the output summary CSV (default: results/gonogo_summary.csv)",
    )
    args = parser.parse_args()

    if not args.data.is_dir():
        log.error("Data directory not found: %s", args.data)
        sys.exit(1)

    data = load_data(args.data)

    summary = (
        data.groupby(["participant", "session"], sort=True)
        .apply(compute_metrics, include_groups=False)
        .reset_index()
    )

    # ── Terminal output ───────────────────────────────────────────────────────
    display_cols = [
        "participant", "session",
        "n_go", "n_nogo",
        "hits", "misses", "false_alarms", "correct_rejections",
        "hit_rate", "fa_rate", "overall_acc", "d_prime",
        "mean_rt_ms", "median_rt_ms", "sd_rt_ms",
    ]
    print("\n" + tabulate(
        summary[display_cols],
        headers=display_cols,
        tablefmt="fancy_grid",
        floatfmt=".3f",
        showindex=False,
    ))

    # ── Save CSV ──────────────────────────────────────────────────────────────
    args.output.parent.mkdir(parents=True, exist_ok=True)
    summary.to_csv(args.output, index=False)
    log.info("Summary saved to %s", args.output)


if __name__ == "__main__":
    main()
