"""Convert multilayer graph and planar graph."""
from typing import Tuple

import networkx as nx

from mgrid.multilayer import MultilayerGrid
from mgrid.planar import COLUMNS, COLUMNS_DI, PlanarGraph

COLUMNS_DI_ORIGINAL = ["source_original", "target_original"]


def planar2multilayer(g: PlanarGraph) -> MultilayerGrid:
    """Convert a planar graph to corresponding multilayer graph.

    Args:
        g: a planar graph to be converted.

    Returns:
        Resulted multilayer graph.
    """
    dg = nx.DiGraph(g)

    inter_edges = g.inter_nodes
    inter_edges["source"] = "default_"
    inter_edges["target"] = "default_"

    # Initiate dataframe **intra-edges** for edges in the planar edge.
    intra_edges = nx.to_pandas_edgelist(g)
    intra_edges[COLUMNS_DI_ORIGINAL[0]] = intra_edges[COLUMNS_DI[0]]
    intra_edges[COLUMNS_DI_ORIGINAL[1]] = intra_edges[COLUMNS_DI[1]]
    intra_edges.set_index(COLUMNS_DI_ORIGINAL, inplace=True)

    def update_intra_edges(
        edges_original: Tuple[str, str], edges: Tuple[str, str]
    ):
        intra_edges.loc[edges_original, COLUMNS_DI] = edges

    for node, row in g.inter_nodes.iterrows():
        in_edges = list(dg.in_edges(nbunch=node, data=True))
        for u, _, data in in_edges:
            edge_new = (u, str(node) + f'_layer{data["layer"]}')
            dg.add_edge(*edge_new, **data)
            update_intra_edges((u, node), edge_new)

        out_edges = list(dg.out_edges(nbunch=node, data=True))
        for _, v, data in out_edges:
            edge_new = (str(node) + f'_layer{data["layer"]}', v)
            dg.add_edge(*edge_new, **data)
            update_intra_edges((node, v), edge_new)

        source = (str(node) + f"_layer{row[COLUMNS[0]]}",)
        target = (str(node) + f"_layer{row[COLUMNS[1]]}",)
        dg.add_edge(source, target)
        inter_edges.loc[node, COLUMNS_DI[0]] = source
        inter_edges.loc[node, COLUMNS_DI[1]] = target

        dg.remove_node(node)

    res = MultilayerGrid(dg)
    res.intra_edges = intra_edges
    res.inter_edges = inter_edges
    return res
