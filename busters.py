# busters.py
# ----------
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


"""
Busters.py is a vengeful variant of Pacman where Pacman hunts ghosts, but
cannot see them.  Numbers at the bottom of the display are noisy distance
readings to each remaining ghost.

To play your first game, type 'python pacman.py' from the command line.
The keys are 'a', 's', 'd', and 'w' to move (or arrow keys).  Have fun!
"""
from __future__ import print_function
from __future__ import division
from builtins import zip
from builtins import str
from builtins import range
from builtins import object
from past.utils import old_div
from game import GameStateData
from game import Game
from game import Directions
from game import Actions
from game import Configuration
from util import nearestPoint
from util import manhattanDistance
import sys, util, types, time, random, layout, os

########################################
# Parameters for noisy sensor readings #
########################################

SONAR_NOISE_RANGE = 15 # Must be odd
SONAR_MAX = old_div((SONAR_NOISE_RANGE - 1),2)
SONAR_NOISE_VALUES = [i - SONAR_MAX for i in range(SONAR_NOISE_RANGE)]
SONAR_DENOMINATOR = 2 ** SONAR_MAX  + 2 ** (SONAR_MAX + 1) - 2.0
SONAR_NOISE_PROBS = [old_div(2 ** (SONAR_MAX-abs(v)), SONAR_DENOMINATOR)  for v in SONAR_NOISE_VALUES]

def getNoisyDistance(pos1, pos2):
    if pos2[1] == 1: return None
    distance = util.manhattanDistance(pos1, pos2)
    # return max(0, distance + util.sample(SONAR_NOISE_PROBS, SONAR_NOISE_VALUES))
    return distance

observationDistributions = {}
def getObservationDistribution(noisyDistance):
    """
    Returns the factor P( noisyDistance | TrueDistances ), the likelihood of the provided noisyDistance
    conditioned upon all the possible true distances that could have generated it.
    """
    global observationDistributions
    if noisyDistance == None:
        return util.Counter()
    if noisyDistance not in observationDistributions:
        distribution = util.Counter()
        for error , prob in zip(SONAR_NOISE_VALUES, SONAR_NOISE_PROBS):
            distribution[max(1, noisyDistance - error)] += prob
        observationDistributions[noisyDistance] = distribution
    return observationDistributions[noisyDistance]

###################################################
# YOUR INTERFACE TO THE PACMAN WORLD: A GameState #
###################################################

class GameState(object):
    """
    A GameState specifies the full game state, including the food, capsules,
    agent configurations and score changes.

    GameStates are used by the Game object to capture the actual state of the game and
    can be used by agents to reason about the game.

    Much of the information in a GameState is stored in a GameStateData object.  We
    strongly suggest that you access that data via the accessor methods below rather
    than referring to the GameStateData object directly.

    Note that in classic Pacman, Pacman is always agent 0.
    """

    ####################################################
    # Accessor methods: use these to access state data #
    ####################################################
    ghostDirections = {}
    
################################################################################################################
################################################################################################################
#Como debería quedar el fichero (ejemplo)
    # @RELATION adult - data - training
    #
    # @ATTRIBUTE age NUMERIC
    #
    # @ATTRIBUTE workclass {Private, Self - emp -not -inc, Self - emp - inc, Federal - gov, Local - gov, State - gov, Without - pay,Never - worked}
    #
    # @data
    # 12,Private
    # 28,Local
