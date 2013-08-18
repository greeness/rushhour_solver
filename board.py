import copy
import sys

""" Represent an enum type in python """
class Enum(set):
    def __getattr__(self, name):
        if name in self:
            return name
        raise AttributeError

"""
Available car types:
Cyan truck: 1x3 or 3x1
Purple car: 2x1
Blue car: 1x2
Green plant: 1x1
"""
class Block :
    """ Block is a building component of a board:
        - Each block consists at least one tile;
        - A block's position is defined by its upper-left corner coordinate
          (x,y) plus its length.
        - A block has its length and in current version every tile can only be
          1xn or nx1 in size. We use row-priority, so 1xn is a horizontal block
          while nx1 is a vertical block;
        - A block is movable or not (Plants are not movable)
        - A block is erasable or not (erased by a bomb for example);
        - A block is rotatable or not (use a power-up to rotate a block by 90 
          degrees; could be a possible extension
    """
    ObjNames = "*ABCDEFGHIJKLMNOPQRSTUVWXY"
    # We have three block types initially:
    #    D: the delivery car
    #    Truck: other movable cars
    #    Obstacle: fixed obstacles, eg. plants """
    BlockKinds = Enum(["D", "BLUE_CAR", "PURPLE_CAR", 
                       "TRUCK", "OBSTACLE", "EMPTY"])
    
    # static class variable to uniquely identify a block
    _id = 0
    def __init__(self, x, y, length, kind, isVertical=True, myid=-1):
        assert(0 <= y < Board.Size)
        self._y = y
        assert(0 <= x < Board.Size)
        self._x = x
        self._kind = kind
        assert(1 <= length <= 3)
        self._length = length
        self._isVertical = isVertical
        if myid == -1:
            self._id = Block._id
            Block._id += 1
        else:
            self._id = myid
        if self._kind == Block.BlockKinds.OBSTACLE:
            self._isMovable = False
            self._isErasable = True
        else:
            self._isMovable = True
            self.IsErasable = False
        self._name = Block.ObjNames[self._id]
        
    def __hash__(self):
        """
        10 bits are enough to decode a block at a unique position
        3 bit |3 bit |1 | 2 bits|1   bit     |
        +------------------------------------+
        |  x  |  y  |dir|length | isDelivery |
        +------------------------------------+
        We don't need to take into account the block id. For example, in below two
        configurations, the block B in the left will be hashed to the same code
        as the block A in the right. Since these two configurations are essentially
        identical, so our hashing works perfect to treat them as the same.         
        
         +-----    --------+    +-----    --------+
        0|BB AA            |0   |AA BB            |0
        1|BB AA            |1   |AA BB            |1
        2|                 |2   |                 |2
        3|                 |3   |                 |3
        4|--    ** GG GG GG|4   |--    ** GG GG GG|4
        5|      ** --    --|5   |      ** --    --|5
        +-----------------+     +-----------------+  
        """
        return (self._x << 7) | (self._y << 4) | (self._isVertical << 3) | \
               (self._length << 1) | (self._kind == Block.BlockKinds.D)
    
    def __cmp__(self, other):
        return cmp(hash(self), hash(other))

class Move: 
    Direction = Enum(["UP", "DOWN", "LEFT", "RIGHT"])
    def __init__(self, blockId, direction, steps):
        self._blockId = blockId
        self._direction = direction
        self._steps = steps

