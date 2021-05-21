  
from __future__ import print_function
# bustersAgents.py
# ----------------
# Licensing Information:  You are free to use or extend these projects for
# educational purposes provided that (1) you do not distribute or publish
# solutions, (2) you retain this notice, and (3) you provide clear
# attribution to UC Berkeley.
# 
# Attribution Information: The Pacman AI projects were developed at UC Berkeley.
# The core projects and autograders were primarily created by John DeNero
# (denero@cs.berkeley.edu) and Dan Klein (klein@cs.berkeley.edu).
# Student side autograding was added by Brad Miller, Nick Hay, and
# Pieter Abbeel (pabbeel@cs.berkeley.edu).

from builtins import range
from builtins import object
import util
from game import Agent
from game import Directions
from keyboardAgents import KeyboardAgent
from learningAgents import ReinforcementAgent
import inference
import busters as otro
from iterationState import IterationState
import os
import numpy as np


class BustersAgent(object):
    "An agent that tracks and displays its beliefs about ghost positions."

    def __init__( self, index = 0, inference = "ExactInference", ghostAgents = None, observeEnable = True, elapseTimeEnable = True):
        inferenceType = util.lookup(inference, globals())
        self.inferenceModules = [inferenceType(a) for a in ghostAgents]
        self.observeEnable = observeEnable

    def registerInitialState(self, gameState):
        "Initializes beliefs and inference modules"
        import __main__
        self.display = __main__._display
        for inference in self.inferenceModules:
            inference.initialize(gameState)
        self.ghostBeliefs = [inf.getBeliefDistribution() for inf in self.inferenceModules]
        self.firstMove = True

    def observationFunction(self, gameState):
        "Removes the ghost states from the gameState"
        agents = gameState.data.agentStates
        gameState.data.agentStates = [agents[0]] + [None for i in range(1, len(agents))]
        return gameState

    def getAction(self, gameState):
        "Updates beliefs, then chooses an action based on updated beliefs."
        #for index, inf in enumerate(self.inferenceModules):
        #    if not self.firstMove and self.elapseTimeEnable:
        #        inf.elapseTime(gameState)
        #    self.firstMove = False
        #    if self.observeEnable:
        #        inf.observeState(gameState)
        #    self.ghostBeliefs[index] = inf.getBeliefDistribution()
        #self.display.updateDistributions(self.ghostBeliefs)
        return self.chooseAction(gameState)

    def chooseAction(self, gameState):

        a = "Stop"
        return a


class QLearningAgent(BustersAgent):
    
    def registerInitialState(self, gameState):
        BustersAgent.registerInitialState(self, gameState)
        self.actions = {"North":0, "East":1, "South":2, "West":3} 
        if os.path.exists("qtable.txt"):
            self.table_file = open("qtable.txt", "r+")
            self.q_table = self.readQtable()
        else:
            self.table_file = open("qtable.txt", "w+")
            self.initQtable(10) #Temporal number, will depend on our args chosen
        
        self.epsilon = 0.2
        self.alpha = 0.1
        self.discount = 0.8
    
    def initQtable(self,rows):
        self.q_table = np.zeros((rows,len(self.actions)))


    def readQtable(self):
        "Read qtable from disc"
        table = self.table_file.readlines()
        q_table = []

        for i, line in enumerate(table):
            row = line.split()
            row = [float(x) for x in row]
            q_table.append(row)
            

        return q_table

    def writeQtable(self):
        "Write qtable to disc"
        self.table_file.seek(0)
        self.table_file.truncate()
        for line in self.q_table:
            for item in line:
                self.table_file.write(str(item)+" ")
            self.table_file.write("\n")

