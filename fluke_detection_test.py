import numpy as np
import matplotlib.pyplot as plt
import json
import networkx as nx


g = nx.read_gpickle("binary_pagerank_085.gpickle")
# g = nx.DiGraph()

#loop through players, and see if they have fluke games
for node in g.nodes:
    print(node)
    num_wins = len(g.in_edges(node))
    num_losses = len(g.out_edges(node))


    win_fluke_potentials = [0] * num_wins
    loss_fluke_potentials = [0] * num_losses

    # sorting likely more efficient
    for wi, win in enumerate(g.predecessors(node)):
        for li, loss in enumerate(g.successors(node)):
            if g.nodes[loss]["score"] < g.nodes[win]["score"]:
                win_fluke_potentials[wi] += 1

    for li, loss in enumerate(g.successors(node)):
        for wi, win in enumerate(g.predecessors(node)):
            if g.nodes[win]["score"] > g.nodes[loss]["score"]:
                loss_fluke_potentials[li] += 1

    print(win_fluke_potentials)
    print(loss_fluke_potentials)

    continue


'''
spring = nx.spring_layout(g, k=1.2)
shell = nx.shell_layout(g)
scores = nx.get_node_attributes(g, 'score')
scores = [scores[name] * 10000 for name in scores]
options = {
    "pos": shell,
    "with_labels": True,
    "node_size": scores,
    "edge_color": "#AAAAAA",
    "node_color": "#D2EAFF"
}

d = nx.draw(g, **options)

plt.show()
'''