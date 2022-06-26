from re import A
import time, random
from Yinsh.yinsh_model import YinshGameRule 
from template import Agent
from copy import deepcopy
from collections import deque
import numpy as np

THINKTIME = 0.5
C_PARAM = 1.414

class Node():
    def __init__(self, state, game_rule=None, agent_id=None, parent=None, parent_action=None):  
        self.state = state
        self.parent = parent
        self.id = agent_id
        self.parent_action = parent_action
        self.children = []
        self.game_rule = game_rule

        self._untried_actions = self.get_legal_actions(self.state)
        self._number_of_visits = 0
        self._results = {}
        self._results[1] = 0
        self._results[-1] = 0
        self._score = self.state.agents[self.id].score
 
    # Current node, victory count minus failure count
    def q(self):  
        wins = self._results[1]
        loses = self._results[-1]
        return wins - loses
 
    # Number of visits to the current node
    def n(self):  
        return self._number_of_visits
    
    # Expand child nodes
    def expand(self):    
        action = self._untried_actions.pop()
        current_state = deepcopy(self.state)

        next_state = self.game_rule.generateSuccessor(current_state, action, self.id)
        child_node = Node(next_state, parent=self, parent_action=action, agent_id=self.id, game_rule=self.game_rule)
        self.children.append(child_node)
        return child_node

 
    # The logic of generating the tree is to first determine whether the node is the final state
    # if not then determine whether it is fully expanded
    # if not then continue to expand the children of the node
    # otherwise choose a random node from the child nodes as the next node to be expanded
    def run_tree_policy(self):  
        current_node=self
        while not current_node.is_terminal_node():
            if not current_node.is_fully_expanded():
                return current_node.expand()
            else:
                current_node=current_node.get_random_child()
        return current_node
    
    def is_terminal_node(self):
        if not self.parent:
            return False
        elif len(self.get_legal_actions(self.state)) == 1:
            return True
        else:
            return self._score == 3 or self.parent._score == 3
    
    def is_fully_expanded(self):
        return len(self._untried_actions) == 0
    
    # Select an optimal node from all the child nodes (next state)
    def choose_best_child(self):
        # UCT algorithm
        try:
            choices_weights = [(c.q() / c.n()) + C_PARAM * np.sqrt((2*np.log(self.n()) / c.n())) for c in self.children]        
            if self.id == 0: 
                # If the current player is the first player,
                # the child node with the greatest weight is selected as the optimal action
                print("mct best action so far")
                return self.children[np.argmax(choices_weights)] 
            else:  
                # If the current player is a backhand,
                # the child node with the smallest weight (the state with the lowest first-hand win rate)
                # is selected as the optimal action
                print("mct found")
                return self.children[np.argmin(choices_weights)]
        except:
            # error process
            return self.get_random_child()
    
    def get_random_child(self):
        return random.choice(self.children)

    def get_legal_actions(self, current_state):
        return deepcopy(self.game_rule.getLegalActions(current_state, self.id))
         
    # Self-play simulation, random selection of actions for child nodes until the endgame
    def rollout(self):
        current_rollout_state = deepcopy(self.state)
        final_result = 0
        while final_result == 0:
            possible_moves = self.get_legal_actions(current_rollout_state)
            action = random.choice(possible_moves)
            current_rollout_state = deepcopy(self.game_rule.generateSuccessor(current_rollout_state, action, self.id))
            # reward?
            new_score = current_rollout_state.agents[self.id].score
            if new_score == 3 or self._score == 3:
                final_result = 1. if new_score > self._score else -1.
                break
            if len(self.get_legal_actions(current_rollout_state)) == 1:
                break
        return final_result
    
    # Goes back up and passes the win/loss information to the parent nodes
    def backpropagate(self, result):
        self._number_of_visits += 1.
        if result == 0:
            return
        self._results[result] += result
        if self.parent:
            self.parent.backpropagate(result)
    
    # Each node calculates the best action by playing itself
    # and records the result, from which the best child node is selected   
    def calc_best_action(self,stime):
       
        cnt = 0
        while time.time()-stime < THINKTIME:
            cnt += 1
            node = self.run_tree_policy()
            reward = node.rollout()
            node.backpropagate(reward)
        print("mct state",cnt)
       
        return self.choose_best_child() 


# Agent class
class myAgent(Agent):
    def __init__(self, _id):
        super().__init__(_id)
        self.id = _id
        self.game_rule = YinshGameRule(2)
    
    # BFS search algorithm for len(actions) > 70
    def SelectAction_BFS(self, actions, rootstate):
        start_time = time.time()
        queue      = deque([ (deepcopy(rootstate),[]) ]) 
        count =0 
        # Conduct BFS starting from rootstate.
        while len(queue) and time.time()-start_time < THINKTIME:
            count +=1
            state, path = queue.popleft() 
            new_actions = self.game_rule.getLegalActions(state, self.id)
            
            for a in new_actions:
                next_state = deepcopy(state)
                next_path  = path + [a]
                score = state.agents[self.id].score
                new_state = self.game_rule.generateSuccessor(next_state, a, self.id)
                reward = new_state.agents[self.id].score > score 

                if reward:
                    print("BFS found",count)
                    return next_path[0] 
                else:
                    queue.append((next_state, next_path))
        print("BFS random",count)
        return random.choice(actions)

    # MCTS algorithm for len(actions) <= 70
    def SelectAction(self, actions, rootstate):
        start_time = time.time()
        while  time.time()-start_time < THINKTIME:
            if len(actions) > 70:
                
                return self.SelectAction_BFS(actions, rootstate)
            else:
                
                tree = Node(rootstate, game_rule=self.game_rule, agent_id=self.id)
                
                return tree.calc_best_action(start_time).parent_action
        print('mct random')
        return random.choice(actions)
        
