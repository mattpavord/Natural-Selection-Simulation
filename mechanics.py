# coding=utf-8
from __future__ import division
import numpy as np
import random as rd
import string
import time
from numpy.random import normal

# Global variables
CHASERS = [] # List of predators who are currently in a chase (i.e. prey HAS spotted them)
BABIES = [] # List of newly born babies

#Global conts
IGNORE_DIST = 100 # Min distance that animals will ignore each other

#Time measure variables
t_prey_search = 0
t_pred_search = 0
t_move = 0
t_behaviour_move = 0
t_update_state = 0
t_action = 0

class Animal:

	def __init__(self, species,
		location=(0,0), energy=100, age=0,
		parents = None, mutation_chance=0.1):
        
        # genes to potentially add:
        # hearing

        # Inherent
		self.number = species.number #ID
		self.species = species #  Instance, see Species class below
		self.diet = species.diet # C/H
		self.name = species.name + ' ' + str(self.number) # unique
		self.gender = 'M' if rd.random() < 0.5 else 'F'

		# Genes, Env independent, only used in breeding
		if parents==None: # First generation
			self.gstealth = normal(species.stealth, species.stealth_std, 1)[0] 
			self.gdetection = normal(species.detection, species.detection_std, 1)[0] 
			self.gstrength = normal(species.strength, species.strength_std, 1)[0] 
			self.gsize = normal(species.size, species.size_std, 1)[0] 
			self.gspeed = normal(species.speed, species.speed_std, 1)[0] 
			self.gacceleration = normal(species.acceleration, species.acceleration_std, 1)[0]
			self.gideal_temp = normal(species.ideal_temp, species.ideal_temp_std, 1)[0] 
			self.gmature_age = normal(species.mature_age, species.mature_age_std, 1)[0] 
			self.glife_expectancy = normal(species.life_expectancy, species.life_expectancy_std, 1)[0] 
			self.genergy_loss = normal(species.energy_loss, species.energy_loss_std, 1)[0]
			self.gfield_view = normal(species.field_view, species.field_view_std, 1)[0]	
			self.gobs_time = normal(species.obs_time, species.obs_time_std, 1)[0]	
			self.gbreeding_gap = normal(species.breeding_gap, species.breeding_gap_std, 1)[0]
			self.gattraction = normal(50, 20, 1)[0]	
	
		else: # Second gen or later
			self.gstealth = parents[0].gstealth if rd.random() < 0.5 else parents[1].gstealth
			self.gdetection = parents[0].gdetection if rd.random() < 0.5 else parents[1].gdetection
			self.gstrength = parents[0].gstrength if rd.random() < 0.5 else parents[1].gstrength 
			self.gsize = parents[0].gsize if rd.random() < 0.5 else parents[1].gsize
			self.gspeed = parents[0].gspeed if rd.random() < 0.5 else parents[1].gspeed
			self.gacceleration = parents[0].gacceleration if rd.random() < 0.5 else parents[1].gacceleration
			self.gideal_temp = parents[0].gideal_temp if rd.random() < 0.5 else parents[1].gideal_temp 
			self.gmature_age = parents[0].gmature_age if rd.random() < 0.5 else parents[1].gmature_age
			self.glife_expectancy = parents[0].glife_expectancy if rd.random() < 0.5 else parents[1].glife_expectancy
			self.genergy_loss = parents[0].genergy_loss if rd.random() < 0.5 else parents[1].genergy_loss
			self.gfield_view = parents[0].gfield_view if rd.random() < 0.5 else parents[1].gfield_view
			self.gobs_time = parents[0].gobs_time if rd.random() < 0.5 else parents[1].gobs_time
			self.gbreeding_gap = parents[0].gbreeding_gap if rd.random() < 0.5 else parents[1].gbreeding_gap
			self.gattraction = parents[0].gattraction if rd.random() < 0.5 else parents[1].gattraction

		# traits
		self.traits = []
		if parents == None:
			for trait, prob in species.traits:
				if rd.random() < prob:
					self.traits.append(trait)
		else:
			for trait in parents[0].traits: # mums traits
				if trait in parents[1].traits: # trait in both parents = 100% chance of inheritance
					self.traits.append(trait)
				elif rd.random() < 0.5:
					self.traits.append(trait)
			for trait in parents[1].traits: # dads traits
				if trait not in self.traits and rd.random() < 0.5:
					self.traits.append(trait)

		# Genetic independent
		self.location = location # Coords (x,y) in m
		self.speed = 0
		self.direction = 2*np.pi*rd.random()
		self.energy = energy # %
		self.age = age # Years
		self.behaviour = bRoam
		self.prey_target = [] # animals that self will hunt, can be more than one however will only hunt first
		self.predators = [] # animals that could hunt self
		self.food = None # Food interest (instance)
		self.breeding_ground = None # Breeding_ground instance
		self.desired_location = None # location (x,y) Used for migrate behaviour, TO DO make instance possible
		self.mate = None # Animal instance
		self.dead = False
		if self.age < self.gmature_age:
			self.breeding_age = self.gmature_age # will go up by a gap when it has a baby
		else:
			self.breeding_age = self.age + self.gbreeding_gap *rd.random() # stop first gen all breeding at once

		# Env and self dependent, add to update_state
		self.stealth = self.gstealth # %
		self.detection = self.gdetection # %
		self.strength = self.gstrength 
		self.size = self.gsize # kg
		self.maxspeed = self.gspeed # top speed in m/s
		self.acceleration = self.gacceleration # m/s/s
		self.obs_time = int(self.gobs_time) # how frequently they observe (int)		

		# Rooted in genes, constant
		self.ideal_temp = self.gideal_temp 
		self.energy_loss = self.genergy_loss 
		self.mature_age = self.gmature_age # Years
		self.life_expectancy = self.glife_expectancy # Years
		self.attraction = self.gattraction # % chance to attract a mate
		self.field_view = self.gfield_view *np.pi/180 # angle at which can spot company (rad)
		self.breeding_gap = self.gbreeding_gap

		# Plotting only
		self.color = species.color
		self.shape = species.shape

		# Misc.
		self.timer = rd.randint(0,2000) # in s, used for update_state and obs_time

		# Other variables
		species.number += 1

	######################################################################################
	########################## Level 1 Functions - Coordination ##########################
	######################################################################################

	def action(self, time_p, env, zoo):
		'''Generic 'do' function, organise self.behaviour here'''
		global t_action
		tik = time.time()
		if self.timer % time_p.s_per_day == 0:
			self.update_state(env, time_p, end_day=True)
		else:
			self.update_state(env, time_p)

		self.behaviour_move(time_p, env)
		if len(self.traits) > 0:
			self.trait_move(time_p, env)
		self.location_move(time_p, env)

		if (self.timer % int(self.obs_time*self.behaviour.obs_time_f+0.5) == 0 and 
			self.behaviour.name not in ["Chase", "Stalk"]): # look
			if self.diet == 'H':
				self.search_predator(zoo)
			elif self.diet == 'C':
				self.search_prey(zoo)
		t_action += time.time() - tik

	#################################################################################
	########################## Level 2 Functions - Routine ##########################
	#################################################################################

	# Every Update

	def location_move(self, time_p, env):
		'''Update self.location based on behaviour'''
		global t_move
		tik = time.time()
		x, y = self.location
		dt = time_p.dt
		direction_change = 0 # direction changed in rad
		prob_change_dir = self.behaviour.prob_change_dir # probability to completely change direction
		drift = self.behaviour.drift # max drifting angle in rad
		ideal_speed = self.gspeed*self.behaviour.ideal_speed_f
		if ideal_speed > self.maxspeed:
			ideal_speed = self.maxspeed

		if self.behaviour.name in ["Chase", "Stalk"]:
			if len(self.prey_target)>0: # Point towards target
				direction_change = self.angle(self.prey_target[0]) - self.direction
			else: # Should not be the case
				print self.behaviour.name, "without target???", "Investigate this"
				self.passive_response()

		elif self.behaviour.name in ["Court"]:
			if self.mate: # Point towards target
				direction_change = self.angle(self.mate) - self.direction
			else: # Should not be the case
				print self.behaviour.name, "without mate???", "Investigate this"
				self.passive_response()

		elif self.behaviour.name in ["Migrate"]:
			if self.desired_location != None:
				if isinstance(self.desired_location, tuple): # if desired location is in form (x,y)
					direction_change = self.angle_to_loc(self.desired_location) - self.direction
				else: # desired location is an object with a location element, e.g. breeding ground
					direction_change = self.angle(self.desired_location) - self.direction
			else:
				self.passive_response()

		elif self.behaviour.name in ["Chased", "Retreat"]:
			if len(self.predators)>0: # point away from target
				direction_change = np.pi + self.angle(self.predators[0]) - self.direction
				# needs fixing for more than one predator
				# use a weighted average (weighted by distance)

		if self.speed < ideal_speed:
			self.speed += self.acceleration*dt # constant finite acceleration
		if self.speed > ideal_speed:
			self.speed = ideal_speed # instant deceleration

		# Boundary deterrent
		if self.behaviour.name != 'Migrate':
			if x > env.high_bound*9/10 and np.cos(self.direction+direction_change)>0:
				prob_change_dir += 0.2
			elif x < env.low_bound*9/10 and np.cos(self.direction+direction_change)<0:
				prob_change_dir += 0.2
			elif y > env.high_bound*9/10 and np.sin(self.direction+direction_change)>0:
				prob_change_dir += 0.2
			elif y < env.low_bound*9/10 and np.sin(self.direction+direction_change)<0:
				prob_change_dir += 0.2

		# Random Direction changes
		if rd.random() < prob_change_dir:
			direction_change += np.pi + np.pi/2 * (2*rd.random()-1)
		direction_change += drift * (2*rd.random()-1)

		# Movement mechanisms
		self.direction += direction_change
		while self.direction > np.pi:
			self.direction -= 2*np.pi # keep direction range between -pi, pi
		while self.direction < -np.pi:
			self.direction += 2*np.pi 
		self.speed *= np.cos(direction_change) # cannot swoop back
		if self.speed < 0:
			self.speed = 0
		x += self.speed * np.cos(self.direction) * dt
		y += self.speed * np.sin(self.direction) * dt
		self.location = (x,y)
		t_move += time.time() - tik

		## TRAIT MECHANISMS ##

	
	def behaviour_move(self, time_p, env):
		'''Action due to behaviour'''
		# Starving response, emergency, do not rely on
		global t_behaviour_move 
		tik = time.time()
		if self.energy < 40 and self.behaviour.name not in ["Chase", "Chased", "Stalk", "Eat", "Graze", "Hunt"]:
			if self.diet == 'H':
				self.behaviour = bGraze
			elif self.diet == 'C':
				self.behaviour = bHunt

		# if self.behaviour.name not in ["Chase", "Stalk"]: 
		# 	self.prey_target = [] # Can only have prey target for these behaviours

		if self.behaviour.name not in ["Roam", "Retreat"]: # save time if in roam

			if self.behaviour.name == "Hide":
				for animal in self.predators:
					distance = self.distance(animal)
					if distance < 5: # too close, run
						self.behaviour = bChased
					
			elif self.behaviour.name == "Migrate":
				if self.desired_location == None: # remove after test
					raise NameError("Animal migrating with no desired location")
				if isinstance(self.desired_location, tuple): # if it is a location
					if self.distance_to_loc(self.desired_location) < 1:
						self.desired_location = None
						self.passive_response() # arrived
				elif self.distance(self.desired_location) < self.desired_location.radius:
						self.desired_location = None
						self.passive_response() # arrived
				if self.energy < 75: # food comes first
					self.passive_response()

			elif self.behaviour.name == "Stalk":
				distance = self.distance(self.prey_target[0])
				if distance < 10: # Point at which chasing, may need varying
					self.behaviour = bChase
				if self in self.prey_target[0].predators: # Spotted, give chase
					self.behaviour = bChase

			elif self.behaviour.name == "Chase":# Do not evaluate chase conclusions here, unfair on prey if pred moves first
				global CHASERS
				if self not in CHASERS:
					CHASERS.append(self)
					if self not in self.prey_target[0].predators: # if prey has not spotted predator
						self.prey_target[0].predators.append(self) # prey spots predator
					self.prey_target[0].behaviour = bChased # prey starts running

			elif self.behaviour.name == "Eat":
				if self.food.food - self.size/40 *time_p.dt >= 0: # can only eat 1/40 of size of food per s
					amount_eaten = self.size/40 *time_p.dt
				else:
					amount_eaten = self.food.food # will remove object elsewhere
				self.update_state(env, time_p, mass_eaten=amount_eaten) # will remove self.food if full here
				
			elif self.behaviour.name == "Graze":
				self.update_state(env, time_p, mass_eaten=env.veg) # passive response built in update_state

			elif self.behaviour.name == "Mate":
				if self.breeding_ground:
					sbg = self.breeding_ground
					if self.distance(sbg) < sbg.radius:
						if self.gender == 'M':
							self.search_mate(self.breeding_ground) # will turn to court if valid
					else:
						self.behaiour = bMigrate
						self.desired_location = self.breeding_ground
				else: # select a breeding ground
					self.search_bg(env)
				if self.energy < 75: # food comes first
					self.passive_response()

			elif self.behaviour.name == "Court": # Male only
				if self.mate in self.breeding_ground.females:
					if self.melee(self.mate):
						if self.mate.accept_male(self): # if female accepts male
							Generate_babies(mother=self.mate, father=self, env=env)
						else:
							self.mate = None
							self.passive_response()
					elif self.energy < 75:
						self.passive_response()
				else:
					self.passive_response()

		# ignore animals further away than IGNORE_DIST
		remove = []
		for animal in self.prey_target: 
			if self.distance(animal) > IGNORE_DIST:
				remove.append(animal)
		for animal in remove:
			self.prey_target.remove(animal)
		remove = []
		for animal in self.predators: 
			if self.distance(animal) > 2*IGNORE_DIST: # make longer to stop prey forgetting about a current chase
				remove.append(animal)
		for animal in remove:
			self.predators.remove(animal)
		if self.behaviour.name in ["Stalk", "Chase", "Chased", "Hide", "Retreat", "Roam"]:	
			if len(self.predators) == 0 and len(self.prey_target) == 0:
				self.passive_response()
		t_behaviour_move += time.time() - tik


	def trait_move(self, time_p, env):
		'''Trait responses'''

		if self.behaviour.name == "Chase":

			if "Pounce" in self.traits: # Pounce onto prey 
				if self.distance(self.prey_target[0]) < 5:
					self.location = self.prey_target[0].location

		if self.behaviour.name == "Chased":

			if "Bound" in self.traits: # Change direction without speed penalty
				if self.distance(self.predators[0]) < 5:
					self.direction = self.direction + np.pi/2 * rd.randint(-1,1)
					if self.direction > np.pi:
						self.direction -= np.pi*2
					if self.direction < -1*np.pi:
						self.direction += np.pi*2


	def update_state(self, env, time_p, mass_eaten=0, end_day=False):
		'''To be run after every tick, at the end of each day and after eating'''
		global t_update_state
		tik = time.time()
		if mass_eaten > 0:
			self.energy += 500*mass_eaten/self.size # Requires 20% of body size to fill completely
			if self.energy > 100:
				self.food = None
				self.passive_response() # must have been eating to be in this situation, only eat when passive
				self.energy = 100
		if self.energy<=0:
			print self.name, "starved to death"
			self.dead=True
		if end_day:
			self.age += 1 / time_p.day_per_year
			if self.will_it_die():
				# print self.name, "died of old age"
				self.dead=True
		self.qf = self.eval_qf(env)
		self.stealth = self.gstealth * self.behaviour.stealth_f * env.vis
		if self.stealth > 99:
			self.stealth = 99
		self.detection = self.gdetection * self.behaviour.detection_f # can have detection = 0 or > 100
		self.size = self.eval_size() 
		self.strength = self.gstrength * self.qf
		self.maxspeed = self.gspeed * self.qf
		self.acceleration = self.gacceleration * self.qf	
		self.timer += time_p.dt
		self.energy -= self.energy_loss * self.behaviour.energy_loss_f * time_p.dt / time_p.s_per_day
		# include cold loss as well
		t_update_state += time.time() - tik


	# Search (Slow) functions

	def search_prey(self, zoo):
		'''Searches for nearby prey, input zoo, changes self.prey_target if found'''
		global t_prey_search
		tik = time.time()
		if self.diet=='C' and len(self.prey_target)==0:
			for family in zoo:
				if len(family) != 0 and family[0].diet=='H':
					for animal in family:
						if self.detect(animal):
							#print self.name, 'has detected', animal.name
							if self.will_it_attack(animal):
								self.prey_target.append(animal)
								self.prey_spotted_response()
		t_prey_search += time.time() - tik

	def search_predator(self, zoo):
		'''Searches for nearby predators, input zoo, changes self.predators if found'''
		global t_pred_search
		tik = time.time()
		for family in zoo:
			if len(family) != 0 and family[0].diet=='C': # does family contain live carnivores
				for animal in family:
					if animal not in self.predators:
						if self.detect(animal):
							#print self.name, 'has detected', animal.name
							self.predators.append(animal)
							self.predator_spotted_response()
		t_pred_search += time.time() - tik

	def search_mate(self, bg):
		'''Males search for female mates in breeding ground'''
		if self.gender == 'F': # get rid of eventually
			raise NameError('No women allowed in this function')
		best_dist = 1e8
		for animal in bg.females:
			if animal.behaviour.name == 'Mate': # consent is key
				if self.distance(animal) < best_dist: # replace with suitability
					self.mate = animal
					best_dist = self.distance(animal)
		if self.mate != None:
			self.behaviour = bCourt

	def search_bg(self, env):
		'''Search for a suitable breeding ground'''
		potential_bg = []
		for bg in env.breeding_grounds[self.species.index]:
			if bg.name == self.species.name:
				potential_bg.append(bg)
		if len(potential_bg) == 0:
			error_msg = (self.species.name + 
				" cannot reproduce as there are no breeding grounds for this species")
			raise NameError(error_msg)
		best_dist = 1e8 # a number that is bigger than any distance
		for bg in potential_bg:
			dist = self.distance(bg)
			if dist < best_dist:
				self.breeding_ground = bg
				best_dist = dist
		if self.gender == 'M':
			self.breeding_ground.males.append(self)
		elif self.gender == 'F':
			self.breeding_ground.females.append(self)

	################################################################################
	######################## Level 3 Functions - Evaluate ##########################
	################################################################################

	# Stats

	def eval_qf(self, env): #environment dependent quality factor
		'''Returns quality factor based off Temp, hunger'''
		temp_difference = env.T - self.gideal_temp
		if self.energy > 60: # greater than 60% will not feel any effect
			qf = 1
		elif self.energy > 30:
			qf = 0.5 + 0.5 * (self.energy-30)/30
		if self.energy <= 30:
			qf = 0.5
		if abs(temp_difference) > 20:
			qf *= 0.5 # TO DO - Environment effect on qf
		return qf

	def eval_size(self):
		if self.age >= self.mature_age:
			return self.gsize
		else:
			return self.gsize * (1/20 + 19/20*self.age/self.mature_age)

	def will_it_die(self):
		'''TO DO'''
		if self.age > self.life_expectancy:
			return True
		else:
			return False

	def distance(self, company):
		'''Return distance between animal and another animal or instance with location'''
		x1, y1 = self.location
		x2, y2 = company.location
		return ((x2-x1)**2 + (y2-y1)**2)**0.5

	def distance_to_loc(self, loc):
		'''Return distance between animal and specified location'''
		x1, y1 = self.location
		x2, y2 = loc
		return ((x2-x1)**2 + (y2-y1)**2)**0.5

	def melee(self, company):
		'''Returns true if in melee company for breeding or fighting'''
		if self.distance(company) < 1:
			return True
		else:
			return False

	def angle(self, company):
		'''Returns angle required to turn (aclock) from East to face company range(-pi,pi)'''
		return self.angle_to_loc(company.location)

	def angle_to_loc(self, loc):
		'''Returns angle required to turn (aclock) from East to face specified location'''
		x1, y1 = self.location
		x2, y2 = loc
		dy = y2 - y1
		dx = x2 - x1
		theta = np.arctan(dy/dx)
		if dx < 0: # arctan cyclic to pi
			theta-=np.pi
		if theta > np.pi:
			theta -= 2*np.pi
		return theta

	def detect(self, company, max_distance=IGNORE_DIST):
		'''Returns true or false whether company is detected'''
		# check if it is in view range
		distance = self.distance(company)
		if distance > max_distance:
			return False
		if distance < 1:
			return True
		angle = self.angle(company)
		if (self.direction - self.field_view/2 < angle < self.direction + self.field_view/2
			or self.direction - self.field_view/2 < angle+2*np.pi < self.direction + self.field_view/2
			or self.direction - self.field_view/2 < angle-2*np.pi < self.direction + self.field_view/2):
			prob = self.detection/100*(1-company.stealth/100) *np.exp((1/2-distance/20)) # needs revising
			# if distance < 40:
			# 	print distance, prob # Test code
			if prob > 1:
				return True
			if rd.random() < prob:
				return True
			else:
				return False
		else:
			return False

	def will_it_attack(self, company):
		'''To Do'''
		return True

	def win_battle(self, company):
		'''Returns True if self wins a battle against company
		Returns False if company not killed
		Only use if self has inititated the battle  TO DO'''
		return True	

	def accept_male(self, company):
		'''Returns true or false on whether a female will accept a male mate'''
		if self.gender == 'M':
			raise NameError("No boys in this function!") # remove post testing
		return True

	# Behaviour responses (Not to be run every loop)

	def predator_spotted_response(self):
		'''Change behaviour based on a predator being spotted'''
		remove = []
		for animal in self.predators:
			if len(animal.prey_target) > 0:
				if animal.prey_target[0].name == self.name: # a predator is hunting self
					self.behaviour = bChased
				else:
					remove.append(animal) # predator is interested in other prey, remove from self interest
			else: # Predator has not spotted self yet
				# TO DO change behaviour to chased, retreat or hide based on random, behavioural factors and distance
				self.behaviour = bChased 
		for animal in remove:
			self.predators.remove(animal)

	def prey_spotted_response(self):
		'''To be run only on the loop that prey is spotted
		TO DO'''
		self.behaviour = bStalk

	def passive_response(self):
		'''Behaviour change based on no predator or prey
		TO DO - Rewrite in terms of random and learnt behaviours'''
		#print self.name, "Passive response"
		if self.food != None:
			self.behaviour = bEat
		elif self.energy < 75: # Food
			if self.diet == 'C':
				self.behaviour = bHunt
			elif self.diet == 'H':
				self.behaviour = bGraze
		elif self.desired_location != None:
			self.behaviour = bMigrate
		elif self.age > self.breeding_age:
			self.behaviour = bMate
		else: 
			self.behaviour = bRoam


