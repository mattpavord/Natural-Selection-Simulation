# coding=utf-8
from __future__ import division
from mechanics import *
import matplotlib
matplotlib.use("TkAgg")
from matplotlib import pyplot as plt
import plot
import data
from tkinter import ttk
import Tkinter as tk
from tkColorChooser import askcolor
from tkinter import filedialog as fd

################################ CONSTANTS ################################

N = 401
dt = 1 # s
map_size = 2000
n_foxes = 20
n_rabbits = 500

pause_const = 0.0001

VIEW = True
KILL = True # kills the program

################################ Initialise ################################

# Global variables
FILENAME = "Species.mat"
SPECIES_LIST = data.read_species_data(FILENAME)
N_ANIMALS = np.zeros(len(SPECIES_LIST), dtype=int) # more appropriate long term
N_ANIMALS = np.array((n_rabbits, n_foxes), dtype=int) # default values (for now)

# to be redefined in itialise function
ZOO = None
ENV = None
N_ANIMAL_TIME = None
AVG_GENE_TIME = None

TIME_P = Time(dt=dt,
	s_per_day=200,
	day_per_year=10) 
Max_time = 3000 # days

################################ Tkinter Function ################################

def execute(commands):
	'''Execute list of strings as python code'''
	for command in commands:
		exec(command)

def kill_command():
	'''Function to kill simulation for kill button'''
	global KILL
	KILL = True

def get_color():
	color = askcolor()[0] # Tkinter function
	return (color[0]/256, color[1]/256, color[2]/256)

def open_species_data():
	global SPECIES_LIST, FILENAME
	filename = fd.askopenfilename()
	if filename[-4:] == '.mat':
		try:
			SPECIES_LIST = data.read_species_data(filename)
			FILENAME = filename
		except:
			print "Cannot open this file"
	else:
		print "Wrong file format"

def saveas_species_data():
	global FILENAME
	FILENAME = fd.asksaveasfilename()
	save_species_data()

def save_species_data():
	data.write_species_data(SPECIES_LIST, FILENAME)

def menu(root):
	menubar = tk.Menu(root)
	filemenu = tk.Menu(menubar, tearoff=0)
	filemenu.add_command(label="Open", command=open_species_data)
	filemenu.add_command(label="Save", command=save_species_data)
	filemenu.add_command(label="Save as", command=saveas_species_data)
	menubar.add_cascade(label="File", menu=filemenu)
	root.config(menu=menubar)

################################################################

