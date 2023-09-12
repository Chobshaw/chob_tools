from collections import defaultdict, deque
from collections.abc import Mapping, Iterable, Iterator
from functools import cache, reduce
import time
from typing import Any, Literal, Optional, TypeVar, get_args

NT = TypeVar('NT')

GraphType = Literal['edges', 'dependencies']
NodesOrGroups = Literal['nodes', 'groups']


class CycleError(ValueError):
    def __init__(self, cycle: Iterable[NT]) -> None:
        self.cycle = cycle
        super().__init__(f'Cycle detected in graph: {" -> ".join(cycle)}.')


def _get_cycle(
    graph: Mapping[NT, Iterable[NT]], node: Optional[NT] = None
) -> list[NT]:
    @cache
    def dfs(curr: NT, level: int) -> Optional[list[NT]]:
        if curr == node and level != 0:
            return [curr]
        neighbours = graph[curr]
        if len(neighbours) == 0:
            return
        for neighbour in graph[curr]:
            path = dfs(neighbour, level + 1)
            if path is not None:
                return [curr] + path

    if node:
        return dfs(node, 0)
    for node in graph:
        path = dfs(node, 0)
        if path:
            return path


def _get_edges_from_dependencies(
    graph: Mapping[NT, Iterable[NT]]
) -> tuple[dict[NT, list[NT]], defaultdict[NT, int]]:
    new_graph = {}
    indegree = defaultdict(int)
    for node, dependencies in graph.items():
        if node not in new_graph:
            new_graph[node] = []
        for dependency in dependencies:
            if dependency == node:
                continue
            if dependency not in new_graph:
                new_graph[dependency] = []
            new_graph[dependency].append(node)
            indegree[node] += 1
    return new_graph, indegree


def _prepare_graph(
    graph: Mapping[NT, Iterable[NT]]
) -> tuple[dict[NT, list[NT]], defaultdict[NT, int]]:
    new_graph = {}
    indegree = defaultdict(int)
    for node, neighbours in graph.items():
        new_graph[node] = []
        for neighbour in neighbours:
            if neighbour == node:
                continue
            if neighbour not in graph:
                new_graph[neighbour] = []
            new_graph[node].append(neighbour)
            indegree[neighbour] += 1
    return new_graph, indegree


def _check_cycle(graph: dict[NT, list[NT]], visited: set[NT]) -> None:
    if len(visited) < len(graph):
        cycle = _get_cycle(
            {
                node: neighbours
                for node, neighbours in graph.items()
                if node not in visited
            }
        )
        raise CycleError(cycle)


def _node_generator(
    graph: dict[NT, list[NT]], indegree: defaultdict[NT, int], queue: deque[NT]
) -> Iterator[NT]:
    visited = set()
    while queue:
        node = queue.popleft()
        visited.add(node)
        yield node
        for neighbour in graph[node]:
            indegree[neighbour] -= 1
            if indegree[neighbour] == 0:
                queue.append(neighbour)
    _check_cycle(graph, visited)


def _group_generator(
    graph: dict[NT, list[NT]],
    indegree: defaultdict[NT, int],
    queue: deque[NT],
    *,
    sort_groups: bool = False,
) -> Iterator[list[NT]]:
    visited = set()
    batch, next_degree = [], []
    while queue:
        node = queue.popleft()
        visited.add(node)
        batch.append(node)
        for neighbour in graph[node]:
            indegree[neighbour] -= 1
            if indegree[neighbour] == 0:
                next_degree.append(neighbour)
        if not queue:
            yield sorted(batch) if sort_groups else batch
            queue.extend(next_degree)
            batch, next_degree = [], []
    _check_cycle(graph, visited)


def topological_sort_generator(
    graph: Mapping[NT, Iterable[NT]],
    /,
    return_type: NodesOrGroups = 'nodes',
    *,
    sort_groups: bool = False,
    graph_type: GraphType = 'edges',
) -> Iterator[NT] | Iterator[list[NT]]:
    new_graph, indegree = (
        _get_edges_from_dependencies(graph)
        if graph_type == 'dependencies'
        else _prepare_graph(graph)
    )
    queue = deque()
    for node in new_graph:
        if indegree[node] == 0:
            queue.append(node)
    if return_type == 'nodes':
        if sort_groups:
            for group in _group_generator(
                new_graph, indegree, queue, sort_groups=sort_groups
            ):
                yield from group
        else:
            yield from _node_generator(new_graph, indegree, queue)
    else:
        yield from _group_generator(
            new_graph, indegree, queue, sort_groups=sort_groups
        )


