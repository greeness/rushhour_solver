from board import Block, Board, BoardFactory
import random
from bfs import BFS

class Generator:
    # accumulative probability
    P = {
        Block.BlockKinds.OBSTACLE: 0.05,
        Block.BlockKinds.PURPLE_CAR: 0.40,
        Block.BlockKinds.BLUE_CAR: 0.7,
        Block.BlockKinds.TRUCK:1.0
    }
    def __init__(self):
        self.board = Board()
    
    def GetAnObject(self, x, y):
        num = random.random()
        if num < Generator.P[Block.BlockKinds.OBSTACLE]:
            return Block(x, y, 1, Block.BlockKinds.OBSTACLE, False);
        if num < Generator.P[Block.BlockKinds.PURPLE_CAR]:
            return Block(x, y, 2, Block.BlockKinds.PURPLE_CAR, True)
        if num < Generator.P[Block.BlockKinds.BLUE_CAR]:
            return Block(x, y, 2, Block.BlockKinds.BLUE_CAR, False)
        
        if random.randint(1,10) <= 3:
            return Block(x, y, 3, Block.BlockKinds.TRUCK, True)
        return Block(x, y, 3, Block.BlockKinds.TRUCK, False)
        
    def Assemble(self):
        while True:
            self.board.Clear()
            # first place the delivery car at the exit
            self.board.AddDelivery(4, 2)
            num_tries = 0
            # filling in object until we think there are enough
            while len(self.board._blocks) <= random.randint(9,12):
                # pick a position to place the next object
                x = random.randint(0, 5)
                y = random.randint(0, 5)
                obj = self.GetAnObject(x, y)
                if (x <= 4 and y == 2 and (obj._kind == Block.BlockKinds.OBSTACLE or
                                           obj._isVertical)):
                    continue
                num_tries += 1               
                if self.board.IsBlockAddable(obj):
                    self.board.AddBlock(obj)
            minSteps = BFS(self.board, visitAll=False)
            if minSteps >= 15:
                print "Found a board with %d moves" % minSteps
                self.board.PrintData()
                self.board.PrintBlocksInfo()

if __name__ == "__main__":
    #random.seed(0)
    bg = Generator()
    bg.Assemble()
    print "Done"