class Board:
    Size = 6
    def __init__(self):
        self.Clear()
        
    def Clear(self):
        self._data = [[' ' for _ in xrange(Board.Size)] 
                        for _ in xrange(Board.Size)]
        self._blocks = []
        
    def AddBlue(self, x, y):
        self._blocks.append(Block(x, y, 2, 
                                  Block.BlockKinds.BLUE_CAR, False))
    def AddPlant(self, x, y):
        self._blocks.append(Block(x, y, 1, 
                                  Block.BlockKinds.OBSTACLE, False))
        
    def AddDelivery(self, x, y):
        self._blocks.append(Block(x, y, 2,
                                  Block.BlockKinds.D, True))
        
    def AddPurple(self, x, y):
        self._blocks.append(Block(x, y, 2, 
                                  Block.BlockKinds.PURPLE_CAR, True))
    
    def AddTruck(self, x, y, isVertical=True):
        self._blocks.append(Block(x, y, 3, 
                                  Block.BlockKinds.TRUCK, isVertical))        
    
    def IsEndingState(self):
        for block in self._blocks:
            if (block._kind == Block.BlockKinds.D and 
                block._x == 0 and block._y == 2):
                return True
        return False
    
    def TryMove1(self, blockId, direction):
        #print "Checking: Move block %s and try direction %s" \
        #    %(Block.ObjNames[blockId], direction)
        assert 0 <= blockId < len(self._blocks)
        block = self._blocks[blockId]
        assert block._kind != Block.BlockKinds.OBSTACLE
        assert \
            (block._isVertical == True and \
            (direction == Move.Direction.UP or direction == Move.Direction.DOWN)) or \
            (block._isVertical == False and \
            (direction == Move.Direction.LEFT or direction == Move.Direction.RIGHT))
        
        if direction == Move.Direction.LEFT:
            if block._y == 0:
                #print " = Touching left border, cannot move left any more"
                return None
            if self._data[block._x][block._y-1] != ' ':
                #print " = There is no empty space to move left"
                return None
            #print " = Moved block %s to left: (%d,%d)" \
            #    % (Block.ObjNames[block._id], block._x, block._y-1)
            return Block(block._x, block._y-1, block._length, 
                         block._kind, block._isVertical, block._id)
            
        if direction == Move.Direction.RIGHT:
            if block._y + block._length == Board.Size:
                #print " = Touching right border, cannot move right any more"
                return None
            if self._data[block._x][block._y + block._length] != ' ':
                #print " = There is no empty space to move right"
                return None
            #print " = Moved block %s to right: (%d,%d)" \
            #    % (Block.ObjNames[block._id], block._x, block._y+1)
            return Block(block._x, block._y+1, block._length, 
                         block._kind, block._isVertical, block._id)
        if direction == Move.Direction.DOWN:
            if block._x + block._length == Board.Size:
                #print " = Touching bottom border, cannot move down any more"
                return None
            if self._data[block._x+block._length][block._y] != ' ':
                #print " = There is no empty space to move right"
                return None
            #print " = Moved block %s to down: (%d, %d)" \
            #    % (Block.ObjNames[block._id], block._x+1, block._y)
            return Block(block._x+1, block._y, block._length, 
                         block._kind, block._isVertical, block._id)
        # Since we will always use /IsEndingState/ to check, we assume we are never
        # at a ending_move state here.
        if direction == Move.Direction.UP:
            if block._x == 0:
                #print " = Touching top border, cannot move up any more"
                return None
            if self._data[block._x-1][block._y] != ' ':
                #print " = There is no empty space to move up"
                return None
            #print " = Moved block %s to up: (%d, %d)" \
            #    % (Block.ObjNames[block._id], block._x-1, block._y)
            return Block(block._x-1, block._y, block._length, 
                         block._kind, block._isVertical, block._id)
   
    def Move(self):
        actionQueue = []
        for block in self._blocks:
            if block._kind == Block.BlockKinds.OBSTACLE:
                continue
            # for an object that is vertical, try moving up/down
            if block._isVertical:
                    actionQueue.append((block._id, Move.Direction.UP))
                    actionQueue.append((block._id, Move.Direction.DOWN))
            # for an object that is horizontal, try moving left/right
            else:
                    actionQueue.append((block._id, Move.Direction.LEFT))
                    actionQueue.append((block._id, Move.Direction.RIGHT))
        
        newBoardQueue = []
        for (blockId, direction) in actionQueue:
            newBlock = self.TryMove1(blockId, direction)
            if newBlock:
                newBoard = copy.deepcopy(self)
                newBoard.ClearBlockInData(blockId)
                newBoard._blocks[blockId] = newBlock
                newBoard.AddBlockInData(blockId)
                #print " = A new state is found with hash code %d" % hash(newBoard)
                newBoardQueue.append((blockId, direction, newBoard))
                    
        return newBoardQueue
                    
    def ClearBlockInData(self, blockId):
        block = self._blocks[blockId]
        if not block._isVertical:
            for i in xrange(block._length):
                self._data[block._x][block._y+i] = ' '
        else:
            for i in xrange(block._length):
                self._data[block._x+i][block._y] = ' '
    
    def AddBlockInData(self, blockId):
        block = self._blocks[blockId]
        if block._kind == Block.BlockKinds.EMPTY:
            c = ' '
        elif block._kind == Block.BlockKinds.OBSTACLE: 
            c = '-'
        else:
            c = Block.ObjNames[block._id]
        
        if not block._isVertical:
            for i in xrange(block._length):
                self._data[block._x][block._y+i] = c
        else:
            for i in xrange(block._length):
                self._data[block._x+i][block._y] = c        
    def BlocksToData(self):
        self._data = [[' ' for _ in xrange(Board.Size)] 
                        for _ in xrange(Board.Size)]
        for block in self._blocks:
            self.AddBlockInData(block._id)
            
    def PrintData(self):
        self.BlocksToData()
        sys.stdout.write('  0  1  2  3  4  5\n');    
        sys.stdout.write(''.join([' +', '-'*5, '    ', '-'*8, '+\n']))
        for i in xrange(Board.Size*Board.Size):
            if i % Board.Size == 0: 
                sys.stdout.write('%d|' % (i/Board.Size))
            c = self._data[i/Board.Size][i%Board.Size]
            sys.stdout.write("%s%s" % (c,c))
            if i % Board.Size == Board.Size-1: 
                sys.stdout.write("|%d\n" % (i/Board.Size))
            else: sys.stdout.write(' ')
        sys.stdout.write(''.join([' +', '-'*17, '+\n']))   
        sys.stdout.write('  0  1  2  3  4  5\n');   
           
    def PrintBlocksInfo(self):
        print "Totally %d Known objects on Board; board hash value %d" \
            % (len(self._blocks), hash(self))
        for block in sorted(self._blocks):
            print "ID: %2d, Name: %s, Type: %12s At (%d,%d), Length %d, hash %d" \
                % (block._id, Block.ObjNames[block._id], \
                   block._kind, block._x, block._y, block._length, hash(block))
            
    def __hash__(self):
        """ To create a hash for a board, just add each block to construct a tuple 
        sorted by block's hash value; To simplify the hash, we can skip those fixed
        objects since they never change their positions. However, if we later introduce
        the bomb, this assumption will be violated. So for now, I will include all objects
        in a board state hash.
        """
        hashable_state = []
        for block in sorted(self._blocks):
            hashable_state.append(hash(block))
        return hash(tuple(hashable_state))

