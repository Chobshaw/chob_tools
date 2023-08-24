import pytest

from chob_tools.algorithms.topological_sort import (
    CycleError,
    _get_cycle,
    topological_sort,
)

TEST_GRAPH = {'D': ['B', 'C'], 'C': ['A', 'C', 'E'], 'B': ['A']}
SORTED_TEST_GRAPH_GROUPS = [['D'], ['B', 'C'], ['A', 'E']]
SORTED_TEST_GRAPHS = [
    ['D', 'B', 'C', 'A', 'E'],
    ['D', 'B', 'C', 'E', 'A'],
    ['D', 'C', 'B', 'A', 'E'],
    ['D', 'C', 'B', 'E', 'A'],
    ['D', 'C', 'E', 'B', 'A'],
]
INV_TEST_GRAPH = {'A': ['B', 'C'], 'B': ['B', 'D'], 'C': ['D'], 'E': ['C']}
SORTED_INV_TEST_GRAPH_GROUPS = list(reversed(SORTED_TEST_GRAPH_GROUPS))
SORTED_INV_TEST_GRAPHS = [list(reversed(graph)) for graph in SORTED_TEST_GRAPHS]


def test_topological_sort():
    # Test breadth-first search method
    assert topological_sort(TEST_GRAPH, 'bfs') in SORTED_TEST_GRAPHS
    assert topological_sort(INV_TEST_GRAPH, 'bfs') in SORTED_INV_TEST_GRAPHS
    assert (
        topological_sort(TEST_GRAPH, 'bfs', graph_type='dependencies')
        in SORTED_INV_TEST_GRAPHS
    )
    assert (
        topological_sort(INV_TEST_GRAPH, 'bfs', graph_type='dependencies')
        in SORTED_TEST_GRAPHS
    )

    # Test depth-first search method
    assert topological_sort(TEST_GRAPH, 'dfs') in SORTED_TEST_GRAPHS
    assert topological_sort(INV_TEST_GRAPH, 'dfs') in SORTED_INV_TEST_GRAPHS
    assert (
        topological_sort(TEST_GRAPH, 'dfs', graph_type='dependencies')
        in SORTED_INV_TEST_GRAPHS
    )
    assert (
        topological_sort(INV_TEST_GRAPH, 'dfs', graph_type='dependencies')
        in SORTED_TEST_GRAPHS
    )


def test_group_return_type():
    def sort_elems(groups: list[list]) -> list[list]:
        return [sorted(group) for group in groups]

    assert (
        sort_elems(topological_sort(TEST_GRAPH, 'bfs', 'groups'))
        == SORTED_TEST_GRAPH_GROUPS
    )
    assert (
        sort_elems(topological_sort(INV_TEST_GRAPH, 'bfs', 'groups'))
        == SORTED_INV_TEST_GRAPH_GROUPS
    )
    assert (
        sort_elems(
            topological_sort(
                TEST_GRAPH, 'bfs', 'groups', graph_type='dependencies'
            )
        )
        == SORTED_INV_TEST_GRAPH_GROUPS
    )
    assert (
        sort_elems(
            topological_sort(
                INV_TEST_GRAPH, 'bfs', 'groups', graph_type='dependencies'
            )
        )
        == SORTED_TEST_GRAPH_GROUPS
    )
    with pytest.raises(ValueError):
        topological_sort(TEST_GRAPH, 'dfs', 'groups')


def test_sort_groups():
    assert (
        topological_sort(TEST_GRAPH, 'bfs', 'nodes', sort_groups=True)
        == SORTED_TEST_GRAPHS[0]
    )
    assert (
        topological_sort(INV_TEST_GRAPH, 'bfs', 'nodes', sort_groups=True)
        == SORTED_INV_TEST_GRAPHS[-2]
    )
    assert (
        topological_sort(TEST_GRAPH, 'bfs', 'groups', sort_groups=True)
        == SORTED_TEST_GRAPH_GROUPS
    )
    assert (
        topological_sort(INV_TEST_GRAPH, 'bfs', 'groups', sort_groups=True)
        == SORTED_INV_TEST_GRAPH_GROUPS
    )
    with pytest.raises(ValueError):
        topological_sort(TEST_GRAPH, 'dfs', sort_groups=True)


def test_cycle_error():
    CYCLE_TEST_GRAPH = {
        'G': [],
        'F': [],
        'D': ['B', 'C'],
        'C': ['E', 'A'],
        'B': ['A', 'F'],
        'A': ['D'],
    }
    # assert _get_cycle(CYCLE_TEST_GRAPH, 'D') == ['D', 'B', 'A', 'D']
    with pytest.raises(CycleError):
        topological_sort(CYCLE_TEST_GRAPH)
    with pytest.raises(CycleError):
        topological_sort(CYCLE_TEST_GRAPH, 'dfs')


def test_invalid_parameters():
    with pytest.raises(ValueError):
        topological_sort(TEST_GRAPH, method='cfs')
    with pytest.raises(ValueError):
        topological_sort(TEST_GRAPH, return_type='bananas')
    with pytest.raises(ValueError):
        topological_sort(TEST_GRAPH, graph_type='graph')
