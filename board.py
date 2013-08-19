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
    #_id = 0
    def __init__(self, x, y, length, kind, isVertical=True):
        assert(0 <= y < Board.Size)
        self._y = y
        assert(0 <= x < Board.Size)
        self._x = x
        self._kind = kind
        assert(1 <= length <= 3)
        self._length = length
        self._isVertical = isVertical
        if self._kind == Block.BlockKinds.OBSTACLE:
            self._isMovable = False
            self._isErasable = True
        else:
            self._isMovable = True
            self.IsErasable = False
        self._id = -1
        self._name = ""
        
        
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

class Board:
    Size = 6
    Direction = Enum(["UP", "DOWN", "LEFT", "RIGHT"])
    def __init__(self):
        self.Clear()
        
    def Clear(self):
        """ Reset the internal data and block list """
        self._data = [[' ' for _ in xrange(Board.Size)] 
                        for _ in xrange(Board.Size)]
        self._blocks = []
        
    def IsBlockAddable(self, block):
        if not block._isVertical:
            for i in xrange(block._length):
                # We cannot add a block to contains an non-empty tile
                if block._y+i >= Board.Size or self._data[block._x][block._y+i] != ' ':
                    return False                
        else:
            for i in xrange(block._length):
                if block._x+i >= Board.Size or self._data[block._x+i][block._y] != ' ':
                    return False
        return True
    
    def AddBlock(self, block):
        """ Add a building block to the board """
        block._id = len(self._blocks)
        block._name = Block.ObjNames[block._id]
        self._blocks.append(block)
        self.AddBlockInData(block._id)
               
    def AddBlue(self, x, y):
        self.AddBlock(Block(x, y, 2, 
                            Block.BlockKinds.BLUE_CAR, False))
    def AddPlant(self, x, y):
        self.AddBlock(Block(x, y, 1, 
                            Block.BlockKinds.OBSTACLE, False))
        
    def AddDelivery(self, x, y):
        self.AddBlock(Block(x, y, 2,
                            Block.BlockKinds.D, True))
        
    def AddPurple(self, x, y):
        self.AddBlock(Block(x, y, 2, 
                      Block.BlockKinds.PURPLE_CAR, True))
    
    def AddTruck(self, x, y, isVertical=True):
        self.AddBlock(Block(x, y, 3, 
                            Block.BlockKinds.TRUCK, isVertical))        
    
    def IsEndingState(self):
        """ Check if we are at the state that is ending the game successfully """
        for block in self._blocks:
            if (block._kind == Block.BlockKinds.D and 
                block._x == 0 and block._y == 2):
                return True
        return False
    
    def ReplaceBlock(self, blockId, block):
        self.ClearBlockInData(blockId)
        block._id = blockId
        block._name = Block.ObjNames[blockId]
        self._blocks[blockId] = block
        self.AddBlockInData(blockId)
    
    def TryMove(self, blockId, direction):
        """ Try to move a given block in the specified direction by 1 step.
            If we cannot move in such a direction (border constrain, blocked by other cars,
              return None.
            Otherwise, return the new block object after moving.
        """
        assert 0 <= blockId < len(self._blocks)
        block = self._blocks[blockId]
        assert block._kind != Block.BlockKinds.OBSTACLE
        assert \
            (block._isVertical == True and \
            (direction == Board.Direction.UP or direction == Board.Direction.DOWN)) or \
            (block._isVertical == False and \
            (direction == Board.Direction.LEFT or direction == Board.Direction.RIGHT))
        
        if direction == Board.Direction.LEFT:
            if block._y == 0:
                return None
            if self._data[block._x][block._y-1] != ' ':
                return None
            return Block(block._x, block._y-1, block._length, 
                         block._kind, block._isVertical)
            
        if direction == Board.Direction.RIGHT:
            if block._y + block._length == Board.Size:
                return None
            if self._data[block._x][block._y + block._length] != ' ':
                return None
            return Block(block._x, block._y+1, block._length, 
                         block._kind, block._isVertical)
        if direction == Board.Direction.DOWN:
            if block._x + block._length == Board.Size:
                return None
            if self._data[block._x+block._length][block._y] != ' ':
                return None
            return Block(block._x+1, block._y, block._length, 
                         block._kind, block._isVertical)
        # Since we will always use /IsEndingState/ to check, we assume we are never
        # at a ending_move state here.
        if direction == Board.Direction.UP:
            if block._x == 0:
                return None
            if self._data[block._x-1][block._y] != ' ':
                return None
            return Block(block._x-1, block._y, block._length, 
                         block._kind, block._isVertical)
   
    def Move(self):
        """ For a given board state, try every possible moving action for any movable
        object. 
        Return a list of (blockId, new Board) resulting from any possible moves. 
        """
        actionQueue = []
        for block in self._blocks:
            if block._kind == Block.BlockKinds.OBSTACLE:
                continue
            # for an object that is vertical, try moving up/down
            if block._isVertical:
                actionQueue.append((block._id, Board.Direction.UP))
                actionQueue.append((block._id, Board.Direction.DOWN))
            # for an object that is horizontal, try moving left/right
            else:
                actionQueue.append((block._id, Board.Direction.LEFT))
                actionQueue.append((block._id, Board.Direction.RIGHT))
        
        newBoardQueue = []
        for (blockId, direction) in actionQueue:
            # Apply the move opeartion in the given direction
            newBlock = self.TryMove(blockId, direction)
            if newBlock:
                newBoard = copy.deepcopy(self)
                # Update the 2-d data in the new Board
                newBoard.ReplaceBlock(blockId, newBlock)
                newBoardQueue.append((blockId, newBoard))
        return newBoardQueue
                    
    def ClearBlockInData(self, blockId):
        """ Used after a block is moved to clear the 2-d tile """
        block = self._blocks[blockId]
        if not block._isVertical:
            for i in xrange(block._length):
                self._data[block._x][block._y+i] = ' '
        else:
            for i in xrange(block._length):
                self._data[block._x+i][block._y] = ' '
    
    def AddBlockInData(self, blockId):
        """ Used after a new block is added or a block is moved to update
        the 2d tiles"""
        block = self._blocks[blockId]
        if block._kind == Block.BlockKinds.EMPTY:
            c = ' '
        elif block._kind == Block.BlockKinds.OBSTACLE: 
            c = '-'
        else:
            c = block._name
        if not block._isVertical:
            for i in xrange(block._length):
                # We cannot add a block to contains an non-empty tile
                assert self._data[block._x][block._y+i] == ' '
                self._data[block._x][block._y+i] = c
        else:
            for i in xrange(block._length):
                assert self._data[block._x+i][block._y] == ' '
                self._data[block._x+i][block._y] = c        
    
    def BlocksToData(self):
        """ Refresh the 2d tile data completed according to the current block list"""
        self._data = [[' ' for _ in xrange(Board.Size)] 
                        for _ in xrange(Board.Size)]
        for block in self._blocks:
            self.AddBlockInData(block._id)
            
    def PrintData(self):
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
            print "ID: %2d, Name: %s, Type: %12s At (%d,%d), Length %d, IsVertical %d, hash %d" \
                % (block._id, block._name, \
                   block._kind, block._x, block._y, block._length, block._isVertical, hash(block))
            
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
        """
          0  1  2  3  4  5
         +-----    --------+
        0|AA AA AA       EE|0
        1|   BB BB       EE|1
        2|CC CC    FF DD DD|2
        3|GG       FF      |3
        4|GG    ** FF      |4
        5|GG    ** HH HH HH|5
         +-----------------+
          0  1  2  3  4  5
        """
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
        """
          0  1  2  3  4  5
         +-----    --------+
        0|AA AA AA    CC DD|0
        1|BB BB BB    CC DD|1
        2|HH HH **       EE|2
        3|LL GG ** II II EE|3
        4|LL GG    FF JJ JJ|4
        5|LL KK KK FF      |5
         +-----------------+
          0  1  2  3  4  5
        """
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
        """
          0  1  2  3  4  5
         +-----    --------+
        0|AA BB BB BB II   |0
        1|AA CC DD DD II   |1
        2|AA CC EE EE GG GG|2
        3|   CC FF FF    JJ|3
        4|      ** KK    JJ|4
        5|HH HH ** KK      |5
         +-----------------+
          0  1  2  3  4  5
        """
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
        """
          0  1  2  3  4  5
         +-----    --------+
        0|AA       BB DD DD|0
        1|AA EE EE BB HH CC|1
        2|FF FF GG GG HH CC|2
        3|   JJ II II HH   |3
        4|   JJ ** KK      |4
        5|      ** KK LL LL|5
         +-----------------+
          0  1  2  3  4  5
        """        
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
    for (blockId, board) in b.Move():
        print "="*80, "before Moving"
        b.PrintData()
        print "Move %s , resulting ..." % (board._blocks[blockId]._name)
        board.PrintData()    
        
if __name__ == "__main__":
    TestTryMove()
    