#  benchmark.py
#  Runs all sorting algorithms and returns a comparison table.


from algorithms import ALL_ALGOS, ALGO_INFO, run_sort


def benchmark_all(records, column, sample_size=1000):
    """
    Run every sorting algorithm on a sample of the dataset.
    Returns a list of dicts with time, comparisons, swaps, etc.
    """
    if not records:
        return []

    sample = records[:sample_size] if len(records) > sample_size else records
    results = []

    for algo in ALL_ALGOS:
        info = ALGO_INFO[algo]
        try:
            _, t_ms, comps, swaps = run_sort(algo, sample, column)
            results.append({
                "algorithm": algo,
                "time_ms": round(t_ms, 2),
                "comparisons": comps,
                "swaps": swaps,
                "complexity": info["complexity"],
                "stable": "Yes" if info["stable"] else "No",
                "type": "Extra" if info["extra"] else "Class",
            })
        except Exception as e:
            results.append({
                "algorithm": algo,
                "time_ms": -1,
                "comparisons": 0,
                "swaps": 0,
                "complexity": info["complexity"],
                "stable": "Yes" if info["stable"] else "No",
                "type": "Extra" if info["extra"] else "Class",
                "error": str(e),
            })
    return results