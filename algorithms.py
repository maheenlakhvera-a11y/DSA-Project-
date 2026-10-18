# =========================================================
#  algorithms.py
#  All sorting algorithms with comparison and swap tracking.
# =========================================================

import time


# =========================================================
#  ALGORITHM METADATA
# =========================================================
ALGO_INFO = {
    "Bubble Sort":       {"complexity": "O(n²)",      "stable": True,  "extra": False},
    "Insertion Sort":    {"complexity": "O(n²)",      "stable": True,  "extra": False},
    "Selection Sort":    {"complexity": "O(n²)",      "stable": False, "extra": False},
    "Merge Sort":        {"complexity": "O(n log n)", "stable": True,  "extra": False},
    "Hybrid Merge Sort": {"complexity": "O(n log n)", "stable": True,  "extra": False},
    "Quick Sort":        {"complexity": "O(n log n)", "stable": False, "extra": False},
    "Counting Sort":     {"complexity": "O(n + k)",   "stable": True,  "extra": False},
    "Radix Sort":        {"complexity": "O(nk)",      "stable": True,  "extra": False},
    "Heap Sort":         {"complexity": "O(n log n)", "stable": False, "extra": True},
    "Shell Sort":        {"complexity": "O(n^1.3)",   "stable": False, "extra": True},
}

ALL_ALGOS = list(ALGO_INFO.keys())

NUMERIC_COLUMNS = {"author_count", "subject_count", "pages", "figures",
                   "year", "month", "title_words"}


# =========================================================
#  METRICS TRACKER
# =========================================================
class Metrics:
    """Tracks the number of comparisons and swaps."""
    def __init__(self):
        self.comparisons = 0
        self.swaps = 0


def _key(value):
    """Normalize values for comparison."""
    if value is None:
        return ""
    if isinstance(value, str):
        return value.lower()
    return value


# =========================================================
#  SORTING ALGORITHMS
# =========================================================

def bubble_sort(arr, key_index, m):
    """Repeatedly swap adjacent elements if they are in the wrong order."""
    a = arr[:]
    n = len(a)
    for i in range(n):
        swapped = False
        for j in range(0, n - i - 1):
            m.comparisons += 1
            if _key(a[j][key_index]) > _key(a[j + 1][key_index]):
                a[j], a[j + 1] = a[j + 1], a[j]
                m.swaps += 1
                swapped = True
        if not swapped:
            break
    return a


def insertion_sort(arr, key_index, m):
    """Build the sorted array one element at a time."""
    a = arr[:]
    for i in range(1, len(a)):
        cur = a[i]
        j = i - 1
        while j >= 0:
            m.comparisons += 1
            if _key(a[j][key_index]) > _key(cur[key_index]):
                a[j + 1] = a[j]
                m.swaps += 1
                j -= 1
            else:
                break
        a[j + 1] = cur
    return a


def selection_sort(arr, key_index, m):
    """Repeatedly select the minimum element and place it at the start."""
    a = arr[:]
    n = len(a)
    for i in range(n):
        min_idx = i
        for j in range(i + 1, n):
            m.comparisons += 1
            if _key(a[j][key_index]) < _key(a[min_idx][key_index]):
                min_idx = j
        if min_idx != i:
            a[i], a[min_idx] = a[min_idx], a[i]
            m.swaps += 1
    return a


def merge_sort(arr, key_index, m):
    """Divide and conquer — split, sort, merge. Stable."""
    a = arr[:]
    _merge_sort_rec(a, 0, len(a) - 1, key_index, m)
    return a


def _merge_sort_rec(a, left, right, key_index, m):
    if left < right:
        mid = (left + right) // 2
        _merge_sort_rec(a, left, mid, key_index, m)
        _merge_sort_rec(a, mid + 1, right, key_index, m)
        _merge(a, left, mid, right, key_index, m)


def _merge(a, left, mid, right, key_index, m):
    L = a[left:mid + 1]
    R = a[mid + 1:right + 1]
    i = j = 0
    k = left
    while i < len(L) and j < len(R):
        m.comparisons += 1
        if _key(L[i][key_index]) <= _key(R[j][key_index]):
            a[k] = L[i]
            i += 1
        else:
            a[k] = R[j]
            j += 1
        k += 1
    while i < len(L):
        a[k] = L[i]
        i += 1
        k += 1
    while j < len(R):
        a[k] = R[j]
        j += 1
        k += 1


def hybrid_merge_sort(arr, key_index, m, threshold=16):
    """Merge sort that switches to insertion sort for small chunks."""
    a = arr[:]
    _hybrid_rec(a, 0, len(a) - 1, key_index, m, threshold)
    return a


def _hybrid_rec(a, left, right, key_index, m, threshold):
    if right - left + 1 <= threshold:
        for i in range(left + 1, right + 1):
            cur = a[i]
            j = i - 1
            while j >= left:
                m.comparisons += 1
                if _key(a[j][key_index]) > _key(cur[key_index]):
                    a[j + 1] = a[j]
                    m.swaps += 1
                    j -= 1
                else:
                    break
            a[j + 1] = cur
    elif left < right:
        mid = (left + right) // 2
        _hybrid_rec(a, left, mid, key_index, m, threshold)
        _hybrid_rec(a, mid + 1, right, key_index, m, threshold)
        _merge(a, left, mid, right, key_index, m)


def quick_sort(arr, key_index, m):
    """Pick a pivot and partition around it."""
    a = arr[:]
    _quick_rec(a, 0, len(a) - 1, key_index, m)
    return a