def plot_menu():
	'''Menu to plot data from simulations'''

	def plot_genes():

		def cancel():
			root.destroy()

		def plot():
			try:
				plt.close()
			except:
				pass
			plt.ioff()
			days_passed = len(AVG_GENE_TIME[0,0,:])
			g_idx = gene_var.get()
			for s in range(len(SPECIES_LIST)):
				if species_checkbox_vars[s].get() == 1:
					plt.plot(range(days_passed), AVG_GENE_TIME[g_idx, s],
						label = SPECIES_LIST[s].name, color=SPECIES_LIST[s].color)
			plt.legend(frameon=False)
			plt.xlabel('Days passed')
			plt.ylabel('Average ' + data.neaten_string(GENES[g_idx]))
			plt.show()

		root = tk.Tk()
		root.title("Plot genes")
		root.geometry('%dx%d+%d+%d' % (400, 600, 950, 150))
		topFrame = tk.Frame(root)
		topFrame.pack(side = tk.TOP)
		bottomFrame = tk.Frame(root)
		bottomFrame.pack(side = tk.BOTTOM)

		# Radiobutton for which gene to plot
		tk.Label(topFrame, text="Gene").grid(row=1, column=1)
		gene_var = tk.IntVar(topFrame)
		for g in range(len(GENES)):	
			tk.Radiobutton(topFrame, text=data.neaten_string(GENES[g]), variable=gene_var, value=g).grid(row=2+g, column=1)
		gene_var.set(GENES[0])

		# Checkbox for which species to plot
		tk.Label(topFrame, text="Species").grid(row=1, column=3)
		species_checkbox_vars = []
		s=-1
		for species in SPECIES_LIST:
			s+=1
			species_checkbox_vars.append(tk.IntVar(topFrame))
			checkbutton = tk.Checkbutton(topFrame, text = species.name, 
				variable = species_checkbox_vars[s], anchor =tk.W, onvalue = 1, offvalue = 0, height=1, width = 5)
			checkbutton.grid(row=2+s, column=3)
			species_checkbox_vars[-1].set(1)

		tk.Button(bottomFrame, text='Cancel', command=cancel).pack(side=tk.LEFT)
		tk.Button(bottomFrame, text='Plot', command=plot).pack(side=tk.RIGHT)

		root.mainloop()

	#####################################################################

	def plot_traits():

		def cancel():
			root.destroy()

		def plot():
			try:
				plt.close()
			except:
				pass
			plt.ioff()
			days_passed = len(TRAIT_PROP_TIME[0,0,:])
			tr_idx = trait_var.get()
			for s in range(len(SPECIES_LIST)):
				if species_checkbox_vars[s].get() == 1:
					plt.plot(range(days_passed), TRAIT_PROP_TIME[tr_idx, s],
						label = SPECIES_LIST[s].name, color=SPECIES_LIST[s].color)
			plt.legend(frameon=False)
			plt.xlabel('Days passed')
			plt.ylabel('Proportion with ' + data.neaten_string(TRAITS[tr_idx] + ' / %'))
			plt.show()

		root = tk.Tk()
		root.title("Plot traits")
		root.geometry('%dx%d+%d+%d' % (400, 600, 950, 150))
		topFrame = tk.Frame(root)
		topFrame.pack(side = tk.TOP)
		bottomFrame = tk.Frame(root)
		bottomFrame.pack(side = tk.BOTTOM)

		# Radiobutton for which gene to plot
		tk.Label(topFrame, text="Trait").grid(row=1, column=1)
		trait_var = tk.IntVar(topFrame)
		for tr in range(len(TRAITS)):	
			tk.Radiobutton(topFrame, text=data.neaten_string(TRAITS[tr]), variable=trait_var, value=tr).grid(row=2+tr, column=1)
		trait_var.set(TRAITS[0])

		# Checkbox for which species to plot
		tk.Label(topFrame, text="Species").grid(row=1, column=3)
		species_checkbox_vars = []
		s=-1
		for species in SPECIES_LIST:
			s+=1
			species_checkbox_vars.append(tk.IntVar(topFrame))
			checkbutton = tk.Checkbutton(topFrame, text = species.name, 
				variable = species_checkbox_vars[s], anchor =tk.W, onvalue = 1, offvalue = 0, height=1, width = 5)
			checkbutton.grid(row=2+s, column=3)
			species_checkbox_vars[-1].set(1)

		tk.Button(bottomFrame, text='Cancel', command=cancel).pack(side=tk.LEFT)
		tk.Button(bottomFrame, text='Plot', command=plot).pack(side=tk.RIGHT)

		root.mainloop()

	#####################################################################

	def plot_numbers():
		plot.plot_populations(N_ANIMAL_TIME, SPECIES_LIST)
		plt.show()

	def ok1():
		root.destroy()

	root = tk.Tk()
	root.title("Plot")
	root.geometry('%dx%d+%d+%d' % (400, 600, 950, 150))

	topFrame = tk.Frame(root)
	topFrame.pack(side = tk.TOP)
	bottomFrame = tk.Frame(root)
	bottomFrame.pack(side = tk.BOTTOM)

	tk.Button(topFrame, text='Plot numbers', command=plot_numbers).grid(row=0, column=2)
	tk.Button(topFrame, text='Plot traits', command=plot_traits).grid(row=1, column=0)
	tk.Button(topFrame, text='Plot genes', command=plot_genes).grid(row=1, column=3)

	tk.Button(bottomFrame, text='Ok', command=ok1).grid(row=0, column=0)

############################## WILDLIFE ##################################

