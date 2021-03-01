from lib import *
from sys import argv

class BestPath:
    def __init__(self, rows=5, cols=5):
        self.screen_width = 800
        self.screen_height = 600
        self.board_rows = rows
        self.board_cols = cols
        self.board_gap = 1
        self.board_pos = (0,0)
        self.block_size = 50
        self.agents = sprite.Group()
        self.goals = sprite.Group()
        self.wall_factory = None
        self.board = None
        self.screen = None
        self.running = False
        self.agent_center = (0,0)
        self.goal_center = (0,0)
        self.wall_center = (0,0)
        self.clock = None
        self.speed = 100
        
        self.bfs_button = None
        self.bfs_button_center = (0,0)
        self.dfs_button = None
        self.dfs_button_center = (0,0)
        self.reset_button = None
        self.reset_button_center = (0,0)

        self.bfs_cost = 0
        self.dfs_cost = 0

        self.bfs_text = None
        self.bfs_text_pos = (0,0)
        self.dfs_text_pos = (0,0)
        self.dfs_text = None
        self.text_color = (0,0,0)
        self.text_size = 12

        self.font = None

    def __del__(self):
        pg.quit()

    def _positionate(self):
        board_width = self.board_cols * (self.block_size + self.board_gap) - self.board_gap
        board_height = self.board_rows * (self.block_size + self.board_gap) - self.board_gap

        if board_height <= 400:
            self.screen_height = 500
            self.board_pos = (25, round(self.screen_height - 1.5*board_height))
        else:
            self.screen_height = board_height + 50
            self.board_pos = (25,25)
        self.screen_width = board_width + 150        

        self.bfs_button_center = (self.screen_width-55, 35)
        self.dfs_button_center = (self.screen_width-55, 85)
        self.reset_button_center = (self.screen_width-55, 135)
        self.bfs_text_pos = (self.screen_width-110, 175)
        self.dfs_text_pos = (self.screen_width-110, 225)
        self.agent_center = (self.screen_width-50, 300)
        self.goal_center = (self.screen_width-50, 350)
        self.wall_center = (self.screen_width-50, 400)

    def create_agent(self):
        new_agent = Agent(self.block_size)
        new_agent.set_center(self.agent_center)
        new_agent.set_board(self.board)
        self.agents.add(new_agent)

    def create_goal(self):
        new_goal = Goal(self.block_size)
        new_goal.set_center(self.goal_center)
        new_goal.set_board(self.board)
        self.goals.add(new_goal)

    def create_wall_factory(self):
        self.wall_factory = WallFactory(self.block_size)
        self.wall_factory.set_board(self.board)
        self.wall_factory.set_center(self.wall_center)
    
    def init(self):
        self._positionate()
        pg.init()
        pg.display.set_caption("Best Path")
        pg.font.init()
        self.font = pg.font.SysFont('Arial', self.text_size)
        self.bfs_text = self.font.render('BFS BP: 0  V: 0',True,self.text_color)
        self.dfs_text = self.font.render('DFS BP: 0  V: 0',True,self.text_color)
        self.screen = pg.display.set_mode((self.screen_width, self.screen_height))
        self.board = Board(self.board_rows, self.board_cols, self.block_size, self.board_gap)
        self.board.set_pos(self.board_pos[0], self.board_pos[1])
        self.board.draw()
        self.board.update()

        bfs_surf = img_load(str(assets/Path("BFS.png")),100,50)
        bfs_surf.set_colorkey((0, 0, 0), RLEACCEL)
        self.bfs_button = Button(bfs_surf)
        self.bfs_button.set_center(self.bfs_button_center)
        self.bfs_button.mouse_signal = self._solve_bfs_signal

        dfs_surf = img_load(str(assets/Path("DFS.png")),100,50)
        dfs_surf.set_colorkey((0, 0, 0), RLEACCEL)
        self.dfs_button = Button(dfs_surf)
        self.dfs_button.set_center(self.dfs_button_center)
        self.dfs_button.mouse_signal = self._solve_dfs_signal

        reset_surf = img_load(str(assets/Path("Reset.png")),100,50)
        reset_surf.set_colorkey((0, 0, 0), RLEACCEL)
        self.reset_button = Button(reset_surf)
        self.reset_button.set_center(self.reset_button_center)
        self.reset_button.mouse_signal = self._reset_signal

        self.running = True

    def loop(self):
        if self.running:
            for event in pg.event.get():
                if event.type == KEYDOWN:
                    if event.key == K_ESCAPE:
                        self.running = False
                
                elif event.type == QUIT:
                    self.running = False

                DragSprite.loop(event)
                Button.loop(event)

            self.screen.fill((135, 206, 250))

            self.board.blit(self.screen)
            DragSprite.blit(self.screen)
            Button.blit(self.screen)
            self.screen.blit(self.bfs_text,self.bfs_text_pos)
            self.screen.blit(self.dfs_text,self.dfs_text_pos)
            
            pg.display.flip()
        return self.running

    def reset(self):
        for row in self.board:
            for i in row:
                i.draw_grass()

    def quit(self):
        pg.quit()


    def solve_bfs(self, start: BoardPosition):
        self.reset()
        queue = [[start]]
        visited = []

        if start.type == BoardPosition.Type.GOAL:
            queue = []
            visited = [start]
            solution = [start]

        solution = None
        while queue:
            path = queue.pop(0)
            node = path[-1]
            if node not in visited:
                ng = self.board.node(node)
                for n in ng:
                    new_path = list(path)
                    new_path.append(n)
                    queue.append(new_path)
                    if n.type == BoardPosition.Type.GOAL:
                        solution = new_path
                        break
                visited.append(node)
                if solution is not None:
                    visited.append(solution[-1])
                    break
        
        if solution is None:
            print("No solution found!")
            return

        self.bfs_text = self.font.render(f'BFS BP: {len(solution)}  V: {len(visited)}',True,self.text_color)
        
        for i in visited:
            i.draw_path()
            t = pg.time.get_ticks()
            while (pg.time.get_ticks() - t) <= self.speed:
                if not self.loop():
                    return

        for i in solution:
            i.draw_solution()
            t = pg.time.get_ticks()
            while (pg.time.get_ticks() - t) <= self.speed:
                if not self.loop():
                    return
        


    def _dfs_recursion(self, start, visited, path):
        visited.append(start)
        path.append(start)

        if start.type == BoardPosition.Type.GOAL:
            return path
        
        else:
            ng = self.board.node(start)
            for n in ng:
                if n not in visited:
                    ret = self._dfs_recursion(n,visited,path)
                    if len(ret) > 0:
                        return ret

        path.pop()
        return []


    def solve_dfs(self, start: BoardPosition):
        self.reset()
        visited = []
        path = []

        path = self._dfs_recursion(start,visited,path)

        if len(path) == 0:
            print("No solution found!")
            return

        self.dfs_text = self.font.render(f'DFS BP: {len(path)}  V: {len(visited)}',True,self.text_color)
        
        for i in visited:
            i.draw_path()
            t = pg.time.get_ticks()
            while (pg.time.get_ticks() - t) <= self.speed:
                if not self.loop():
                    return

        for i in path:
            i.draw_solution()
            t = pg.time.get_ticks()
            while (pg.time.get_ticks() - t) <= self.speed:
                if not self.loop():
                    return


    def _solve_bfs_signal(self, button, event):
        if event == MOUSEBUTTONDOWN:
            button.surf = img_load(str(assets/Path("BFS_clicked.png")),100,50)
            button.surf.set_colorkey((0, 0, 0), RLEACCEL)
            try:
                self.solve_bfs(self.agents.sprites()[0].pos)
            except:
                print("BFS Failed!")

        elif event == MOUSEBUTTONUP:
            button.surf = img_load(str(assets/Path("BFS.png")),100,50)
            button.surf.set_colorkey((0, 0, 0), RLEACCEL)

    def _solve_dfs_signal(self, button, event):
        if event == MOUSEBUTTONDOWN:
            button.surf = img_load(str(assets/Path("DFS_clicked.png")),100,50)
            button.surf.set_colorkey((0, 0, 0), RLEACCEL)
            try:
                self.solve_dfs(self.agents.sprites()[0].pos)
            except:
                print("DFS Failed!")
        elif event == MOUSEBUTTONUP:
            button.surf = img_load(str(assets/Path("DFS.png")),100,50)
            button.surf.set_colorkey((0, 0, 0), RLEACCEL)

    def _reset_signal(self, button, event):
        if event == MOUSEBUTTONDOWN:
            button.surf = img_load(str(assets/Path("Reset_clicked.png")),100,50)
            button.surf.set_colorkey((0, 0, 0), RLEACCEL)
            self.reset()
        elif event == MOUSEBUTTONUP:
            button.surf = img_load(str(assets/Path("Reset.png")),100,50)
            button.surf.set_colorkey((0, 0, 0), RLEACCEL)

        
if __name__=="__main__":
    rows = 8
    cols = 5

    if len(argv) == 3:
        rows = int(argv[1])
        cols = int(argv[2])

    bp = BestPath(rows,cols)
    bp.init()
    bp.create_agent()
    bp.create_goal()
    bp.create_wall_factory()
    while bp.loop():
        pass
