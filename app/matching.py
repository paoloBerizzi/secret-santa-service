import random
from dataclasses import dataclass
from time import monotonic
from typing import Literal

from app.i18n import translate

MAX_PARTICIPANTS = 32


@dataclass(frozen=True)
class MatchResult:
    status: Literal['feasible', 'infeasible', 'indeterminate']
    messages: tuple[str, ...] = ()
    assignments: dict[int, int] | None = None


def solve(
    roster: dict[int, str],
    groups: dict[str, set[int]],
    exclusions: set[tuple[int, int]],
    *,
    no_reciprocal: bool = False,
    rng: random.Random | None = None,
    node_limit: int = 50_000,
    seconds: float = 0.5,
    locale: str = 'en',
) -> MatchResult:
    if not 2 <= len(roster) <= MAX_PARTICIPANTS:
        return MatchResult('infeasible', (translate(locale, 'Use 2 to {limit} participants.', limit=MAX_PARTICIPANTS),))

    domains = {giver: set(roster) - {giver} for giver in roster}
    messages = []
    for name, members in groups.items():
        members = members & roster.keys()
        if 2 * len(members) > len(roster):
            messages.append(translate(locale, '{name}: members outnumber available recipients outside the subgroup.', name=name))
        for giver in members:
            domains[giver].difference_update(members)
    for giver, receiver in exclusions:
        if giver in domains:
            domains[giver].discard(receiver)
    for giver, candidates in domains.items():
        if not candidates:
            messages.append(translate(locale, '{name} has no valid recipients.', name=roster[giver]))
    for receiver in roster.keys() - set().union(*domains.values()):
        messages.append(translate(locale, '{name} has no possible givers.', name=roster[receiver]))
    if messages:
        return MatchResult('infeasible', tuple(messages))

    assigned: dict[int, int] = {}
    remaining = set(roster)
    deadline = monotonic() + seconds
    visited = 0

    def search() -> bool | None:
        nonlocal visited
        if len(assigned) == len(roster):
            return True
        if visited >= node_limit or monotonic() >= deadline:
            return None
        visited += 1
        choices = {}
        for giver in domains.keys() - assigned.keys():
            candidates = domains[giver] & remaining
            if no_reciprocal:
                candidates = {receiver for receiver in candidates if assigned.get(receiver) != giver}
            if not candidates:
                return False
            choices[giver] = candidates
        if set().union(*choices.values()) != remaining:
            return False

        owners: dict[int, int] = {}

        def reserve(giver: int, seen: set[int]) -> bool:
            for receiver in choices[giver]:
                if receiver in seen:
                    continue
                seen.add(receiver)
                if receiver not in owners or reserve(owners[receiver], seen):
                    owners[receiver] = giver
                    return True
            return False

        order = sorted(choices)
        if rng is not None:
            rng.shuffle(order)
        order.sort(key=lambda giver: len(choices[giver]))
        if not all(reserve(giver, set()) for giver in order):
            return False
        giver = order[0]
        candidates = sorted(choices[giver])
        if rng is not None:
            rng.shuffle(candidates)
        for receiver in candidates:
            assigned[giver] = receiver
            remaining.remove(receiver)
            result = search()
            if result is True:
                return True
            remaining.add(receiver)
            del assigned[giver]
            if result is None:
                return None
        return False

    result = search()
    if result is True:
        return MatchResult('feasible', assignments=assigned)
    if result is None:
        return MatchResult('indeterminate', (translate(locale, 'Could not verify within the search limit. Relax a rule and try again.'),))
    return MatchResult('infeasible', (translate(locale, 'The combined rules prevent a complete draw. Try relaxing an exclusion or allowing reciprocal pairs.'),))