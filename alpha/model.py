from mesa import Model
from mesa.time import RandomActivation
from mesa.space import MultiGrid
from agent import EvolutionaryAgent
import strategies
import random

# Main model which controls the agents
class EvolutionaryModel(Model):
    """A model with some number of agents."""
    def __init__(self, N, width, height):
        self.num_agents = N
        self.grid = MultiGrid(width, height, True)
        self.schedule = RandomActivation(self)

        # Create agents
        for i in range(self.num_agents):
            evolutionaryStrategy = random.choice(strategies.strategyList)
            a = EvolutionaryAgent(i, self, evolutionaryStrategy, 1)
            self.schedule.add(a)

            # Add the agent to a random grid cell
            x = self.random.randrange(self.grid.width)
            y = self.random.randrange(self.grid.height)
            self.grid.place_agent(a, (x, y))
            
    def step(self):
        self.schedule.step()


model = EvolutionaryModel(50, 10, 10)
for i in range(10):
    model.step()