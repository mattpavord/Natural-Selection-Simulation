# coding=utf-8
from mechanics import *

DIET_ORDER = ['H', 'C'] # Order to which will generate zoo, h first for chases

def organise_species_list(species_list):
	ordered_list = [] 
	for di in DIET_ORDER:
		for species in species_list:
			if species.diet == di:
				ordered_list.append(species)
	for i in range(len(ordered_list)):
		ordered_list[i].index = i
	return ordered_list

def write_species_data(species_list, filename="Species.mat"):
	'''Writes a .mat file containing all the data in a species'''
	if filename[-4:] != '.mat':
		filename = filename + '.mat'
	database = open(filename, 'w')
	species_list = organise_species_list(species_list)

	# Write file
	for species in species_list: 
		database.write('BEGIN SPECIES ' + species.name +'\n')
		properties = species.__dict__.keys() # All properties of a species instance
		for prop in properties:
			line = prop + '\t\t' + str(eval('species'+'.'+ prop)).replace(' ', '')
			database.write(line + '\n')
		database.write('END' + '\n')
		database.write('\n\n' + '################' + '\n\n')

	database.close()
		

def read_species_data(filename="Species.mat"):
	'''Function that reads a species database (in format of write_species_data)
		Returns a Species list'''
	if filename[-4:] != '.mat':
		filename = filename + '.mat'
	try:
		database = open(filename)
	except:
		raise NameError('Could not find database: ' + filename)

	species_list = []
	read_species = False
	command = [] # list of strings
	for line in database:
		split = string.split(line) # split is a list of string words of the line
		if len(split) > 0:
			if split[0] == 'BEGIN':
				read_species = True
			elif split[0] == 'END':
				read_species = False
				command = 'species_list.append(Species(' + string.join(command, ', ') + '))' 
				eval(command)
				command = []

		if read_species:
			if len(split) == 2: # add to command
				try:
					float(split[1]) # argument is a number
					argument = split[0] + '=' + split[1]
				except: # argument is a string, list or tuple
					if split[1][0] == '(' or split[1][0] == '[':
						argument = split[0] + '=' + split[1]
					else: # string
						argument = split[0] + '=' + '"' + split[1] + '"'
				command.append(argument)

		else:
			command = []

	species_list = organise_species_list(species_list)
	return species_list

def generate_zoo(species_list, numbers, env):
	'''Output a n_species size list of lists each containing the animals
	each list is sized according to input (tuple)
	MUST MAKE SURE PREY GOES BEFORE PREDATORS, messes up chase mech otherwise'''
	n = len(species_list)
	if len(numbers) != n:
		raise nameError("Please input an array size that equals the number of database species")
	zoo = []
	for s in range(n):
		zoo.append([])
	s = -1
	for species in species_list: 
		s+=1
		for i in range(numbers[s]):
			zoo[s].append(Animal(
				species = species, 
				location=((2*rd.random()-1)*env.high_bound, (2*rd.random()-1)*env.high_bound),
				energy = rd.random()*40+60,
				age = rd.uniform(0, species.life_expectancy)
				))
	return zoo

def neaten_string(name):
	'''Function that replaces _ with space and capitalises first letter'''
	neat = string.split(name, '_')
	neat = string.join(neat)
	capital = neat[0]
	if capital in string.ascii_lowercase:
		index = string.ascii_lowercase.index(capital)
		capital = string.ascii_uppercase[index]
	neat = neat[1:]
	return capital + neat