###################################################################################

class Behaviour:

	def __init__(self, name, ideal_speed_f,
		drift=0, prob_change_dir=0, 
		stealth_f=1, energy_loss_f=1, detection_f=1, obs_time_f=1):

		self.name = name
		self.ideal_speed_f = ideal_speed_f # fraction of genetic speed <=1
		self.stealth_f = stealth_f # stealth boost factor
		self.energy_loss_f = energy_loss_f # energy loss factor
		self.detection_f = detection_f # detection factor
		self.drift = drift # max angle that animal will drift when moving in rad
		self.prob_change_dir = prob_change_dir # Probability of direction change
		self.obs_time_f = obs_time_f # factor to increase/decrease obs time

bRoam = Behaviour( # Nothing to do
	name= "Roam", 
	ideal_speed_f= 0.2,
	drift= np.pi/4, 
	prob_change_dir= 0.2)

bHide = Behaviour( # Hide from spotted predator
	name= "Hide", 
	ideal_speed_f= 0,
	drift= 0, 
	prob_change_dir=0, 
	stealth_f=1.6) #revise

bChase = Behaviour(
	name="Chase", 
	drift= np.pi/16, 
	prob_change_dir= 0, 
	energy_loss_f=1.5,
	stealth_f=1, # Instant reveal to prey target elsewhere
	ideal_speed_f = 1,
	obs_time_f = 100) 

