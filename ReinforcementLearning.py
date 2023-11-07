#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Oct 28 16:46:50 2023

@author: augmdc
"""

import numpy as np
import Constants

WALL_VALUE = Constants.WALL_VALUE
GOAL_REWARD = Constants.GOAL_REWARD

# Moves robot multiple times for an "episode"
def Q_learning(world, rewards, episodes, actions, gamma, epsilon, alpha,
               living_reward, step_var, decay_rate_epsilon, max_epsilon, min_epsilon,
               decay_rate_alpha):
    
    q_values = np.zeros((10, 10, 4))

    initial_alpha = alpha
    for episode in range(episodes):
        alpha = initial_alpha / (1 + episode * decay_rate_alpha)  # Update alpha
        steps = 0
        i, j = world.robot_pos # Capture initial position
        coords_seen = set()
        
        # Initialize vars related to epsilon scaling
        # Epsilon is scaled down proportionally to percent_cells_explored
        # This ensures that exploration and exploitation are balanced based on current world knowledge
        epsilon = max_epsilon  # Start by favouring exploration over exploitation
        epsilon_range = max_epsilon - min_epsilon
        num_cells_explored = 0  # Count of novel cells visited
        percent_cells_explored = 0
        unvisited_cells = []  # Track coodinates of all cells that are not walls, and have not been explored in any episode
        
        # Populate unvisited_cells list
        for i in range(world.size):
            for j in range(world.size):
                if rewards[i][j] != WALL_VALUE:
                    unvisited_cells.append([i,j])
        total_cells = len(unvisited_cells)  # Number of cells in world that are not walls
        
        while steps < step_var:
            
            # Ensure agent only visits squares that they have not seen yet
            possible_action_indexes = [0, 1, 2, 3]
            while True:
                random_value = np.random.rand()
                #Exploration
                if random_value < epsilon: 
                    action_index = np.random.choice(possible_action_indexes)
               #Exploitation
                else:
                    action_index = possible_action_indexes[np.argmax(q_values[i, j, possible_action_indexes])]
                    
                actual_action = actions[action_index]
                
                new_i, new_j = i + actual_action[0], j + actual_action[1] # New position
                
                if (new_i, new_j) not in coords_seen:
                    break
                else: # Remove the action previously seen
                    possible_action_indexes.remove(action_index)
          
            
            # Ensure the agent stays within the grid
            new_i = max(0, min(10 - 1, new_i))
            new_j = max(0, min(10 - 1, new_j))
            
            # If tries to move into a wall, do not update Q-values
            if rewards[new_i, new_j] != WALL_VALUE:
                
                # Takes into account goal, penalty and reward states
                # 1. Calculate the sample using the reward and the maximum Q-value of the next state
                sample = rewards[i , j] + gamma * np.max(q_values[new_i, new_j]) + living_reward

                # 2. Update Q-value using the Q-learning update rule (weighted average)
                q_values[i, j, action_index] = (1 - alpha) * q_values[i, j, action_index] + alpha * sample
                
                # Update current position
                i, j = new_i, new_j
                
                # If hits goal, restart episode
                if rewards[new_i, new_j] == GOAL_REWARD:
                    #print("Break")
                    break
                
            #print(f"Episode {episode}, step {steps}")
            steps += 1
          
        # Update vars related to epsilon scaling
        num_cells_explored = total_cells - len(unvisited_cells)
        percent_cells_explored = num_cells_explored / total_cells
        
        # Scale epsilon down proportionally to percent_cells_explored
        epsilon = max_epsilon - (epsilon_range * percent_cells_explored)
            
    return q_values

def final_policy(n, m, rewards, q_values, actions):
    final_policy = np.zeros((n, m), dtype=object)
    for i in range(n):
        for j in range(m):
            # If terminal state
            if rewards[i, j] == GOAL_REWARD: #rewards[i][j] == 10 or rewards[i][j] == -10
                final_policy[i][j] = "*"
                continue
            
            # Choose best among q_values for each square (4 per [n, m] pair)
            best_action_idx = np.argmax(q_values[i, j])
            final_policy[i][j] = best_action_idx
    
    # Convert numeric policy to direction symbols, leaving "*" as is
    directions_map = {0: "←", 1: "↑", 2: "→", 3: "↓", "*": "*"}
    symbolic_policy = np.vectorize(directions_map.get)(final_policy)
    return symbolic_policy
    

