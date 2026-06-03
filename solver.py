from collections import deque
from game import transform


def bfs(grid, player_position, end):
    """BFS solver to find the optimal next 5 steps
    to the end from a given starting position.

    Input:
        player_position: tuple
        grid: List(List())
        end: tuple

    Output: 
        solution: List()

    """
    queue = deque([[player_position]])
    visited = set()

    visited.add(player_position)

    while queue:
        current_path = queue.popleft()
        row, col = current_path[-1]
        if (row, col) == end:
            return current_path 
        for dx, dy in [(-1,0), (1,0), (0,-1), (0,1)]:
            new_row, new_col = row + dx, col + dy
            step = (new_row, new_col)
            if step not in visited and 0 <= new_row < len(grid) and 0 <= new_col < len(grid[0]) and grid[new_row][new_col] == 0:
                visited.add(step)
                queue.append(current_path + [step])


def bfs_cube(grids, transitions, player_position, player_face, player_orientation, end_face, end_pos):
    """Multi-face BFS for the cube maze.
    State: (face, disp_row, disp_col, orientation). positions are in the display frame,
    matching how player_position is stored in Game.
    Returns path as a list of states, or None if no path exists.
    """
    N = len(list(grids.values())[0])
    start = (player_face, player_position[0], player_position[1], player_orientation)

    queue = deque([[start]])
    visited = set()
    visited.add(start)

    while queue:
        current_path = queue.popleft()
        face, row, col, orientation = current_path[-1]

        # convert display position back to world frame and compare with end
        world_r, world_c = transform(row, col, -orientation, N)
        if face == end_face and (world_r, world_c) == tuple(end_pos):
            return current_path

        grid = grids[face]
        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            new_row, new_col = row + dx, col + dy

            if 0 <= new_row < N and 0 <= new_col < N:
                wr, wc = transform(new_row, new_col, -orientation, N)
                if grid[wr][wc] == 1:
                    continue
                new_face = face
                new_orientation = orientation
                nr, nc = new_row, new_col
            else:
                if new_row < 0:         
                    display_side = 0
                elif new_col >= N:       
                    display_side = 1
                elif new_row >= N:       
                    display_side = 2
                else:                    
                    display_side = 3
                side = (display_side - orientation) % 4
                new_face = transitions[face][side][0]
                delta_rotation = transitions[face][side][1]
                new_orientation = (orientation + delta_rotation) % 4
                nr, nc = new_row % N, new_col % N

            new_state = (new_face, nr, nc, new_orientation)
            if new_state not in visited:
                visited.add(new_state)
                queue.append(current_path + [new_state])
