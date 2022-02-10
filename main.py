import random

class Grid:
  def __init__(self, width, height, mines):
    self.width = width
    self.height = height
    self.mines = mines
    self._grid = [Cell(self, i%width, i//width) for i in range(width*height)]
    for mine in random.sample(self._grid, mines):
      mine.set_mine()

  def get_cell(self, x, y):
    if x >= self.width or y >= self.height:
      return None
    return self._grid[y*self.width+x]
  

class Cell:
  def __init__(self, grid, x, y):
    self._mine = False
    self.exploded = False
    self.covered = True
    self._grid: Grid = grid
    self._x = x
    self._y = y

  def set_mine(self):
    self._mine = True

  def expose(self):
    self.covered = False
    if self._mine:
      self.exploded = True
      return -1
    count = 0
    for y in range(self._y-1, self._y+2):
      for x in range(self._x-1, self._x+2):
        cell = self._grid.get_cell(x,y)
        if not cell:
          continue
        if cell._mine:
          count += 1
    return count

def main():
  grid = Grid(100,100,50)
  for x in range(100):
    for y in range(100):
      c = grid.get_cell(x,y).expose()
      if c == -1:
        print('*', end='')
      else:
        print(c, end='')
    print()

if __name__ == '__main__':
  main()