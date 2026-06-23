# board.py
class Board:
    def __init__(self, initial_grid=None):
        if initial_grid is None:
            self.rows = 5
            self.cols = 5
            self.initial_grid = [[5 for _ in range(self.cols)] for _ in range(self.rows)]
            self.grid = [row[:] for row in self.initial_grid]
        else:
            self.rows = len(initial_grid)
            if self.rows == 0:
                raise ValueError("Grid cannot be empty")

            self.cols = len(initial_grid[0])
            if self.cols == 0:
                raise ValueError("Grid columns cannot be zero")

            for i, row in enumerate(initial_grid):
                if len(row) != self.cols:
                    raise ValueError(f"Row {i} has length {len(row)}, expected {self.cols}. Grid must be rectangular.")

            self.initial_grid = [row[:] for row in initial_grid]
            self.grid = [row[:] for row in initial_grid]

        self.crossed = [[False for _ in range(self.cols)] for _ in range(self.rows)]

        # ✅ Undo/Redo 栈
        self.undo_stack = []
        self.redo_stack = []
        self._snapshot()

    def _snapshot(self):
        """保存当前状态到 Undo 栈"""
        snapshot = {
            "grid": [row[:] for row in self.grid],
            "crossed": [row[:] for row in self.crossed]
        }
        self.undo_stack.append(snapshot)
        self.redo_stack.clear()

    def undo(self):
        """撤销一步"""
        if len(self.undo_stack) <= 1:
            return False
        self.redo_stack.append(self.undo_stack.pop())
        snap = self.undo_stack[-1]
        self.grid = [row[:] for row in snap["grid"]]
        self.crossed = [row[:] for row in snap["crossed"]]
        return True

    def redo(self):
        """重做一步"""
        if not self.redo_stack:
            return False
        snap = self.redo_stack.pop()
        self.undo_stack.append(snap)
        self.grid = [row[:] for row in snap["grid"]]
        self.crossed = [row[:] for row in snap["crossed"]]
        return True

    def reset_to_initial(self):
        """重置棋盘到初始状态"""
        self.grid = [row[:] for row in self.initial_grid]
        self.clear_crosses()
        self._snapshot()

    def get_cell(self, row, col):
        if 0 <= row < self.rows and 0 <= col < self.cols:
            return self.grid[row][col]
        return None

    def set_cell(self, row, col, value):
        if 0 <= row < self.rows and 0 <= col < self.cols:
            self.grid[row][col] = value
            return True
        return False

    def toggle_cross(self, row, col):
        if 0 <= row < self.rows and 0 <= col < self.cols:
            if self.grid[row][col] == 5:
                self.crossed[row][col] = not self.crossed[row][col]
                self._snapshot()
                return True
        return False

    def is_crossed(self, row, col):
        if 0 <= row < self.rows and 0 <= col < self.cols:
            return self.crossed[row][col]
        return False

    def remove_cross(self, row, col):
        if 0 <= row < self.rows and 0 <= col < self.cols:
            self.crossed[row][col] = False

    def clear_crosses(self):
        self.crossed = [[False for _ in range(self.cols)] for _ in range(self.rows)]

    def place_bulb(self, row, col):
        if self.grid[row][col] == 5:
            if self.crossed[row][col]:
                return False
            self.set_cell(row, col, 9)
            self._snapshot()
            return True
        return False

    def remove_bulb(self, row, col):
        if self.grid[row][col] == 9:
            self.set_cell(row, col, 5)
            self._snapshot()
            return True
        return False

    def print_board(self):
        print("当前棋盘:")
        print("  " + " ".join(str(i) for i in range(self.cols)))

        for row in range(self.rows):
            row_str = f"{row} "
            for col in range(self.cols):
                value = self.grid[row][col]

                if value == 5:
                    if self.crossed[row][col]:
                        row_str += "X "
                    else:
                        row_str += "□ "
                elif value == 9:
                    row_str += "○ "
                elif value == -1:
                    row_str += "■ "
                elif value == 0:
                    row_str += "0 "
                elif 1 <= value <= 4:
                    row_str += f"{value} "
                else:
                    row_str += "? "

            print(row_str)

    def is_valid_move(self, row, col):
        if self.grid[row][col] != 5:
            return False
        if self.crossed[row][col]:
            return False

        for c in range(col - 1, -1, -1):
            cell = self.grid[row][c]
            if cell == 9:
                return False
            elif cell != 5:
                break

        for c in range(col + 1, self.cols):
            cell = self.grid[row][c]
            if cell == 9:
                return False
            elif cell != 5:
                break

        for r in range(row - 1, -1, -1):
            cell = self.grid[r][col]
            if cell == 9:
                return False
            elif cell != 5:
                break

        for r in range(row + 1, self.rows):
            cell = self.grid[r][col]
            if cell == 9:
                return False
            elif cell != 5:
                break

        return True

    def is_cell_lit(self, row, col):
        if self.grid[row][col] != 5:
            return True

        for c in range(col - 1, -1, -1):
            cell = self.grid[row][c]
            if cell == 9:
                return True
            elif cell != 5:
                break

        for c in range(col + 1, self.cols):
            cell = self.grid[row][c]
            if cell == 9:
                return True
            elif cell != 5:
                break

        for r in range(row - 1, -1, -1):
            cell = self.grid[r][col]
            if cell == 9:
                return True
            elif cell != 5:
                break

        for r in range(row + 1, self.rows):
            cell = self.grid[r][col]
            if cell == 9:
                return True
            elif cell != 5:
                break

        return False

    def check_all_white_cells_lit(self):
        for row in range(self.rows):
            for col in range(self.cols):
                if self.grid[row][col] == 5:
                    if not self.is_cell_lit(row, col):
                        return False, (row, col)
        return True, None

    def check_bulb_constraints(self):
        bulbs = []
        for row in range(self.rows):
            for col in range(self.cols):
                if self.grid[row][col] == 9:
                    bulbs.append((row, col))

        for i in range(len(bulbs)):
            for j in range(i + 1, len(bulbs)):
                r1, c1 = bulbs[i]
                r2, c2 = bulbs[j]

                if r1 == r2:
                    min_c, max_c = min(c1, c2), max(c1, c2)
                    conflict = True
                    for c in range(min_c + 1, max_c):
                        if self.grid[r1][c] != 5:
                            conflict = False
                            break
                    if conflict:
                        return False, f"灯泡({r1},{c1})和({r2},{c2})在同一行冲突"

                elif c1 == c2:
                    min_r, max_r = min(r1, r2), max(r1, r2)
                    conflict = True
                    for r in range(min_r + 1, max_r):
                        if self.grid[r][c1] != 5:
                            conflict = False
                            break
                    if conflict:
                        return False, f"灯泡({r1},{c1})和({r2},{c2})在同一列冲突"

        return True, None

    def check_number_constraints(self):
        for row in range(self.rows):
            for col in range(self.cols):
                value = self.grid[row][col]
                if 0 <= value <= 4:
                    required = value
                    actual = 0

                    for dr, dc in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
                        r, c = row + dr, col + dc
                        if 0 <= r < self.rows and 0 <= c < self.cols:
                            if self.grid[r][c] == 9:
                                actual += 1

                    if actual != required:
                        return False, f"格子({row},{col})需要{required}个灯泡，实际有{actual}个"

        return True, None

    def is_solved(self):
        lit_ok, lit_info = self.check_all_white_cells_lit()
        bulb_ok, bulb_info = self.check_bulb_constraints()
        num_ok, num_info = self.check_number_constraints()

        return lit_ok and bulb_ok and num_ok, (lit_info, bulb_info, num_info)

    def cycle_cell_state(self, row, col, edit_states, current_index):
        current_state = self.grid[row][col]

        if current_state not in edit_states:
            new_state = edit_states[0]
            new_index = 0
        else:
            try:
                current_idx = edit_states.index(current_state)
                new_index = (current_idx + 1) % len(edit_states)
                new_state = edit_states[new_index]
            except ValueError:
                new_state = edit_states[0]
                new_index = 0

        self.set_cell(row, col, new_state)
        return new_index, new_state

    def get_grid_copy(self):
        return [row[:] for row in self.grid]