from __future__ import annotations

from collections.abc import MutableMapping, Iterator
from typing import Optional, TypeVar


KT = TypeVar('KT')
VT = TypeVar('VT')


class InvertibleDict(MutableMapping[KT, VT]):
    __slots__ = ('_forward', '_backward')

    def __init__(
        self,
        forward: Optional[dict[KT, VT]] = None,
        /,
        *,
        _backward: Optional[dict[KT, VT]] = None,
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

    def __getitem__(self, key) -> VT:
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

    def __iter__(self) -> Iterator[KT]:
        return iter(self._forward)

    def __len__(self) -> int:
        return len(self._forward)

    @property
    def inv(self) -> InvertibleDict[VT, KT]:
        return self.__class__(self._backward, _backward=self._forward)

    def _check_non_invertible(self) -> None:
        seen = set()
        for val in self._forward.values():
            if val in seen:
                raise ValueError(
                    'Dictionary values must be unique to maintain invertability'
                )
            seen.add(val)
