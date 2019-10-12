from mesa import Model
from mesa.time import RandomActivation
from mesa.space import MultiGrid
from mesa.datacollection import DataCollector
from agent import EvolutionaryAgent
import strategies
import random
import matplotlib.pyplot as plt
import configparser
import io

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
            # Initial Wealth is set to a random number between 1 and 15
            initialWealth = random.randrange(1, 16, 1)
            # 50 % are owners
            owner = 0
            if random.randrange(1, 11, 1) <= 5:
                owner = round(0.8 * initialWealth)
                initialWealth = round(0.2 * initialWealth)
            a = EvolutionaryAgent(i, self, evolutionaryStrategy, initialWealth, owner)
            self.schedule.add(a)

            # Add the agent to a random grid cell
            x = self.random.randrange(self.grid.width)
            y = self.random.randrange(self.grid.height)
            self.grid.place_agent(a, (x, y))

    def step(self):
        self.schedule.step()
        # Natural selection
        strategies.naturalSelection(self)


# Load the configuration file
CONFIG = configparser.ConfigParser()
CONFIG.read("./config/config.ini")
CONFIG_MODEL = CONFIG['model']

all_wealth = []
all_strategies = []
all_hawks = []
all_doves = []
all_traderHawks = []
all_traderDoves = []

n_hawks = []
n_doves = []
n_traderHawks = []
n_traderDoves = []
n_traders = []
n_nonTraders = []
n_steps = int(CONFIG_MODEL['total_agents'])
# EvolutionaryModel(N, width, height, step_cost, die_value, reproduce_value)
model = EvolutionaryModel(n_steps, 10, 10, 2, 0, 10)


for i in range(n_steps):
    model.step()
    number_hawks = 0
    number_doves = 0
    number_traders = 0
    number_nonTraders = 0
    number_TraderDoves = 0
    number_TraderHawks = 0
    for agent in model.schedule.agents:
        if agent.strategy['name'] == "hawk":
            number_hawks += 1
        elif agent.strategy['name'] == "dove":
            number_doves += 1
        elif agent.strategy['name'] == "traderHawk":
            number_TraderHawks += 1
        else:
            number_TraderDoves += 1

        if agent.strategy['trader']:
            number_traders += 1
        else:
            number_nonTraders += 1

    n_doves.append(number_doves)
    n_hawks.append(number_hawks)
    n_traderHawks.append(number_TraderHawks)
    n_traderDoves.append(number_TraderDoves)
    n_traders.append(number_traders)
    n_nonTraders.append(number_nonTraders)


for agent in model.schedule.agents:
    print("I'm a " + agent.strategy['name'] + " and I have " + str(agent.wealth) + "and I own" + str(agent.owner))

# Store the results
for agent in model.schedule.agents:
    all_wealth.append(agent.wealth)
    all_strategies.append(agent.strategy['name'])
    if agent.strategy['name'] == "hawk":
        all_hawks.append(agent.wealth)
    elif agent.strategy['name'] == "dove":
        all_doves.append(agent.wealth)
    elif agent.strategy['name'] == "traderHawk":
        all_traderHawks.append(agent.wealth)
    else:
        all_traderDoves.append(agent.wealth)


# shows a histogram of the total number of hawks and doves
plt.hist((all_strategies))
plt.title("Total number of each remaining strategy")
plt.show()

# shows a histogram of the wealth of hawks and doves
plt.hist((all_hawks, all_doves, all_traderHawks, all_traderDoves), label=('Hawks', 'Doves', 'Trader Hawks', 'Trader Doves'))
plt.title("Histogram of the wealth each strategy")
plt.legend()
plt.show()

plt.plot(n_hawks, label=('Hawks'))
plt.plot(n_doves, label=('Doves'))
plt.plot(n_traderHawks, label=('Trader Hawks'))
plt.plot(n_traderDoves, label=('Trader Doves'))
plt.title("Plot of number of hawks and doves at each step")
plt.legend()
plt.show()

plt.plot(n_traders, label=('Traders'))
plt.plot(n_nonTraders, label=('Non-Traders'))
plt.title("Plot of number of traders and non-traders at each step")
plt.legend()
plt.show()
