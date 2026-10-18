# =========================================================
#  multi_sort.py
#  Multi-level sorting logic.
#
#  Idea:
#    To sort by multiple columns with priority, sort by the
#    least significant column first, then by the next one,
#    and so on. Because each subsequent pass uses a STABLE
#    sort (merge sort), the previous ordering is preserved.
#
#  Example:
#    Sort by (Year DESC, Title ASC)
#      Step 1: Stable sort by Title ASC
#      Step 2: Stable sort by Year DESC  (final order)
# =========================================================

from algorithms import merge_sort, Metrics, _prepare_tuples


def multi_level_sort(records, columns_with_order):
    """
    Sort records by multiple columns in priority order.

    Parameters
    ----------
    records : list[dict]
        The dataset to sort.
    columns_with_order : list[tuple[str, bool]]
        A list of (column_name, ascending) pairs, ordered from
        highest priority to lowest priority.
        Example: [("year", False), ("title", True)]

    Returns
    -------
    list[dict]
        A new list of records sorted by the given columns.
    """
    result = list(records)
    if not result:
        return result

    m = Metrics()

    # Process from lowest priority to highest priority.
    # The last sort dominates the final order.
    for col, asc in reversed(columns_with_order):
        keys, tuples, key_index = _prepare_tuples(result, col)
        if key_index is None:
            continue

        # merge_sort is stable, so it preserves the previous ordering
        sorted_tuples = merge_sort(tuples, key_index, m)

        # For descending order, we negate the comparison by reversing
        # groups of equal keys (keeps stability within groups).
        if not asc:
            sorted_tuples = _reverse_stable(sorted_tuples, key_index)

        result = [dict(zip(keys, t)) for t in sorted_tuples]

    return result


def _reverse_stable(sorted_tuples, key_index):
    """
    Reverse the list in a stability-preserving way.
    Reverses the order of distinct-key groups without flipping
    the order within each group.
    """
    if not sorted_tuples:
        return sorted_tuples

    # Build a list of (key_value, group) pairs
    groups = []
    current_key = sorted_tuples[0][key_index]
    current_group = [sorted_tuples[0]]

    for row in sorted_tuples[1:]:
        if row[key_index] == current_key:
            current_group.append(row)
        else:
            groups.append((current_key, current_group))
            current_key = row[key_index]
            current_group = [row]
    groups.append((current_key, current_group))

    # Reverse the group order
    groups.reverse()

    # Flatten
    result = []
    for _, group in groups:
        result.extend(group)
    return result