#!/usr/bin/env python
"""Provides utility functions."""


def split(clauses: list) -> (list, list):
    """
    Splits the given list of constraints/clauses into two parts.
    :param clauses: a list of clauses
    :return: a tuple of two lists
    """
    half_size = len(clauses) // 2
    return clauses[:half_size], clauses[half_size:]


def diff(list_x: list, list_y: list) -> list:
    """
    Returns the difference of two lists.
    :param list_x: list
    :param list_y: list
    :return: list
    """
    return [item for item in list_x if item not in list_y]


def get_hashcode(clauses: list) -> str:
    """
    Returns the hashcode of the given CNF formula.
    :param clauses: a list of clauses
    :return: the hashcode of the given CNF formula
    """
    clauses = sorted(clauses, key=lambda x: x[0])
    return str(clauses)


def has_intersection(list1: list, list2: list) -> bool:
    return any(i in list1 for i in list2)


def contains(list_of_lists: list, a_list: list) -> bool:
    return any(a_list == x for x in list_of_lists)


def contains_all(greater: list, smaller: list) -> bool:
    return all(i in smaller for i in greater)