def _quick_rec(a, low, high, key_index, m):
    if low < high:
        pi = _partition(a, low, high, key_index, m)
        _quick_rec(a, low, pi - 1, key_index, m)
        _quick_rec(a, pi + 1, high, key_index, m)


def _partition(a, low, high, key_index, m):
    pivot = a[high]
    i = low - 1
    for j in range(low, high):
        m.comparisons += 1
        if _key(a[j][key_index]) <= _key(pivot[key_index]):
            i += 1
            if i != j:
                a[i], a[j] = a[j], a[i]
                m.swaps += 1
    if i + 1 != high:
        a[i + 1], a[high] = a[high], a[i + 1]
        m.swaps += 1
    return i + 1


def heap_sort(arr, key_index, m):
    """Build a max-heap and extract the maximum repeatedly."""
    a = arr[:]
    n = len(a)

    def heapify(n, i):
        largest = i
        l = 2 * i + 1
        r = 2 * i + 2
        if l < n:
            m.comparisons += 1
            if _key(a[l][key_index]) > _key(a[largest][key_index]):
                largest = l
        if r < n:
            m.comparisons += 1
            if _key(a[r][key_index]) > _key(a[largest][key_index]):
                largest = r
        if largest != i:
            a[i], a[largest] = a[largest], a[i]
            m.swaps += 1
            heapify(n, largest)

    for i in range(n // 2 - 1, -1, -1):
        heapify(n, i)
    for i in range(n - 1, 0, -1):
        a[0], a[i] = a[i], a[0]
        m.swaps += 1
        heapify(i, 0)
    return a


def shell_sort(arr, key_index, m):
    """Generalized insertion sort using decreasing gaps."""
    a = arr[:]
    n = len(a)
    gap = n // 2
    while gap > 0:
        for i in range(gap, n):
            temp = a[i]
            j = i
            while j >= gap:
                m.comparisons += 1
                if _key(a[j - gap][key_index]) > _key(temp[key_index]):
                    a[j] = a[j - gap]
                    m.swaps += 1
                    j -= gap
                else:
                    break
            a[j] = temp
        gap //= 2
    return a


def counting_sort(arr, key_index, m):
    """Stable counting sort — works only for integer values."""
    if not arr:
        return arr[:]
    a = arr[:]
    try:
        values = [int(x[key_index]) for x in a]
    except (ValueError, TypeError):
        return merge_sort(arr, key_index, m)

    mn, mx = min(values), max(values)
    size = mx - mn + 1
    count = [0] * size
    for v in values:
        count[v - mn] += 1
    for i in range(1, size):
        count[i] += count[i - 1]

    output = [None] * len(a)
    for i in range(len(a) - 1, -1, -1):
        v = int(a[i][key_index])
        count[v - mn] -= 1
        output[count[v - mn]] = a[i]
        m.swaps += 1
    return output


def radix_sort(arr, key_index, m):
    """Radix sort — works only for non-negative integers."""
    if not arr:
        return arr[:]
    a = arr[:]
    try:
        values = [int(x[key_index]) for x in a]
    except (ValueError, TypeError):
        return merge_sort(arr, key_index, m)

    if min(values) < 0:
        return merge_sort(arr, key_index, m)

    max_val = max(values)
    exp = 1
    while max_val // exp > 0:
        a = _counting_radix(a, key_index, exp, m)
        exp *= 10
    return a


def _counting_radix(a, key_index, exp, m):
    n = len(a)
    output = [None] * n
    count = [0] * 10
    for i in range(n):
        idx = (int(a[i][key_index]) // exp) % 10
        count[idx] += 1
    for i in range(1, 10):
        count[i] += count[i - 1]
    for i in range(n - 1, -1, -1):
        idx = (int(a[i][key_index]) // exp) % 10
        count[idx] -= 1
        output[count[idx]] = a[i]
        m.swaps += 1
    return output


# =========================================================
#  DISPATCHER
# =========================================================
SORT_FUNCS = {
    "Bubble Sort":       bubble_sort,
    "Insertion Sort":    insertion_sort,
    "Selection Sort":    selection_sort,
    "Merge Sort":        merge_sort,
    "Hybrid Merge Sort": hybrid_merge_sort,
    "Quick Sort":        quick_sort,
    "Counting Sort":     counting_sort,
    "Radix Sort":        radix_sort,
    "Heap Sort":         heap_sort,
    "Shell Sort":        shell_sort,
}


def _prepare_tuples(records, column):
    """Convert list of dicts to list of tuples for faster access."""
    keys = list(records[0].keys()) if records else []
    if column not in keys:
        return [], [], None
    key_index = keys.index(column)
    tuples = []
    for r in records:
        row = list(r.get(k, "") for k in keys)
        if column in NUMERIC_COLUMNS:
            try:
                row[key_index] = int(row[key_index])
            except (ValueError, TypeError):
                row[key_index] = 0
        tuples.append(tuple(row))
    return keys, tuples, key_index


def run_sort(algo_name, records, column):
    """
    Run a single sorting algorithm on the given records.
    Returns: (sorted_records, time_ms, comparisons, swaps)
    """
    if not records:
        return [], 0.0, 0, 0

    keys, tuples, key_index = _prepare_tuples(records, column)
    if key_index is None:
        return records, 0.0, 0, 0

    m = Metrics()
    fn = SORT_FUNCS[algo_name]

    t0 = time.perf_counter()
    sorted_tuples = fn(tuples, key_index, m)
    t1 = time.perf_counter()

    elapsed_ms = (t1 - t0) * 1000
    result = [dict(zip(keys, t)) for t in sorted_tuples]
    return result, elapsed_ms, m.comparisons, m.swaps