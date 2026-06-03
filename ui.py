# UI using Tkinter

import tkinter as tk
from tkinter import ttk, messagebox
from game import Game, transform
from maze_data import MAZE
from solver import bfs, bfs_cube

class MazeUI:
    def __init__(self, root):
        self.game = Game(MAZE[1])
        self.root = root
        self.player_id = None

        # level select and top bar
        self.top_bar = tk.Frame(self.root)
        self.top_bar.pack(side="top", fill="x")
        self.current_level = 1
        self.level_var = tk.StringVar(value="Level 1")
        self.level_dropdown = ttk.Combobox(
            self.top_bar,
            textvariable=self.level_var,
            values=[f"Level {i}" for i in range(1, len(MAZE)+1)],
            state="readonly"
        )
        self.level_dropdown.pack(side="left")
        self.level_dropdown.bind("<<ComboboxSelected>>", self.on_level_change)

        # hint button
        self.hint_button = tk.Button(self.top_bar, text="Hint", command=self.show_hint)
        self.hint_button.pack(side="right", padx=6, pady=2)

        self.hint_ids = []
        self._hint_after_ids = []

        # screen dimension
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()

        # size of the game window
        w = int(0.5*screen_width)
        h = int(0.7*screen_height)

        center_x = int((screen_width - w) / 2)
        center_y = int((screen_height - h) / 2) 

        self.root.geometry(f'{w}x{h}+{center_x}+{center_y}')


        self.canvas = tk.Canvas(self.root, bg='white')
        self.canvas.pack(fill="both", expand=True)
        self.canvas.focus_set()  

        self.canvas.bind("<Configure>", lambda e: self.draw_grid())
        self.canvas.bind("<w>", lambda e: self.move_and_update(-1,0))
        self.canvas.bind("<s>", lambda e: self.move_and_update(1,0))
        self.canvas.bind("<a>", lambda e: self.move_and_update(0,-1))
        self.canvas.bind("<d>", lambda e: self.move_and_update(0,1))
        self.canvas.bind("<Up>", lambda e: self.move_and_update(-1,0))
        self.canvas.bind("<Down>", lambda e: self.move_and_update(1,0))
        self.canvas.bind("<Left>", lambda e: self.move_and_update(0,-1))
        self.canvas.bind("<Right>", lambda e: self.move_and_update(0,1))


    def draw_grid(self):
        """ Draws the current grid the player is on."""
        self.clear_hints()
        self.canvas.delete("all")

        w = self.canvas.winfo_width()
        h = self.canvas.winfo_height()

        pixel_x = w / self.game.cols
        pixel_y = h / self.game.rows
        self.pixel_size = int(0.8 * min(pixel_x, pixel_y))
        
        self.offset_x = (w - self.pixel_size * self.game.cols) // 2
        self.offset_y = (h - self.pixel_size * self.game.rows) // 2

        for r, row in enumerate(self.game.grid):
            for c, cell in enumerate(row):
                bg_color = "black" if cell == 1 else "white"

                # rotate the grid according to the players orientation
                new_r, new_c = transform(r, c, self.game.player_orientation, self.game.rows)

                x1 = self.offset_x + new_c*self.pixel_size
                y1 = self.offset_y + new_r*self.pixel_size
                x2 = x1 + self.pixel_size
                y2 = y1 + self.pixel_size

                self.canvas.create_rectangle((x1,y1), (x2,y2), fill=bg_color)
        self.draw_special_squares()
        self.draw_player()
        label_y = max(self.offset_y // 2, 14)
        self.canvas.create_text(
            w // 2, label_y,
            text=f"Level {self.current_level}",
            font=("Arial", 18, "bold"),
            fill="black"
        )

    def draw_special_squares(self):
        start_row, start_col = transform(*self.game.start, self.game.player_orientation, self.game.rows)
        end_row, end_col = transform(*self.game.end, self.game.player_orientation, self.game.rows)

        if self.game.player_face == self.game.start_face:
            x1 = self.offset_x + start_col*self.pixel_size
            y1 = self.offset_y + start_row*self.pixel_size
            x2 = x1 + self.pixel_size
            y2 = y1 + self.pixel_size

            self.canvas.create_rectangle((x1,y1), (x2,y2), fill="yellow")

        if self.game.player_face == self.game.end_face:
            x1 = self.offset_x + end_col*self.pixel_size
            y1 = self.offset_y + end_row*self.pixel_size
            x2 = x1 + self.pixel_size
            y2 = y1 + self.pixel_size

            self.canvas.create_rectangle((x1,y1), (x2,y2), fill="green")
            
    def draw_player(self):
        """draws the player in their local frame"""

        if self.player_id is not None:
            self.canvas.delete(self.player_id)

        r,c = self.game.player_position

        padding = 0.15*self.pixel_size
        x1 = padding + self.offset_x + c*self.pixel_size
        y1 = padding + self.offset_y + r*self.pixel_size
        x2 = x1 + self.pixel_size - 2*padding
        y2 = y1 + self.pixel_size - 2*padding

        self.player_id = self.canvas.create_oval(x1, y1, x2, y2, fill='blue')

    def on_level_change(self, event):
        level_text = self.level_var.get()   
        level_num = int(level_text.split()[1])
        self.current_level = level_num
        self.load_level(level_num)

    def load_level(self, n):
        self.game = Game(MAZE[n])
        self.level_var.set(f"Level {n}")
        self.draw_grid()
        self.canvas.focus_set()    

    def move_and_update(self, dx, dy):
        """ Moves the player if valid, detects edge crossings and if so displays new face"""
        self.clear_hints()
        edge_crossed = self.game.move_player(dx, dy)
        self.draw_player()
        if edge_crossed:
            self.draw_grid()
        self.check_win()

    def show_hint(self):
        self.clear_hints()
        if len(self.game.grids) > 1:
            # cube level. show steps on current face only
            path = bfs_cube(
                self.game.grids, self.game.transitions,
                tuple(self.game.player_position), self.game.player_face,
                self.game.player_orientation, self.game.end_face, self.game.end
            )
            if not path:
                return
            steps = []
            for face, row, col, _ in path[1:]:
                if face != self.game.player_face:
                    break
                steps.append((row, col))
                if len(steps) >= 5:
                    break
            for i, (r, c) in enumerate(steps):
                after_id = self.root.after(i * 200, lambda r=r, c=c: self._draw_hint_square(r, c))
                self._hint_after_ids.append(after_id)
            return

        # 2D level: BFS in world frame
        start = tuple(transform(*self.game.player_position, -self.game.player_orientation, self.game.rows))
        end = tuple(self.game.end)
        path = bfs(self.game.grid, start, end)
        if not path:
            return
        for i, (gr, gc) in enumerate(path[1:6]):
            dr, dc = transform(gr, gc, self.game.player_orientation, self.game.rows)
            after_id = self.root.after(i * 200, lambda r=dr, c=dc: self._draw_hint_square(r, c))
            self._hint_after_ids.append(after_id)

    def _draw_hint_square(self, r, c):
        padding = 0.15 * self.pixel_size
        x1 = padding + self.offset_x + c * self.pixel_size
        y1 = padding + self.offset_y + r * self.pixel_size
        x2 = x1 + self.pixel_size - 2 * padding
        y2 = y1 + self.pixel_size - 2 * padding
        hint_id = self.canvas.create_rectangle(x1, y1, x2, y2, fill="#f0a030", outline="")
        self.hint_ids.append(hint_id)

    def clear_hints(self):
        for after_id in self._hint_after_ids:
            self.root.after_cancel(after_id)
        self._hint_after_ids = []
        for hint_id in self.hint_ids:
            self.canvas.delete(hint_id)
        self.hint_ids = []

    def check_win(self):
        display_end = list(transform(*self.game.end, self.game.player_orientation, self.game.rows))
        if list(self.game.player_position) == display_end and self.game.player_face == self.game.end_face:
            if self.current_level < len(MAZE):
                self.current_level += 1
                self.load_level(self.current_level)
            elif self.current_level == len(MAZE):
                messagebox.showinfo("Congratulations", "You completed all levels!")
                return
            

