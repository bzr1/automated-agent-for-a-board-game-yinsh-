from template import Agent
import random
import sys
sys.path.append('agents/t_056/')
import time,heapq
from Yinsh.yinsh_model import YinshGameRule 
from copy import deepcopy
from collections import deque
import pickle
import math,re

THINKTIME = 0.85


#from util.py assignment 1
class PriorityQueue:
    """
      Implements a priority queue data structure. Each inserted item
      has a priority associated with it and the client is usually interested
      in quick retrieval of the lowest-priority item in the queue. This
      data structure allows O(1) access to the lowest-priority item.
    """
    def  __init__(self):
        self.heap = []
        self.count = 0

    def push(self, item, priority):
        entry = (priority, self.count, item)
        heapq.heappush(self.heap, entry)
        self.count += 1

    def pop(self):
        (_, _, item) = heapq.heappop(self.heap)
        return item

    def isEmpty(self):
        return len(self.heap) == 0

    def update(self, item, priority):
        # If item already in priority queue with higher priority, update its priority and rebuild the heap.
        # If item already in priority queue with equal or lower priority, do nothing.
        # If item not in priority queue, do the same thing as self.push.
        for index, (p, c, i) in enumerate(self.heap):
            if i == item:
                if p <= priority:
                    break
                del self.heap[index]
                self.heap.append((priority, c, item))
                heapq.heapify(self.heap)
                break
        else:
            self.push(item, priority)

class myAgent():
    def __init__(self,_id):
        self.move=0
        with open("agents/t_056/Ah.pkl", "rb") as a_file:
            self.h = pickle.load(a_file)
        self.id = _id # Agent needs to remember its own id.
        self.game_rule = YinshGameRule(2) # Agent stores an instance of GameRule, from which to obtain functions.
        
        

    # Generates actions from this state.
    def GetActions(self, state):
        return self.game_rule.getLegalActions(state, self.id)
    
    # Carry out a given action on this state and return True if reward received.
    def DoAction(self, state, action):
        
        score = state.agents[self.id].score
        state = self.game_rule.generateSuccessor(state, action, self.id)
        return state.agents[self.id].score > score

    def CalH(self,board):
        min_h=51
        for i in range(1,10):
            startpoints= [(0,0),(4,6),(3,6),(2,6),(1,6),(1,5),(0,5),(0,4),(0,3),(0,2)]
            start,end = startpoints[i]
            for j in range(start,end):
                horizontal=str(self.id)+str(board[i,j])+str(board[i,j+1])+str(board[i,j+2])+str(board[i,j+3])+str(board[i,j+4])
                vertical=str(self.id)+str(board[j,i])+str(board[j+1,i])+str(board[j+2,i])+str(board[j+3,i])+str(board[j+4,i])
                horval=100
                verval=100
                horval=self.h[horizontal]
                verval=self.h[vertical]

                min_h=min(horval,verval)
            for i in range(4,11):
                startpoints=[(0,0),(0,0),(0,0),(0,0),(2,6),(1,7),(0,7),(0,7),(0,7),(0,6),(1,5)]
                start,end = startpoints[i]
                for j in range(start,end):
                    diagonal=str(self.id)+str(board[i,j])+str(board[i-1,j+1])+str(board[i-2,j+2])+str(board[i-3,j+3])+str(board[i-4,j+4])
                    digval=100
                    digval=self.h[diagonal]
                    min_h=min(min_h,digval)
        return min_h



    def SelectAction(self, actions, rootstate):
        start_time = time.time()
       
        #while time.time()-start_time < THINKTIME:
        if self.move <=4:
            MinDisC=100
            MinDisR=100
            
            
                    
            RingAct = random.choice(actions)
            placepos= RingAct['place pos']
            if self.id ==0 :
                for i in range(11):
                    for j in range(11):
                        if rootstate.board[i][j]==0:
                            dis_center=abs(i-5)+abs(j-5)
                            if MinDisC > dis_center:
                                MinDisC=dis_center
                                placepos=(i,j)
                RingAct['place pos']=placepos
                self.move +=1
                return RingAct
            elif self.id ==1:
                    rivalID = 1-self.id
                    ravel_rings = rootstate.ring_pos[rivalID]
                    for i in range(11):
                        for j in range(11):
                            if rootstate.board[i][j]==0:
                                dis_center=abs(i-5)+abs(j-5)
                                for ring in ravel_rings:
                                    x,y=ring
                                    dis_r = abs(i-x)+abs(j-y)
                                    if (MinDisR> dis_r) or (MinDisC > dis_center):
                                        MinDisC=dis_center
                                        MinDisR = dis_r
                                        placepos=(i,j)
                    RingAct['place pos']=placepos
                    self.move +=1
                    return RingAct
        else:
            
                queue      = PriorityQueue() # Initialise queue. First node = root state and an empty path.
                queue.push( (deepcopy(rootstate),0,[]),0 )
                count = 0
                best_g = dict()
                # Conduct A* starting from rootstate.
                while not queue.isEmpty() and time.time()-start_time < THINKTIME:
                    count +=1
                    state, g,path = queue.pop() # Pop the next node (state, path) in the queue.
                    #print(state.board)
                    # for x in state.board:
                    #     for y in x:
                    #         key="".join(str(y))
                    key = "".join(map(str, state.board))

                    if(key not in best_g) or g< best_g[key]:
                            best_g[key]=g
                            new_actions = self.GetActions(state) # Obtain new actions available to the agent in this state.
                            
                            for a in new_actions: # Then, for each of these actions...
                                
                                next_state = deepcopy(state)              # Copy the state.
                                next_path  = path + [a]                   # Add this action to the path.
                                reward     = self.DoAction(next_state, a) # Carry out this action on the state, and note any reward.
                                if reward:
                                    print("A*",count)
                                    #print(f'Move {len(next_path)}, path found:', next_path)
                                    return next_path[0] # If this action was rewarded, return the initial action that led there.
                                else:
                                    queue.push((next_state, g+1,next_path),g+1+self.CalH(next_state.board)) # Else, simply add this state, its path  and f value to the queue.
                print("A* random",count)
                return random.choice(actions)
        #return random.choice(actions) # If no reward was found in the time limit, return a random action.
        
# def aStarSearch(problem, heuristic=nullHeuristic):
#     """Search the node that has the lowest combined cost and heuristic first."""
#     "*** YOUR CODE HERE ***"
#     myPQ = PriorityQueue()
#     startState = problem.getStartState()
#     startNode = (startState, '',0, [])
#     myPQ.push(startNode,heuristic(startState,problem))
#     visited = set()
#     best_g = dict()
#     while not myPQ.isEmpty():
#         node = myPQ.pop()
#         state, action, cost, path = node
#         if (not state in visited) or cost < best_g.get(state):
#             visited.add(state)
#             best_g[state]=cost
#             if problem.isGoalState(state):
#                 path = path + [(state, action)]
#                 actions = [action[1] for action in path]
#                 del actions[0]
#                 return actions
#             for succ in problem.getSuccessors(state):
#                 succState, succAction, succCost = succ
#                 newNode = (succState, succAction, cost + succCost, path + [(node, action)])
#                 myPQ.push(newNode,heuristic(succState,problem)+cost+succCost)
#     util.raiseNotDefined()