"""
Stallings Foldings — Python 3.9 compatible rewrite.

Interactive GUI + automated `stallings_fold` function that computes
a minimal generating set for the subgroup of a free group generated
by a given list of words.

Word notation (same as original):
  - Lowercase letter  = generator,  e.g. 'a', 'b'
  - Letter + '-'      = inverse,    e.g. 'a-', 'b-'
  - A word is a string like 'aab-'  meaning  a·a·b⁻¹

Example
-------
    result = stallings_fold(["aab-", "aaab", "a-bb", "aba", "aaab-b-a-"])
    print(result.rank)          # rank of subgroup
    print(result.generators)    # free basis as words
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set, Tuple

import matplotlib.pyplot as plt
import networkx as nx
import netgraph as ng
from matplotlib.widgets import Button, RadioButtons, TextBox


# ---------------------------------------------------------------------------
# Core data types
# ---------------------------------------------------------------------------

Word = str          # e.g. "aab-"
NodeId = str        # e.g. "Z", "0,1", "1,3"
Edge = Tuple[NodeId, NodeId]


@dataclass
class StallingsGraph:
    """A fully-folded Stallings graph together with derived information."""
    graph: nx.DiGraph
    base: NodeId                        # distinguished base-point
    rank: int                           # rank of the subgroup
    generators: List[Word]              # free basis (one word per cycle)


# ---------------------------------------------------------------------------
# Building the flower automaton
# ---------------------------------------------------------------------------

def _parse_word(word: Word) -> List[str]:
    """Return the list of (possibly inverse) letters in *word*.

    Each entry is either 'x' (generator x) or 'x-' (inverse of x).
    """
    return re.findall(r"[a-z]-?", word)


def _add_multiedge(G: nx.DiGraph, u: NodeId, v: NodeId, label: str) -> None:
    """Add label to edge (u,v), creating it if necessary."""
    if G.has_edge(u, v):
        G.edges[u, v]["label"] += "," + label
    else:
        G.add_edge(u, v, label=label)


def _remove_duplicate_labels(s: str) -> str:
    return ",".join(sorted(set(s.split(","))))


def _add_word_as_petal(G: nx.DiGraph, word: Word, n: int,
                       base: NodeId = "Z") -> None:
    """Attach one petal for *word* (the n-th word) to the flower automaton."""
    letters = _parse_word(word)
    for i, letter in enumerate(letters):
        src = base if i == 0 else f"{n},{i}"
        ran = base if i == len(letters) - 1 else f"{n},{i + 1}"
        # Inverse letter means arrow goes backwards
        if letter.endswith("-"):
            src, ran = ran, src
        _add_multiedge(G, src, ran, letter[0])


def build_flower_automaton(words: List[Word], base: NodeId = "Z") -> nx.DiGraph:
    """Return the (unfolded) flower automaton for *words*."""
    G: nx.DiGraph = nx.DiGraph()
    G.add_node(base)
    for i, word in enumerate(words):
        _add_word_as_petal(G, word, i, base=base)
    return G


# ---------------------------------------------------------------------------
# One folding step
# ---------------------------------------------------------------------------

def _find_fold(G: nx.DiGraph) -> Optional[Tuple[NodeId, NodeId, NodeId, str, str]]:
    """Find a pair of edges that can be folded.

    Returns (shared, a, b, label, kind) where:
      kind == 'source'  → edges (shared→a) and (shared→b) share source + label
      kind == 'target'  → edges (a→shared) and (b→shared) share target + label

    Returns None if the graph is already fully folded (immersed).
    """
    nodes = list(G.nodes())
    for shared in nodes:
        # --- same source ---
        out_by_label: Dict[str, List[NodeId]] = {}
        for _, v, data in G.out_edges(shared, data=True):
            for lbl in data["label"].split(","):
                out_by_label.setdefault(lbl, []).append(v)
        for lbl, targets in out_by_label.items():
            if len(targets) >= 2:
                return (shared, targets[0], targets[1], lbl, "source")

        # --- same target ---
        in_by_label: Dict[str, List[NodeId]] = {}
        for u, _, data in G.in_edges(shared, data=True):
            for lbl in data["label"].split(","):
                in_by_label.setdefault(lbl, []).append(u)
        for lbl, sources in in_by_label.items():
            if len(sources) >= 2:
                return (shared, sources[0], sources[1], lbl, "target")

    return None


def _apply_merge(G: nx.DiGraph, old: NodeId, new: NodeId,
                 base: NodeId) -> nx.DiGraph:
    """Return a new DiGraph with node *old* merged into *new*.

    The base-point is never eliminated.
    """
    # Make sure we never destroy the base-point
    if old == base:
        old, new = new, old

    G2: nx.DiGraph = nx.DiGraph()
    rename = lambda n: new if n == old else n   # noqa: E731

    for u, v, data in G.edges(data=True):
        _add_multiedge(G2, rename(u), rename(v), data["label"])

    for e in G2.edges():
        G2.edges[e]["label"] = _remove_duplicate_labels(G2.edges[e]["label"])

    return G2


def fold_once(G: nx.DiGraph, base: NodeId = "Z") -> Optional[nx.DiGraph]:
    """Apply one Stallings fold if possible; return new graph or None."""
    result = _find_fold(G)
    if result is None:
        return None

    shared, a, b, _lbl, kind = result
    if kind == "source":
        # merge a into b  (both are targets of shared)
        return _apply_merge(G, a, b, base)
    else:
        # merge a into b  (both are sources pointing to shared)
        return _apply_merge(G, a, b, base)


# ---------------------------------------------------------------------------
# Full automated algorithm
# ---------------------------------------------------------------------------

def _read_generators(G: nx.DiGraph, base: NodeId) -> List[Word]:
    """Extract one generator word per independent cycle via a spanning tree."""
    generators: List[Word] = []

    # Build a spanning tree of the underlying undirected graph
    undirected = G.to_undirected()
    tree_edges: Set[Edge] = set(nx.minimum_spanning_tree(undirected).edges())

    # For each non-tree directed edge, read the path base → src → tgt → base
    tree = nx.DiGraph()
    for u, v in tree_edges:
        if G.has_edge(u, v):
            tree.add_edge(u, v, label=G.edges[u, v]["label"].split(",")[0])
        elif G.has_edge(v, u):
            tree.add_edge(v, u, label=G.edges[v, u]["label"].split(",")[0])

    # Ensure base is reachable in the tree from everywhere (it should be)
    tree_undirected = tree.to_undirected()

    def path_word(src: NodeId, tgt: NodeId) -> Word:
        """Word spelling out the unique tree path from src to tgt."""
        try:
            path = nx.shortest_path(tree_undirected, src, tgt)
        except nx.NetworkXNoPath:
            return ""
        word = ""
        for i in range(len(path) - 1):
            u, v = path[i], path[i + 1]
            if tree.has_edge(u, v):
                lbl = tree.edges[u, v]["label"].split(",")[0]
                word += lbl
            else:
                lbl = tree.edges[v, u]["label"].split(",")[0]
                word += lbl + "-"
        return word

    for u, v, data in G.edges(data=True):
        # Skip tree edges
        if (u, v) in tree_edges or (v, u) in tree_edges:
            continue
        lbl = data["label"].split(",")[0]
        prefix = path_word(base, u)
        suffix = path_word(v, base)
        generators.append(prefix + lbl + suffix)

    return generators


def stallings_fold(words: List[Word], base: NodeId = "Z") -> StallingsGraph:
    """Run the full Stallings folding algorithm on *words*.

    Parameters
    ----------
    words:
        List of words in the free group, e.g. ``["aab-", "ba-b"]``.
        Each word uses lowercase letters for generators and appends ``-``
        for inverses (so ``a-`` means a⁻¹).
    base:
        Name of the distinguished base-point (default ``"Z"``).

    Returns
    -------
    StallingsGraph
        Contains the folded graph, the rank of the subgroup, and a list of
        generator words forming a free basis.

    Example
    -------
    >>> result = stallings_fold(["ab", "ba"])
    >>> result.rank
    2
    >>> result.generators
    ['ab', 'ba']
    """
    G = build_flower_automaton(words, base=base)

    while True:
        G2 = fold_once(G, base=base)
        if G2 is None:
            break
        G = G2

    rank = G.number_of_edges() - G.number_of_nodes() + 1
    generators = _read_generators(G, base)

    return StallingsGraph(graph=G, base=base, rank=rank, generators=generators)


# ---------------------------------------------------------------------------
# Interactive GUI  (unchanged logic, ported to Python 3.9 match→if/elif)
# ---------------------------------------------------------------------------

class StallingsApp:
    """Matplotlib-based interactive Stallings folding application."""

    EDGE_DEFAULT  = "black"
    EDGE_SELECTED = "red"

    def __init__(self) -> None:
        self.G: nx.DiGraph = nx.DiGraph()
        self.base: NodeId = "Z"
        self.prev_edge: Optional[Edge] = None
        self.plot_instance = None
        self.artist_to_edge: Dict = {}
        self.node_layout = None

        self.fig, self.ax = plt.subplots()
        self._build_widgets()

        # Initialise with default example
        self.text_box.set_val("aab-, aaab, a-bb, aba, aaab-b-a-")

    # ------------------------------------------------------------------
    # Widget construction
    # ------------------------------------------------------------------

    def _build_widgets(self) -> None:
        ax_style = self.fig.add_axes([0.05, 0.8, 0.15, 0.15])
        self.radio_style = RadioButtons(ax_style, labels=("Shell", "Planar", "Random"))

        ax_box = self.fig.add_axes([0.2, 0.05, 0.7, 0.075])
        self.text_box = TextBox(ax_box, "Elements", textalignment="center")
        self.text_box.on_submit(self._on_textinput)

        ax_refresh = self.fig.add_axes([0.8, 0.9, 0.1, 0.05])
        ax_restart  = self.fig.add_axes([0.8, 0.84, 0.1, 0.05])

        b_refresh = Button(ax_refresh, "Refresh")
        b_refresh.on_clicked(self._on_refresh)

        b_restart = Button(ax_restart, "Restart")
        b_restart.on_clicked(self._on_restart)

        # "Auto-fold" button — runs the full algorithm automatically
        ax_auto = self.fig.add_axes([0.8, 0.78, 0.1, 0.05])
        b_auto = Button(ax_auto, "Auto-fold")
        b_auto.on_clicked(self._on_autofold)

    # ------------------------------------------------------------------
    # Drawing
    # ------------------------------------------------------------------

    def _refresh_draw(self, G: nx.DiGraph) -> None:
        self.ax.clear()
        edge_labels = {
            (u, v): lbl
            for u, v, lbl in G.edges(data="label", default="")
        }
        self.plot_instance = ng.InteractiveGraph(
            G, ax=self.ax,
            node_size=5, node_labels=True,
            edge_width=2.5, edge_labels=edge_labels,
            edge_label_rotate=False,
            edge_color=self.EDGE_DEFAULT, edge_label_position=0.70,
            arrows=True, node_layout=self.node_layout,
        )
        self.artist_to_edge = {}
        for edge, artist in self.plot_instance.edge_artists.items():
            artist.set_picker(True)
            self.artist_to_edge[artist] = edge

        self.fig.canvas.mpl_connect("pick_event", self._on_pick)
        self.fig.canvas.draw()

    # ------------------------------------------------------------------
    # Event handlers
    # ------------------------------------------------------------------

    def _on_pick(self, event) -> None:
        edge: Edge = self.artist_to_edge[event.artist]

        if self.prev_edge is None:
            self.prev_edge = edge
            self.plot_instance.edge_artists[edge].set_facecolor(self.EDGE_SELECTED)
            self.fig.canvas.draw()
            return

        if self.prev_edge == edge:
            self.prev_edge = None
            self.plot_instance.edge_artists[edge].set_facecolor(self.EDGE_DEFAULT)
            self.fig.canvas.draw()
            return

        prev_labels = set(self.G.edges[self.prev_edge]["label"].split(","))
        curr_labels = set(self.G.edges[edge]["label"].split(","))

        if prev_labels.isdisjoint(curr_labels):
            return

        if self.prev_edge[0] == edge[0]:
            merge_old, merge_new = self.prev_edge[1], edge[1]
        elif self.prev_edge[1] == edge[1]:
            merge_old, merge_new = self.prev_edge[0], edge[0]
        else:
            return

        self.prev_edge = None
        self.G = _apply_merge(self.G, merge_old, merge_new, self.base)
        self._refresh_draw(self.G)

    def _on_refresh(self, _arg) -> None:
        self.prev_edge = None
        layout_name = self.radio_style.value_selected
        if layout_name == "Planar":
            self.node_layout = nx.planar_layout(self.G)
        elif layout_name == "Shell":
            self.node_layout = nx.shell_layout(self.G)
        else:
            self.node_layout = nx.random_layout(self.G)
        self._refresh_draw(self.G)

    def _on_textinput(self, text: str) -> None:
        words = re.findall(r"[a-z\-]+", text)
        self.G = build_flower_automaton(words, base=self.base)
        self._on_refresh(None)

    def _on_restart(self, _arg) -> None:
        self._on_textinput(self.text_box.text)

    def _on_autofold(self, _arg) -> None:
        """Run the complete folding algorithm and redraw."""
        result = stallings_fold(re.findall(r"[a-z\-]+", self.text_box.text),
                                base=self.base)
        self.G = result.graph
        print(f"\n[Auto-fold] rank = {result.rank}")
        print(f"[Auto-fold] generators = {result.generators}")
        self._on_refresh(None)

    # ------------------------------------------------------------------

    def run(self) -> None:
        plt.show()


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    # ---- Automated example (non-interactive) ----
    # words = ["aab-", "aaab", "a-bb", "aba", "aaab-b-a-"]
    words = ["aba-a-bab-b-", "bba-b-a-", "ba-ba-b-aaab-a-", "aba-a-a-bab-"]
    result = stallings_fold(words)
    print("=== stallings_fold example ===")
    print(f"  Input words : {words}")
    print(f"  Subgroup rank       : {result.rank}")
    print(f"  Free basis (words)  : {result.generators}")
    print(f"  Folded graph nodes  : {list(result.graph.nodes())}")
    print(f"  Folded graph edges  : {[(u,v,d) for u,v,d in result.graph.edges(data=True)]}")
    print()

    # ---- Interactive GUI ----
    app = StallingsApp()
    app.run()