################################################################################################################

    def printLineData(self, action, scoreNext):
        state = GameState(self)
        x = [0,0,0,0,0]
        y = [0,0,0,0,0]
        x[0], y[0] = state.getPacmanPosition()
        gState = [0,0,0,0]
        d = [0,0,0,0]
        
        n = 0
        s = 0
        w = 0
        e = 0
        
        i = 0
        
        while (i < 4):
            x[i+1], y[i+1] = state.getGhostPositions()[i]
            if not state.getLivingGhosts()[i+1]:
                gState[i] = 0
                d[i] = 0
            else:
                gState[i] = 1
                d[i] = self.getNoisyGhostDistances()[i]
            i+=1
        
        i = 0
        while (i < len(state.getLegalPacmanActions())):
            if(state.getLegalPacmanActions()[i] == "North"):
                n = 1
            
            if(state.getLegalPacmanActions()[i] == "South"):
                s = 1
            
            if(state.getLegalPacmanActions()[i] == "East"):
                e = 1
            
            if(state.getLegalPacmanActions()[i] == "West"):
                w = 1
            
            i+=1
            
            
        scoreNext += state.getScore()
        
        linea = str(x[0]) + "," + str(y[0]) + "," + str(n) + "," + str(s) + "," + str(e) + "," + str(w) + "," + str(gState[0]) + "," + str(gState[1]) + "," + \
                str(gState[2]) + "," + str(gState[3]) + "," + str(x[1]) + "," + str(y[1]) + "," + str(x[2]) + "," + str(y[2]) + "," + str(x[3]) + "," + str(y[3]) + "," + \
                str(x[4]) + "," + str(y[4]) + "," + str(d[0]) + "," + str(d[1]) + "," + str(d[2]) + "," + str(d[3]) + "," + str(state.getScore()) + "," + str(scoreNext) + "," + str(action)
                
        path='./'
        
        new_file_line = "@RELATION pacman-data-training\n\n\t@ATTRIBUTE pacman_positionX NUMERIC\n\t@ATTRIBUTE pacman_positionY NUMERIC" \
                        "\n\t@ATTRIBUTE legal_north {0,1}\n\t@ATTRIBUTE legal_south {0,1}\n\t@ATTRIBUTE legal_east {0,1}\n\t@ATTRIBUTE legal_west {0,1}" \
                        "\n\t@ATTRIBUTE living_ghost1 {0,1}\n\t@ATTRIBUTE living_ghost2 {0,1}\n\t@ATTRIBUTE living_ghost3 {0,1}\n\t@ATTRIBUTE living_ghost4 {0,1}" \
                        "\n\t@ATTRIBUTE ghost1_positionX NUMERIC\n\t@ATTRIBUTE ghost1_positionY NUMERIC\n\t@ATTRIBUTE ghost2_positionX NUMERIC\n\t@ATTRIBUTE ghost2_positionY NUMERIC" \
                        "\n\t@ATTRIBUTE ghost3_positionX NUMERIC\n\t@ATTRIBUTE ghost3_positionY NUMERIC\n\t@ATTRIBUTE ghost4_positionX NUMERIC\n\t@ATTRIBUTE ghost4_positionY NUMERIC" \
                        "\n\t@ATTRIBUTE ghost1_distance NUMERIC\n\t@ATTRIBUTE ghost2_distance NUMERIC\n\t@ATTRIBUTE ghost3_distance NUMERIC\n\t@ATTRIBUTE ghost4_distance NUMERIC" \
                        "\n\t@ATTRIBUTE food_distance NUMERIC\n\t@ATTRIBUTE food_position_x NUMERIC\n\t@ATTRIBUTE food_position_y NUMERIC\n\t@ATTRIBUTE score NUMERIC" \
                        "\n\t@ATTRIBUTE score_siguiente NUMERIC\n\t@ATTRIBUTE next_move {West,East,North,South,Stop}\n\n@DATA"
        print("HELLO!!")
        if not os.path.exists(path+"/log.arff"):
            with open(path+"/log.arff",'w') as le:
                le.write(new_file_line + '\n\n')
                le.write(linea+'\n')
        else:
            with open(path+"/log.arff",'a') as le:
                le.write(linea+'\n')