bChased = Behaviour(
	name="Chased", 
	ideal_speed_f=1,
	drift=0, 
	stealth_f=0.7,
	prob_change_dir=0,
	energy_loss_f=1.5)

bRetreat = Behaviour( # if predator in sight but far away and self not spotted
	name="Retreat", 
	ideal_speed_f=0.5,
	drift=0, 
	prob_change_dir=0, 
	stealth_f=1.1)

bGraze = Behaviour( # regenerate energy on veg for grazing animals
	name="Graze", 
	ideal_speed_f=0.05,
	drift=0, 
	prob_change_dir=0.5, 
	stealth_f=1,
	obs_time_f = 2)

bHunt = Behaviour( # Search for prey (no prey targets)
	name="Hunt", 
	ideal_speed_f=0.2,
	drift=np.pi/16, 
	prob_change_dir=0.01, 
	detection_f=1.5,
	obs_time_f=0.2)

bMigrate = Behaviour( # Migrate towards a specific location
	name="Migrate", 
	ideal_speed_f=0.2,
	drift=0, 
	prob_change_dir=0)

bStalk = Behaviour( # Stalk prey target 
	name="Stalk", 
	ideal_speed_f=0.1,
	drift=0, 
	prob_change_dir=0, 
	stealth_f=1.5,
	obs_time_f = 100)

