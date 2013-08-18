from collections import deque
from board import BoardFactory

def BFS():
    board = BoardFactory.CreateHardBoard2()
    queue = deque()
    # -1 indicates the starting state
    queue.append((-1, None, board, 0))
    seen = set()
    seen.add(hash(board))
    boardId = 0
    met_dups = 0
    visited = 0
    found = False
    
    while queue:
        blockId, direction, board, depth = queue.popleft()
        # check if b is the ending state
        visited += 1
        if board.IsEndingState():
            # let's trace back
            if not found:
                print "Food Delivered in %d steps after visiting %d states" \
                    % (depth, visited)
                found = True
        
        for (blockId, direction, new_board) in board.Move():
            if hash(new_board) not in seen:
                queue.append((blockId, direction, new_board, depth+1))
                seen.add(hash(new_board))
                #print '=' * 80
                #b.PrintData()
                #print "Move %s to %s " % (Block.ObjNames[blockId], direction)
                #new_board.PrintData()
                boardId += 1
                if (boardId % 100 == 0):
                    print "visited %d, depth %d, queue size %d, boardId %d, met dups %d times"  \
                        % (visited, depth, len(queue), boardId, met_dups)
                   
            else:
                met_dups += 1
    if not found:
        print "no solution was found after visited %d states" % visited
    else:
        print "Total states %d" % (visited)

if __name__ == "__main__":
    BFS()
    print "DONE"
    
    
    
    
    