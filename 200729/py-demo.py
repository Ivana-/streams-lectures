"""Py demo."""

from core import TR, evalTR, CS, evalCS
from timeit import default_timer as timer

######################################################################################
# trampoline
######################################################################################

# sum from 1 to n

def f_trec(n, a): return a if (0 == n) else f_trec(n-1, n+a)

def f_TR(n, a): return a if (0 == n) else TR(lambda: f_TR(n-1, n+a))

# print("f_trec: ", evalTR(f_trec(10, 0))) # 10, 10000
# print("f_TR:   ", evalTR(f_TR(10000, 0))) # 10, 10000

# even / odd

def isEven(n): return True if (n == 0) else TR(lambda: isOdd(n-1))
def isOdd(n): return False if (n == 0) else TR(lambda: isEven(n-1))

# print("isEven: ", evalTR(isEven(10000)))
# print("isOdd:  ", evalTR(isOdd(10000)))

######################################################################################
# custom stack
######################################################################################

# fibonacci

def fib(n): return n if (n < 2) else CS(fold = lambda x, y: x+y,
                                        args = [lambda: fib(n-1), lambda: fib(n-2)],
                                        memo = n)
# print("fib:    ", evalCS(fib(50)))

# even / odd

def isEven(n): return True if (n == 0) else CS(lambda: isOdd(n-1))
def isOdd(n): return False if (n == 0) else CS(lambda: isEven(n-1))

# print("isEven: ", evalCS(isEven(10000)))
# print("isOdd:  ", evalCS(isOdd(10000)))

######################################################################################
# coin change
######################################################################################

def ccN(s, coins):
  def go(s, i):
    if (s == 0): return 1
    elif (s < 0 or i >= len(coins)): return 0
    else: return go(s, i+1) + go(s-coins[i], i)
  return go(s, 0)

def ccCS(s, coins):
  def go(s, i):
    if (s == 0): return 1
    elif (s < 0 or i >= len(coins)): return 0
    else:
      return CS(fold = lambda x, y: x+y,
                args = [lambda: go(s, i+1), lambda: go(s-coins[i], i)])
  return evalCS(go(s, 0))

def ccC(s, coins):
  def go(s, i, cont):
    if (s == 0): return cont(1)
    elif (s < 0 or i >= len(coins)): return cont(0)
    else:
      return TR(lambda: go(s, i+1, lambda x: TR(lambda: go(s-coins[i], i, lambda y: TR(lambda: cont(x+y))))))
  return evalTR(go(s, 0, lambda x: x))

# without memoization

def time(f, *args):
  start = timer()
  r = f(*args)
  return (r, timer() - start)

n = 200 # 200
coins = [1, 5, 10, 25, 50]

rN,  tN  = time(ccN,  n, coins)
rCS, tCS = time(ccCS, n, coins)
rC,  tC  = time(ccC,  n, coins)

# print("N/CS/C: ", (rN, rCS, rC))
# print("tCS/tN: ", "{:.2f}".format(tCS / tN))
# print("tC /tN: ", "{:.2f}".format(tC  / tN))

# with memoization

def ccCS(s, coins):
  def go(s, i):
    if (s == 0): return 1
    elif (s < 0 or i >= len(coins)): return 0
    else:
      return CS(fold = lambda x, y: x+y,
                args = [lambda: go(s, i+1), lambda: go(s-coins[i], i)],
                memo = (s, i))
  return evalCS(go(s, 0))


def ccC(s, coins):
  memo = {}

  def memoize(k, x):
    memo[k] = x
    return x

  def go(s, i, cont):
    k = (s, i)

    if (s == 0): return cont(1)
    elif (s < 0 or i >= len(coins)): return cont(0)
    elif (k in memo): return cont(memo[k])
    else:
      return TR(lambda: go(s, i+1, lambda x: TR(lambda: go(s-coins[i], i, lambda y: TR(lambda: cont(memoize(k, x+y)))))))

  return evalTR(go(s, 0, lambda x: x))


n = 10000
coins = [1, 5, 10, 25, 50]

rCS, tCS = time(ccCS, n, coins)
rC,  tC  = time(ccC,  n, coins)

print("ccCS:   ", rCS, "{:.2f}".format(tCS))
print("ccC:    ", rC,  "{:.2f}".format(tC))