#         self.table_file_csv.seek(0)
#         self.table_file_csv.truncate()
#         for line in self.q_table:
#             for item in line[:-1]:
#                 self.table_file_csv.write(str(item)+", ")
#             self.table_file_csv.write(str(line[-1]))                
#             self.table_file_csv.write("\n")

            
    def printQtable(self):
        "Print qtable"
        for line in self.q_table:
            print(line)
        print("\n")    
            
    def __del__(self):
        "Destructor. Invokation at the end of each episode"
        self.writeQtable()
        self.table_file.close()

    def computePosition(self, state):
        """
        Compute the row of the qtable for a given state.
        
        """
        if state.nearestdirection == 'Stop':
            return 9

        row = {'North':0, 'East':2, 'South':4, 'West':6}[state.nearestdirection]
        row += state.food
        return row


    def getQValue(self, state, action):

        """
          Returns Q(state,action)
          Should return 0.0 if we have never seen a state
          or the Q node value otherwise
        """
        position = self.computePosition(state)
        action_column = self.actions[action]

        return self.q_table[position][action_column]


    def computeValueFromQValues(self, state):
        """
          Returns max_action Q(state,action)
          where the max is over legal actions.  Note that if
          there are no legal actions, which is the case at the
          terminal state, you should return a value of 0.0.
        """
        legalActions = state.getLegalActionsRemaining()
        if len(legalActions)==0:
          return 0
        return max(self.q_table[self.computePosition(state)])

    def computeActionFromQValues(self, state):
        """
          Compute the best action to take in a state.  Note that if there
          are no legal actions, which is the case at the terminal state,
          you should return None.
        """
        legalActions = state.getLegalActionsRemaining()
        if 'Stop' in legalActions:
            legalActions.remove("Stop")
        if len(legalActions)==0:
          return None

        best_actions = [legalActions[0]]
        best_value = self.getQValue(state, legalActions[0])
        for action in legalActions:
            value = self.getQValue(state, action)
            print(action, value)
            if value == best_value:
                best_actions.append(action)
            if value > best_value:
                best_actions = [action]
                best_value = value
                print(best_actions, best_value)
        return random.choice(best_actions)

    def getAction(self, state):
        """
          Compute the action to take in the current state.  With
          probability self.epsilon, we should take a random action and
          take the best policy action otherwise.  Note that if there are
          no legal actions, which is the case at the terminal state, you
          should choose None as the action.
        """

        # Pick Action
        qstate= IterationState(state)
        legalActions = qstate.getLegalActionsRemaining()
        action = None

        if len(legalActions) == 0:
             return action

        flip = util.flipCoin(self.epsilon)
        best = self.getPolicy(qstate)
        print(best)
        if flip:
            return random.choice(legalActions)
        return best


    def update(self, state, action, nextState, reward):
        
        best_action = self.computeActionFromQValues(nextState)
        if best_action == None:
                return
        
        position = self.computePosition(state)
        action_column = self.actions[action]
        qvalue = (1 - self.alpha) * self.getQValue(state, action) + self.alpha * (reward + self.discount * self.getQValue(nextState, best_action))

        self.q_table[position][action_column] = qvalue
        self.writeQtable()



    def getPolicy(self, state):
        "Return the best action in the qtable for a given state"
        return self.computeActionFromQValues(state)

    def getValue(self, state):
        "Return the highest q value for a given state"
        return self.computeValueFromQValues(state)
       
    def getReward(self, state, action, nextstate, gameState, nextGameState):
        reward = 0

        directions = {"North": 1, "South": -1, "East": 2, "West": -2, 'Stop': 0}
        dir = gameState.data.agentStates[0].getDirection()
        next_dir = nextGameState.data.agentStates[0].getDirection()

        if self.getdistnear(nextGameState) < self.getdistnear(gameState):
            reward += 15
        else:
            reward -= 5
        if directions[dir] == -directions[next_dir]:
            reward -= 10
        if state.countGhosts(gameState) - nextstate.countGhosts(nextGameState) != 0:
            reward += 150
        if nextGameState.getNumFood() < gameState.getNumFood():
            reward += 75
        print(reward)
        return reward

    def getdistnear(self, gameState):
        i = 0
        closestGhost = 0
        d = [0,0,0,0]
        while (i < len(gameState.getNoisyGhostDistances())):
            if not gameState.getLivingGhosts()[i+1]:
                d[i] = 9999
            else:
                d[i] = gameState.getNoisyGhostDistances()[i]
                if d[i] < d[closestGhost]:
                    closestGhost = i
            if gameState.getNoisyGhostDistances()[i] == None:
                d[i] = 9999
            i+=1

        GhostDistance=d[closestGhost]
        return GhostDistance


