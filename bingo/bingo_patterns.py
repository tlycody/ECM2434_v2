DEBUG_PATTERNS = False


class BingoPatternDetector:
    """
    Class to detect various bingo patterns on a 3x3 grid
    """

    @staticmethod
    def create_grid_from_tasks(user_tasks, all_tasks, grid_size=3):
        """
        Creates a 3x3 grid representation of completed tasks

        Args:
            user_tasks: List of UserTask objects that are completed
            all_tasks: List of all Task objects
            grid_size: Size of the grid (default 3x3)

        Returns:
            2D grid where True represents completed tasks and False represents incomplete tasks
        """
        # Create a set of completed task IDs for quick lookup
        completed_task_ids = {task.task.id for task in user_tasks}

        # Debug info
        if DEBUG_PATTERNS:
            print(f"Completed task IDs: {completed_task_ids}")

        # Get only the tasks that will fit in the grid
        grid_tasks = list(all_tasks[:grid_size * grid_size])

        # Debug: List grid tasks
        if DEBUG_PATTERNS:
            grid_task_ids = [task.id for task in grid_tasks]
            print(f"Grid task IDs (in order): {grid_task_ids}")

        # Create the grid
        grid = [[False for _ in range(grid_size)] for _ in range(grid_size)]

        # Map tasks to grid positions based on their sequence in the list
        for i, task in enumerate(grid_tasks):
            row = i // grid_size
            col = i % grid_size

            # Debug position mapping
            if DEBUG_PATTERNS:
                print(f"Task {task.id} at position ({row}, {col})")

            # Mark as completed if this task is in the completed set
            if task.id in completed_task_ids:
                grid[row][col] = True
                if DEBUG_PATTERNS:
                    print(f"  - Marked as completed")

        return grid

    @staticmethod
    def check_o_pattern(grid, size=3):
        """Check if the outer edge is complete (O pattern)"""
        # For a 3x3 grid, the outer edge is all cells except the center
        # Check top and bottom rows
        for col in range(size):
            if not grid[0][col] or not grid[size - 1][col]:
                return False

        # Check left and right columns (excluding corners which were already checked)
        for row in range(1, size - 1):
            if not grid[row][0] or not grid[row][size - 1]:
                return False

        return True

    @staticmethod
    def check_h_pattern(grid, size=3):
        """
        Check if H pattern is complete
        H pattern = [0, 2, 3, 4, 5, 6, 8] in a zero-indexed 3x3 grid
        """
        # Check left column (except middle)
        if not grid[0][0] or not grid[2][0]:
            return False

        # Check right column (except middle)
        if not grid[0][2] or not grid[2][2]:
            return False

        # Check middle row
        if not grid[1][0] or not grid[1][1] or not grid[1][2]:
            return False

        return True

    @staticmethod
    def check_v_pattern(grid, size=3):
        """
        Check if V pattern is complete
        V pattern = [0, 2, 3, 5, 7] in a zero-indexed 3x3 grid
        """
        # Check top corners
        if not grid[0][0] or not grid[0][2]:
            return False

        # Check middle row edges
        if not grid[1][0] or not grid[1][2]:
            return False

        # Check bottom middle
        if not grid[2][1]:
            return False

        return True

    @staticmethod
    def check_x_pattern(grid, size=3):
        """
        Check if X pattern is complete (corners and center)
        """
        # Check corners
        if not grid[0][0] or not grid[0][size - 1] or not grid[size - 1][0] or not grid[size - 1][size - 1]:
            return False

        # Check center
        if not grid[1][1]:
            return False

        return True

    @staticmethod
    def check_horizontal_line(grid, size=3):
        """Check if any horizontal line is complete"""
        for row in range(size):
            all_completed = True
            for col in range(size):
                if not grid[row][col]:
                    all_completed = False
                    break
            if all_completed:
                return True
        return False

    @staticmethod
    def check_vertical_line(grid, size=3):
        """Check if any vertical line is complete"""
        for col in range(size):
            all_completed = True
            for row in range(size):
                if not grid[row][col]:
                    all_completed = False
                    break
            if all_completed:
                return True
        return False

    @staticmethod
    def detect_patterns(grid, size=3):
        """
        Detect all patterns in the grid

        Returns:
            A list of pattern types found (e.g. ["O", "X", "H", "V", "HORIZ", "VERT"])
        """
        patterns = []

        # Check for each pattern with logging
        if DEBUG_PATTERNS:
            print("Checking for O pattern...")
        if BingoPatternDetector.check_o_pattern(grid, size):
            patterns.append("O")
            if DEBUG_PATTERNS:
                print("✓ O pattern detected!")
        elif DEBUG_PATTERNS:
            print("✗ O pattern not detected")

        # Check for H pattern (new letter pattern)
        if DEBUG_PATTERNS:
            print("Checking for H pattern...")
        if BingoPatternDetector.check_h_pattern(grid, size):
            patterns.append("H")
            if DEBUG_PATTERNS:
                print("✓ H pattern detected!")
        elif DEBUG_PATTERNS:
            print("✗ H pattern not detected")

        # Check for V pattern (new letter pattern)
        if DEBUG_PATTERNS:
            print("Checking for V pattern...")
        if BingoPatternDetector.check_v_pattern(grid, size):
            patterns.append("V")
            if DEBUG_PATTERNS:
                print("✓ V pattern detected!")
        elif DEBUG_PATTERNS:
            print("✗ V pattern not detected")

        # Check for X pattern
        if DEBUG_PATTERNS:
            print("Checking for X pattern...")
        if BingoPatternDetector.check_x_pattern(grid, size):
            patterns.append("X")
            if DEBUG_PATTERNS:
                print("✓ X pattern detected!")
        elif DEBUG_PATTERNS:
            print("✗ X pattern not detected")

        # Check for horizontal line pattern (basic pattern)
        if DEBUG_PATTERNS:
            print("Checking for horizontal line pattern...")
        if BingoPatternDetector.check_horizontal_line(grid, size):
            patterns.append("HORIZ")
            if DEBUG_PATTERNS:
                print("✓ Horizontal pattern detected!")
        elif DEBUG_PATTERNS:
            print("✗ Horizontal pattern not detected")

        # Check for vertical line pattern (basic pattern)
        if DEBUG_PATTERNS:
            print("Checking for vertical line pattern...")
        if BingoPatternDetector.check_vertical_line(grid, size):
            patterns.append("VERT")
            if DEBUG_PATTERNS:
                print("✓ Vertical pattern detected!")
        elif DEBUG_PATTERNS:
            print("✗ Vertical pattern not detected")

        return patterns