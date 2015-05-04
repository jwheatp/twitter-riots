import os
import math 
import time
from random import randrange

def build_space(users,words) :
    nt = len(words)

    matrix = []
    
    i = 0
    for user in users :
	init = [0] * nt
        matrix.append(init)
        if math.fmod(i,1000) == 0 :
            tokens = user[1][1].keys()
	for t in tokens :
	        j = words.index(t)
	        matrix[i][j] = 1
	i += 1

    return matrix

def mode_s(values):
    return max(set(values), key=values.count)

def isPrime(n) :
    if n % 2 == 0 and n > 2: 
        return False
    return all(n % i for i in range(3, int(math.sqrt(n)) + 1, 2))

def getFirstPrime(n) :
    p = False
    k = n
    while not p :
	k += 1
	p = isPrime(k)
    return k

class Hash :
    "Hash function"
    def __init__(self,N) :
	self.a = randrange(1,N)
	self.b = randrange(1,N)
	self.p = getFirstPrime(N)
	self.N = N
    def value(self,x) :
	v = self.a * x + self.b
	v = math.fmod(v,self.p)
	v = math.fmod(v,self.N)
	return v

def mhsgn(m,k) :
    "Generate signatures"

    N = len(m)
    nt = len(m[0])
    hf = []
   
    for i in xrange(k) :
	hf.append(Hash(N))

#    sigm = np.full((N,k),-1,dtype=int)

    sigm = x = [[-1]*k for i in range(N)] 
   
    for j in range(nt) :
        if math.fmod(j,10000) == 0 :
	    print(j)
        for i in range(N) :
	    if m[i][j] == 1 :
                for o in xrange(k) :
                    h = hf[o].value(j)
		    if sigm[i][o] == -1 or h < sigm[i][o] :
                        sigm[i][o] = h

    return hf,sigm

def banding(sigm,c) :
    "Banding"
    
    bands = []
    htable = {}

    nrow = len(sigm)
    ncol = len(sigm[0])    
    
    for i in range(0,ncol,c) :
        bands.append({})

    values = []
    for i in range(nrow) :
        if math.fmod(i,10000) :
	    print(i)
        for j in range(0,ncol+1) :
	    if not j == 0 and math.fmod(j,c) == 0 :
		b = j/c - 1
	        h = hash(tuple(values))
	        bands[b][h] = bands[b].get(h,[]) + [i]
		values = []	
	    if j < ncol :
	        values.append(sigm[i][j])
    return bands

def prepareQuery(query,mode,n,hf,k,c) :
    "Prepare query"
    nt = int(100 * math.pow(2,n))

    sig = [-1]*nt
  
    for j in range(nt) :
        if query[j] == 1 :
            for o in range(k) :
                h = hf[o].value(j)
                if sig[o] == -1 or h < sig[o] :
                    sig[o] = h

    # print(sig)
    ncol = len(sig)
    code = []
    values = []
    for j in range(0,ncol+1) :
        if not j == 0 and math.fmod(j,c) == 0 :
            h = hash(tuple(values))
            code.append(h)
            values = []
        if j < ncol :
            values.append(sig[j])

    return code


def knna(q,db) :
    "kNN approximate"
    candidates = []
    for i in range(len(db)) :
	h = q[i]
	candidates += db[i].get(h,[])
   
    candidates = [x for x in candidates if x >= 1000]
    return candidates

def approximate(k,c,mode,n,m,queries) :
    print("signatures..")
    hf,sigm = mhsgn(m,k)
    print("bands..")
    bands = banding(sigm,c)
    cand = []
    nn = []
    code = []

    i = 0
    for query in queries :
        if math.fmod(i,10000) == 0 :
	    print("-- pr "+str(mode)+" ("+str(n)+") : "+str(i))
        code.append(prepareQuery(query,mode,n,hf,k,c))
	i += 1

    start = time.clock()
    i = 0
    for query in queries :
        cd = knna(code[i],bands)
	cand.append(cd)
	if len(cd) > 0 :
	    nn.append((i,mode_s(cd)))
	else :
	    nn.append((i,-1))
        i += 1
    time_elapsed = time.clock() - start

    print "time elapsed : ", time_elapsed
    fn = "log_ap_" + mode + "_" + str(n) + ".txt"
    f = open(fn,"w")
    f.write(str(time_elapsed))
    f.close()
    print "TE # ", mode,"-", str(n), "#", time_elapsed
    
    fn = "log_can_" + mode + "_" + str(n) + ".txt"
    f = open(fn,"w")
    f.write(str(nn))
    f.close()