################################################################################################################
################################################################################################################
################################################################################################################
################################################################################################################
    def getLegalActions( self, agentIndex=0 ):
        """
        Returns the legal actions for the agent specified.
        """

        if self.isWin() or self.isLose():
            return []

        if agentIndex == 0:  # Pacman is moving
            return PacmanRules.getLegalActions( self )
        else:
            return GhostRules.getLegalActions( self, agentIndex )

    def generateSuccessor( self, agentIndex, action):
        """
        Returns the successor state after the specified agent takes the action.
        """
        # Check that successors exist
        if self.isWin() or self.isLose(): raise Exception('Can\'t generate a successor of a terminal state.')

        # Copy current state
        state = GameState(self)
        
        
        
        # Let agent's logic deal with its action's effects on the board
        if agentIndex == 0:  # Pacman is moving
            state.data._eaten = [False for i in range(state.getNumAgents())]
            PacmanRules.applyAction( state, action )
        else:                # A ghost is moving
            GhostRules.applyAction( state, action, agentIndex )

        # Time passes
        if agentIndex == 0:
            state.data.scoreChange += -TIME_PENALTY # Penalty for waiting around
        else:
            GhostRules.decrementTimer( state.data.agentStates[agentIndex] )

        # Resolve multi-agent effects
        GhostRules.checkDeath( state, agentIndex )

        # Check food eaten
        GhostRules.checkFoodEaten ( state, agentIndex )

        
        # Book keeping
        state.data._agentMoved = agentIndex

        self.printLineData(action, state.data.scoreChange)
        state.data.score += state.data.scoreChange
        p = state.getPacmanPosition()
        state.data.ghostDistances = [getNoisyDistance(p, state.getGhostPosition(i)) for i in range(1,state.getNumAgents())]
        state.ghostPositions = self.ghostPositions = [self.getGhostPosition(i) for i in range(1, self.getNumAgents())]
        a = 0
        for i in range(1, self.getNumAgents()):
            self.ghostDirections[a] = (state.data.agentStates[i].configuration.getDirection())
            a += 1
        if agentIndex == self.getNumAgents() - 1:
            state.numMoves += 1
        return state

    def getLegalPacmanActions( self ):
        return self.getLegalActions( 0 )

    def generatePacmanSuccessor( self, action ):
        """
        Generates the successor state after the specified pacman move
        """
        return self.generateSuccessor( 0, action )

    def getPacmanState( self ):
        """
        Returns an AgentState object for pacman (in game.py)

        state.pos gives the current position
        state.direction gives the travel vector
        """
        return self.data.agentStates[0].copy()

    def getPacmanPosition( self ):
        return self.data.agentStates[0].getPosition()

    def getNumAgents( self ):
        return len( self.data.agentStates )

    def getScore( self ):
        return self.data.score

    def getCapsules(self):
        """
        Returns a list of positions (x,y) of the remaining capsules.
        """
        return self.data.capsules

    def getNumFood( self ):
        return self.data.food.count()

    def getFood(self):
        """
        Returns a Grid of boolean food indicator variables.

        Grids can be accessed via list notation, so to check
        if there is food at (x,y), just call

        currentFood = state.getFood()
        if currentFood[x][y] == True: ...
        """
        return self.data.food

    def getWalls(self):
        """
        Returns a Grid of boolean wall indicator variables.

        Grids can be accessed via list notation, so to check
        if there is food at (x,y), just call

        walls = state.getWalls()
        if walls[x][y] == True: ...
        """
        return self.data.layout.walls

    def hasFood(self, x, y):
        return self.data.food[x][y]

    def hasWall(self, x, y):
        return self.data.layout.walls[x][y]

    ##############################
    # Additions for Busters Pacman #
    ##############################

    def getLivingGhosts(self):
        """
        Returns a list of booleans indicating which ghosts are not yet captured.

        The first entry (a placeholder for Pacman's index) is always False.
        """
        return self.livingGhosts

    def getDistanceNearestFood(self):
        """
        Returns the distance to the nearest food
        """
        global nearestFood
        if(self.getNumFood() > 0):
            minDistance = 900000
            pacmanPosition = self.getPacmanPosition()
            for i in range(self.data.layout.width):
                for j in range(self.data.layout.height):
                    if self.hasFood(i, j):
                        foodPosition = i, j
                        distance = util.manhattanDistance(pacmanPosition, foodPosition)
                        if distance < minDistance:
                            print("\t" + str(i) + "," + str(j))
                            nearestFood = i, j
                            minDistance = distance
            return minDistance

        else:
            return None;

    def getGhostPositions(self):
        return self.ghostPositions

    def getGhostDirections(self):
        return self.ghostDirections

    def setGhostNotLiving(self, index):
        self.livingGhosts[index] = False

    def isLose( self ):
        return self.maxMoves > 0 and self.numMoves >= self.maxMoves

    def isWin( self ):
        return self.livingGhosts.count(True) == 0

    def getNoisyGhostDistances(self):
        """
        Returns a noisy distance to each ghost.
        """
        return self.data.ghostDistances

    #############################################
    #             Helper methods:               #
    # You shouldn't need to call these directly #
    #############################################

    def __init__( self, prevState = None ):
        """
        Generates a new state by copying information from its predecessor.
        """
        if prevState != None:
            self.data = GameStateData(prevState.data)
            self.livingGhosts = prevState.livingGhosts[:]
            self.ghostPositions = prevState.ghostPositions[:]
            self.numMoves = prevState.numMoves;
            self.maxMoves = prevState.maxMoves;
        else: # Initial state
            self.data = GameStateData()
            self.numMoves = 0;
            self.maxMoves = -1;
            self.data.ghostDistances = []

    def deepCopy( self ):
        state = GameState( self )
        state.data = self.data.deepCopy()
        state.data.ghostDistances = self.data.ghostDistances
        return state

    def __eq__( self, other ):
        """
        Allows two states to be compared.
        """
        if (other):
            return self.data == other.data


    def __hash__( self ):
        """
        Allows states to be keys of dictionaries.
        """
        return hash( str( self ) )

    def __str__( self ):

        return str(self.data)

    def initialize( self, layout, numGhostAgents=1000 ):
        """
        Creates an initial game state from a layout array (see layout.py).
        """
        self.data.initialize(layout, numGhostAgents)
        self.livingGhosts = [False] + [True for i in range(numGhostAgents)]
        self.data.ghostDistances = [getNoisyDistance(self.getPacmanPosition(), self.getGhostPosition(i)) for i in range(1, self.getNumAgents())]
        self.ghostPositions = [self.getGhostPosition(i) for i in range(1, self.getNumAgents())]

    def getGhostPosition( self, agentIndex ):
        if agentIndex == 0:
            raise Exception("Pacman's index passed to getGhostPosition")
        return self.data.agentStates[agentIndex].getPosition()
    def getGhostDirection( self, agentIndex ):
        if agentIndex == 0:
            raise Exception("Pacman's index passed to getGhostDirection")
        return self.data.agentStates[agentIndex].getDirection()

    def getGhostState( self, agentIndex ):
        if agentIndex == 0:
            raise Exception("Pacman's index passed to getGhostPosition")
        return self.data.agentStates[agentIndex]

