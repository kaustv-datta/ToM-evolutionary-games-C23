import random
strategyList = ['hawk','dove']

# Hawk-Dove OR Dove-Hawk
def emulateHawkDoveStrategy(hawk, dove, wealth):
    # hawk gains resource
    hawk.wealth += wealth
    hawk.saySomething('I am hawk. I gained ' + str(wealth))
    # dove loses resource
    dove.saySomething('I am dove. I lost')

# Hawk-Hawk
def emulateHawkHawkStrategy(hawk1, hawk2, wealth):
    # every fight costs the hawk a random number between 1 and 15
    h = random.randrange(1, 16, 1)
    # hawk loses resource
    hawk1.wealth += wealth/2 - h
    hawk1.saySomething('I am hawk1. I gained ' + str(wealth/2 - h))
    # hawk loses resource
    hawk2.wealth += wealth/2 - h
    hawk2.saySomething('I am hawk2. I gained ' + str(wealth/2 - h))

# Dove-Dove
def emulateDoveDoveStrategy(dove1, dove2, wealth):
    # dove always shares resource
    dove1.wealth += wealth/2
    dove1.saySomething('I am dove1. I gained ' + str(wealth/2))
    # dove always shares resource resource
    dove2.wealth += wealth/2
    dove2.saySomething('I am dove2. I gained ' + str(wealth/2))
