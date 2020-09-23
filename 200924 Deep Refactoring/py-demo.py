"""Custom stack core."""

######################################################################################
# bare-bones trampoline
######################################################################################

class TR:
  def __init__(self, fn): self.fn = fn

def evalTR(tr):
  while isinstance(tr, TR): tr = tr.fn()
  return tr

######################################################################################
# non-tail recursion: custom-stack evaluation with optional memoization
######################################################################################

class CS:
  def __init__(self, args = None, fold = None, memo = None):
    self.args = args if isinstance(args, list) else [args]
    self.fold = fold
    self.memo = memo
    self.i = 0

def evalCS(cs):
  if not isinstance(cs, CS): return cs

  m = {}
  s = [cs]
  # d, c = 0, 0
  while (True):
    # l = len(s)
    # d = l if l > d else d # d = max(d, len(s))
    # c += 1
    h = s[-1]

    if h.i < len(h.args):
      v = h.args[h.i]
      if callable(v): v = v()

      if isinstance(v, CS):
        if v.memo is not None and v.memo in m:
          v = m[v.memo]
        else:
          if h.fold is None and h.i == len(h.args) - 1:
            s[-1] = v # TCO
          else:
            s.append(v)
          continue
      h.args[h.i] = v
      h.i += 1

    else:
      v = h.args[-1] if h.fold is None else h.fold(*h.args)

      if isinstance(v, CS):
        if v.memo is not None and v.memo in m:
          v = m[v.memo]
        else:
          s[-1] = v
          continue

      if h.memo is not None: m[h.memo] = v
      s.pop()
      if not s:
        # print("evalCS (stack/cycles):", d, "/", c)
        return v
      else:
        h = s[-1]
        h.args[h.i] = v
        h.i += 1


def evalXX(o):
  while (True):
    if   isinstance(cs, TR): o = evalTR(o)
    elif isinstance(cs, CS): o = evalCS(o)
    else: return o

# """Py demo."""

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

# sum from 1 to n

def bar(n): return 0 if (0 == n) else n + bar(n-1)

# print("bar:    ", bar(10000))

def bar(n): return 0 if (0 == n) else CS(lambda: bar(n-1), lambda v: n+v)

# print("bar:    ", evalCS(bar(10000)))

# fibonacci

def fib(n): return n if (n < 2) else CS([lambda: fib(n-1), lambda: fib(n-2)],
                                        lambda x, y: x+y,
                                        n)
# print("fib:    ", evalCS(fib(50)))

# even / odd

def isEven(n): return True if (n == 0) else CS(lambda: isOdd(n-1))
def isOdd(n): return False if (n == 0) else CS(lambda: isEven(n-1))

# print("isEven: ", evalCS(isEven(10000)))
# print("isOdd:  ", evalCS(isOdd(10000)))

# height

def height(n, m):
  return 0 if (m <= 0 or n <= 0) else CS([lambda: height(n, m-1), lambda: height(n-1, m-1)],
                                         lambda x, y: x+y+1,
                                         (n, m))

# print("height: ", evalCS(height(5, 3000)))

# side effects!!! - hanoi

def hanoi(n, f, v, t):
  if n == 0: return
  hanoi(n-1, f, t, v)
  print("from", f, "to", t)
  hanoi(n-1, v, f, t)

def hanoiCS(n, f, v, t):
  return None if n == 0 else CS([lambda: hanoiCS(n-1, f, t, v),
                                 lambda: print("from", f, "to", t),
                                 lambda: hanoiCS(n-1, v, f, t)])

# print("Hanoi tower rec:")
# hanoi(3, 1, 2, 3)
# print("\nHanoi tower CS:")
# evalCS(hanoiCS(3, 1, 2, 3))

######################################################################################
# coin change
######################################################################################

# without memoization

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
      return CS([lambda: go(s, i+1), lambda: go(s-coins[i], i)], lambda x, y: x+y)
  return evalCS(go(s, 0))

def ccC(s, coins):
  def go(s, i, cont):
    if (s == 0): return cont(1)
    elif (s < 0 or i >= len(coins)): return cont(0)
    else:
      return TR(lambda: go(s, i+1, lambda x: TR(lambda: go(s-coins[i], i, lambda y: TR(lambda: cont(x+y))))))
  return evalTR(go(s, 0, lambda x: x))


n = 100 # 200
coins = [1, 5, 10, 25, 50]

# print("ccN:  ", ccN(n, coins))
# print("ccCS: ", ccCS(n, coins))
# print("ccC:  ", ccC(n, coins))


# with memoization

def ccCS(s, coins):
  def go(s, i):
    if (s == 0): return 1
    elif (s < 0 or i >= len(coins)): return 0
    else:
      return CS([lambda: go(s, i+1), lambda: go(s-coins[i], i)],
                lambda x, y: x+y,
                (s, i))
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

# print("ccCS: ", ccCS(n, coins))
# print("ccC:  ", ccC(n, coins))
