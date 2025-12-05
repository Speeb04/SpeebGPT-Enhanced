from __future__ import annotations

from typing import final


@final
class Singleton(type):
    """
    Singleton pattern implementation.
    This allows classes to be instantiated only once, especially when dealing
    with API requests
    """
    _instance = None

    def __call__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instance
