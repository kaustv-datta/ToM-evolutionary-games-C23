from mesa import Model
from mesa.time import RandomActivation
from mesa.space import MultiGrid
from mesa.datacollection import DataCollector
from agent import EvolutionaryAgent
import strategies
import random
import matplotlib.pyplot as plt

# Main model which controls the agents
class EvolutionaryModel(Model):
    """A model with some number of agents."""
    def __init__(self, N, width, height, step_cost, die_value, reproduce_value):
        self.num_agents = N
        self.grid = MultiGrid(width, height, True)
        self.step_cost = step_cost
        self.die_value = die_value
        self.reproduce_value = reproduce_value
        self.schedule = RandomActivation(self)
        self.latest_id = N-1

        # Create agents
        for i in range(self.num_agents):
            evolutionaryStrategy = random.choice(strategies.strategyList)
            # Initial Wealth is set to 10
            a = EvolutionaryAgent(i, self, evolutionaryStrategy, 10)
            self.schedule.add(a)

            # Add the agent to a random grid cell
            x = self.random.randrange(self.grid.width)
            y = self.random.randrange(self.grid.height)
            self.grid.place_agent(a, (x, y))

    def step(self):
        self.schedule.step()
        # Natural selection
        strategies.naturalSelection(self)

all_wealth = []
all_strategies = []
all_hawks = []
all_doves = []

n_hawks = []
n_doves = []
# EvolutionaryModel(N, width, height, step_cost, die_value, reproduce_value)
model = EvolutionaryModel(50, 10, 10, 2, 0, 10)

n_steps=10
for i in range(n_steps):
    model.step()
    number_hawks = 0
    number_doves = 0
    for agent in model.schedule.agents:
        if agent.strategy == "hawk":
            number_hawks += 1
        elif agent.strategy == "dove":
            number_doves += 1

    n_doves.append(number_doves)
    n_hawks.append(number_hawks)


for agent in model.schedule.agents:
    print("I'm a " + agent.strategy + " and I have " + str(agent.wealth))

# Store the results
for agent in model.schedule.agents:
    all_wealth.append(agent.wealth)
    all_strategies.append(agent.strategy)
    if agent.strategy == "hawk":
        all_hawks.append(agent.wealth)
    else:
        all_doves.append(agent.wealth)

# shows a histogram of the total number of hawks and doves
plt.hist((all_strategies))
plt.title("Total number of hawks and doves")
plt.show()
# shows a histogram of the wealth of hawks and doves
plt.hist((all_hawks, all_doves), label=('Hawks', 'Doves'))
plt.title("Histogram of the wealth of hawks and doves")
plt.legend()
plt.show()

plt.plot(n_hawks, label=('Hawks'))
plt.plot(n_doves, label=('Doves'))
plt.title("Plot of number of hawks and doves at each step")
plt.legend()
plt.show()
