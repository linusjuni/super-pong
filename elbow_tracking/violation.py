from detector import ElbowPositions


def check_violation(elbows: ElbowPositions, table_edge_x: int | None) -> bool:
    """Return True if either elbow crosses past the table edge."""
    if table_edge_x is None:
        return False
    return elbows.right_x > table_edge_x or elbows.left_x > table_edge_x
