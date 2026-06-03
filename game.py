def transform(row, col, orientation, N):
    """ Returns the rotated (row, col) given an orientation (0-3) and grid size N. """
    orientation = orientation % 4
    if orientation == 0:
        return (row, col)
    elif orientation == 1:
        return (col, N - 1 - row)
    elif orientation == 2:
        return (N - 1 - row, N - 1 - col)
    elif orientation == 3:
        return (N - 1 - col, row)


class Game:
    def __init__(self, maze_data):
        self.player_position = maze_data["start"][1:]
        self.player_face = maze_data["start"][0] # "front"
        self.player_orientation = 0

        self.start = maze_data["start"][1:] # tuple of start row and col
        self.start_face = maze_data["start"][0]
        self.end = maze_data["end"][1:]
        self.end_face = maze_data["end"][0]

        self.grids = maze_data["faces"]
        self.grid = self.grids[self.player_face]   # current grid.

        self.transitions = maze_data["transitions"]

        self.rows = len(self.grid) 
        self.cols = len(self.grid[0]) #should be the same as self.rows

    def move_player(self, dx, dy):
        """ Updates player position if valid. Note: this is in the players local frame
         returns True if an edge has been crossed, False otherwise. 
        """

        new_col = self.player_position[1] + dy
        new_row = self.player_position[0] + dx

        r, c = transform(new_row, new_col, -self.player_orientation, self.rows)

        if (0 <= new_col < self.cols) and (0 <= new_row < self.rows): # move is within bounds
            if self.grid[r][c] == 0: # move is to a valid square
                self.player_position = (new_row, new_col)           
            return False
        
        if len(self.grids) > 1: #multiple faces
            # Edge detection. The idea is to identify the crossed edge (in the local frame) with a number
            # as follows: up: 0, right: 1, down: 2, left: 3. The edge the player actually crossed
            # (in the orientation=0 frame) is just this value + orientation (mod 4) 
            if new_row < 0: #too far up
                side = (0 - self.player_orientation) % 4
            elif new_col >= self.cols: # too far right
                side = (1 - self.player_orientation) % 4
            elif new_row >= self.rows: # too far down
                side = (2 - self.player_orientation) % 4
            elif new_col < 0: # too far left
                side = (3 - self.player_orientation) % 4
            
            # update players current face
            old_face = self.player_face
            self.player_face = self.transitions[self.player_face][side][0] # string like "front"
            #update grid using new current face
            self.grid = self.grids[self.player_face]

            # update players orientation
            delta_rotation = self.transitions[old_face][side][1]
            self.player_orientation = (self.player_orientation + delta_rotation) % 4

            # move the player to the correct position in the new grid
            self.player_position = (new_row % self.rows, new_col % self.cols)
            return True 
        return False