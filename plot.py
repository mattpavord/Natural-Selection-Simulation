# coding=utf-8
from __future__ import division
import matplotlib.pyplot as plt
import numpy as np
import time
import data

loop = 0
setting = "Back"
t_animate = 0
t_load_data = 0

def plot(zoo, env):
	global x, y, fig, ax, sc
	plt.ion()
	fig, ax = plt.subplots(figsize = (7,7))
	ax.set_facecolor((178./256.,255./256.,102./256.)) # lush green grass

	# Breeding grounds
	x,y,s = [], [], []
	for bg_list in env.breeding_grounds:
		for bg in bg_list:
			x.append(bg.location[0])
			y.append(bg.location[1])
			s.append(bg.radius**2)
	ax.scatter(x, y, s, color=(140./256.,255./256.,90./256.))

	# animals
	x, y = [],[]
	sc = []
	for family in zoo:
		if len(family) >0:
			sc.append(ax.scatter(x,y, 
				color=family[0].color,
				marker=family[0].shape))
		else:
			sc.append(ax.scatter(x,y)) 
	plt.xlim(env.low_bound, env.high_bound)
	plt.ylim(env.low_bound, env.high_bound)
	plt.draw()

def update(zoo, env, pause=0.0001):
	i = -1
	global loop
	global fig
	global t_load_data, t_animate
	loop += 1
	tik = time.time()
	for family in zoo:
		x,y,s = [], [], []
		i+=1
		for animal in family:
			x.append(animal.location[0])
			y.append(animal.location[1])
			s.append(animal.size)
		sc[i].set_offsets(np.c_[x,y])
		sc[i].set_sizes(s)
	t_load_data += time.time() - tik
	tik = time.time()
	fig.canvas.draw_idle()
	if setting == "Front": # less buggy but cannot be kept in background
		plt.pause(pause)
	else:
		if loop==1:
			plt.pause(pause)
		else:
			fig.canvas.flush_events()
			time.sleep(pause)
	t_animate += time.time() - tik

# def close():
# 	global fig
# 	plt.show(fig)

def plot_populations(n_species, species_list):
	plt.ioff()
	global fig, ax
	days_passed = len(n_species[0])
	fig, ax = plt.subplots(figsize = (7,7))
	for i in range(len(n_species)):
		ax.plot(range(days_passed), n_species[i], label=species_list[i].name)
	ax.legend()

def print_times(total_time):
	t_plot = t_load_data + t_animate
	print 'Plot time:', np.around(100*t_plot/total_time, 2), '%'
	print 'Of which time spent on:'
	print 'Load Data:', np.around(100*t_load_data/t_plot, 2), '%'
	print 'Animate:', np.around(100*t_animate/t_plot, 2), '%'