############################################################################
#                     THE HIDDEN SECRETS OF PACMAN                         #
#                                                                          #
# You shouldn't need to look through the code in this section of the file. #
############################################################################

COLLISION_TOLERANCE = 0.7 # How close ghosts must be to Pacman to kill
TIME_PENALTY = 1 # Number of points lost each round

class BustersGameRules(object):
    """
    These game rules manage the control flow of a game, deciding when
    and how the game starts and ends.
    """

    def newGame( self, layout, pacmanAgent, ghostAgents, display, maxMoves= -1 ):
        agents = [pacmanAgent] + ghostAgents
        initState = GameState()
        initState.initialize( layout, len(ghostAgents))
        game = Game(agents, display, self)
        game.state = initState
        game.state.maxMoves = maxMoves
        return game

    def process(self, state, game):
        """
        Checks to see whether it is time to end the game.
        """
        if state.isWin(): self.win(state, game)
        if state.isLose(): self.lose(state, game)

    def win( self, state, game ):
        game.gameOver = True

    def lose( self, state, game ):
        game.gameOver = True

class PacmanRules(object):
    """
    These functions govern how pacman interacts with his environment under
    the classic game rules.
    """
    def getLegalActions( state ):
        """
        Returns a list of possible actions.
        """
        return Actions.getPossibleActions( state.getPacmanState().configuration, state.data.layout.walls )
    getLegalActions = staticmethod( getLegalActions )

    def applyAction( state, action ):
        """
        Edits the state to reflect the results of the action.
        """
        legal = PacmanRules.getLegalActions( state )
        if action not in legal:
            raise Exception("Illegal action", action)

        pacmanState = state.data.agentStates[0]

        # Update Configuration
        vector = Actions.directionToVector( action, 1)
        pacmanState.configuration = pacmanState.configuration.generateSuccessor( vector )

    applyAction = staticmethod( applyAction )

