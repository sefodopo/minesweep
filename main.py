import random
import tkinter as tk
from tkinter import ttk, messagebox
import os


class Grid:
  def __init__(self, root: ttk.Widget, width, height, mines, minesweeper):
    self.width = width
    self.height = height
    self.mines = mines
    self.flags = 0
    self.minesweeper = minesweeper
    self.incorrect_flags = 0
    self.initialized = False
    self.done = False

    self.mines_left = tk.StringVar(root, f'{mines} 💣')
    self.lmines_left = ttk.Label(root, textvariable=self.mines_left)
    self.lmines_left.grid(column=0, row=height, columnspan=width, pady=5)

    self.zoom = tk.IntVar(root, 30)
    self.zoom_spin = ttk.Spinbox(root, textvariable=self.zoom, from_=20, to_=75, increment=5, command=self.update_zoom, width=5)
    self.zoom_spin.grid(column=width-5, row=height, pady=10, columnspan=5)

    style = ttk.Style()
    self.theme = tk.StringVar(root, style.theme_use())
    self.theme_select = ttk.Combobox(root, textvariable=self.theme, values=style.theme_names(), width=9)
    self.theme_select.bind('<<ComboboxSelected>>', lambda e: style.theme_use(self.theme.get()))
    self.theme_select.grid(column=0, columnspan=5, row=height, pady=10)

    self._grid = [Cell(root, self, i%width, i//width) for i in range(width*height)]
    self.covered_cells = self._grid.copy()

  def get_cell(self, x, y):
    if x >= self.width or y >= self.height or min(x,y)<0:
      return None
    return self._grid[y*self.width+x]

  def update_mines(self):
    self.mines_left.set(f'{self.mines-self.flags} 💣')

  def initialize(self, mines: list):
    self.initialized = True
    for mine in random.sample([cell for cell in self._grid if cell not in mines], self.mines):
      mine.set_mine()
      self.covered_cells.remove(mine)

  def update_zoom(self):
    for cell in self._grid:
      cell.frame['height'] = self.zoom.get()
      cell.frame['width'] = self.zoom.get()
  

class Cell:
  def __init__(self, root: ttk.Widget, grid, x, y):
    self._mine = False
    self.root = root
    self.exploded = False
    self.covered = True
    self._flag = False
    self._grid: Grid = grid
    self._x = x
    self._y = y
    self.frame = ttk.Frame(root, height=25, width=25)
    self.frame.grid(column=x, row=y)
    self.frame.pack_propagate(0)
    self.button = ttk.Button(self.frame, text='', width=2, command=self.expose)
    self.button.bind('<3>', lambda e: self.flag())
    self.button.pack(fill=tk.BOTH, expand=1)

  def set_mine(self):
    self._mine = True

  def flag(self):
    self._flag = not self._flag
    if self._flag:
      self.button['text'] = '🚩'
      self._grid.flags += 1
      if not self._mine:
        self._grid.incorrect_flags += 1
    else:
      self.button['text'] = ''
      self._grid.flags -= 1
      if not self._mine:
        self._grid.incorrect_flags -= 1
    self._grid.update_mines()

  def get_neighbors(self):
    neighbors = []
    for y in range(self._y-1, self._y+2):
      for x in range(self._x-1, self._x+2):
        if x == self._x and y == self._y:
          continue
        cell = self._grid.get_cell(x,y)
        if cell:
          neighbors.append(cell)
    return neighbors

  def expose(self):
    if not self.covered or self._flag or self._grid.done:
      return
    self.covered = False
    self.button.destroy()
    self.button = ttk.Label(self.frame, anchor=tk.CENTER)
    self.button.pack(fill=tk.BOTH, expand=1)

    if not self._grid.initialized:
      neighbors = self.get_neighbors()
      neighbors.append(self)
      self._grid.initialize(neighbors)

    if self._mine:
      self.exploded = True
      self._grid.done = True
      messagebox.showerror('Boom!', 'You exploded!')

      button = ttk.Button(self.root, text='Restart', command=self._grid.minesweeper.show_intro)
      button.grid(column=0, row=self._grid.height+1, columnspan=self._grid.width, pady=10)
      for cell in self._grid._grid:
        if cell._mine:
          if cell._flag:
            cell.button['style'] = 'G.TButton'
          else:
            cell.button['style'] = 'R.TButton'
          cell.button['text'] = '💣'
        elif cell._flag:
          cell.button['style'] = 'G.TButton'
      self.button['style'] = 'R.TLabel'
      return
    count = 0
    for cell in self.get_neighbors():
      if cell._mine:
        count += 1
    if count != 0:
      self.button['text'] = count
    else:
      for cell in self.get_neighbors():
        cell.expose()
    self._grid.covered_cells.remove(self)
    if len(self._grid.covered_cells) == 0:
      if messagebox.askyesno('Winner!', 'You won! Want to play again?'):
        self._grid.minesweeper.show_intro()
      else:
        self._grid.minesweeper.mainframe.quit()

    
    

class MineSweeper:
  def __init__(self, root):
    self.root = root
    root.title('Minesweeper!')
    mf = self.mainframe = ttk.Frame(self.root, padding="3 3 12 12")
    mf.grid(column=0, row=0, stick=(tk.N, tk.W, tk.E, tk.S))
    self.width = tk.IntVar(mf, 40)
    self.height = tk.IntVar(mf, 30)
    self.mines = tk.IntVar(mf, 120)
    self.show_intro()

  def show_intro(self):
    mf = self.mainframe
    for child in mf.winfo_children():
      child.destroy()
    lwidth = ttk.Label(mf, text='Width:')
    lwidth.grid(column=0, row=0)
    lheight = ttk.Label(mf, text="Height:")
    lheight.grid(column=0, row=1)
    lmines = ttk.Label(mf, text="Mines:")
    lmines.grid(column=0, row=2)

    ewidth = ttk.Spinbox(mf, textvariable=self.width, from_=10, to=1000, width=5)
    eheight = ttk.Spinbox(mf, textvariable=self.height, from_=10, to=1000, width=5)
    emines = ttk.Spinbox(mf, textvariable=self.mines, from_=10, to=1000, width=5)
    ewidth.grid(column=1, row=0)
    eheight.grid(column=1, row=1)
    emines.grid(column=1, row=2)

    button = ttk.Button(mf, text='Start', command=self.start)
    button.grid(column=0, row=4, columnspan=2)
    
    for child in mf.winfo_children():
      child.grid_configure(padx=5, pady=5)

  def start(self):
    mf = self.mainframe
    for child in mf.winfo_children():
      child.destroy()
    self.grid = Grid(mf, self.width.get(), self.height.get(), self.mines.get(), self)

def main():
  root = tk.Tk()
  style = ttk.Style()
  style.map('R.TButton',
    foreground=[('!disabled', 'red')]
    )
  style.map('G.TButton',
    foreground=[('!disabled', 'gray')]
    )
  style.map('R.TLabel',
    foreground=[('!disabled', 'red')]
    )
  root.resizable(False, False)
  minesweeper = MineSweeper(root)
  root.mainloop()


if __name__ == '__main__':
  main()