class BoardFactory:
    @staticmethod
    def CreateEasyBoard():
        b = Board();
        
        b.AddDelivery(4,2)
        b.AddTruck(0,0,False)
        b.AddBlue(1,1)
        b.AddBlue(2,0)
        b.AddBlue(2,4)
        b.AddPurple(0,5)
        b.AddTruck(2, 3, True)
        b.AddTruck(3, 0, True)
        b.AddTruck(5, 3, False) 
        b.PrintData()
        b.PrintBlocksInfo()
        return b
    @staticmethod
    def CreateHardBoard2():
        b = Board()
        b.AddDelivery(2,2)
        b.AddTruck(0,0,False)
        b.AddTruck(1,0,False)
        b.AddPurple(0,4)
        b.AddPurple(0,5)
        b.AddPurple(2,5)
        b.AddPurple(4,3)
        b.AddPurple(3,1)
        b.AddBlue(2,0)
        b.AddBlue(3,3)
        b.AddBlue(4,4)
        b.AddBlue(5,1)
        b.AddTruck(3,0)
        
        b.PrintData()
        b.PrintBlocksInfo()
        return b
    @staticmethod
    def CreateHardBoard1():
        b = Board()
        b.AddDelivery(4,2)
        b.AddTruck(0,0)
        b.AddTruck(0,1,False)
        b.AddTruck(1,1)
        b.AddBlue(1,2)
        b.AddBlue(2,2)
        b.AddBlue(3,2)
        b.AddBlue(2,4)
        b.AddBlue(5,0)
        b.AddPurple(0,4)
        b.AddPurple(3,5)
        b.AddPurple(4,3)
        
        b.PrintData()
        b.PrintBlocksInfo()
        return b
    
    @staticmethod
    def CreateHardBoard():
        b = Board();
        b.AddDelivery(4,2)
        b.AddPurple(0,0)
        b.AddPurple(0,3)
        b.AddPurple(1,5)
        b.AddBlue(0,4)
        b.AddBlue(1,1)
        b.AddBlue(2,0)
        b.AddBlue(2,2)
        b.AddTruck(1,4)
        b.AddBlue(3,2)
        b.AddPurple(3,1)
        b.AddPurple(4,3)
        b.AddBlue(5,4)
        b.PrintData()
        b.PrintBlocksInfo()
        return b

def TestTryMove():
    b = BoardFactory.CreateEasyBoard()
    for (blockId, direction, board) in b.Move():
        print "="*80, "before Moving"
        b.PrintData()
        print "Move %s to %s, resulting ..." % (board._blocks[blockId]._name, direction)
        board.PrintData()    
        
if __name__ == "__main__":
    TestTryMove()