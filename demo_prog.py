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
        
def implies(x, y):
	try:
		return (x and y) or (not x and not y)
	except:
		raise incompatibleTypes

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
        return x <= y
    except:
        raise incompatibleTypes

def gt(x, y):
    try:
        return x >= y
    except:
        raise incompatibleTypes

def forall(expr, **vars):
    try:
        return_val = True
        i = 0
        while i < 4:
            vars['i'] = i
            i += 1
            return_val = return_val and expr.calc(**vars)
        return return_val
    except:
        return return_val

def exists(expr, **vars):
    try:
        return_val = False
        i = 0
        while i < 4:
            vars['i'] = i
            i += 1
            return_val = return_val or expr.calc(**vars)
        return return_val
    except:
        return return_val

params = [1, [1, 2, 3, 4]] #enter the program input parameters as a single list

def inputProgram(p = params):
    #enter the program or function here
    if p[0] in p[1]:
        exists = 1
    else:
        exists = -1
    return locals() #return all the local variables in current scope

def getrandom(var):
    if type(var) is int or type(var) is long or type(var) is float:
        return randint(-10, 10)
    elif type(var) is list:
        return [randint(-10, 10)\
                for i in xrange(len(var))]

# define the class comprising the program organism
class MyProg(ProgOrganism):
    """
    """
    arithfuncs = {
        '+' : add,
#       '-' : sub,
#       '*' : mul
#       '/' :div
        }
    boolfuncs = {
        '=' : equal,
#        '<=' : lt,
#        '>=' : gt
        }
    conjunctions = {
        '^' : _and,
#        '<->': implies,
#        '!' : _not,
        #'v' : _or,
        'Ei' : exists,
        'Vi' : forall
        }
    quantifiers = {
    }

    vars = []
    arrays = []
    testVals = []
    wrongTestVals = []
    consts = [1]
    numCases = 100

    for j in range(1,numCases):
        # first get a list of all the parameters and generate a random input for program
        testParams = []
        testCase = {}
        wrongTestCase = {}
        for i in params:
            testParams.append(getrandom(i))
        origParams = testParams[:]

        # insert all the local variables encountered while running the program in testCase
        testCase = inputProgram(testParams)
        del testCase['p']
        key = choice(testCase.keys())
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

        testVals.append(testCase)

        #create a wrong testcase by mutating the original testcase
        wrongTestCase = testCase.copy()
        wrongTestCase[key] = getrandom(wrongTestCase[key])
        wrongTestVals.append(wrongTestCase)

    #now take a testcase and insert the values in vars and arrays
    for key, val in testCase.iteritems():
        if type(val) is int or type(val) is long or type(val) is float:
            vars.append(key)
        if type(val) is list:
            arrays.append(key)
    print testCase
    print wrongTestCase
    print vars
    print arrays

    mutProb = 0.4

    def testFunc(self, **vars):
        """
        Just wanting to model x^2 + y
        """
        return vars['c'] ** 2 + vars['b']

    def fitness(self):
        # choose 1000 random values
        matches = 0
        for correct, incorrect in zip(self.testVals, self.wrongTestVals):
            try:
                if self.calc(**correct) == 1 and self.calc(**incorrect) == 0:
                    matches += 2
                elif self.calc(**correct) == 1:
                    matches += 1
            except:
                return 200
        return (200 - matches)

    # maximum tree depth when generating randomly
    initDepth = 4

# now create the population class
class ProgPop(Population):

    species = MyProg
    initPopulation = 100

    # cull to this many children after each generation
    childCull = 200

    # number of children to create after each generation
    childCount = 200

    incest = 50

    numNewOrganisms = 50

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
        #if b.fitness() <= 0:
            #print "a perfect invariant found"
            #b.dump()
        #if pop.fitness() <= 0:
            #print "the whole population consists of perfect invariants"
            #for organism in pop.organisms:
                #organism.dump()
            #break
        i += 1
        ngens += 1

        #if ngens < 15:
        pop.gen()
        #else:
            #for organism in pop.organisms:
                #organism.dump()
                #print organism.fitness()
            #break
            #print "failed after 100 generations, restarting"
            #pop = ProgPop()
            #ngens = 0

if __name__ == '__main__':
    main()
    pass