class GhostRules(object):
    """
    These functions dictate how ghosts interact with their environment.
    """
    def getLegalActions( state, ghostIndex ):
        conf = state.getGhostState( ghostIndex ).configuration
        return Actions.getPossibleActions( conf, state.data.layout.walls )
    getLegalActions = staticmethod( getLegalActions )

    def applyAction( state, action, ghostIndex):
        legal = GhostRules.getLegalActions( state, ghostIndex )
        if action not in legal:
            raise Exception("Illegal ghost action: " + str(action))

        ghostState = state.data.agentStates[ghostIndex]
        vector = Actions.directionToVector( action, 1 )
        ghostState.configuration = ghostState.configuration.generateSuccessor( vector )
    applyAction = staticmethod( applyAction )

    def decrementTimer( ghostState):
        timer = ghostState.scaredTimer
        if timer == 1:
            ghostState.configuration.pos = nearestPoint( ghostState.configuration.pos )
        ghostState.scaredTimer = max( 0, timer - 1 )
    decrementTimer = staticmethod( decrementTimer )

    def checkDeath( state, agentIndex):
        pacmanPosition = state.getPacmanPosition()
        if agentIndex == 0: # Pacman just moved; Anyone can kill him
            for index in range( 1, len( state.data.agentStates ) ):
                ghostState = state.data.agentStates[index]
                ghostPosition = ghostState.configuration.getPosition()
                if GhostRules.canKill( pacmanPosition, ghostPosition ):
                    GhostRules.collide( state, ghostState, index )
        else:
            ghostState = state.data.agentStates[agentIndex]
            ghostPosition = ghostState.configuration.getPosition()
            if GhostRules.canKill( pacmanPosition, ghostPosition ):
                GhostRules.collide( state, ghostState, agentIndex )
    checkDeath = staticmethod( checkDeath )

    def checkFoodEaten( state, agentIndex):
        pacmanPosition = state.getPacmanPosition()
        if agentIndex == 0: # Pacman just moved; Anyone can kill him
            if state.hasFood(pacmanPosition[0], pacmanPosition[1]):
                state.data._foodEaten = pacmanPosition[0], pacmanPosition[1]
                state.data.food[pacmanPosition[0]][pacmanPosition[1]] = False
                state.data.scoreChange += 100
    checkFoodEaten = staticmethod( checkFoodEaten )


    def collide( state, ghostState, agentIndex):
        state.data.scoreChange += 200
        GhostRules.placeGhost(ghostState, agentIndex)
        # Added for first-person
        state.data._eaten[agentIndex] = True
        state.setGhostNotLiving(agentIndex)
    collide = staticmethod( collide )

    def canKill( pacmanPosition, ghostPosition ):
        return manhattanDistance( ghostPosition, pacmanPosition ) <= COLLISION_TOLERANCE
    canKill = staticmethod( canKill )

    def placeGhost(ghostState, agentIndex):
        pos = (agentIndex * 2 - 1, 1)
        direction = Directions.STOP
        ghostState.configuration = Configuration(pos, direction)
    placeGhost = staticmethod( placeGhost )

class RandomGhost(object):
    def __init__( self, index ):
        self.index = index

    def getAction( self, state ):
        return random.choice( state.getLegalActions( self.index ) )

    def getDistribution( self, state ):
        actions = state.getLegalActions( self.index )
        prob = 1.0 / len( actions )
        return [( prob, action ) for action in actions]

#############################
# FRAMEWORK TO START A GAME #
#############################

def default(str):
    return str + ' [Default: %default]'

def parseAgentArgs(str):
    if str == None: return {}
    pieces = str.split(',')
    opts = {}
    for p in pieces:
        if '=' in p:
            key, val = p.split('=')
        else:
            key,val = p, 1
        opts[key] = val
    return opts