class NullGraphics(object):
    "Placeholder for graphics"
    def initialize(self, state, isBlue = False):
        pass
    def update(self, state):
        pass
    def pause(self):
        pass
    def draw(self, state):
        pass
    def updateDistributions(self, dist):
        pass
    def finish(self):
        pass

class KeyboardInference(inference.InferenceModule):
    """
    Basic inference module for use with the keyboard.
    """
    def initializeUniformly(self, gameState):
        "Begin with a uniform distribution over ghost positions."
        self.beliefs = util.Counter()
        for p in self.legalPositions: self.beliefs[p] = 1.0
        self.beliefs.normalize()

    def observe(self, observation, gameState):
        noisyDistance = observation
        emissionModel = busters.getObservationDistribution(noisyDistance)
        pacmanPosition = gameState.getPacmanPosition()
        allPossible = util.Counter()
        for p in self.legalPositions:
            trueDistance = util.manhattanDistance(p, pacmanPosition)
            if emissionModel[trueDistance] > 0:
                allPossible[p] = 1.0
        allPossible.normalize()
        self.beliefs = allPossible

    def elapseTime(self, gameState):
        pass

    def getBeliefDistribution(self):
        return self.beliefs




class BustersKeyboardAgent(BustersAgent, KeyboardAgent):
    "An agent controlled by the keyboard that displays beliefs about ghost positions."

    def __init__(self, index = 0, inference = "KeyboardInference", ghostAgents = None):
        KeyboardAgent.__init__(self, index)
        BustersAgent.__init__(self, index, inference, ghostAgents)

    def getAction(self, gameState):
        return BustersAgent.getAction(self, gameState)

    def chooseAction(self, gameState):
        return KeyboardAgent.getAction(self, gameState)

from distanceCalculator import Distancer
from game import Actions
from game import Directions
import random, sys

'''Random PacMan Agent'''
class RandomPAgent(BustersAgent):

    def registerInitialState(self, gameState):
        BustersAgent.registerInitialState(self, gameState)
        self.distancer = Distancer(gameState.data.layout, False)
        
    ''' Example of counting something'''
    def countFood(self, gameState):
        food = 0
        for width in gameState.data.food:
            for height in width:
                if(height == True):
                    food = food + 1
        return food
    
    ''' Print the layout'''  
    def printGrid(self, gameState):
        table = ""
        ##print(gameState.data.layout) ## Print by terminal
        for x in range(gameState.data.layout.width):
            for y in range(gameState.data.layout.height):
                food, walls = gameState.data.food, gameState.data.layout.walls
                table = table + gameState.data._foodWallStr(food[x][y], walls[x][y]) + ","
        table = table[:-1]
        return table
        
    def chooseAction(self, gameState):
        move = Directions.STOP
        legal = gameState.getLegalActions(0) ##Legal position from the pacman
        move_random = random.randint(0, 3)
        if   ( move_random == 0 ) and Directions.WEST in legal:  move = Directions.WEST
        if   ( move_random == 1 ) and Directions.EAST in legal: move = Directions.EAST
        if   ( move_random == 2 ) and Directions.NORTH in legal:   move = Directions.NORTH
        if   ( move_random == 3 ) and Directions.SOUTH in legal: move = Directions.SOUTH
        return move
        
class GreedyBustersAgent(BustersAgent):
    "An agent that charges the closest ghost."

    def registerInitialState(self, gameState):
        "Pre-computes the distance between every two points."
        BustersAgent.registerInitialState(self, gameState)
        self.distancer = Distancer(gameState.data.layout, False)

    def chooseAction(self, gameState):
        """
        First computes the most likely position of each ghost that has
        not yet been captured, then chooses an action that brings
        Pacman closer to the closest ghost (according to mazeDistance!).
        To find the mazeDistance between any two positions, use:
          self.distancer.getDistance(pos1, pos2)
        To find the successor position of a position after an action:
          successorPosition = Actions.getSuccessor(position, action)
        livingGhostPositionDistributions, defined below, is a list of
        util.Counter objects equal to the position belief
        distributions for each of the ghosts that are still alive.  It
        is defined based on (these are implementation details about
        which you need not be concerned):
          1) gameState.getLivingGhosts(), a list of booleans, one for each
             agent, indicating whether or not the agent is alive.  Note
             that pacman is always agent 0, so the ghosts are agents 1,
             onwards (just as before).
          2) self.ghostBeliefs, the list of belief distributions for each
             of the ghosts (including ghosts that are not alive).  The
             indices into this list should be 1 less than indices into the
             gameState.getLivingGhosts() list.
        """
        pacmanPosition = gameState.getPacmanPosition()
        legal = [a for a in gameState.getLegalPacmanActions()]
        livingGhosts = gameState.getLivingGhosts()
        livingGhostPositionDistributions = \
            [beliefs for i, beliefs in enumerate(self.ghostBeliefs)
             if livingGhosts[i+1]]
        return Directions.EAST

