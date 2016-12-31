import random, math, heapq, collections
from PIL import Image, ImageDraw


class Cell(object):
    def __init__(self, row, column):
        self.row = row
        self.column = column
        self.north = None
        self.east = None
        self.south = None
        self.west = None
        self.links = dict()

        self.visited = 'white'

    def link(self, cell, bidi=True):
        self.links[cell] = True
        if bidi == True:
            cell.link(self, False)
        return self

    def unlink(self, cell, bidi=True):
        try:
            del self.links[cell]
        except KeyError:
            pass

        if bidi == True:
            cell.unlink(self, False)
        return self

    def getLinks(self):
        return self.links.keys()

    def linked(self, cell):
        return cell in self.links

    def neighbors(self):
        neighbors = []
        if self.north:
            neighbors.append(self.north)

        if self.east:
            neighbors.append(self.east)

        if self.south:
            neighbors.append(self.south)

        if self.west:
            neighbors.append(self.west)

        return neighbors

    def reset_visited(self):
        self.visited = 'white'

    def __str__(self):
        return "Index=[{}, {}]".format(self.row, self.column)


class Grid(object):
    def __init__(self, rows, columns, cell_class=Cell):
        self.rows = rows
        self.columns = columns
        self.cell_class = cell_class
        self.grid = self._prepare_grid()
        self._configure_cells()

    def _prepare_grid(self):
        return [[self.cell_class(row, column) for column in range(self.columns)] for row in range(self.rows)]

    def _configure_cells(self):
        for cell in self:
            row = cell.row
            col = cell.column
            cell.north = self[row-1, col]
            cell.east = self[row, col+1]
            cell.south = self[row+1, col]
            cell.west = self[row, col-1]

    def random_cell(self):
        return self[random.randint(0, self.rows-1), random.randint(0, self.columns-1)]

    def reset_visited(self):
        for cell in self:
            cell.reset_visited()

    def __getitem__(self, pos):
        row, col = pos

        if not (0 <= row < self.rows):
            return None

        if not (0 <= col < self.columns):
            return None

        return self.grid[row][col]

    def __iter__(self):
        for row in self.grid:
            for cell in row:
                yield cell

    def __len__(self):
        return self.rows * self. columns

class GridImager(object):
    def __init__(self, cell_size=10, grid_offset=5):
        self.cell_size = cell_size
        self.grid_offset = grid_offset
        self.background_color = (224, 224, 224)

    def fill_cell(self, bitmap, cell, color=(255, 255, 255)):
        x = (cell.column * self.cell_size) + self.grid_offset + 1
        y = (cell.row * self.cell_size) + self.grid_offset + 1

        for i in range(x, x + self.cell_size):
            for j in range(y, y + self.cell_size):
                bitmap[i, j] = color

        #draw.rectangle([(x, y), (x + self.cell_size - 1, y + self.cell_size - 1)], fill=color)

    def outline_cell(self, bitmap, cell, color=(0, 0, 0)):
        x = (cell.column * self.cell_size) + self.grid_offset
        y = (cell.row * self.cell_size) + self.grid_offset

        if not cell.linked(cell.north):
            for i in range(x, x + self.cell_size):
                bitmap[i, y] = color

        if not cell.linked(cell.east):
            for i in range(y, y + self.cell_size):
                bitmap[x + self.cell_size, i] = color

        if not cell.linked(cell.south):
            for i in range(x, x + self.cell_size):
                bitmap[i, y + self.cell_size] = color

        if not cell.linked(cell.west):
            for i in range(y, y + self.cell_size):
                bitmap[x, i] = color

    def snapshot(self, grid, current_cell=None):
        width = grid.columns
        height = grid.rows
        image_width = (width * self.cell_size) + (self.grid_offset * 2) + 1
        image_height = (height * self.cell_size) + (self.grid_offset * 2) + 1

        img = Image.new("RGBA", (image_width, image_height), (224, 224, 224, 255))
        bitmap = img.load()

        for cell in grid:
            # Fill Cell
            if cell.visited == 'black':
                self.fill_cell(bitmap, cell, color=(255, 255, 255, 0))

            if cell.visited == 'grey':
                self.fill_cell(bitmap, cell, color=(255, 204, 204, 255))

            if cell.visited == 'white':
                self.fill_cell(bitmap, cell, color=(192, 192, 192, 255))

            # Outline Cell
            self.outline_cell(bitmap, cell)

        if current_cell:
            self.fill_cell(bitmap, current_cell, color=(255, 153, 153, 255))

        return img

class OpenMaze(object):
    def __init__(self, grid):
        self.grid = grid
        self._build()

    def _build(self):
        for cell in self.grid:
            for neighbor in cell.neighbors():
                cell.link(neighbor)


class RecursiveBacktrackingMaze(object):
    def __init__(self, grid, imager):
        self.grid = grid
        self.imager = imager
        self.snapshot_images = []
        self._build()

    def _available_neighbors(self, cell):
        return [neighbor for neighbor in cell.neighbors() if neighbor.visited == 'white']

    def _build(self):
        start_cell = self.grid.random_cell()
        stack = [start_cell]

        while stack:
            cell = stack.pop()
            cell.visited = 'grey'
            available_cells = self._available_neighbors(cell)

            self._snapshot(current_cell=cell)

            while available_cells:
                self._snapshot(current_cell=cell)

                next_cell = random.choice(available_cells)
                cell.link(next_cell)
                next_cell.visited = 'grey'
                stack.append(cell)
                stack.append(next_cell)
                available_cells = self._available_neighbors(next_cell)
                cell = next_cell

            cell.visited = 'black'

        self._snapshot()

    def _snapshot(self, current_cell=None):
        img = self.imager.snapshot(self.grid, current_cell)
        self.snapshot_images.append(img)

    def save_animation(self, file_name="maze.gif"):
        img = self.imager.snapshot(self.grid)
        img.save(file_name, format="GIF", save_all=True, append_images=self.snapshot_images)


class Solver(object):
    def __init__(self, grid, imager):
        self.grid = grid
        self.imager = imager
        self.snapshot_images = []
        self.grid.reset_visited()
        self._solve()

    def _solve(self):
        pass

    def _snapshot(self, current_cell=None):
        img = self.imager.snapshot(self.grid, current_cell)
        self.snapshot_images.append(img)

    def save_animation(self, file_name="maze.gif"):
        img = self.snapshot_images[0]
        img.save(file_name, format="GIF", save_all=True, append_images=self.snapshot_images, transparency=255)


class BFSSolver(Solver):
    def _solve(self):
        start = self.grid[0, 0]
        end = self.grid[self.grid.rows-1, self.grid.columns-1]
        frontier = [start]
        came_from = {start: None}

        while frontier:
            current = frontier.pop(0)

            if current is end:
                break

            for cell in current.getLinks():
                if cell not in came_from:
                    frontier.append(cell)
                    came_from[cell] = current
                cell.visited = 'grey'
                self._snapshot()
            self._snapshot()
        self._snapshot()

        current = end
        while current:
            current.visited = 'black'
            self._snapshot(current_cell=current)
            current = came_from[current]

        self._snapshot()


class DijkstraSolver(Solver):
    def _solve(self):
        pass


class AStarSolver(Solver):
    def _solve(self):
        pass

def execute():

    grid = Grid(10, 10)
    imager = GridImager()
    maze = RecursiveBacktrackingMaze(grid, imager)
    # maze = OpenMaze(grid)
    # maze.save_animation()

    solver = BFSSolver(grid, imager)
    solver.save_animation()



if __name__ == "__main__":
    execute()
