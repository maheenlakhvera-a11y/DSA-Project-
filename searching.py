
#  searching.py
#  Searching algorithms, advanced filters, and composite search.

def _match_value(val, query, mode):
    """Check if a value matches the query under the given mode."""
    v = str(val).lower()
    q = str(query).lower()

    if mode == "equals":
        return v == q
    if mode == "contains":
        return q in v
    if mode == "starts with":
        return v.startswith(q)
    if mode == "ends with":
        return v.endswith(q)
    if mode == "greater than":
        try:
            return float(v) > float(q)
        except ValueError:
            return False
    if mode == "less than":
        try:
            return float(v) < float(q)
        except ValueError:
            return False
    return q in v


# =========================================================
#  SEARCH ALGORITHMS
# =========================================================
def linear_search(records, column, query, mode="contains"):
    """Simple linear search across a single column."""
    results = []
    for r in records:
        if _match_value(r.get(column, ""), query, mode):
            results.append(r)
    return results


def binary_search(records, column, query, mode="equals"):
    """
    Binary search on a pre-sorted column. Falls back to linear search
    if the data is not sorted.
    """
    # Simple binary search assuming records are already sorted by column
    values = [str(r.get(column, "")).lower() for r in records]
    q = str(query).lower()

    lo, hi = 0, len(values) - 1
    while lo <= hi:
        mid = (lo + hi) // 2
        if values[mid] == q:
            # expand to include duplicates
            results = [records[mid]]
            i = mid - 1
            while i >= 0 and values[i] == q:
                results.append(records[i])
                i -= 1
            i = mid + 1
            while i < len(values) and values[i] == q:
                results.append(records[i])
                i += 1
            return results
        elif values[mid] < q:
            lo = mid + 1
        else:
            hi = mid - 1
    return []


def advanced_search(records, column, query, mode="contains"):
    """Alias for linear search with advanced modes."""
    return linear_search(records, column, query, mode)


# =========================================================
#  COMPOSITE SEARCH (AND / OR / NOT)
# =========================================================
def composite_search(records, conditions):
    """
    Apply multiple conditions in sequence with AND / OR / NOT logic.
    conditions: list of dicts with keys:
        column, query, mode, logic
    """
    if not conditions:
        return list(records)

    result = list(records)
    for i, cond in enumerate(conditions):
        matches = linear_search(
            result, cond["column"], cond["query"],
            cond.get("mode", "contains")
        )
        match_ids = set(id(r) for r in matches)
        logic = cond.get("logic", "AND").upper()

        if i == 0:
            if logic == "NOT":
                result = [r for r in result if id(r) not in match_ids]
            else:
                result = [r for r in result if id(r) in match_ids]
        else:
            if logic == "AND":
                result = [r for r in result if id(r) in match_ids]
            elif logic == "OR":
                current_ids = set(id(r) for r in result)
                for r in records:
                    if id(r) in match_ids and id(r) not in current_ids:
                        result.append(r)
            elif logic == "NOT":
                result = [r for r in result if id(r) not in match_ids]
    return result