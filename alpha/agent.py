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
        if len(cellmates) > 1:
            other = self.random.choice(cellmates)
            wealth = random.randrange(1, 16, 1)
            # other.wealth += 1
            # self.wealth -= 1
            # self.saySomething()
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
    
    # Action to be performed per tick of the model
    def step(self):
        self.move()
        # if self.wealth > 0:
        self.interact()