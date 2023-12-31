#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Oct 24 15:36:20 2023

@author: augmdc
"""

import numpy as np
import Constants
WALL_VALUE = Constants.WALL_VALUE
GOAL_REWARD = Constants.GOAL_REWARD

# Equivalent of T(s, a, s')
# Computes the probability of moving from state s to state s' when performing an action
# Returns a list that maps an action to it's probability
def transition_probability(all_actions, noise_prob, action_performed):
    probs = []
    for possible_action in all_actions: # Four possible outcomes
        if possible_action == action_performed: # This is the probability that the intended action is executed successfully
            transition_prob = 1 - noise_prob # if noise_prob is 0.2, there's an 80% chance the intended action will occur.
        else:
            transition_prob = noise_prob/3 #  there's an equal chance it could be any of the other three actions.
        probs.append({"action": possible_action, "transition_prob": transition_prob})
    return probs

def compute_difference(arr1, arr2):
    if len(arr1) != len(arr2) or len(arr1[0]) != len(arr2[0]):
        raise ValueError("Input arrays must have the same dimensions.")

    n = len(arr1)
    m = len(arr1[0])

    total_difference = 0

    for i in range(n):
        for j in range(m):
            total_difference += abs(arr1[i][j] - arr2[i][j])

    average_difference = total_difference / (n * m)
    
    return average_difference

# Equivalent of V*(s)
# Returns a grid with each cell representing values
def value_iteration(n, m, actions, rewards, noise_prob, living_reward):
    values = np.zeros((n, m))      
    
    # While the change between iterations is less than 0.0001, run the value iteration process
    difference= np.inf
    it = 0
    while difference > 0.000001:
        # Temporary matrix to hold the updated values during this iteration.
        old_values = values
        
        new_values = np.zeros((n, m))
        # For each cell
        for i in range(n):
            for j in range(m):
                # If the current cell is a terminal state, penalty, reward or wall, keep it
                if rewards[i, j] == GOAL_REWARD or rewards[i, j] == -10 or rewards[i, j] == 10:
                    new_values[i, j] = rewards[i, j]
                    continue
                    
                # Calculate the maximum expected value for the current state by considering all possible actions.
                cell_values = []
                for action in actions:
                    expected_value = 0
                    probs = transition_probability(actions, noise_prob, action)
                    
                    for prob in probs:
                        # For each action-action pair, calculate the Q*(s, a) values
                        ni, nj = i + prob["action"][0], j + prob["action"][1]
                        
                        # Reward function is already implemented here
                        if 0 <= ni < n and 0 <= nj < m and values[ni, nj] !=  WALL_VALUE:
                            expected_value += prob["transition_prob"] * 0.9 * (living_reward + values[ni, nj])
                            
                        else: # If the action results in hitting the wall/edge of the map, bounce back
                            expected_value += prob["transition_prob"] * 0.9 * (living_reward + values[i, j])
                        
                    cell_values.append(expected_value)
                    
                # The Bellman equation: the value of a cell is the maximum expected reward of all possible actions.
                new_values[i, j] = max(cell_values)
                
        # Update the value function with the new computed values.
        values = new_values
        
        # Compare the old_values to the iterated ones
        difference = compute_difference(old_values, values)
        
        it += 1
    return values
        
def final_policy(n, m, rewards, values, actions):
    # Compute the policy based on the final state values
    final_policy = np.zeros((n, m), dtype=object)  # Change dtype to object to allow strings and numbers

    for i in range(n):
        for j in range(m):
            # If terminal state
            if rewards[i][j] == GOAL_REWARD: #if we're at the GOAL_REWARD
                final_policy[i][j] = "*"
                continue

            # For each action, compute the resulting state and its value
            action_values = []
            for action in actions:
                ni, nj = i + action[0], j + action[1]
                if 0 <= ni < n and 0 <= nj < m and rewards[ni, nj] != WALL_VALUE and values[ni][nj] != WALL_VALUE:
                    action_values.append(values[ni][nj])
                else:
                    action_values.append(WALL_VALUE)
            if i == 9 and j == 1:
                print(action_values)
            # Choose the action that leads to the highest state value
            best_action_idx = np.argmax(action_values)
            final_policy[i][j] = best_action_idx

    # Convert numeric policy to direction symbols, leaving "*" as is
    directions_map = {0: "←", 1: "↑", 2: "→", 3: "↓", "*": "*"}
    symbolic_policy = np.vectorize(directions_map.get)(final_policy)
    print(symbolic_policy[1, 5])
    print(symbolic_policy)
    # Print the final symbolic policy
    return symbolic_policy


