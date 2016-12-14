import sys, random, StringIO
from PIL import Image, ImageDraw


class Cell(object):
    def __init__(self, row, col):
        self.N = True
        self.E = True
        self.S = True
        self.W = True
        self.row = row
        self.col = col

        self.visited = 'white'


class Maze(object):
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.grid = [[Cell(row, col) for col in range(width)] for row in range(height)]

    def connect_cells(self, cell, direction):
        if direction == 'N':
            if cell.row > 0:
                cell.N = False
                self.grid[cell.row - 1][cell.col].S = False

        elif direction == 'E':
            if cell.col + 1 < len(self.grid[0]):
                cell.E = False
                self.grid[cell.row][cell.col + 1].W = False

        elif direction == 'S':
            if cell.row + 1 < len(self.grid):
                cell.S = False
                self.grid[cell.row + 1][cell.col].N = False

        elif direction == 'W':
            if cell.col > 0:
                cell.W = False
                self.grid[cell.row][cell.col - 1].E = False

        else:
            return

        return


def execute():

    def fill_cell(draw, cell, color=(0,0,0)):
        x = (cell.col * cell_size) + grid_offset + 1
        y = (cell.row * cell_size) + grid_offset + 1

        draw.rectangle([(x, y), (x + cell_size - 1, y + cell_size - 1)], fill=color)


    def outline_cell(draw, cell, color=(0,0,0)):
        x = (cell.col * cell_size) + grid_offset
        y = (cell.row * cell_size) + grid_offset

        if cell.N:
            draw.line([(x, y), (x + cell_size, y)], fill=color)

        if cell.E:
            draw.line([(x + cell_size, y), (x + cell_size, y + cell_size)], fill=color)

        if cell.S:
            draw.line([(x + cell_size, y + cell_size), (x, y + cell_size)], fill=color)

        if cell.W:
            draw.line([(x, y + cell_size), (x, y)], fill=color)


    def draw_maze(current_cell, maze, last=False):
        img = Image.new("RGBA", (image_width, image_height), (192,192,192))
        draw = ImageDraw.Draw(img)

        for row in maze.grid:
            for cell in row:
                #Fill Cell
                if cell.visited == 'black':
                    fill_cell(draw, cell, color=(255,255,255))

                if cell.visited == 'grey':
                    fill_cell(draw, cell, color=(255,204,204))

                if cell.visited == 'white':
                    fill_cell(draw, cell, color=(192,192,192))

                # Outline Cell
                outline_cell(draw, cell, color=(0,0,0))

        if not last:
            fill_cell(draw, current_cell, color=(255, 153, 153))

        del draw
        return img


    def get_available_cells(cell, maze):
        i = cell.row
        j = cell.col
        w = maze.width
        h = maze.height
        available_cells = []

        if i > 0:
            next_cell = maze.grid[i - 1][j]
            if next_cell.visited == 'white':
                available_cells.append((next_cell, 'N'))

        if j + 1 < w:
            next_cell = maze.grid[i][j + 1]
            if next_cell.visited == 'white':
                available_cells.append((next_cell, 'E'))

        if i + 1 < h:
            next_cell = maze.grid[i + 1][j]
            if next_cell.visited == 'white':
                available_cells.append((next_cell, 'S'))

        if j > 0:
            next_cell = maze.grid[i][j - 1]
            if next_cell.visited == 'white':
                available_cells.append((next_cell, 'W'))

        return available_cells


    def create_maze(start_cell, maze, image_list=None):
        stack = [start_cell]

        if not image_list:
            image_list = []

        while stack:
            cell = stack.pop()
            cell.visited = 'grey'
            image_list.append(draw_maze(cell, maze))

            available_cells = get_available_cells(cell, maze)
            while available_cells:
                image_list.append(draw_maze(cell, maze))
                next_cell, direction = available_cells[random.randint(0, len(available_cells)-1)]
                maze.connect_cells(cell, direction)
                next_cell.visited = 'grey'
                stack.append(cell)
                stack.append(next_cell)
                available_cells = get_available_cells(next_cell, maze)
                cell = next_cell

            cell.visited = 'black'

        # Entry and Exit Points
        maze.grid[0][0].N = False
        maze.grid[maze.height-1][maze.width-1].S = False

        image_list.append(draw_maze(start_cell, maze, last=True))

        return image_list

    cell_size = 25
    maze_width = 25
    maze_height = 25
    maze = Maze(maze_width, maze_height)

    grid_offset = 0
    image_width = (maze_width * cell_size) + (grid_offset * 2) + 1
    image_height = (maze_height * cell_size) + (grid_offset * 2) + 1

    img = Image.new("RGBA", (image_width, image_height), (192,192,192))

    # Random Starting Cell
    start_x = random.randint(0, maze.height-1)
    start_y = random.randint(0, maze.width-1)
    start_cell = maze.grid[start_x][start_y]

    step_images = create_maze(start_cell, maze)

    img.save(sys.stdout, format="GIF", save_all=True, append_images=step_images, loop=True)

if __name__ == "__main__":
    execute()
