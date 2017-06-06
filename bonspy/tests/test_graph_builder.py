from unittest.mock import Mock
from random import random
from bonspy.graph_builder import GraphBuilder, ConstantBidder, EstimatorBidder


def test_graph_builder_small(small_data_features_and_file):
    features, path = small_data_features_and_file
    builder = GraphBuilder(path, features, lazy_formatters=(('os', str), ('city', str)))
    graph = builder.get_graph()
    leaves = [n for n in graph.node if graph.out_degree(n) == 0]
    normal_leaves = [n for n in leaves if graph.node[n].get('is_leaf')]
    default_leaves = [n for n in leaves if graph.node[n].get('is_default_leaf')]

    assert len(normal_leaves) + len(default_leaves) == len(leaves)
    assert len(normal_leaves) == 6
    assert len(default_leaves) == 4
    assert len(graph.node) == len(leaves) + 4


def test_graph_builder_lazy_formatters(small_data_features_and_file_numeric):
    features, path = small_data_features_and_file_numeric
    builder = GraphBuilder(path, features, lazy_formatters=(('city', str), ('user_day', int)))
    graph = builder.get_graph()

    for node in graph.node:
        state = graph.node[node]['state']
        for feature, feature_value in state.items():
            assert isinstance(feature_value, builder.lazy_formatters[feature]) or feature_value is None


def test_graph_builder(data_features_and_file):
    features, path = data_features_and_file
    builder = GraphBuilder(path, features)
    graph = builder.get_graph()
    leaves = [n for n in graph.node if graph.out_degree(n) == 0]

    assert all([graph.node[n].get('is_leaf', graph.node[n].get('is_default_leaf', False)) for n in leaves])


def test_constant_bidder(data_features_and_file):
    features, path = data_features_and_file
    builder = GraphBuilder(path, features)
    graph = builder.get_graph()

    bidder = ConstantBidder(bid=1.)
    graph = bidder.compute_bids(graph)
    leaves = [n for n in graph.node if graph.out_degree(n) == 0]

    assert all([graph.node[n]['output'] == 1. for n in leaves])


def test_estimator_bidder(data_features_and_file):
    features, path = data_features_and_file
    builder = GraphBuilder(path, features)
    graph = builder.get_graph()

    rate_estimator = Mock()
    rate_estimator.dict_vectorizer = lambda x, **kwargs: x
    rate_estimator.predict = lambda x: 0.5 * (1 + random())

    bidder = EstimatorBidder(base_bid=5., estimators=(rate_estimator, ))
    graph = bidder.compute_bids(graph)
    leaves = [n for n in graph.node if graph.out_degree(n) == 0]

    assert all([2.5 <= graph.node[n]['output'] <= 5. for n in leaves])
