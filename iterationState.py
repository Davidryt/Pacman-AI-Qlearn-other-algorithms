class IterationState():

    def __init__(self, gameState):
        self.nearestdirection = self.getDir(gameState)
        self.legal_actions = gameState.getLegalActions()

    def countGhosts(self, gameState):
        count = 0
        aliveGhosts = gameState.getLivingGhosts()[1:]
        for i in range(len(aliveGhosts)):
            if aliveGhosts[i]:
                count += 1
        return count

    def getDir(self, gameState):

        [x, y] = gameState.getPacmanPosition()
        available_actions = gameState.getLegalActions().copy()
        pacmanDirection = gameState.data.agentStates[0].getDirection()


        # stop as an action????? REVIEW

        if 'Stop' in available_actions:
            available_actions.remove("Stop")

        move = "Stop"

        i = 0
        closestGhost = 0
        d = [0, 0, 0, 0]
        while (i < len(gameState.getNoisyGhostDistances())):
            if not gameState.getLivingGhosts()[i + 1]:
                d[i] = 9999
            else:
                d[i] = gameState.getNoisyGhostDistances()[i]
                if d[i] < d[closestGhost]:
                    closestGhost = i
            if gameState.getNoisyGhostDistances()[i] == None:
                d[i] = 9999
            i += 1

        GhostDistance = d[closestGhost]

        if GhostDistance != 0:
            ghostPosition = gameState.getGhostPositions()[closestGhost]
            if len(available_actions) > 1:
                if x < ghostPosition[0] and "East" in available_actions:
                    move = "East"
                if x > ghostPosition[0] and "West" in available_actions:
                    move = "West"
                if y < ghostPosition[1] and "North" in available_actions:
                    if x < ghostPosition[0] and "East" in available_actions:
                        move = "NorthEast"
                    elif x > ghostPosition[0] and "West" in available_actions:
                        move = "NorthWest"
                    elif x == ghostPosition[0]:
                        move = "North"
                elif y > ghostPosition[1] and "South" in available_actions:
                    if x < ghostPosition[0] and "East" in available_actions:
                        move = "SouthEast"
                    elif x > ghostPosition[0] and "West" in available_actions:
                        move = "SouthWest"
                    elif x == ghostPosition[0]:
                        move = "South"
                elif move == "Stop" and pacmanDirection in available_actions:
                    move = pacmanDirection

            else:
                if len(available_actions) > 0:
                    move = available_actions[0]

        return move

    def getLegalActionsRemaining(self):
        return self.legal_actions
