#!/usr/bin/env python
"""
Master Pipeline Orchestrator
=============================
Execute the complete Bluestock MF Capstone project ETL and analytics pipeline.

This script runs all analysis stages in sequence:
1. Data Ingestion (Day 1): Load and profile raw datasets
2. Data Cleaning (Day 2): Clean, validate, and prepare processed data
3. EDA (Day 3): Generate exploratory visualizations
4. Fund Performance (Day 4): Compute risk-adjusted performance metrics
5. Dashboard (Day 5): Build interactive multi-page dashboard
6. Advanced Analytics (Day 6): Risk analysis, cohort behavior, recommendations

Usage:
    python run_pipeline.py              # Run entire pipeline
    python run_pipeline.py --help       # Show available options
    python run_pipeline.py --stage day2 # Run only Day 2 cleaning

Exit codes:
    0 = Success
    1 = Error in any stage
"""

from __future__ import annotations

import sys
import traceback
from pathlib import Path
import argparse
from typing import Callable

PROJECT_ROOT = Path(__file__).resolve().parent.parent

# Import all pipeline stages
try:
    from data_ingestion import main as day1_main
    from day2_data_cleaning import main as day2_main
    from day3_eda import main as day3_main
    from day4_fund_performance import main as day4_main
    from day5_dashboard import main as day5_main
    from day6_advanced_analytics import main as day6_main
except ImportError as e:
    print(f"ERROR: Failed to import pipeline modules: {e}")
    sys.exit(1)


PIPELINE_STAGES: dict[str, tuple[str, Callable[[], None]]] = {
    "day1": ("Data Ingestion - Load & Profile", day1_main),
    "day2": ("Data Cleaning - Standardize & Validate", day2_main),
    "day3": ("EDA - Exploratory Visualizations", day3_main),
    "day4": ("Fund Performance - Risk Metrics", day4_main),
    "day5": ("Interactive Dashboard - Visualization", day5_main),
    "day6": ("Advanced Analytics - Risk & Behavior", day6_main),
}


def run_stage(stage_key: str) -> bool:
    """
    Execute a single pipeline stage.

    Args:
        stage_key: Key of the stage to run (e.g., 'day1', 'day2', etc.)

    Returns:
        True if successful, False otherwise.
    """
    if stage_key not in PIPELINE_STAGES:
        print(f"ERROR: Unknown stage '{stage_key}'. Available: {', '.join(PIPELINE_STAGES.keys())}")
        return False

    stage_name, stage_func = PIPELINE_STAGES[stage_key]
    print(f"\n{'='*70}")
    print(f"Running {stage_key.upper()}: {stage_name}")
    print(f"{'='*70}")

    try:
        stage_func()
        print(f"✓ {stage_key.upper()} completed successfully\n")
        return True
    except Exception as e:
        print(f"✗ {stage_key.upper()} failed with error:")
        print(f"  {type(e).__name__}: {e}")
        traceback.print_exc()
        return False


def run_full_pipeline() -> bool:
    """
    Execute the entire pipeline from Day 1 through Day 6.

    Returns:
        True if all stages succeed, False if any stage fails.
    """
    print("\n" + "="*70)
    print("BLUESTOCK MF CAPSTONE - COMPLETE PIPELINE EXECUTION")
    print("="*70)

    all_success = True
    completed_stages: list[str] = []

    for stage_key in PIPELINE_STAGES.keys():
        if run_stage(stage_key):
            completed_stages.append(stage_key)
        else:
            all_success = False
            print(f"\nPipeline halted at {stage_key.upper()}. Completed stages: {', '.join(completed_stages)}")
            break

    print("\n" + "="*70)
    if all_success:
        print("✓ PIPELINE COMPLETED SUCCESSFULLY")
        print(f"  All 6 stages executed: {', '.join(completed_stages)}")
    else:
        print("✗ PIPELINE FAILED")
        print(f"  Completed stages: {', '.join(completed_stages)}")
        print(f"  Total stages: {len(PIPELINE_STAGES)}")
    print("="*70 + "\n")

    return all_success


def main() -> None:
    """Parse arguments and execute the appropriate pipeline mode."""
    parser = argparse.ArgumentParser(
        description="Bluestock MF Capstone - Master ETL Pipeline Orchestrator",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run_pipeline.py              # Run full pipeline (Day 1-6)
  python run_pipeline.py --stage day2 # Run only Day 2 cleaning
  python run_pipeline.py --stage day5 # Run only Day 5 dashboard
  python run_pipeline.py --list       # List all available stages
        """,
    )
    parser.add_argument(
        "--stage",
        type=str,
        default=None,
        help="Run a specific stage (e.g., day1, day2, ..., day6)",
    )
    parser.add_argument(
        "--list",
        action="store_true",
        help="List all available stages",
    )

    args = parser.parse_args()

    if args.list:
        print("\nAvailable Pipeline Stages:")
        print("-" * 70)
        for key, (name, _) in PIPELINE_STAGES.items():
            print(f"  {key.upper():8} - {name}")
        print("-" * 70 + "\n")
        return

    if args.stage:
        success = run_stage(args.stage)
        sys.exit(0 if success else 1)
    else:
        success = run_full_pipeline()
        sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
