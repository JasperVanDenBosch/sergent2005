from __future__ import annotations
from dataclasses import dataclass


@dataclass(frozen=True)
class Triggers:
    T1: int = 10
    T2_present: int = 11
    T2_absent: int = 12
    task1: int = 13
    task2: int = 14
    start_trial: int = 15