import numpy as np
import matplotlib.pyplot as plt
import json
import networkx as nx
import fluke_detection


# in this code, game is synonymous with match.


def weighted_edge_initialization(g, game_data):
    scores = game_data["score"]
    total_score = sum(sum(scores, []))  # sum of all in the 2d array
    if game_data["winner"] == "player1":
        winner_score = [game_set[0] for game_set in scores]
    else:
        winner_score = [game_set[1] for game_set in scores]
    winner_score = sum(winner_score)

    # apply laplace's correction
    weight = (winner_score + 1) / (total_score + 2)

    if weight != 0:
        g.add_edge(  # loser to winner, with the weight
            game_data[game_data["loser"]],
            game_data[game_data["winner"]],
            raw_scores=game_data["score"],
            weight=weight,
            fluke_multiplier=1
        )


def compute_sum_of_outgoing_edge_weights(g):  # take fluke multipliers into account
    for node in g.nodes:
        sum_weights = 0
        for oe in g.out_edges(node, data=True):
            sum_weights += oe[2]['weight'] * oe[2]['fluke_multiplier']
        g.nodes[node]['sum_outgoing_weights'] = sum_weights


def compute_sum_of_ingoing_edge_weights(g):  # take fluke multipliers into account
    for node in g.nodes:
        sum_weights = 0
        for ie in g.in_edges(node, data=True):
            sum_weights += ie[2]['weight'] * ie[2]['fluke_multiplier']
        g.nodes[node]['sum_ingoing_weights'] = sum_weights


def populate_graph(data, g, edge_initialization=weighted_edge_initialization):
    # in: data, out: graph
    for game in data["games"]:
        # g.add_node(data[game]["player1"], score=0)
        # g.add_node(data[game]["player2"], score=0)
        # initialize edge weights
        edge_initialization(g, game)


def score_initialization(g):
    # in: graph, out: graph
    # initialize scores with 1/N each.
    N = g.number_of_nodes()
    for node in g.nodes:
        g.nodes[node]['good_score'] = 1 / N
        g.nodes[node]['bad_score'] = 1 / N
        g.nodes[node]['new_good_score'] = 0  # used in iterating
        g.nodes[node]['new_bad_score'] = 0  # used in iterating


def bipagerank_iteration(g: nx.MultiDiGraph, p=0.5):
    # this term technically isn't needed as they cancel each other out
    baseline_good_score = (1 - p) / g.number_of_nodes()
    baseline_bad_score = (1 - p) / g.number_of_nodes()
    # set new_good/bad_score to 0
    for node in g.nodes:
        g.nodes[node]['new_good_score'] = 0
        g.nodes[node]['new_bad_score'] = 0

    for node in g.nodes:
        # first, push good score to players the node lost against (normal pagerank)
        current_good_score = g.nodes[node]['good_score']
        current_bad_score = g.nodes[node]['bad_score']
        if len(g.out_edges(node)) == 0: # dangling node, but this shouldn't happen
            baseline_good_score += p * (current_good_score / g.number_of_nodes())
            # raise Exception("the organization has breached our defenses! prepare our lab's secret weapon for use. "
            #               "El. Psy. Congroo.")
        else:
            for oe in g.out_edges(node, data=True):
                other = oe[1]
                fluke_multiplier = oe[2]['fluke_multiplier']
                edge_weight = oe[2]['weight']

                if len(g.out_edges(node)) == 1: # only 1 out-edge, special case
                    g.nodes[other]['new_good_score'] += p * edge_weight * fluke_multiplier * current_good_score
                    baseline_good_score += (p * (1 - (fluke_multiplier * edge_weight)) * current_good_score) \
                                           / g.number_of_nodes()
                else:
                # if fluke_multiplier != 1 and len(g.out_edges(node)) == 1:  # only 1 out-edge and it's a fluke (special case)
                    # transfer fm to the winner, redistribute rest to everyone
                    # g.nodes[other]['new_good_score'] += fluke_multiplier * current_good_score
                    # baseline_good_score += (1 - fluke_multiplier) * current_good_score
                    g.nodes[other]['new_good_score'] += (p * edge_weight * fluke_multiplier * current_good_score) \
                                                        / g.nodes[node]['sum_outgoing_weights']

        # then, push bad score to players the node won against
        if len(g.in_edges(node)) == 0: # dangling node
            baseline_bad_score += p * (current_bad_score / g.number_of_nodes())
        else:
            for ie in g.in_edges(node, data=True):
                other = ie[0] #was ie[1]
                fluke_multiplier = ie[2]['fluke_multiplier']
                edge_weight = ie[2]['weight']

                if len(g.in_edges(node)) == 1: # only 1 in-edge, special case
                    g.nodes[other]['new_bad_score'] += p * edge_weight * fluke_multiplier * current_bad_score
                    baseline_bad_score += (p * (1 - (fluke_multiplier * edge_weight)) * current_bad_score) \
                                          / g.number_of_nodes()
                else:
                # if fluke_multiplier != 1 and len(g.in_edges(node)) == 1:  # only 1 ingoing edge and it's a fluke (special case)
                    # transfer fm to the loser, redistribute rest to everyone
                    # g.nodes[other]['new_bad_score'] += fluke_multiplier * current_bad_score
                    # baseline_bad_score += (1 - fluke_multiplier) * current_bad_score
                # otherwise, do normal pushing of bad scores

                    g.nodes[other]['new_bad_score'] += (p * edge_weight * fluke_multiplier * current_bad_score) \
                                                       / g.nodes[node]['sum_ingoing_weights']

    for node in g.nodes: # add baseline to every new score, assign every new score to the player's current score
        g.nodes[node]['good_score'] = g.nodes[node]['new_good_score'] + baseline_good_score
        g.nodes[node]['bad_score'] = g.nodes[node]['new_bad_score'] + baseline_bad_score


def compute_final_score(g: nx.MultiDiGraph):
    for node in g.nodes:
        g.nodes[node]['score'] = g.nodes[node]['good_score'] - g.nodes[node]['bad_score']

with open("tennis.json", "r") as f:
    data = json.load(f)

g = nx.MultiDiGraph()
populate_graph(data, g)
compute_sum_of_outgoing_edge_weights(g)
compute_sum_of_ingoing_edge_weights(g)
score_initialization(g)


iters = 100
for _ in range(iters):
    bipagerank_iteration(g, p=0.5)
    compute_final_score(g)

fluke_detection.detect_and_adjust_flukes(g)

for _ in range(iters):
    # fluke_detection.detect_and_adjust_flukes(g)
    compute_sum_of_outgoing_edge_weights(g)
    compute_sum_of_ingoing_edge_weights(g)
    bipagerank_iteration(g, p=0.5)
    compute_final_score(g)




spring = nx.spring_layout(g, k=1.2)
shell = nx.shell_layout(g)
scores = nx.get_node_attributes(g, 'score')
scores = [(scores[name] - min(scores.values())) * 10000 for name in scores]
edge_labels = nx.get_edge_attributes(g,'weight')


options = {
    "pos": shell,
    "with_labels": True,
    "node_size": scores,
    "edge_color": "#AAAAAA",
    "node_color": "#D2EAFF"
}

# nx.draw_networkx_edge_labels(g, pos=options["pos"], edge_labels=edge_labels)
d = nx.draw(g, **options)
# show top 10
for i in sorted(scores, reverse=True):
    print(i)
for i in sorted(g.nodes, key=lambda node: g.nodes[node]['score'], reverse=True):
    print(i)
plt.show()

