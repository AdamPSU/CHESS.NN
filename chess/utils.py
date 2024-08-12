def piece_name(board, piece_pos):
    """
    Converts a piece index to its corresponding piece name.

    Example:
        piece((7, 0)) -> 'wR'
    """

    if None in piece_pos:
        return None

    row = piece_pos[0]
    col = piece_pos[1]

    piece = board[row][col]

    return piece