from mesa import Agent
import strategies
import random

# An evolutionary agent
class EvolutionaryAgent(Agent):
    """ An agent with fixed initial wealth."""
    def __init__(self, unique_id, model, initialStrategy, wealth):
        super().__init__(unique_id, model)
        self.wealth = wealth
        self.strategy = initialStrategy
        
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
        # Fight for wealth, which is a random number between 1 an 15
        wealth = random.randrange(1, 16, 1)
        if self.strategy == 'hawk':
            if other.strategy == 'dove':
                strategies.emulateHawkDoveStrategy(self, other, wealth)
            else:
                strategies.emulateHawkHawkStrategy(self, other, wealth)
        else:
            if other.strategy == 'dove':
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
        a = EvolutionaryAgent(new_unique_id, self.model, self.strategy, 10)
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
        # TODO: To Be Discussed - commenting for now to conform to the paper
        # decreases the wealth of an agent by the step_costs
        # self.wealth -= self.model.step_cost
        # checks if the agent will make it the next round
        # living = self.checkToDie()
        # if living:
        self.move()
        self.interact()
        # TODO: To Be Discussed - paper mentions strategies replicating
        # if the agent has reached a wealth higher than the reproduce_value, it will reproduce itselfe
        # if self.wealth > self.model.reproduce_value:
        #     self.reproduce()