def _bfs_topological_sort(
    graph: Mapping[NT, Iterable[NT]],
    /,
    return_type: NodesOrGroups = 'nodes',
    *,
    sort_groups: bool = False,
    graph_type: GraphType = 'edges',
) -> list[NT] | list[list[NT]]:
    return list(
        topological_sort_generator(
            graph, return_type, sort_groups=sort_groups, graph_type=graph_type
        )
    )


def _dfs_topological_sort(
    graph: Mapping[NT, Iterable[NT]],
    /,
    *,
    graph_type: GraphType = 'edges',
) -> list[NT]:
    new_graph, _ = (
        _get_edges_from_dependencies(graph)
        if graph_type == 'dependencies'
        else _prepare_graph(graph)
    )

    sorted_list = []
    visited = set()
    currently_visiting = set()

    def dfs(node: NT):
        if node in currently_visiting:
            cycle = _get_cycle(graph, node)
            raise CycleError(cycle)
        currently_visiting.add(node)
        for neighbour in new_graph[node]:
            if neighbour not in visited:
                dfs(neighbour)
        currently_visiting.remove(node)
        visited.add(node)
        sorted_list.append(node)

    for node in new_graph:
        if node not in visited:
            dfs(node)

    return sorted_list[::-1]


def _validate_return_type(return_type: Any) -> None:
    if return_type not in get_args(NodesOrGroups):
        raise ValueError(
            f'Return type "{return_type}", invalid. '
            'Return type must be "nodes" or "groups".'
        )


def _validate_graph_type(graph_type: Any) -> None:
    if graph_type not in get_args(GraphType):
        raise ValueError(
            f'Graph type "{graph_type}", invalid. '
            'Graph type must be "edges" or "dependencies".'
        )


def topological_sort(
    graph: Mapping[NT, Iterable[NT]],
    /,
    method: Literal['bfs', 'dfs'] = 'bfs',
    return_type: NodesOrGroups = 'nodes',
    *,
    sort_groups: bool = False,
    graph_type: GraphType = 'edges',
) -> list[NT] | list[list[NT]]:
    _validate_return_type(return_type)
    _validate_graph_type(graph_type)
    if method == 'bfs':
        return _bfs_topological_sort(
            graph, return_type, sort_groups=sort_groups, graph_type=graph_type
        )
    if method == 'dfs':
        if return_type != 'nodes':
            raise ValueError(
                'If sort method is depth-first search, '
                'return type must be "nodes".'
            )
        if sort_groups:
            raise ValueError(
                'If sort method is depth-first search, '
                'cannot sort indegree groups.'
            )
        return _dfs_topological_sort(graph, graph_type=graph_type)
    raise ValueError(
        f'Method "{method}", invalid. Method must be "bfs" or "dfs".'
    )


if __name__ == '__main__':
    test_graph = {'D': ['B', 'C'], 'C': ['E', 'A'], 'B': ['A']}
    test_graph_inv = {'A': ['B', 'C'], 'B': ['D'], 'C': ['D'], 'E': ['C']}
    test_graph_cycle = {
        'D': ['B'],
        'C': ['A', 'B', 'D'],
        'B': ['A'],
        'A': ['D'],
    }
    test_graph_large = {
        'A': ['A'],
        'B': ['A', 'B'],
        'C': ['A', 'C'],
        'D': ['B', 'D'],
        'F': ['C', 'F'],
        'G': ['D', 'E'],
        'H': ['F', 'G'],
        'I': ['G', 'I'],
        'J': [],
        'K': ['H', 'I', 'K'],
        'L': ['J'],
        'N': ['K'],
        'O': ['L', 'M'],
        'P': [],
        'Q': ['O', 'P'],
        'R': ['Q'],
        'S': ['R'],
        'U': ['T'],
        'V': ['U'],
        'W': ['V'],
        'Y': ['X'],
        'Z': ['Y'],
    }
    t1 = time.time()
    for _ in range(1):
        print(topological_sort(test_graph_cycle, 'dfs'))
    print(time.time() - t1)