def wildlife_menu():
	'''Menu to view and edit species properties'''

	####### Edit Species #######

	def edit_menu(species):
		'''Edit or add a species menu'''

		def change_color():
			global species_color
			species_color = get_color()

		def ok2():
			'''ok to edit menu'''
			commands = ["global SPECIES_LIST"]
			command_start = "SPECIES_LIST[" + str(species.index) + "]."

			# profile
			species.diet = diet.get()
			species.name = name_entry.get()
			species.color = species_color

			# genes
			for g in range(len(GENES)):
				command = (command_start + GENES[g] + ' = ' + str(gene_entries[g].get()))
				commands.append(command)
				command = (command_start + GENES[g] + '_std' + ' = ' + str(std_entries[g].get()))
				commands.append(command)
			execute(commands) # cannot use exec in local local code

			# traits
			species.traits = []
			t = -1
			for trait, prob in species_traits:
				t+=1
				prob = float(trait_prob_entry[t].get())
				species.traits.append((trait, prob))

			global SPECIES_LIST
			SPECIES_LIST = data.organise_species_list(SPECIES_LIST)
			update_topframe() # updates lower level (wildlife menu) root
			root.destroy()


		root = tk.Tk()
		if species.name:
			root.title("Edit " + species.name)
		else:
			root.title("Add Species")
		root.geometry('%dx%d+%d+%d' % (400, 600, 950, 150))

		topFrame = tk.Frame(root)
		topFrame.pack(side = tk.TOP)
		bottomFrame = tk.Frame(root)
		bottomFrame.pack(side = tk.BOTTOM)

		# Notebook
		notebook = ttk.Notebook(topFrame, width = 300, height=500)
		profile_page = tk.Frame(notebook)
		genetic_page = tk.Frame(notebook)
		trait_page = tk.Frame(notebook)
		notebook.add(profile_page, text="Profile")
		notebook.add(genetic_page, text="Genetics")
		notebook.add(trait_page, text="Traits")
		notebook.pack()

		ok_button = tk.Button(root, text="Ok", command = ok2)
		ok_button.pack(side = tk.BOTTOM)

		# Genetics #

		tk.Label(genetic_page, text="Mean").grid(row=0, column=1)
		tk.Label(genetic_page, text="Standard Dev.").grid(row=0, column=2)

		# Gne Entries
		gene_entries = [] # list of tk entries mean values
		std_entries = [] # list of tk entries std values
		g = -1
		for gene in GENES: # mechanics global variable containing list of gene strings
			g+=1 # Genetics page
			tk.Label(genetic_page, text=data.neaten_string(gene)).grid(row=g+1, column=0)
			gene_entries.append(tk.Entry(genetic_page, width=4))
			gene_entries[g].grid(row=g+1, column=1)
			gene_value = eval("species." + gene)
			std_entries.append(tk.Entry(genetic_page, width=4))
			std_entries[g].grid(row=g+1, column=2)
			std_value = eval("species." + gene + "_std")
			if gene_value!=None:
				gene_entries[g].insert(0, str(gene_value)) 
			if std_value!=None:
				std_entries[g].insert(0, str(std_value))

		# Profile #

		# Name
		tk.Label(profile_page, text="Name").grid(row=1, column=0)
		name_entry = tk.Entry(profile_page, width=10)
		if species.name:
			name_entry.insert(5, species.name)
		name_entry.grid(row=2, column=0)

		# Diet
		tk.Label(profile_page, text="Diet").grid(row=1, column=1)
		diet = tk.StringVar(profile_page)	
		diet.set(species.diet) # set the default option
		diet_listbox = tk.OptionMenu(profile_page, diet, *data.DIET_ORDER)
		diet_listbox.grid(row = 2, column = 1)

		# Colour
		global species_color
		species_color = species.color
		tk.Button(profile_page, text='Colour', command=change_color).grid(row=3, column=0)

		# Traits #

		def update_traitpage():

			def add_trait():
				trait = trait_var.get()
				if trait=='None':
					return None
				for t in range(len(species_traits)): # if trait not in species_traits
					if species_traits[t][0] == trait:
						return None # species already has trait
				species_traits.append((trait,0)) # will only reach here if species does not have trait
				update_traitpage()

			for widget in trait_page.winfo_children():
				widget.destroy() # prevents overlapping

			available_traits = TRAITS[:] # indexing clones list, removes attachment between 2
			for trait, prob in species_traits:
				available_traits.remove(trait)
			if len(available_traits)==0:
				available_traits.append('None')

			# add traits
			trait_var = tk.StringVar(trait_page)
			trait_listbox = tk.OptionMenu(trait_page, trait_var, *available_traits) 
			trait_listbox.grid(row = 0, column = 1)
			trait_listbox.config(width=10)
			add_trait_button = tk.Button(trait_page, text="Add", command=add_trait)
			add_trait_button.grid(row=0, column=0)

			# Existing traits
			tk.Label(trait_page, text="Trait").grid(row=1, column=1)
			tk.Label(trait_page, text="Fraction").grid(row=1, column=2)

			for entry in trait_prob_entry:
				trait_prob_entry.pop(0) # empty without reassignment
			t=-1
			for trait, prob in species_traits:
				t+=1
				tk.Label(trait_page, text=trait).grid(row=t+2, column=1)
				entry = tk.Entry(trait_page, width=4)
				entry.insert(0, str(prob))
				trait_prob_entry.append(entry)
				trait_prob_entry[t].grid(row=t+2, column=2)

		species_traits = species.traits[:] # copy to be loaded into data in ok2 function (will only contain 0 for prob)
		trait_prob_entry = [] # to be filled with tkinter entries
		update_traitpage()

		root.mainloop()

	####### Wildlife main #######

	def add():
		'''Add a species'''
		global SPECIES_LIST, N_ANIMALS
		N_ANIMALS = np.zeros(len(SPECIES_LIST)+1, dtype=int)
		idx = len(SPECIES_LIST)
		SPECIES_LIST.append(Species(index=idx))
		edit_menu(SPECIES_LIST[idx])

	def ok1():
		'''Ok to species menu'''
		global N_ANIMALS
		N_ANIMALS = get_n_animals(species_entry)
		root.destroy()

	def get_n_animals(species_entry):
		n = len(SPECIES_LIST)
		n_animals = np.zeros(n, dtype=int)
		for i in range(n):
			n_animals[i] = int(species_entry[i].get())
		return n_animals

	def update_topframe():
		'''Updates TopFrame only, destroys everything in it first!'''
		for widget in topFrame.winfo_children():
			widget.destroy() # prevents overlapping
		tk.Label(topFrame, text="Species").grid(row=0, column=0)
		tk.Label(topFrame, text="Diet").grid(row=0, column=1)
		tk.Label(topFrame, text="Number").grid(row=0, column=2)
		s = -1 # species index
		global species_button, species_entry
		species_button = []
		species_entry = [] # species entry is a list of tk.entry (species numbers)
		for species in SPECIES_LIST:
			s+=1
			tk.Label(topFrame, text=species.name).grid(row=s+1, column=0)
			tk.Label(topFrame, text=species.diet).grid(row=s+1, column=1)
			species_entry.append(tk.Entry(topFrame, width=4)) 
			species_entry[s].grid(row=s+1, column=2) 
			species_entry[s].insert(0, str(N_ANIMALS[s]))
			tk.Button(topFrame, text="Edit", command = lambda species = species: edit_menu(species)).grid(row=s+1, column=3)


	root = tk.Tk()
	root.title("Wildlife")
	root.geometry('%dx%d+%d+%d' % (400, 400, 950, 150))
	topFrame = tk.Frame(root)
	topFrame.pack(side = tk.TOP)
	bottomFrame = tk.Frame(root)
	bottomFrame.pack(side = tk.BOTTOM)

	ok_button = tk.Button(bottomFrame, text="Ok", command = ok1)
	ok_button.pack(side = tk.RIGHT)

	add_button = tk.Button(bottomFrame, text='Add', command = add)
	add_button.pack(side = tk.LEFT)

	update_topframe()
	root.mainloop()