bEat = Behaviour( # Eat food instances from environment, e.g. corpse
	name= "Eat", 
	ideal_speed_f= 0,
	drift= 0, 
	prob_change_dir=0)

bMate = Behaviour( # Search for breeding grounds or mates
	name= "Mate", 
	ideal_speed_f= 0.2,
	drift= np.pi/4, 
	prob_change_dir= 0.2)

bCourt = Behaviour( # Court females as potential fathers (M only!)
	name= "Court", 
	ideal_speed_f= 0.4,
	drift= 0, 
	prob_change_dir=0)

###################################################################################

class Environment: # Contains all information about environment, only one instance of this class

	def __init__(self, T, veg, vis, low_bound, high_bound, objects=[], breeding_grounds=[]):
		self.T = T
		self.veg = veg # consider making a function of x,y
		self.vis = vis # consider making a function of x,y
		self.low_bound = low_bound
		self.high_bound = high_bound
		self.objects = objects
		self.breeding_grounds = breeding_grounds

	def generate_bg(self, species_list, n_animals):
		'''Generate breeding grounds, only to be run once!'''
		# breeding grounds NEEDS WORK
		for s in range(len(species_list)):
			self.breeding_grounds.append([])
		for s in range(len(species_list)):
			n_bg = int(n_animals[s]/20)+1 # 20 animals per bg			
			for i in range(n_bg):
				self.breeding_grounds[s].append(Breeding_ground(
					name = species_list[s].name, 
					location = random_position(self, 4/5),
					radius = 10 + 10*rd.random()
					))

	def update(self):
		'''To be run every time loop TO DO'''
		for obj in self.objects:
			pass

