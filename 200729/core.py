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