################################ TIME LOOP ################################

def initialise():
	'''Initialise data and plot'''
	global KILL
	KILL = False
	for i in range(len(CHASERS)): # For second or third run
		CHASERS.pop(0) # important not to reassign, needs to remain a mechanics variable
	for i in range(len(BABIES)):
		BABIES.pop(0)

	global ZOO, ENV
	ENV = Environment(
		T=25, 
		vis=1, 
		veg=0.01, 
		low_bound = -map_size/2, 
		high_bound = map_size/2)
	ENV.generate_bg(SPECIES_LIST, N_ANIMALS)
	ZOO = data.generate_zoo(SPECIES_LIST, N_ANIMALS, ENV)

	# plot data
	global N_ANIMAL_TIME, AVG_GENE_TIME, TRAIT_PROP_TIME
	N_ANIMAL_TIME = np.zeros((len(ZOO), Max_time), dtype=int) # variable of n_animals (for plotting)
	AVG_GENE_TIME = np.zeros((len(GENES), len(ZOO), Max_time), dtype=float) # average gene for all species
	TRAIT_PROP_TIME = np.zeros((len(TRAITS), len(ZOO), Max_time), dtype=float) # average gene for all species

	global SPECIES_TRAIT_INDEX # list (len == len(ZOO)) of lists containing indexes of traits
	SPECIES_TRAIT_INDEX = []
	s=-1
	for species in SPECIES_LIST:
		s+=1
		s_traits = []
		for trait, prob in species.traits:
			s_traits.append(trait)
		SPECIES_TRAIT_INDEX.append([])
		tr=-1
		for trait in TRAITS:
			tr += 1
			if trait in s_traits:
				SPECIES_TRAIT_INDEX[s].append(tr)

	if VIEW:
		plot.plot(ZOO, ENV)


