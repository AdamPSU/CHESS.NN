def piece_name(board, piece_pos):
    """
    Converts a piece index to its corresponding piece name.

    Args:
        board: 2D list representing the chessboard, where each cell holds a piece code (e.g., 'wR', 'bK') or None.
        piece_pos: Tuple of two integers (row, col) indicating the position on the board.

    Returns:
        The piece code at the given position, or None if the position tuple contains None.
    """

    # If either row or column is missing, treat as no valid position
    if None in piece_pos:
        return None

    # Unpack the row and column indices
    row, col = piece_pos

    # Lookup the piece code in the board matrix
    piece = board[row][col]

    return piece