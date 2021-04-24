import numpy as np
import matplotlib.pyplot as plt
import json
import networkx as nx
import math

# g = nx.read_gpickle("binary_pagerank_050.gpickle")
# g = nx.DiGraph()

fluke_weight_function = lambda fp: math.sqrt(1 / (1 + fp))
# fluke_weight_function = lambda fp: 0.01

# given a fluke potential, how much to decrease weight by

# loop through players, and see if they have fluke games
# algorithm 1
def detect_and_adjust_flukes(g:nx.MultiDiGraph, w_fp=fluke_weight_function):
    for node in g.nodes:
        num_wins = len(g.in_edges(node))
        num_losses = len(g.out_edges(node))

        win_fluke_potentials = [0] * num_wins
        loss_fluke_potentials = [0] * num_losses

        # sorting likely more efficient
        # calc losses that are probably flukes
        for oi, oe in enumerate(g.out_edges(node)):
            lost_to = oe[1]
            for _, ie in enumerate(g.in_edges(node)):
                won_against = ie[0]
                if g.nodes[won_against]["score"] > g.nodes[lost_to]["score"]:
                    loss_fluke_potentials[oi] += 1
        # calc wins that are probably flukes
        for ii, ie in enumerate(g.in_edges(node)):
            won_against = ie[0]
            for _, oe in enumerate(g.out_edges(node)):
                lost_to = oe[1]
                if g.nodes[lost_to]["score"] < g.nodes[won_against]["score"]:
                    win_fluke_potentials[ii] += 1
        print(node, win_fluke_potentials, loss_fluke_potentials)
        max_fp = max(win_fluke_potentials + loss_fluke_potentials)
        # iterate through edges again, and set fluke multiplier accordingly

        if max_fp != 0:
            for ii, ie in enumerate(g.in_edges(node, data=True)):  # fluke wins
                if win_fluke_potentials[ii] == max_fp:
                    ie[2]["fluke_multiplier"] *= w_fp(max_fp)
            for oi, oe in enumerate(g.out_edges(node, data=True)):  # fluke losses
                if loss_fluke_potentials[oi] == max_fp:
                    oe[2]['fluke_multiplier'] *= w_fp(max_fp)


'''
spring = nx.spring_layout(g, k=1.2)
shell = nx.shell_layout(g)
scores = nx.get_node_attributes(g, 'score')
scores = [scores[name] * 10000 for name in scores]
edge_labels = nx.get_edge_attributes(g, 'weight')
print(edge_labels)
options = {
    "pos": shell,
    "with_labels": True,
    "node_size": scores,
    "edge_color": "#AAAAAA",
    "node_color": "#D2EAFF"
}

nx.draw_networkx_edge_labels(g, pos=options["pos"], edge_labels=edge_labels)
d = nx.draw(g, **options)

plt.show()
'''
