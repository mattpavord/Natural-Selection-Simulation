# Natural-Selection-Simulation beta 1.0
Natural Selector simulation inspired by Richard Dawkins
This program simulates a natural predator-prey relationship and allows the user to view how the populations change and adapt after an
extended period of time
Default predator prey is fox-rabbit however the user is free to create another species from the GUI

****INSTRUCTIONS****
Run main.py

****VARIABLE AND INSTANCE NAME DEFINITIONS****

Animal: An instance that contains all of the genetics, behavioural and environmental information of an INDIVIDUAL

Species: An instance that contains average and std of a species, as well as base behavioural mechanisms
Species_list: A list of species instances (not string names!)
		
Family: A list of animals of the same species

Zoo: A list of families

Behaviour: An instance containing behavioural mechanisms, e.g. how fast they run, how well they hide in that behaviour
			independent of individuals

Env / Environment: An instance containing boundaries, items, temperature, visibility, vegetation etc. of the environment

Time_p : Time Properties (updates per s (dt), s per day, days per year)

Traits: 
Feature of Species instance - A list of tuples of form (string(name), float(prob))
Feature of Animal instance - A list of strings

Notation:
Classes begin with a capital, their respective objects do not
Loc or location is always a length 2 tuple (x,y)
All directions are done by an angle anticlockwise from east (similar to polar coords) in domain -pi, pi

****GENES****

Procedure to add a gene:

Mechanics.py
1. add to Animal __init__ main body (x3)
2. add to Species __init__ argument 
3. add to Species __init__ main body
4. add to global GENES variable

data.py and main.py
Sit back and relax, everything here is done through the GENES variable

You will need to configure a mean and std value for each species in the GUI or .mat file

****BEHAVIOURS****

Behaviours are independent of genes and species type
How likely they are to enter the behaviour however will depend on genes/species and
most importantly their surroundings and state

Procedure to add a behaviour:

Mechanics.py
1. Add a variable under Behaviour class (global code) calling the class, call variable
	bName
2. Add to end of move function in animal class, need to know what to do at the end of a movement
	Thoroughly read through the behavioural mechanisms setting of this function
	There are a lot of lists with behaviour names in, does the new one belong there?
3. Does the behaviour involve another animal? If not it should go in self.passive_response()


****FUTURE IDEAS****

New diets, e.g. Scavenger (S) that eats corpses and env objects

New feature of Species - Sociality or whatever
Pack - Moves around in packs
Coumminty - Uses breeding grounds
Lone - Picks mate from full family list


****SIMULATION SPEED****

Tests, 1000 rabbits to 10 foxes, map size = 2000 sqm:

  Date		 FPS
31/10/18 	12.50 
04/11/18	10.67 

****TO DO****
Check code for TO DO's
Add mutations
Create a filter mechanism to remove zero food items from env.objects
Potentially add a gradient ascent method for rabbits
Add a suitability method for how likely they will be accepted/chosen as a mate, depend on size, speed etc
Problem loading traits

Order:
Balance - Run simulations for stable rabbit/fox ratios
Mutations
Suitability evalutaion
