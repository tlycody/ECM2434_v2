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
        completed_task_ids = {task.task.id for task in user_tasks if task.completed}
        
        # Map all tasks to grid positions (assuming tasks are ordered from 1-9)
        task_map = {}
        for i, task in enumerate(all_tasks[:grid_size*grid_size]):
            row = i // grid_size
            col = i % grid_size
            task_map[task.id] = (row, col)
        
        # Create the grid
        grid = [[False for _ in range(grid_size)] for _ in range(grid_size)]
        
        # Mark completed tasks
        for task_id in completed_task_ids:
            if task_id in task_map:
                row, col = task_map[task_id]
                grid[row][col] = True
                
        return grid
    
    @staticmethod
    def check_o_pattern(grid, size=3):
        """Check if the outer edge is complete (O pattern)"""
        # For a 3x3 grid, the outer edge is all cells except the center
        # Check top and bottom rows
        for col in range(size):
            if not grid[0][col] or not grid[size-1][col]:
                return False
        
        # Check left and right columns (excluding corners which were already checked)
        for row in range(1, size-1):
            if not grid[row][0] or not grid[row][size-1]:
                return False
                
        return True
    
    @staticmethod
    def check_x_pattern(grid, size=3):
        """Check if diagonals are complete (X pattern)"""
        # Check main diagonal (top-left to bottom-right)
        for i in range(size):
            if not grid[i][i]:
                return False
        
        # Check other diagonal (top-right to bottom-left)
        for i in range(size):
            if not grid[i][size-1-i]:
                return False
                
        return True
    
    @staticmethod
    def check_horizontal_line(grid, size=3):
        """Check if any horizontal line is complete"""
        for row in range(size):
            if all(grid[row]):
                return True
        return False
    
    @staticmethod
    def check_vertical_line(grid, size=3):
        """Check if any vertical line is complete"""
        for col in range(size):
            if all(grid[row][col] for row in range(size)):
                return True
        return False
    
    @staticmethod
    def detect_patterns(grid, size=3):
        """
        Detect all patterns in the grid
        
        Returns:
            A list of pattern types found (e.g. ["O", "X", "H", "V"])
        """
        patterns = []
        
        # Check for each pattern
        if BingoPatternDetector.check_o_pattern(grid, size):
            patterns.append("O")
            
        if BingoPatternDetector.check_x_pattern(grid, size):
            patterns.append("X")
            
        if BingoPatternDetector.check_horizontal_line(grid, size):
            patterns.append("H")
            
        if BingoPatternDetector.check_vertical_line(grid, size):
            patterns.append("V")
            
        return patterns