"use strict"; console.log("################## TCO CASE:")

///////////////////////////////////////////////////////////////////////////////////////////////////////////
// BASICS
///////////////////////////////////////////////////////////////////////////////////////////////////////////

const f_loop = (n) => {
  var a = 0
  for (let i = 0; i <= n; ++i) a += i;
  return a;
}

const f__rec = (n) => n<=0 ? 0 : n + f__rec(n-1) // non-tail recursive call

const f_trec = (n, a) => n<=0 ? a : f_trec(n-1, a+n) // tail recursion case

// 39000 - works, 40000 - dont

// console.log("f_loop: ", f_loop(40000))
// console.log("f__rec: ", f__rec(40000))
// console.log("f_trec: ", f_trec(40000, 0))

const is_even = (n) => n==0 ? true : is_odd(n-1)  // tail call case
const is_odd = (n) => n==0 ? false : is_even(n-1) // tail call case

// console.log("is_even: ", is_even(40000))

///////////////////////////////////////////////////////////////////////////////////////////////////////////
// FINITE LIST
///////////////////////////////////////////////////////////////////////////////////////////////////////////

const cons = (x, y) => [x,y]
const car  = (l)    => l[0]
const cdr  = (l)    => l[1]

const nil = cons(null, null)

const isnull = (l) => car(l) == null && cdr(l) == null

const show = (l) => {
  if (Array.isArray(l)) {
    var r = ''
    while (!isnull(l)) {
      r = r + ' ' + show(car(l))
      l = cdr(l)
    }
    return '(' + r.substring(1) + ')'
  } else return l
}

const listFromTo = (a, b) => {
  var l = nil
  while (b >= a) {
    l = cons(b, l)
    b -= 1
  }
  return l
}

///////////////////////////////////////////////////////////////////////////////////////////////////////////
// MAP
///////////////////////////////////////////////////////////////////////////////////////////////////////////

const mapN = (f, l) => isnull(l) ? nil : cons(f(car(l)), mapN(f, cdr(l)))

const mapT = (f, l) => {
  const go = (l, a) => isnull(l) ? a : go(cdr(l), cons(f(car(l)), a))
  return go(l, nil)
}

const mapL = (f, l) => {
  var a = nil
  while (!isnull(l)) {
    a = cons(f(car(l)), a)
    l = cdr(l)
  }
  return a
}

const a = listFromTo(1, 10)
const b = listFromTo(1, 50000)

const inc = (x) => x+1

// console.log("Init: ", show(a))

// console.log("mapN: ", show(mapN(inc, a)))
// console.log("mapT: ", show(mapT(inc, a)))
// console.log("mapL: ", show(mapL(inc, a)))

// console.log("mapN: ", show(mapN(inc, b)))
// console.log("mapT: ", show(mapT(inc, b)))
// console.log("mapL: ", show(mapL(inc, b)))

// CPS !!!

const mapC = (f, l) => {
  const go = (l, cont) => isnull(l) ? cont(nil) : go(cdr(l), (x) => cont(cons(f(car(l)), x)))
  return go(l, (x) => x)
}

// console.log("mapC: ", show(mapC(inc, a)))

// CPS - CYCLE LAMBDA ACCUMULATION, create continuation via loop

const mapZ = (f, l) => {
  const lambdaGen = (c, v) => (x) => c(cons(f(v), x))

  var cont = (x) => x
  while (!isnull(l)) {
    cont = lambdaGen(cont, car(l))
    l = cdr(l)
  }
  return cont(nil)
}

// console.log("mapZ: ", show(mapZ(inc, b)))


///////////////////////////////////////////////////////////////////////////////////////////////////////////
// COIN CHANGE
///////////////////////////////////////////////////////////////////////////////////////////////////////////

const makeKey = (s, i) => s + "_" + i

// return memo.size

const ccN = (s, coins) => {
  var memo = new Map()
  var memoHas = 0

  const go = (s, i) => {
    const k = makeKey(s, i)

    if (s == 0) return 1
    else if (s < 0 || i >= coins.length) return 0
    else if (memo.has(k)) { memoHas++; return memo.get(k) }
    else {
      const r = go(s, i+1) + go(s-coins[i], i)
      memo.set(k, r)
      return r
    }
  }
  return [go(s, 0), memo.size, memoHas]
}

const ccC = (s, coins) => {
  var memo = new Map()
  var memoHas = 0

  const go = (s, i, cont) => {
    const k = makeKey(s, i)

    if (s == 0) return cont(1)
    else if (s < 0 || i >= coins.length) return cont(0)
    else if (memo.has(k)) { memoHas++; return cont(memo.get(k)) }
    else
      return go(s, i+1, (x) => go(s-coins[i], i, (y) => {
        const r = x+y
        memo.set(k, r)
        return cont(r)
      }))
  }
  return [go(s, 0, (x) => x), memo.size, memoHas]
}

const ccA = (s, coins) => {
  var memo = new Map()
  var memoHas = 0

  const go = (s, i) => {
    const k = makeKey(s, i)

    if (s == 0) return 1
    else if (s < 0 || i >= coins.length) return 0
    else if (memo.has(k)) { memoHas++; return memo.get(k) }
    else {
      var r = 0
      while (s >= 0) {
        r += go(s, i+1)
        s -= coins[i]
      }
      memo.set(k, r)
      return r
    }
  }
  return [go(s, 0), memo.size, memoHas]
}

const coins = [1, 5, 10, 25, 50]

// console.log("ccN: ", ccN(50000, coins)) // 100, 10000, 50000
// console.log("ccC: ", ccC(50000, coins)) // 100, 10000, 50000, 100000
// console.log("ccA: ", ccA(200, coins)) // 100, 10000
