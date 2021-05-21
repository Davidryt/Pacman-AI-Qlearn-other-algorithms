class IterationState():

    def __init__(self, gameState):
        self.nearestdirection = self.getDir(gameState)
        self.legal_actions = gameState.getLegalActions()
        self.food = self.isFood(gameState)

    def countGhosts(self, gameState):
        count = 0
        aliveGhosts = gameState.getLivingGhosts()[1:]
        for i in range(len(aliveGhosts)):
            if aliveGhosts[i]:
                count += 1
        return count

    def isFood(self, gameState):
        if gameState.getNumFood() != 0:
            return 1
        else:
            return 0

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
        FoodDistance = gameState.getDistanceNearestFood()
        if FoodDistance == None:
            FoodDistance = 9999

        if FoodDistance < GhostDistance and FoodDistance != 9999:
            FoodPosition = gameState.getPositionNearestFood()

            if len(available_actions) > 1:
                if y < FoodPosition[1] and "North" in available_actions:
                    move = "North"
                elif y > FoodPosition[1] and "South" in available_actions:
                    move = "South"
                if x < FoodPosition[0] and "East" in available_actions:
                    move = "East"
                if x > FoodPosition[0] and "West" in available_actions:
                    move = "West"
                elif move == "Stop" and pacmanDirection in available_actions:
                    move = pacmanDirection

            else:
                if len(available_actions) > 0:
                    move = available_actions[0]

        elif GhostDistance <= FoodDistance and GhostDistance != 0:
            ghostPosition = gameState.getGhostPositions()[closestGhost]
            if len(available_actions) > 1:
                if y < ghostPosition[1] and "North" in available_actions:
                    move = "North"
                elif y > ghostPosition[1] and "South" in available_actions:
                    move = "South"
                if x < ghostPosition[0] and "East" in available_actions:
                    move = "East"
                if x > ghostPosition[0] and "West" in available_actions:
                    move = "West"
                elif move == "Stop" and pacmanDirection in available_actions:
                    move = pacmanDirection

            else:
                if len(available_actions) > 0:
                    move = available_actions[0]

        return move

    def getLegalActionsRemaining(self):
        return self.legal_actions
