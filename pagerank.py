import numpy as np
import matplotlib.pyplot as plt
import json
import networkx as nx
import fluke_detection


with open("tennis.json", "r") as f:
    data = json.load(f)


def binary_edge_initialization(g, game_data):
    # in: graph, out: none, but an edge is created in the graph
    # more points scored means an edge with a weight of 1.
    # '''
    g.add_edge(
        game_data[game_data["loser"]],
        game_data[game_data["winner"]],
        raw_scores=game_data["score"],
        weight=1
    )


def reduce_low_match_player_importance(g: nx.DiGraph):
    # in: graph, out: graph
    for node in g.nodes:
        num_matches = len(g.out_edges(node)) + len(g.in_edges(node))
        if num_matches == 1:
            g.nodes[node]['transfer_multiplier'] = 0.5
        if num_matches == 2:
            g.nodes[node]['transfer_multiplier'] = 0.75
        # for digraphs you have to iterate through both for some reason



def populate_graph(data, g, edge_initialization=binary_edge_initialization):
    # in: data, out: graph
    for game in data["games"]:
        # g.add_node(data[game]["player1"], score=0)
        # g.add_node(data[game]["player2"], score=0)
        # initialize edge weights
        edge_initialization(g, game)

    # set transfer multiplier to 1
    for node in g.nodes:
        g.nodes[node]['transfer_multiplier'] = 1


def score_initialization(g):
    # in: graph, out: graph
    # initialize scores with 1/N each.
    N = g.number_of_nodes()
    for node in g.nodes:
        g.nodes[node]['score'] = 1 / N


def simple_pagerank_iteration(g, p=0.85):
    # in: graph, out: graph
    # traditional pagerank algorithm that consists of 3 terms:
    # 1. score gained from other nodes due to victories
    # 2. p/N, in this context the baseline score
    # 3. additional baseline score, redistributed from sinks (players who haven't lost)

    N = g.number_of_nodes()
    baseline_score = (1 - p) / N

    # set all new_scores to 0
    for node in g.nodes:
        g.nodes[node]['new_score'] = 0

    for node in g.nodes:
        num_successors = len(g.out_edges(node))
        #sum weights
        sum_outbound_weights = 0
        for edge in g.out_edges(node):
            sum_outbound_weights += g[edge[0]][edge[1]]['weight']
        current_score = g.nodes[node]['score']

        if num_successors == 0 or sum_outbound_weights == 0:  # dangling node, redistribute score to all players
            baseline_score += p * (current_score / N)
        else:

            for successor in g.successors(node):  # transfer score to successors
                # add score to successor nodes
                successor_gain = g.nodes[node]['transfer_multiplier'] * p * current_score * \
                                 (g[node][successor]['weight'] / sum_outbound_weights)
                g.nodes[successor]['new_score'] += successor_gain

    for node in g.nodes:  # add baseline score + assign new_score to scores
        g.nodes[node]['score'] = g.nodes[node]['new_score'] + baseline_score


g = nx.DiGraph()
populate_graph(data, g)
score_initialization(g)
# reduce_low_match_player_importance(g)

iters = 100
for i in range(iters):
    simple_pagerank_iteration(g, p=0.50)

# fluke detection
fluke_detection.detect_and_adjust_flukes(g)

# recompute
for i in range(iters):
    simple_pagerank_iteration(g, p=0.50)

spring = nx.spring_layout(g, k=1.2)
shell = nx.shell_layout(g)
scores = nx.get_node_attributes(g, 'score')
scores = [scores[name] * 10000 for name in scores]
edge_labels = nx.get_edge_attributes(g,'weight')


options = {
    "pos": shell,
    "with_labels": True,
    "node_size": scores,
    "edge_color": "#AAAAAA",
    "node_color": "#D2EAFF"
}
nx.draw_networkx_edge_labels(g, pos=options["pos"], edge_labels=edge_labels)
d = nx.draw(g, **options)
# show top 10
for i in sorted(scores, reverse=True):
    print(i)
for i in sorted(g.nodes, key=lambda node: g.nodes[node]['score'], reverse=True):
    print(i)
plt.show()

# save graph
#nx.write_gpickle(g, "binary_pagerank_050.gpickle")

