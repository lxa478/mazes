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
        return self.rows * self.columns


class GridImager(object):
    def __init__(self, cell_size=10, cell_inset=2):
        self.cell_size = cell_size
        self.cell_inset = cell_inset
        self.background_color = (224, 224, 224)

    def cell_coordinates(self, x, y):
        x1 = x
        x4 = x + self.cell_size
        x2 = x1 + self.cell_inset
        x3 = x4 - self.cell_inset

        y1 = y
        y4 = y + self.cell_size
        y2 = y1 + self.cell_inset
        y3 = y4 - self.cell_inset

        return x1, x2, x3, x4, y1, y2, y3, y4

    def draw_cell(self, draw, cell, x, y, cell_color=(255, 255, 255), wall_color=(0, 0, 0), inset_color=(224, 224, 224)):

        x1, x2, x3, x4, y1, y2, y3, y4 = self.cell_coordinates(x, y)

        # Fill Cell
        draw.rectangle([(x1, y1), (x4, y4)], fill=cell_color, outline=inset_color)

        # Fill Walls
        if not cell.linked(cell.north):
            draw.rectangle([(x1, y1), (x4, y2)], fill=inset_color)
        else:
            draw.rectangle([(x1, y1), (x2, y2)], fill=inset_color)

        if not cell.linked(cell.east):
            draw.rectangle([(x3, y1), (x4, y4)], fill=inset_color)
        else:
            draw.rectangle([(x3, y1), (x4, y2)], fill=inset_color)

        if not cell.linked(cell.south):
            draw.rectangle([(x1, y3), (x4, y4)], fill=inset_color)
        else:
            draw.rectangle([(x3, y3), (x4, y4)], fill=inset_color)

        if not cell.linked(cell.west):
            draw.rectangle([(x1, y1), (x2, y4)], fill=inset_color)
        else:
            draw.rectangle([(x1, y3), (x2, y4)], fill=inset_color)

        # Trace Walls
        if cell.linked(cell.north):
            draw.line([(x2, y1), (x2, y2)], fill=wall_color)
            draw.line([(x3, y1), (x3, y2)], fill=wall_color)
        else:
            draw.line([(x2, y2), (x3, y2)], fill=wall_color)

        if cell.linked(cell.east):
            draw.line([(x3, y2), (x4, y2)], fill=wall_color)
            draw.line([(x3, y3), (x4, y3)], fill=wall_color)
        else:
            draw.line([(x3, y2), (x3, y3)], fill=wall_color)

        if cell.linked(cell.south):
            draw.line([(x2, y3), (x2, y4)], fill=wall_color)
            draw.line([(x3, y3), (x3, y4)], fill=wall_color)
        else:
            draw.line([(x2, y3), (x3, y3)], fill=wall_color)

        if cell.linked(cell.west):
            draw.line([(x1, y2), (x2, y2)], fill=wall_color)
            draw.line([(x1, y3), (x2, y3)], fill=wall_color)
        else:
            draw.line([(x2, y2), (x2, y3)], fill=wall_color)

    def snapshot(self, grid, current_cell=None):
        image_width = self.cell_size * grid.columns
        image_height = self.cell_size * grid.rows

        img = Image.new("RGBA", (image_width, image_height), (224, 224, 224, 255))
        draw = ImageDraw.Draw(img)

        for cell in grid:
            cell_color = (255, 204, 204)

            if cell.visited == 'black':
                cell_color = (255, 255, 255)

            if cell.visited == 'grey':
                cell_color = (255, 204, 204)

            if cell.visited == 'white':
                cell_color = (192, 192, 192)

            if cell is current_cell:
                cell_color = (255, 153, 153)

            x = cell.column * self.cell_size
            y = cell.row * self.cell_size

            self.draw_cell(draw, cell, x, y, cell_color)

        del draw
        return img

class Open(object):
    @staticmethod
    def apply(grid):
        for cell in grid:
            for neighbor in cell.neighbors():
                cell.link(neighbor)


class RecursiveBacktrackingMaze(object):
    def __init__(self, grid, imager):
        self.grid = grid
        self.imager = imager
        self.snapshot_images = []
        self._build()

    def _build(self):
        start_cell = self.grid.random_cell()
        stack = [start_cell]

        while stack:
            cell = stack.pop()
            cell.visited = 'grey'

            available_cells = [neighbor for neighbor in cell.neighbors() if neighbor.visited == 'white']

            self._snapshot(current_cell=cell)

            while available_cells:
                next_cell = random.choice(available_cells)
                next_cell.visited = 'grey'
                cell.link(next_cell)
                stack.append(cell)
                stack.append(next_cell)
                cell = next_cell
                available_cells = [neighbor for neighbor in cell.neighbors() if neighbor.visited == 'white']

                self._snapshot(current_cell=cell)

            cell.visited = 'black'

        self._snapshot()

    def _snapshot(self, current_cell=None):
        img = self.imager.snapshot(self.grid, current_cell)
        self.snapshot_images.append(img)

    def save_animation(self, file_name="maze.gif"):
        img = self.snapshot_images[0]
        img.save(file_name, format="GIF", save_all=True, append_images=self.snapshot_images)

    def save_still(self, file_name="maze.gif"):
        img = self.snapshot_images[-1]
        img.save(file_name, format="GIF")


class Solver(object):
    def __init__(self, grid, imager):
        self.grid = grid
        self.imager = imager
        self.snapshot_images = []
        self._solve()

    def _solve(self):
        pass

    def _snapshot(self, current_cell=None):
        img = self.imager.snapshot(self.grid, current_cell)
        self.snapshot_images.append(img)

    def save_animation(self, file_name="maze.gif"):
        img = self.snapshot_images[0]
        img.save(file_name, format="GIF", save_all=True, append_images=self.snapshot_images)

    def save_still(self, file_name="maze.gif"):
        img = self.snapshot_images[-1]
        img.save(file_name, format="GIF")


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
                    cell.visited = 'grey'
                    frontier.append(cell)
                    came_from[cell] = current
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

    grid = Grid(20, 20)
    grid_imager = GridImager(cell_size=10, cell_inset=1)
    maze = RecursiveBacktrackingMaze(grid, grid_imager)
    #maze.save_animation()

    #grid = Grid(10, 10)
    #RecursiveBacktracking.apply(grid)

    #imager = GridImager()
    #img = imager.snapshot(grid)
    #img.save("maze.png", format="PNG")

    # maze = OpenMaze(grid)
    # maze.save_animation()

    grid.reset_visited()
    solver = BFSSolver(grid, GridImager(cell_size=20, cell_inset=1))
    solver.save_animation()



if __name__ == "__main__":
    execute()