def readCommand( argv ):
    """
    Processes the command used to run pacman from the command line.
    """
    from optparse import OptionParser
    usageStr = """
    USAGE:      python busters.py <options>
    EXAMPLE:    python busters.py --layout bigHunt
                  - starts an interactive game on a big board
    """
    parser = OptionParser(usageStr)

    parser.add_option('-n', '--numGames', dest='numGames', type='int',
                      help=default('the number of GAMES to play'), metavar='GAMES', default=1)
    parser.add_option('-l', '--layout', dest='layout',
                      help=default('the LAYOUT_FILE from which to load the map layout'),
                      metavar='LAYOUT_FILE', default='oneHunt')
    parser.add_option('-p', '--pacman', dest='pacman',
                      help=default('the agent TYPE in the pacmanAgents module to use'),
                      metavar='TYPE', default='BustersKeyboardAgent')
    parser.add_option('-a','--agentArgs',dest='agentArgs',
                      help='Comma seperated values sent to agent. e.g. "opt1=val1,opt2,opt3=val3"')
    parser.add_option('-g', '--ghosts', dest='ghost',
                      help=default('the ghost agent TYPE in the ghostAgents module to use'),
                      metavar = 'TYPE', default='StaticGhost')
    parser.add_option('-q', '--quietTextGraphics', action='store_true', dest='quietGraphics',
                      help='Generate minimal output and no graphics', default=False)
    parser.add_option('-k', '--numghosts', type='int', dest='numGhosts',
                      help=default('The maximum number of ghosts to use'), default=4)
    parser.add_option('-z', '--zoom', type='float', dest='zoom',
                      help=default('Zoom the size of the graphics window'), default=1.0)
    parser.add_option('-f', '--fixRandomSeed', action='store_true', dest='fixRandomSeed',
                      help='Fixes the random seed to always play the same game', default=False)
    parser.add_option('-s', '--showGhosts', action='store_true', dest='showGhosts',
                      help='Renders the ghosts in the display (cheating)', default=True)
    parser.add_option('-t', '--frameTime', dest='frameTime', type='float',
                      help=default('Time to delay between frames; <0 means keyboard'), default=0.1)

    options, otherjunk = parser.parse_args()
    if len(otherjunk) != 0:
        raise Exception('Command line input not understood: ' + otherjunk)
    args = dict()

    # Fix the random seed
    if options.fixRandomSeed: random.seed('bustersPacman')

    # Choose a layout
    args['layout'] = layout.getLayout( options.layout )
    if args['layout'] == None: raise Exception("The layout " + options.layout + " cannot be found")

    # Choose a ghost agent
    ghostType = loadAgent(options.ghost, options.quietGraphics)
    args['ghosts'] = [ghostType( i+1 ) for i in range( options.numGhosts )]

    # Choose a Pacman agent
    noKeyboard = options.quietGraphics
    pacmanType = loadAgent(options.pacman, noKeyboard)
    agentOpts = parseAgentArgs(options.agentArgs)
    agentOpts['ghostAgents'] = args['ghosts']
    pacman = pacmanType(**agentOpts) # Instantiate Pacman with agentArgs
    args['pacman'] = pacman
    import graphicsDisplay
    args['display'] = graphicsDisplay.FirstPersonPacmanGraphics(options.zoom, \
                                                                  options.showGhosts, \
                                                                  frameTime = options.frameTime)
    args['numGames'] = options.numGames

    return args

def loadAgent(pacman, nographics):
    # Looks through all pythonPath Directories for the right module,
    pythonPathStr = os.path.expandvars("$PYTHONPATH")
    if pythonPathStr.find(';') == -1:
        pythonPathDirs = pythonPathStr.split(':')
    else:
        pythonPathDirs = pythonPathStr.split(';')
    pythonPathDirs.append('.')

    for moduleDir in pythonPathDirs:
        if not os.path.isdir(moduleDir): continue
        moduleNames = [f for f in os.listdir(moduleDir) if f.endswith('gents.py')]
        for modulename in moduleNames:
            try:
                module = __import__(modulename[:-3])
            except ImportError:
                continue
            if pacman in dir(module):
                if nographics and modulename == 'keyboardAgents.py':
                    raise Exception('Using the keyboard requires graphics (not text display)')
                return getattr(module, pacman)
    raise Exception('The agent ' + pacman + ' is not specified in any *Agents.py.')

def runGames( layout, pacman, ghosts, display, numGames, maxMoves=-1):
    # Hack for agents writing to the display
    import __main__
    __main__.__dict__['_display'] = display

    rules = BustersGameRules()
    games = []

    for i in range( numGames ):
        game = rules.newGame( layout, pacman, ghosts, display, maxMoves )
        game.run()
        games.append(game)

    if numGames > 1:
        scores = [game.state.getScore() for game in games]
        wins = [game.state.isWin() for game in games]
        winRate = wins.count(True)/ float(len(wins))
        print('Average Score:', sum(scores) / float(len(scores)))
        print('Scores:       ', ', '.join([str(score) for score in scores]))
        print('Win Rate:      %d/%d (%.2f)' % (wins.count(True), len(wins), winRate))
        print('Record:       ', ', '.join([ ['Loss', 'Win'][int(w)] for w in wins]))

    return games

if __name__ == '__main__':
    """
    The main function called when pacman.py is run
    from the command line:

    > python pacman.py

    See the usage string for more details.

    > python pacman.py --help
    """
    args = readCommand( sys.argv[1:] ) # Get game components based on input
    runGames( **args )
