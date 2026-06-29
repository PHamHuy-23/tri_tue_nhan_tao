"""
Module containing common helper functions and utilities for the AI algorithms and projects.
"""

def print_log(step, state, frontier, explored):
    """
    Prints search algorithm step log in a standardized format.
    """
    print(f"Step: {step}")
    print(f"  Current State: {state}")
    print(f"  Frontier Size: {len(frontier)}")
    print(f"  Explored Size: {len(explored)}")
    print("-" * 40)
