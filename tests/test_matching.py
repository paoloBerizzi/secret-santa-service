from itertools import permutations
from random import Random

from app.matching import solve


def roster(size):
    return {index: f'Person {index}' for index in range(size)}


def test_local_checks_and_search_budget():
    assert solve(roster(1), {}, set()).status == 'infeasible'
    result = solve(roster(4), {'Household': {0, 1, 2}}, set())
    assert 'Household' in result.messages[0]
    result = solve(roster(3), {}, {(0, 1), (0, 2), (1, 0), (1, 2)})
    assert 'Person 0 has no valid recipients.' in result.messages
    assert 'Person 2 has no possible givers.' in result.messages
    assert solve(roster(4), {}, set(), node_limit=1).status == 'indeterminate'


def test_equal_group_and_reciprocity():
    result = solve(roster(4), {'Household': {0, 1}}, set())
    assert {result.assignments[0], result.assignments[1]} == {2, 3}
    assert solve(roster(2), {}, set()).assignments == {0: 1, 1: 0}
    assert solve(roster(2), {}, set(), no_reciprocal=True).status == 'infeasible'


def test_static_bottleneck_with_nonempty_domains():
    exclusions = {(giver, receiver) for giver in (0, 1, 2) for receiver in (0, 1, 2)}
    result = solve(roster(5), {}, exclusions)
    assert result.status == 'infeasible'
    assert 'combined rules' in result.messages[0]


def test_against_brute_force_for_small_rosters():
    rng = Random(23)
    for size in range(2, 7):
        people = roster(size)
        for trial in range(20):
            groups = {f'Group {index}': set(rng.sample(list(people), size // 2)) for index in range(2)}
            exclusions = {(giver, receiver) for giver in people for receiver in people if rng.random() < .15}
            no_reciprocal = trial % 2 == 0

            def valid(assignments):
                return all(giver != receiver and (giver, receiver) not in exclusions
                           and all(not {giver, receiver} <= members for members in groups.values())
                           and (not no_reciprocal or assignments[receiver] != giver)
                           for giver, receiver in assignments.items())

            expected = any(valid(dict(zip(people, order))) for order in permutations(people))
            result = solve(people, groups, exclusions, no_reciprocal=no_reciprocal, rng=rng)
            assert result.status == ('feasible' if expected else 'infeasible')
            if expected:
                assert result.assignments.keys() == people.keys()
                assert set(result.assignments.values()) == people.keys()
                assert valid(result.assignments)