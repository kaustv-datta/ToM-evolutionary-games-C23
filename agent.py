from mesa import Agent
import strategies
import random
import configparser
import ToM

# Load the configuration file
CONFIG = configparser.ConfigParser()
CONFIG.read('./config/config.ini')
CONFIG_MODEL = CONFIG['model']
CONFIG_RESULTS = CONFIG['results']
WEALTH_TYPE = CONFIG_MODEL['initial_wealth_type']
FIXED_WEALTH_VALUE = int(CONFIG_MODEL['fixed_wealth_value'])
PROPERTY_INFLATION_PRICE = float(CONFIG_MODEL['property_buy_price_percentage'])
FIXED_PROPERTY_VALUE = int(CONFIG_MODEL['fixed_property_value'])
VERBOSE = CONFIG_RESULTS['verbose_mode']

N_DELTAS = 10
N_CONTEXTS = 10

# An evolutionary agent
class EvolutionaryAgent(Agent):
    """ An agent with fixed initial wealth."""

    def __init__(self, unique_id, model, initialStrategy, wealth, owner):
        """Agent constructor method

        Arguments:
            Agent {mesa_object} -- mesa_object
            unique_id {integer} -- unique agent ID
            model {mesa_object} -- mesa_object model
            initialStrategy {string} -- strategy of the agent (dove/hawk/...)
            wealth {integer} -- wealth/money with the agent
            owner {integer} -- value of property owned by agent
        """
        super().__init__(unique_id, model)
        self.wealth = wealth
        self.strategy = initialStrategy
        self.owner = owner

        if  self.strategy=='traderToM1' or (self.strategy!='traderToM0' and random.random() >= 0.5) :
            self.ToMAgent = ToM.ToM1(N_DELTAS, N_CONTEXTS, self)
        else:
            self.ToMAgent = ToM.ToM0(N_DELTAS, N_CONTEXTS, self)

    def getTotalWealth(self):
        """Get total wealth owned by agent

        Returns:
            integer -- wealth and property owned by agent
        """
        return self.wealth + self.owner

    def assignPropertyToAgent(self):
        """Assign Property to Agent.
        """
        current_wealth = self.wealth
        # Property value is set from config file
        if WEALTH_TYPE == 'fixed':
            updated_wealth = current_wealth
            updated_owner = FIXED_PROPERTY_VALUE
        else:
            updated_wealth = round(0.2 * current_wealth)
            updated_owner = round(0.8 * current_wealth)
        self.updateAgentResource(updated_wealth, updated_owner)

    def updateAgentResource(self, wealth, owner):
        """Update the agent's resources

        Arguments:
            wealth {integer} -- money owned by agent
            owner {integer} -- property value owned by agent
        """
        self.wealth = wealth
        self.owner = owner

    def move(self):
        """Move to a random surrounding tile
        """
        possible_steps = self.model.grid.get_neighborhood(
            self.pos,
            moore=True,
            include_center=False
        )
        new_position = self.random.choice(possible_steps)
        self.model.grid.move_agent(self, new_position)

    def interact(self):
        """If another agent is on the same tile, interact with it
        """
        cellmates = self.model.grid.get_cell_list_contents([self.pos])
        # don't fight against yourself
        cellmates.remove(self)
        if len(cellmates) > 1:
            other = self.random.choice(cellmates)
            self.chooseInteraction(other)

    def chooseInteraction(self, other):
        """Choose if agent is owner or intruder

        Arguments:
            other {Agent} -- the other agent to interact with
        """
        if self.owner > 0 and other.owner == 0:
            self.chooseOwnerIntruderInteraction(self, other)
        elif self.owner == 0 and other.owner > 0:
            self.chooseOwnerIntruderInteraction(other, self)

    def chooseOwnerIntruderInteraction(self, owner, intruder):
        """Handle all interaction scenarios for various strategies

        Arguments:
            owner {Agent} -- Owner of the cell
            intruder {Agent} -- Agent intruding the cell
        """

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
        """Agent can speak

        Arguments:
            something {string} -- what to say
        """
        if VERBOSE == 'on':
            print(something)

    def reproduce(self):
        """Agent can reproduce another agent with it's own strategy

        Returns:
            object -- Reproduced agent
        """
        # generate agent with same strategy as parent
        self.saySomething('I am a ' + self.strategy +
              str(self.unique_id) + ' and I am reproducing')
        new_unique_id = self.model.latest_id + 1
        self.model.latest_id += 1

        # Initial Wealth is set from config - to a random number OR fixed amount
        if WEALTH_TYPE == 'fixed':
            initialWealth = FIXED_WEALTH_VALUE
        else:
            initialWealth = random.randrange(int(CONFIG_MODEL['initial_wealth_range_lower']), int(
                CONFIG_MODEL['initial_wealth_range_upper']))

        a = EvolutionaryAgent(new_unique_id, self.model,
                              self.strategy, initialWealth, 0)

        # the reproduced agent will stay on the same position as the parent
        self.model.grid.place_agent(a, self.pos)
        self.model.schedule.add(a)
        return a

    def die(self):
        """Death
        """
        self.saySomething('I am a ' + self.strategy +
              str(self.unique_id) + ' and I am dead')
        self.model.grid._remove_agent(self.pos, self)
        self.model.schedule.remove(self)

    def step(self):
        """Agent action to be performed per tick of the model
        """
        self.move()
        self.interact()
