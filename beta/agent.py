from mesa import Agent
import strategies
import random

# An evolutionary agent
class EvolutionaryAgent(Agent):
    """ An agent with fixed initial wealth."""
    def __init__(self, unique_id, model, initialStrategy, wealth, owner):
        super().__init__(unique_id, model)
        self.wealth = wealth
        self.strategy = initialStrategy
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
        else:
            self.chooseWealthInteraction(other)

    def chooseOwnerIntruderInteraction(self, owner, intruder):
        # The intruder values the property as v = 0.9 of its own wealth
        # Agents will trade if both are traders and if the intruder values the property more then the owner
        if owner.strategy['trader'] and intruder.strategy['trader'] and owner.owner < round(0.8 * intruder.wealth):
            strategies.emulateTraders(owner, intruder)
        elif intruder.strategy['nonTradeStrategy'] == 'dove':
            strategies.emulatePossessorDove(owner, intruder)
        else:
            strategies.emulatePossessorHawk(owner, intruder)

    def chooseWealthInteraction(self, other):
        # Fight for wealth, which is a random number between 1 an 15
        wealth = random.randrange(1, 16, 1)
        if self.strategy['nonTradeStrategy'] == 'hawk':
            if other.strategy['nonTradeStrategy'] == 'dove':
                strategies.emulateHawkDoveStrategy(self, other, wealth)
            else:
                strategies.emulateHawkHawkStrategy(self, other, wealth)
        else:
            if other.strategy['nonTradeStrategy'] == 'dove':
                strategies.emulateDoveDoveStrategy(self, other, wealth)
            else:
                strategies.emulateHawkDoveStrategy(other, self, wealth)
            
    def saySomething(self, something):
        print(something)

    def reproduce(self):
        # generate agent with same strategy as parent
        # print('I am a ' + self.strategy + str(self.unique_id) + ' and I am reproducing')
        new_unique_id = self.model.latest_id + 1
        self.model.latest_id += 1
        # Initial Wealth is set to a random number between 1 and 16
        initialWealth = random.randrange(1, 16, 1)
        # a newborn has a probability to own a property of 50 %
        owner = 0
        if random.randrange(1, 11, 1) <= 5:
            owner = round(0.8 * initialWealth)
            initialWealth = round(0.2 * initialWealth)
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