def main():
	global N_ANIMAL_TIME, AVG_GENE_TIME, TRAIT_PROP_TIME

	tik = time.time()
	if KILL:
		initialise()
	days_passed = 0

	t=0
	while t < Max_time*TIME_P.s_per_day: # time loop
		clock0 = time.time()
		t+=dt

		# Main body
		for family in ZOO:
			for animal in family:
				animal.action(TIME_P, ENV, ZOO)

		# Resolving chases, (must be done globally)
		remove = []
		for predator in CHASERS:
			if (len(predator.prey_target)>0 and
				predator.prey_target[0].dead == False and
				predator.behaviour.name == "Chase"): # Chase is still on
				prey = predator.prey_target[0]
				if (predator.melee(predator.prey_target[0])): # may need to correct for overtaking
					if predator.win_battle(predator.prey_target[0]):
						print prey.name, "has been killed by", predator.name
						prey.dead = True
						predator.prey_target.remove(prey)
						predator.food = Object("Corpse", prey.location, food = prey.size*4/5)
						ENV.objects.append(predator.food)
						predator.behaviour = bEat
						remove.append(predator)				

			else:
				remove.append(predator)
		for animal in remove:
			CHASERS.remove(animal)

		# if t % 10 == 0:
		# 	print ZOO[1][0].behaviour.name, int(ZOO[1][0].energy) # test code
		# 	print ' '

		# Clean the zoo of dead
		for family in ZOO:
			remove = []
			for animal in family:
				if animal.dead:
					remove.append(animal)
			for animal in remove:
				family.remove(animal)

		# Births
		remove = []
		for animal in BABIES:
			ZOO[animal.species.index].append(animal)
			remove.append(animal)
		for animal in remove:
			BABIES.remove(animal)

		# Plot data at end of day
		if int(t)%int(TIME_P.s_per_day)==0:
			print "End day"
			s = -1
			for family in ZOO:
				s+=1
				N_ANIMAL_TIME[s, days_passed] = len(family)
				
				g=-1
				for gene in GENES:
					g+=1
					total = 0
					for animal in family:
						total += eval("animal." + GENES[g])
					AVG_GENE_TIME[g, s, days_passed] = total/len(family)

				for tr in SPECIES_TRAIT_INDEX[s]:
					trait = TRAITS[tr]
					total = 0
					for animal in family:
						if trait in animal.traits:
							total+=1
					TRAIT_PROP_TIME[tr, s, days_passed] = 100*total/len(family)

			days_passed += 1

		ENV.update()

		delay = time.time() - clock0
		if delay < pause_const:
			pause = pause_const - delay
		else:
			pause = 0
		time.sleep(pause)

		if VIEW:
			plot.update(ZOO, ENV, pause=0.0001)

		if KILL:
			plt.close()

			N_ANIMAL_TIME = N_ANIMAL_TIME[:,0:days_passed]
			AVG_GENE_TIME = AVG_GENE_TIME[:,:,0:days_passed]
			TRAIT_PROP_TIME = TRAIT_PROP_TIME[:,:,0:days_passed]

			print '\n***********************\n'
			total_time = time.time()-tik
			print np.around(N/total_time, 2), 'FPS'
			print np.around(total_time, 2), 's\n'
			print_times(total_time) # from mechanics.py
			print ''
			plot.print_times(total_time)
			print ''

			return None

# main(N_ANIMALS)

################# Tkinter ######################

root = tk.Tk()
root.title("Menu")
root.geometry('%dx%d+%d+%d' % (400, 400, 950, 150))
topFrame = tk.Frame(root)
topFrame.pack(side = tk.TOP)
bottomFrame = tk.Frame(root)
bottomFrame.pack(side = tk.BOTTOM)

start_button = tk.Button(bottomFrame, text="Start", command = main)
kill_button = tk.Button(bottomFrame, text="Kill", command = kill_command)
wildlife_button = tk.Button(bottomFrame, text="Wildlife", command = wildlife_menu)
plot_button = tk.Button(bottomFrame, text="Plot", command = plot_menu)
menu(root)

start_button.grid(row = 0, column = 0)
kill_button.grid(row = 0, column = 1)
wildlife_button.grid(row=0, column=3)
plot_button.grid(row=0, column=2)

root.mainloop()