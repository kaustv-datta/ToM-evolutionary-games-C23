from mesa import Agent
import strategies
import random
import configparser
import ToM

# Load the configuration file
CONFIG = configparser.ConfigParser()
CONFIG.read('./config/config.ini')
CONFIG_MODEL = CONFIG['model']
WEALTH_TYPE = CONFIG_MODEL['initial_wealth_type']
FIXED_WEALTH_VALUE = int(CONFIG_MODEL['fixed_wealth_value'])
PROPERTY_INFLATION_PRICE = float(CONFIG_MODEL['property_buy_price_percentage'])
FIXED_PROPERTY_VALUE = int(CONFIG_MODEL['fixed_property_value'])

N_DELTAS = 10
N_CONTEXTS = 10

# An evolutionary agent
class EvolutionaryAgent(Agent):
    """ An agent with fixed initial wealth."""
    def __init__(self, unique_id, model, initialStrategy, wealth, owner):
        super().__init__(unique_id, model)
        self.wealth = wealth
        self.strategy = initialStrategy
        self.owner = owner

        if  self.strategy=='traderToM1' or (self.strategy!='traderToM0' and random.random() >= 0.5) :
            self.ToMAgent = ToM.ToM1(N_DELTAS, N_CONTEXTS, self)
        else:
            self.ToMAgent = ToM.ToM0(N_DELTAS, N_CONTEXTS, self)

    def getTotalWealth(self):
        return self.wealth + self.owner

    # Update agent wealth and property owned
    def updateAgentResource(self, wealth, owner):
        self.wealth = wealth
        self.owner = owner
        
    # Move to a random surrounding tile
    def move(self):
        possible_steps = self.model.grid.get_neighborhood(
            self.pos,
            moore=True,
            include_center=False
        )
        new_position = self.random.choice(possible_steps)
        self.model.grid.move_agent(self, new_position)
        
    # If another agent is on the same tile, interact with it
    def interact(self):
        cellmates = self.model.grid.get_cell_list_contents([self.pos])
        # don't fight against yourself
        cellmates.remove(self)
        if len(cellmates) > 1:
            other = self.random.choice(cellmates)
            self.chooseInteraction(other)

    def chooseInteraction(self, other):
        if self.owner > 0 and other.owner == 0:
            self.chooseOwnerIntruderInteraction(self, other)
        elif self.owner == 0 and other.owner > 0:
            self.chooseOwnerIntruderInteraction(other, self)

    def chooseOwnerIntruderInteraction(self, owner, intruder):
        # The intruder values the property as v = 0.8 of its own wealth
        # Agents will trade if both are traders and if the intruder values the property more then the owner
        estimated_buying_price = owner.owner + (PROPERTY_INFLATION_PRICE * owner.owner)

        if owner.strategy == 'dove':
            # check if intruder is dove/hawk/possessor/trader
            if intruder.strategy == 'dove':
                # dove-dove
                strategies.emulateDoveDoveStrategy(owner, intruder)
            elif intruder.strategy == 'hawk':
                # dove-hawk
                strategies.emulateHawkDoveStrategy(intruder, owner)
            elif intruder.strategy == 'possessor':
                # dove-possessor == dove-dove
                strategies.emulateDoveDoveStrategy(owner, intruder)
            elif intruder.strategy == 'trader':
                # dove-trader
                strategies.emulateDoveDoveStrategy(owner, intruder)
            elif intruder.strategy == 'traderToM0':
                # dove-trader
                strategies.emulateDoveDoveStrategy(owner, intruder)
            elif intruder.strategy == 'traderToM1':
                # dove-trader
                strategies.emulateDoveDoveStrategy(owner, intruder)

        elif owner.strategy == 'hawk':
            # check if intruder is dove/hawk/possessor/trader
            if intruder.strategy == 'dove':
                # hawk-dove
                strategies.emulateHawkDoveStrategy(owner, intruder)
            elif intruder.strategy == 'hawk':
                # hawk-hawk
                strategies.emulateHawkHawkStrategy(owner, intruder)
            elif intruder.strategy == 'possessor':
                # hawk-possessor == hawk-dove
                strategies.emulateHawkDoveStrategy(owner, intruder)
            elif intruder.strategy == 'trader':
                # hawk-traderm == hawk-possessor == hawk-dove
                strategies.emulateHawkDoveStrategy(owner, intruder)
            elif intruder.strategy == 'traderToM0':
                # hawk-traderm == hawk-possessor == hawk-dove
                strategies.emulateHawkDoveStrategy(owner, intruder)
            elif intruder.strategy == 'traderToM1':
                # hawk-traderm == hawk-possessor == hawk-dove
                strategies.emulateHawkDoveStrategy(owner, intruder)

        elif owner.strategy == 'possessor':
            # check if intruder is dove/hawk/possessor/trader
            if intruder.strategy == 'dove':
                # possessor-dove
                strategies.emulateHawkDoveStrategy(owner, intruder)
            elif intruder.strategy == 'hawk':
                # possessor-hawk
                strategies.emulateHawkHawkStrategy(owner, intruder)
            elif intruder.strategy == 'possessor':
                # possessor-possessor
                strategies.emulateHawkDoveStrategy(owner, intruder)
            elif intruder.strategy == 'trader':
                # possessor-trader
                strategies.emulateHawkDoveStrategy(owner, intruder)
            elif intruder.strategy == 'traderToM0':
                # hawk-traderm == hawk-possessor == hawk-dove
                strategies.emulateHawkDoveStrategy(owner, intruder)
            elif intruder.strategy == 'traderToM1':
                # hawk-traderm == hawk-possessor == hawk-dove
                strategies.emulateHawkDoveStrategy(owner, intruder)

        elif owner.strategy == 'trader':
            # check if intruder is dove/hawk/possessor/trader
            if intruder.strategy == 'dove':
                # trader-dove
                strategies.emulateHawkDoveStrategy(owner, intruder)
            elif intruder.strategy == 'hawk':
                # trader-hawk
                strategies.emulateHawkHawkStrategy(owner, intruder)
            elif intruder.strategy == 'possessor':
                # trader-possessor
                strategies.emulateHawkDoveStrategy(owner, intruder)

            elif intruder.strategy == 'trader':
                # trader-trader
                if estimated_buying_price < intruder.wealth:
                    strategies.emulateTradersStrategy(owner, intruder)

            elif intruder.strategy == 'traderToM0' or intruder.strategy == 'traderToM1':
                #trader no ToM - trader with ToM
                if estimated_buying_price < intruder.wealth:
                    strategies.emulateTraderToMStrategy(owner, intruder)

        elif owner.strategy == 'traderToM0' or owner.strategy == 'traderToM1':
            # check if intruder is dove/hawk/possessor/trader
            if intruder.strategy == 'dove':
                # trader-dove
                strategies.emulateHawkDoveStrategy(owner, intruder)
            elif intruder.strategy == 'hawk':
                # trader-hawk
                strategies.emulateHawkHawkStrategy(owner, intruder)
            elif intruder.strategy == 'possessor':
                # trader-possessor
                strategies.emulateHawkDoveStrategy(owner, intruder)
            elif intruder.strategy == 'trader':
                # trader with ToM-trader
                if estimated_buying_price < intruder.wealth:
                    strategies.emulateToMTraderStrategy(owner, intruder)

            elif intruder.strategy == 'traderToM0' or intruder.strategy == 'traderToM1':
                # trader no ToM - trader with ToM
                if estimated_buying_price < intruder.wealth:
                    strategies.emulateToMToMStrategy(owner, intruder)

            
    def saySomething(self, something):
        if 1==0:
            print(something)

    def reproduce(self):
        # generate agent with same strategy as parent
        # print('I am a ' + self.strategy + str(self.unique_id) + ' and I am reproducing')
        new_unique_id = self.model.latest_id + 1
        self.model.latest_id += 1
        
        # Initial Wealth is set from config - to a random number OR fixed amount
        if WEALTH_TYPE == 'fixed':
            initialWealth = FIXED_WEALTH_VALUE
        else:
            initialWealth = random.randrange(int(CONFIG_MODEL['initial_wealth_range_lower']), int(
            CONFIG_MODEL['initial_wealth_range_upper']))
        
        # a newborn has a probability to own a property of 50 %
        owner = 0
        if random.randrange(1, 11, 1) <= 5:
            if WEALTH_TYPE == 'fixed':
                owner = FIXED_PROPERTY_VALUE
            else:
                initialWealth = round(0.2 * initialWealth)
                owner = round(0.8 * initialWealth)
        
        a = EvolutionaryAgent(new_unique_id, self.model, self.strategy, initialWealth, owner)
        
        # the reproduced agent will stay on the same position as the parent
        self.model.grid.place_agent(a, self.pos)
        self.model.schedule.add(a)

    def die(self):
        # Death
        # print('I am a ' + agent.strategy + str(agent.unique_id) + ' and I am dead')
        self.model.grid._remove_agent(self.pos, self)
        self.model.schedule.remove(self)

    def checkToDie(self):
        # if the wealth of the agent is lower than the 'die_value', the die() method will be called
        living = True
        if self.wealth <= self.model.die_value:
            living = False
            self.die()
        return living

    
    # Action to be performed per tick of the model
    def step(self):
        self.move()
        self.interact()