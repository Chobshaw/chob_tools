from __future__ import annotations

from collections import defaultdict
from collections.abc import MutableMapping, Mapping, Iterator
from typing import cast


class InvertibleDict[K, V](MutableMapping[K, V]):
    __slots__ = ('_forward', '_backward')

    def __init__(
        self,
        forward: Optional[dict[K, V]] = None,
        /,
        *,
        _backward: Optional[dict[K, V]] = None,
    ) -> None:
        if forward is None:
            self._forward = {}
            self._backward = {}
        elif _backward is not None:
            self._forward = forward
            self._backward = _backward
        else:
            self._forward = forward
            self._backward = {
                value: key for key, value in self._forward.items()
            }
            self._check_non_invertible()

    def __getitem__(self, key) -> V:
        return self._forward[key]

    def __setitem__(self, key, value) -> None:
        # Ensure the value being assigned is unique to maintain invertibility
        if value in self._backward:
            raise ValueError('Value must be unique to maintain invertibility.')

        # If key is present in the forward dictionary, delete it in the backward dictionary
        if key in self._forward:
            del self._backward[self._forward[key]]

        self._forward[key] = value
        self._backward[value] = key

    def __delitem__(self, key) -> None:
        value = self._forward[key]
        del self._forward[key]
        del self._backward[value]

    def __iter__(self) -> Iterator[K]:
        return iter(self._forward)

    def __len__(self) -> int:
        return len(self._forward)

    @property
    def inv(self) -> InvertibleDict[V, K]:
        return self.__class__(self._backward, _backward=self._forward)

    def _check_non_invertible(self) -> None:
        seen = set()
        for val in self._forward.values():
            if val in seen:
                raise ValueError(
                    'Dictionary values must be unique '
                    'to maintain invertability.'
                )
            seen.add(val)


class InvertibleSetMapping[K, V: set](Mapping[K, V]):
    __slots__ = ("_mapping", "_inverse")

    def __init__(
        self, mapping: Mapping[K, V], /, *, _inverse: Mapping[K, V] | None = None
    ) -> None:
        self._mapping = mapping
        self._inverse = self._get_inverse(mapping) if _inverse is None else _inverse

    def __getitem__(self, key: K) -> V:
        return self._mapping[key]

    def __iter__(self) -> Iterator[K]:
        return iter(self._mapping)

    def __len__(self) -> int:
        return len(self._mapping)

    @property
    def inv(self) -> InvertibleSetMapping[K, V]:
        return self.__class__(self._inverse, _inverse=self._mapping)

    @staticmethod
    def _get_inverse(mapping: Mapping[K, V]) -> defaultdict[K, V]:
        inverse: defaultdict[K, V] = defaultdict(cast(Callable[[], V], set))
        for key, values in mapping.items():
            if not isinstance(values, set):
                raise TypeError(f"Values must be of type set, got {type(values)}")
            for value in values:
                inverse[value].add(key)
        return inverse
