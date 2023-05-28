#!/usr/bin/env python
"""Provides utility functions."""


def split(C: list) -> (list, list):
    """
    Splits the given list of constraints/clauses into two parts.
    :param C: a list of clauses
    :return: a tuple of two lists
    """
    half_size = len(C) // 2
    return C[:half_size], C[half_size:]


def diff(x: list, y: list) -> list:
    """
    Returns the difference of two lists.
    :param x: list
    :param y: list
    :return: list
    """
    return [item for item in x if item not in y]


def get_hashcode(C: list) -> str:
    """
    Returns the hashcode of the given CNF formula.
    :param C: a list of clauses
    :return: the hashcode of the given CNF formula
    """
    C = sorted(C, key=lambda x: x[0])
    return str(C)


def hasIntersection(list1: list, list2: list) -> bool:
    return any(i in list1 for i in list2)


def contains(listofList: list, aList: list) -> bool:
    return any(aList == x for x in listofList)


def contains_all(greater: list, smaller: list) -> bool:
    return all(i in smaller for i in greater)
