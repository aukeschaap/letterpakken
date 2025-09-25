from collections import deque
from typing import List, Tuple

from ._typing import AdjList, LetterSet

INF: int = 10**9


def is_valid(word: str, letter_sets: List[LetterSet]) -> bool:
    """
    Decide if there exists an assignment of positions in ``word`` to the sets
    so that each set consumes exactly one character and that character belongs
    to that set.

    Parameters
    ----------
    word : str
        Candidate word.
    letter_sets : iterable of `LetterSet`
        Sets of letter choices.

    Returns
    -------
    bool
        True iff a perfect matching exists (feasible assignment).

    Notes
    -----
    Builds a bipartite graph from positions to sets and runs Hopcroft–Karp.
    """
    k: int = len(letter_sets)
    if len(word) != k:
        return False

    adj: AdjList = [[] for _ in range(k)]
    for i, ch in enumerate(word):
        edges: List[int] = [j for j, s in enumerate(letter_sets) if ch in s]
        if not edges:
            return False
        adj[i] = edges

    matching, _, _ = _hopcroft_karp(adj, n_left=k, n_right=k)
    return matching == k


def _bfs(
    adj: AdjList, pairU: List[int], pairV: List[int], dist: List[int], n_left: int
) -> bool:
    """
    Breadth-first search step of the Hopcroft–Karp algorithm.

    Parameters
    ----------
    adj : list[list[int]]
        Adjacency list; adj[u] contains neighbor indices on the right.
    pairU : list[int]
        Matched right vertex for each left vertex (or -1).
    pairV : list[int]
        Matched left vertex for each right vertex (or -1).
    dist : list[int]
        Distances used to layer the graph.
    n_left : int
        Number of vertices on the left side.

    Returns
    -------
    bool
        True if there exists at least one augmenting path.
    """
    q: deque[int] = deque()
    for u in range(n_left):
        if pairU[u] == -1:
            dist[u] = 0
            q.append(u)
        else:
            dist[u] = INF

    found: bool = False
    while q:
        u = q.popleft()
        for v in adj[u]:
            pu: int = pairV[v]
            if pu == -1:
                found = True
            elif dist[pu] == INF:
                dist[pu] = dist[u] + 1
                q.append(pu)
    return found


def _dfs(
    u: int, adj: AdjList, pairU: List[int], pairV: List[int], dist: List[int]
) -> bool:
    """
    Depth-first search step of the Hopcroft–Karp algorithm.

    Parameters
    ----------
    u : int
        Left vertex to start from.
    adj : list[list[int]]
        Adjacency list.
    pairU : list[int]
        Matched right vertex for each left vertex (or -1).
    pairV : list[int]
        Matched left vertex for each right vertex (or -1).
    dist : list[int]
        Distances used to guide DFS along layers.

    Returns
    -------
    bool
        True if an augmenting path is found from `u`.
    """
    for v in adj[u]:
        pu: int = pairV[v]
        if pu == -1 or (dist[pu] == dist[u] + 1 and _dfs(pu, adj, pairU, pairV, dist)):
            pairU[u] = v
            pairV[v] = u
            return True
    dist[u] = float("inf")  # type: ignore[assignment]
    return False


def _hopcroft_karp(
    adj: AdjList, n_left: int, n_right: int
) -> Tuple[int, List[int], List[int]]:
    """
    Maximum bipartite matching via Hopcroft–Karp.

    Parameters
    ----------
    adj : list[list[int]]
        Adjacency list for left->right edges; length must be `n_left`.
    n_left : int
        Number of left vertices.
    n_right : int
        Number of right vertices.

    Returns
    -------
    matching : int
        Size of the maximum matching.
    pairU : list[int]
        For each left vertex `u`, the matched right vertex index, or -1.
    pairV : list[int]
        For each right vertex `v`, the matched left vertex index, or -1.

    Raises
    ------
    ValueError
        If `len(adj) != n_left`.

    Notes
    -----
    The algorithm runs in :math:`O(E \\sqrt{V})` time.

    Examples
    --------
    >>> _hopcroft_karp([[0, 1], [0], [1]], n_left=3, n_right=2)
    (2, [1, 0, -1], [1, 0])
    """
    if len(adj) != n_left:
        raise ValueError("adj must have length n_left")

    pairU: List[int] = [-1] * n_left
    pairV: List[int] = [-1] * n_right
    dist: List[int] = [0] * n_left

    matching: int = 0
    while _bfs(adj, pairU, pairV, dist, n_left):
        for u in range(n_left):
            if pairU[u] == -1 and _dfs(u, adj, pairU, pairV, dist):
                matching += 1
    return matching, pairU, pairV
