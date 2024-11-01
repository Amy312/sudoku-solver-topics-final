def is_valid(board: list[list[int]], row: int, col: int, num: int) -> bool:
    for i in range(9):
        if board[row][i] == num or board[i][col] == num:
            return False

    start_row, start_col = 3 * (row // 3), 3 * (col // 3)
    for i in range(start_row, start_row + 3):
        for j in range(start_col, start_col + 3):
            if board[i][j] == num:
                return False
    return True

def solve(board: list[list[int]]) -> bool:
    for row in range(9):
        for col in range(9):
            if board[row][col] == 0:
                for num in range(1, 10):
                    if is_valid(board, row, col, num):
                        board[row][col] = num
                        if solve(board):
                            return True
                        board[row][col] = 0
                return False
    return True

def solve_sudoku(board: list[list[int]]) -> list[list[int]]:
    solved_board = [row[:] for row in board]
    if solve(solved_board):
        print("solver.solve_sudoku: Sudoku was solved")
        return solved_board
    else:
        print("solver.solve_sudoku: Solution was not found")
        return []
