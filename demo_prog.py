#!/usr/bin/python

# Copyright (c) 2012 Anirudh Kumar
#
# Permission is hereby granted, free of charge, to any person
# obtaining a copy of this software and associated documentation
# files (the "Software"), to deal in the Software without
# restriction, including without limitation the rights to use,
# copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the
# Software is furnished to do so, subject to the following
# conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES
# OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
# HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
# WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
# OTHER DEALINGS IN THE SOFTWARE.

"""
Demo of genetic programming

This gp setup seeks to breed an organism which
is an invariant of the program specified in the function inputProgram

Number of invariants is of order 10^3
"""

import math
from random import random, randint, uniform, choice
from pygene.prog import ProgOrganism
from pygene.population import Population

# a tiny batch of functions
def add(x,y):
	#print "add: x=%s y=%s" % (repr(x), repr(y))
	try:
		return x+y
	except:
		#raise
		return x

def sub(x,y):
	#print "sub: x=%s y=%s" % (repr(x), repr(y))
	try:
		return x-y
	except:
		#raise
		return x

def mul(x,y):
	#print "mul: x=%s y=%s" % (repr(x), repr(y))
	try:
		return x*y
	except:
		#raise
		return x

def div(x,y):
	#print "div: x=%s y=%s" % (repr(x), repr(y))
	try:
		return x / y
	except:
		#raise
		return x

def _and(x,y):
	try:
		return x and y
	except:
		raise incompatibleTypes

def _or(x,y):
	try:
		return x or y
	except:
		raise incompatibleTypes
		
def _not(x):
	try:
		return not x
	except:
		raise incompatibleTypes
		
def equal(x, y):
	try:
		return x == y
	except:
		raise incompatibleTypes
		
def lt(x, y):
	try:
		return x < y
	except:
		raise incompatibleTypes

def gt(x, y):
	try:
		return x > y
	except:
		raise incompatibleTypes

def sqrt(x):
	#print "sqrt: x=%s" % repr(x)
	try:
		return math.sqrt(x)
	except:
		#raise
		return x

def pow(x,y):
	#print "pow: x=%s y=%s" % (repr(x), repr(y))
	try:
		return x ** y
	except:
		#raise
		return x

def log(x):
	#print "log: x=%s" % repr(x)
	try:
		return math.log(float(x))
	except:
		#raise
		return x

def sin(x):
	#print "sin: x=%s" % repr(x)
	try:
		return math.sin(float(x))
	except:
		#raise
		return x
	
def cos(x):
	#print "cos: x=%s" % repr(x)
	try:
		return math.cos(float(x))
	except:
		#raise
		return x
		
def tan(x):
	#print "tan: x=%s" % repr(x)
	try:
		return math.tan(float(x))
	except:
		#raise
		return x

params = [1, 2, 3, 4] #enter the program input parameters as a single list

def inputProgram(p = params):
	#enter the program or function here
	p.sort()
	return locals() #return all the local variables in current scope
	
def getrandom(vartype):
	if vartype is int or vartype is long or vartype is float:
		return randint(-10, 10)
	elif vartype is list:
		return [randint(-10, 10)\
				for i in xrange(randint(1,10))]
		
# define the class comprising the program organism
class MyProg(ProgOrganism):
	"""
	"""
	arithfuncs = {
		'+' : add,
#		'-' : sub,
#		'*' : mul
#		'/' :div,
#		'**': pow,
#		'sqrt': sqrt,
#		'log' : log,
#		'sin' : sin,
#		'cos' : cos,
#		'tan' : tan
		}
	boolfuncs = {
		'=' : equal,
		'<' : lt,
		'>' : gt
#		'!' : _not
		}
	conjunctions = {
		'^' : _and,
#		'v' : _or
		}
	

	vars = []
	testVals = []
	wrongTestVals = []
	consts = [1.0, 2.0, 10.0]
	numCases = 500
	
	for j in range(1,numCases):
		# first get a list of all the parameters and generate a random input for program
		testParams = []
		testCase = {}
		wrongTestCase = {}
		for i in params:
			testParams.append(getrandom(type(i)))
		origParams = testParams[:]
		
		# insert all the local variables encountered while running the program in testCase
		testCase = inputProgram(testParams)

		#now check which input parameters have changed as a result running the program
		count = 0
		for i in testParams:
			if origParams[count] != i:
				#print 'parameter changed'
				testCase['p' + str(count) + '.orig'] = origParams[count]
				testCase['p' + str(count) + '.new'] = i
			else:
				testCase['p' + str(count)] = i
			count = count + 1
		del testCase['p']
		testVals.append(testCase)
		
		#create a wrong testcase by mutating the original testcase
		key = choice(testCase.keys())
		wrongTestCase = testCase.copy()
		wrongTestCase[key] = getrandom(type(key))
		wrongTestVals.append(wrongTestCase)

	#now take a testcase and insert the values in vars
	vars = testCase.keys()
	print testCase
	print wrongTestCase
	print vars
	
	mutProb = 0.4

	def testFunc(self, **vars):
		"""
		Just wanting to model x^2 + y
		"""
		return vars['c'] ** 2 + vars['b']

	def fitness(self):
		# choose 1000 random values
		matches = 0
		testcases = 0
		for vars in self.testVals:
			testcases = testcases + 1
			if self.calc(**vars) == 1:
				matches += 1
		for vars in self.wrongTestVals:
			testcases = testcases + 1
			if self.calc(**vars) == 0:
				matches += 1
		return testcases - matches
		
	# maximum tree depth when generating randomly
	initDepth = 6

# now create the population class
class ProgPop(Population):
	
	species = MyProg
	initPopulation = 100
	
	# cull to this many children after each generation
	childCull = 200

	# number of children to create after each generation
	childCount = 200

	mutants = 0.3


pop = ProgPop()

def main(nfittest=10, nkids=100):
	
	global pop

	ngens = 0
	i = 0
	while True:
		b = pop.best()
		b.dump()
		#for organism in pop.organisms:
			#organism.dump()
				
		print "generation %s: %s best=%s average=%s)" % (
			i, str(b), b.fitness(), pop.fitness())
		if b.fitness() <= 0:
			print "a perfect invariant found"
			b.dump()
		if pop.fitness() == 0:
			print "the whole population consists of perfect invariants"
			for organism in pop.organisms:
				organism.dump()
			break
		i += 1
		ngens += 1
		
		#if ngens < 100:
		pop.gen()
		#else:
			#print "failed after 100 generations, restarting"
			#pop = ProgPop()
			#ngens = 0

if __name__ == '__main__':
	main()
	pass