###################################################################################

class Object: # 

	def __init__(self, name, location, food=None):
		self.name = name
		self.location = location
		self.age = 0 # years
		self.food = food # in kg

###################################################################################

class Breeding_ground: # Area for matured animals to meet

	def __init__(self, name, location, radius):
		self.name = name # species name
		self.location = location #(x,y)
		self.radius = radius # float
		self.males = [] # list of animal instances
		self.females = [] # list of animal instances

###################################################################################

class Time:

	def __init__(self, dt, s_per_day, day_per_year):
		self.dt = dt
		self.s_per_day = s_per_day
		self.day_per_year = day_per_year

###################################################################################
        
class Species:

	def __init__(self=None,
		name=None,  
		diet='H',  				
		stealth=None,  
		stealth_std=None, 
		detection=None, 
		detection_std=None,
		strength=None,  
		strength_std=None,  	
		size=None,  
		size_std=None,  	
		speed=None,  
		speed_std=None,
		acceleration=None,
		acceleration_std=None,  
		ideal_temp=None, 
		ideal_temp_std=None,
		mature_age=None,  
		mature_age_std=None,  
		life_expectancy=None,
		life_expectancy_std=None,
		energy_loss=None,  
		energy_loss_std=None, 
		obs_time=None, 
		obs_time_std=None, 
		field_view=None,  	
		field_view_std=None,
		breeding_gap=None,
		breeding_gap_std=None,
		color=None,  			
		shape='.',
		index=None,
		traits=[],
		number=0):

	# constant for all animals of species
		self.name = 	name  
		self.diet =  	diet
		self.color =  	color  
		self.shape =	shape

		# Average genetic values
		self.stealth =  stealth
		self.detection = detection 
		self.strength =  strength  
		self.size = size  
		self.speed = speed  
		self.acceleration =	acceleration
		self.ideal_temp = ideal_temp
		self.mature_age = mature_age  
		self.life_expectancy = life_expectancy
		self.energy_loss =  energy_loss
		self.obs_time = obs_time
		self.field_view = field_view 
		self.breeding_gap = breeding_gap 

		# Standard deviations
		self.stealth_std = 	stealth_std	
		self.detection_std = detection_std
		self.strength_std = strength_std  
		self.size_std =  size_std  
		self.acceleration_std =  acceleration_std 
		self.ideal_temp_std =	ideal_temp_std
		self.mature_age_std =  	mature_age_std 
		self.speed_std = speed_std
		self.life_expectancy_std =	life_expectancy_std
		self.energy_loss_std = 	energy_loss_std
		self.obs_time_std = obs_time_std 
		self.field_view_std =	field_view_std
		self.breeding_gap_std = breeding_gap_std

		# Misc.
		self.index = index # species index in zoo
		self.number = 1 # used for animal identity number
		self.traits = traits

		# Note, as of current species.mat data import, all of these quantities MUST be in
		# the argument, even if they are overwritten, e.g. number