class BasicAgentAA(BustersAgent):

    def registerInitialState(self, gameState):
        BustersAgent.registerInitialState(self, gameState)
        self.distancer = Distancer(gameState.data.layout, False)
        self.countActions = 0
        
    ''' Example of counting something'''
    def countFood(self, gameState):
        food = 0
        for width in gameState.data.food:
            for height in width:
                if(height == True):
                    food = food + 1
        return food
    
    ''' Print the layout'''  
    def printGrid(self, gameState):
        table = ""
        #print(gameState.data.layout) ## Print by terminal
        for x in range(gameState.data.layout.width):
            for y in range(gameState.data.layout.height):
                food, walls = gameState.data.food, gameState.data.layout.walls
                table = table + gameState.data._foodWallStr(food[x][y], walls[x][y]) + ","
        table = table[:-1]
        return table

    def printInfo(self, gameState):
        print("---------------- TICK ", self.countActions, " --------------------------")
        # Map size
        width, height = gameState.data.layout.width, gameState.data.layout.height
        print("Width: ", width, " Height: ", height)
        # Pacman position
        print("Pacman position: ", gameState.getPacmanPosition())
        # Legal actions for Pacman in current position
        print("Legal actions: ", gameState.getLegalPacmanActions())
        # Pacman direction
        print("Pacman direction: ", gameState.data.agentStates[0].getDirection())
        # Number of ghosts
        print("Number of ghosts: ", gameState.getNumAgents() - 1)
        # Alive ghosts (index 0 corresponds to Pacman and is always false)
        print("Living ghosts: ", gameState.getLivingGhosts())
        # Ghosts positions
        print("Ghosts positions: ", gameState.getGhostPositions())
        # Ghosts directions
        print("Ghosts directions: ", [gameState.getGhostDirections().get(i) for i in range(0, gameState.getNumAgents() - 1)])
        # Manhattan distance to ghosts
        print("Ghosts distances: ", gameState.data.ghostDistances)
        # Pending pac dots
        print("Pac dots: ", gameState.getNumFood())
        # Manhattan distance to the closest pac dot
        print("Distance nearest pac dots: ", gameState.getDistanceNearestFood())
        # Map walls
        print("Map:")
        print( gameState.getWalls())
        # Score
        print("Score: ", gameState.getScore())
        
    
    
    class Node:
        # Initialize the class
        def __init__(self, position:(), parent:()):
            self.position = position
            self.parent = parent
            self.g = 0 # Distance to start node
            self.h = 0 # Distance to goal node
            self.f = 0 # Total cost
        # Compare nodes
        def __eq__(self, other):
            return self.position == other.position
        # Sort nodes
        def __lt__(self, other):
             return self.f < other.f
        # Print node
        def __repr__(self):
            return ('({0},{1})'.format(self.position, self.f))
    
    
    #Esta función comprueba si el nodo a esta ya en la lista para abrir
    def can_open(self, opened, neighbor):
        for node in opened:
            if (neighbor == node and neighbor.f >= node.f):
                return False
        return True

    
    def aStarSearch(self, gameState, pos):
        opened = []	#array de nodos por abrir
        visited = []	#array de nodos visitados

        start_node = self.Node(gameState.getPacmanPosition(), None)		#el nodo inicial es la posicion actual
        goal_node = self.Node(gameState.getGhostPositions()[pos], None)	#el nodo final el objetivo

        opened.append(start_node)	#añadomos el nodo actual a la lista de operar

        while len(opened) > 0:	#repetir mientras queden nodos por operar/abrir
            
            
            current_node = opened.pop(0)	#obtenemos un nodo de la lista de por abrir
            
            visited.append(current_node)	#y lo marcamos como visitado
            
            if gameState.getGhostPositions()[pos] == current_node.position:  #se acabo hemos llegado
                path = []
                while current_node != start_node:
                    path.append(current_node.position)
                    current_node = current_node.parent
 
                #devolvemos el camino al reves
                return path[::-1]

            (x, y) = current_node.position	#cogemos las coordenadas
            
            newPosition = []
            direction = [Directions.WEST, Directions.EAST, Directions.SOUTH, Directions.NORTH]
            
            for d in direction:
                if d == Directions.WEST: 
                    newPosition = (x-1, y)
                       
                if d == Directions.EAST: 
                    newPosition = (x+1, y)
                        
                if d == Directions.SOUTH: 
                    newPosition = (x, y-1)
                        
                if d == Directions.NORTH: 
                    newPosition = (x, y+1)
                
                #comprobamos si es una pared
                if not gameState.getWalls()[newPosition[0]][newPosition[1]]:

                    neighbor = self.Node(newPosition, current_node)
                    if neighbor in visited:
                        continue
                    
                    # Genera la heuristica de los nodos (distancia Manhattan)
                    neighbor.g = abs(neighbor.position[0] - start_node.position[0]) + abs(neighbor.position[1] - start_node.position[1])
                    neighbor.h = abs(neighbor.position[0] - goal_node.position[0]) + abs(neighbor.position[1] - goal_node.position[1])
                    neighbor.f = neighbor.g + neighbor.h
                    
                    if(self.can_open(opened, neighbor) == True):
                    #si todo va bien se añade a la lista para abrir
                        opened.append(neighbor)

        return False
    
            
    def chooseAction(self, gameState):
        self.countActions = self.countActions + 1
        self.printInfo(gameState)
        move = Directions.STOP #Default move: stop
        legal = gameState.getLegalActions(0) ##List of Legal positions from the pacman
        dist=999999 #initial dist infinite
        i=1
        for x in gameState.data.ghostDistances:
            if isinstance(x,int):
                if x < dist:
                    dist = x		#this calculates the nearest ghost
            i=+1
        pos= gameState.data.ghostDistances.index(dist)  #position of nearest ghost
        pacpos= gameState.getPacmanPosition()         #pacman position
        coord=gameState.getGhostPositions()[pos]	#coordinates of nearest ghost
        print("NEAREST GHOST IS ",dist)
        print("POSITION IN ARRAY ",pos)
        print("COORD ", coord)
        
        pathToGoal = self.aStarSearch(gameState, pos)	#el camno hasta el fantasma con A*
        
        #print(pathToGoal[0])
        print(gameState.getWalls()[pathToGoal[0][0]][pathToGoal[0][1]])
            
        if pathToGoal[0][0] == gameState.getPacmanPosition()[0]:  #Se mueve siguiendo el pathtogoal especificado, no tiene mucho mas
            if pathToGoal[0][1] < gameState.getPacmanPosition()[1]: move = Directions.SOUTH
            else: move = Directions.NORTH
        else:
            if pathToGoal[0][0] < gameState.getPacmanPosition()[0]: move = Directions.WEST
            else: move = Directions.EAST
        
        print("PathtoGoal",pathToGoal)
        
        return move

    def printLineData(self, gameState):
        linea = str(gameState.getPacmanPosition())+","+ str(gameState.getLegalPacmanActions())+ ","+ str(gameState.getLivingGhosts()) + ","+ str(gameState.getGhostPositions()) + ","+ str(gameState.data.ghostDistances)
        path='./'
        if not os.path.exists(path+"/log.arff"):
            with open(path+"/log.arff",'w') as le:
                le.write('%1. Title: log \n% \n%2. Sources: \n%   (a) Creator: A\n%   (b) Donor: M\n% (c) Date: Daaate\n%\n@Relation pacman\n\n@atribute Position'+' STRING\n@atribute LegalActions STRING\n@atribute GhostsAlive STRING\n@atribute GhostPosition STRING\n@atribute GhostDistances STRING\n@data'+linea+'\n')
        else:
            with open(path+"/log.arff",'a') as le:
                le.write(linea+'\n')
        return linea
