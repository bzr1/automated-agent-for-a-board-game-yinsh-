from Yinsh.yinsh_utils import EMPTY
from template import Agent
import random

import heapq, re, time
from Yinsh.yinsh_model import YinshGameRule
from copy import deepcopy


THINKTIME = 0.90

# from util.py assignment 1
class PriorityQueue:
    """
      Implements a priority queue data structure. Each inserted item
      has a priority associated with it and the client is usually interested
      in quick retrieval of the lowest-priority item in the queue. This
      data structure allows O(1) access to the lowest-priority item.
    """

    def __init__(self):
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


class myAgent(Agent):
    def __init__(self, _id):
        self.id = _id  # Agent needs to remember its own id.
        self.game_rule = YinshGameRule(
            2
        )  # Agent stores an instance of GameRule, from which to obtain functions.
        # More advanced agents might find it useful to not be bound by the functions in GameRule, instead executing
        # their own custom functions under GetActions and DoAction.

    # Generates actions from this state.
    def GetActions(self, state):
        return self.game_rule.getLegalActions(state, self.id)

    # Carry out a given action on this state and return True if reward received.
    def DoAction(self, state, action):
        score = state.agents[self.id].score
        state = self.game_rule.generateSuccessor(state, action, self.id)
        return state.agents[self.id].score > score

    def PlaceRing(self, state):
        ring_pos = state.ring_pos
        rings_to_place = state.rings_to_place

        self_ring_pos = ring_pos[self.id]
        oppo_ring_pos = ring_pos[1-self.id]

        if rings_to_place == 10:
            return {'type': 'place ring',
                    'place pos': (4, 4)}


        x_to_place, y_to_place = self_ring_pos[0]
        while state.board[x_to_place, y_to_place] != EMPTY:
            oppo_ring = random.choice(oppo_ring_pos)
            pos_on_line = self.game_rule.positionsOnLine(oppo_ring, random.choice(['h','v','d']))
            x_to_place, y_to_place = random.choice(pos_on_line)

        # print(f'{self.id} place ring, {(x_to_place, y_to_place)}, oppo_ring {oppo_ring}')
        return {'type': 'place ring',
                'place pos': (x_to_place, y_to_place)}

    def SelectAction(self, actions, rootstate):
        start_time = time.time()
        # Initialise queue. First node = root state and an empty path.
        queue = PriorityQueue()
        queue.push((deepcopy(rootstate), 0, []), 0)
        # count = 0
        best_g = dict()
        # Conduct BFS starting from rootstate.
        while not queue.isEmpty() and time.time() - start_time < THINKTIME:
            # count +=1
            # Pop the next node (state, path) in the queue.
            (state, g, path) = queue.pop()

            key = "".join(map(str, state.board))

            if (key not in best_g) or g < best_g[key]:
                best_g[key] = g
                # Obtain new actions available to the agent in this state.
                new_actions = self.GetActions(state)
                if new_actions[0]["type"] == "place ring":
                    # print(f"uniform, place ring")
                    return self.PlaceRing(state)
                for a in new_actions:  # Then, for each of these actions...
                    # print(a)
                    next_state = deepcopy(state)  # Copy the state.
                    next_path = path + [a]  # Add this action to the path.
                    reward = self.DoAction(
                        next_state, a
                    )  # Carry out this action on the state, and note any reward.
                    if reward:
                        # print("A*",count)
                        # print(f"uniform, Move {len(next_path)}, path found:", next_path)
                        return next_path[
                            0
                        ]  # If this action was rewarded, return the initial action that led there.
                    else:
                        queue.push(
                            (next_state, g + 1, next_path),
                            g + 1,
                        )  # Else, simply add this state and its path to the queue.
        # print("A*",count)
        # print(f"uniform, random choice")
        return random.choice(
            actions
        )  # If no reward was found in the time limit, return a random action.