# Global variable, must be exactly as written in species as it will be used in eval() functions
GENES = ["stealth", "detection", "strength", "size",
		"speed", "acceleration", "ideal_temp", "mature_age", "life_expectancy",
		"energy_loss", "obs_time", "field_view", "breeding_gap"]		
MISC = ["name", "diet", "color"] # Other species variables, does not have to be all of them

TRAITS = ["Bound", "Pounce"]

###################################################################################

def random_location(r_max, loc = (0,0), const_r=False):
	'''Returns a random location within distance r_max from loc'''
	x,y = loc
	if const_r:
		r = r_max
	else:
		r = (2*rd.random()-1) * r_max
	theta = (2*rd.random()-1) * np.pi
	x += r*np.cos(theta)
	y += r*np.sin(theta)
	return (x,y)

def random_position(env, border_factor=1):
	'''Returns a random location the map boundaries'''
	x = env.high_bound * (2*rd.random()-1) * border_factor
	y = env.high_bound * (2*rd.random()-1) * border_factor
	return (x,y)

def Generate_babies(mother, father, env, n=1):
	'''Puts n babies in BABIES list for addition to ZOO globally'''
	global BABIES
	if mother.species.name != father.species.name:
		raise NameError('Breeding of different species occuring')
	mother.breeding_ground.females.remove(mother)
	father.breeding_ground.males.remove(father)
	for animal in [mother, father]:
		animal.breeding_age += animal.breeding_gap
		animal.breeding_ground = None
		animal.mate = None
		animal.desired_location = random_location(300, animal.location) # TO DO
		animal.passive_response()
	#print "A", mother.species.name, "has been born"
	for i in range(n):
		BABIES.append(Animal(
			species = mother.species, 
			location=mother.location, 
			parents = [mother, father], 
			mutation_chance=0.1
			))

def print_times(total_time):
	print 'Action time:', np.around(100*t_action/total_time, 2), '%'
	print 'Of which time spent on:'
	print 'Prey search:', np.around(100*t_prey_search/t_action, 2), '%'
	print 'Pred search:', np.around(100*t_pred_search/t_action, 2), '%'
	print 'Moving:', np.around(100*t_move/t_action, 2), '%'
	print 'Behaviour move', np.around(100*t_behaviour_move/t_action, 2), '%'
	print 'Update state:', np.around(100*t_update_state/t_action, 2), '%'