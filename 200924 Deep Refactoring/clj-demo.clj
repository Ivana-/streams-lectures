;; https://rextester.com/
;; https://ideone.com/
;; https://repl.it/
;; https://paiza.io/
;; https://www.mycompiler.io/new/clojure


;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
;; bare-bones trampoline
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;


(defmacro tr [f & args] `(with-meta (fn [] (~f ~@args)) {:trampoline? true}))

(defn eval-tr [f & args]
  (loop [t (apply f args)] (if (:trampoline? (meta t)) (recur (t)) t)))


;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
;; non-tail recursion: custom-stack evaluation with optional memoization
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;


(defmacro cs [f & args]
  ^:custom-stack? {:function f
                   :args (mapv #(list 'fn '[] %) args)})

(defmacro cs-memo [args-memo f & args]
  ^:custom-stack? {:function f
                   :args (mapv #(list 'fn '[] %) args)
                   :args-memo args-memo})

(defn trace [{:keys [eval-args not-eval-args args-memo]} d]
  (let [spaces (apply str (replicate d " "))
        msg (cond
              (seq eval-args) eval-args
              args-memo args-memo
              :else (let [x (first not-eval-args)]
                      (if (map? x) "???" x)))]
    (println (str spaces msg))))

(defn eval-cs [f & args]
  (let [r (apply f args)]
    (if-not (:custom-stack? (meta r))
      r
      (let [make-si (fn [x] (merge (dissoc x :args)
                                   {:eval-args []
                                    :not-eval-args (map (fn [f] (f)) (:args x))}))
            m (atom {})]
        (loop [[h & t] (list (make-si r))]
          ;; (trace h (count t))

          (let [hne (-> h :not-eval-args first)]
            (cond

              (empty? (:not-eval-args h))
              (let [{:keys [function eval-args]} h
                    r (if function (apply function eval-args) (first eval-args))
                    [ht & tt] t]
                (cond
                  (:custom-stack? (meta r)) (recur (cons (make-si r) t))
                  (empty? t) r
                  :else (do
                          (when (contains? h :args-memo) (swap! m assoc (:args-memo h) r))
                          (recur (cons (update ht :eval-args conj r) tt)))))

              (:custom-stack? (meta hne))
              (if (and (contains? hne :args-memo) (contains? @m (:args-memo hne)))
                (recur (cons (-> h
                                 (update :eval-args conj (get @m (:args-memo hne)))
                                 (update :not-eval-args rest)) t))
                (recur (->> t
                            (cons (update h :not-eval-args rest))
                            (cons (make-si hne)))))

              :else
              (recur (cons (-> h
                               (update :eval-args conj hne)
                               (update :not-eval-args rest)) t)))))))))

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
;; examples
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

(comment

  "tail recursion - recur or trampoline"

  (defn foo [n a] (if (= 0 n) a (foo (- n 1) (+ n a))))
  (prn (foo 10000 0))

  ;; tail recursion - recur...
  (defn foo [n a] (if (= 0 n) a (recur (- n 1) (+ n a))))
  (prn (foo 10000 0))

  ;; ... or trampoline
  (defn foo [n a] (if (= 0 n) a (tr foo (- n 1) (+ n a))))
  (prn (eval-tr foo 10000 0))


  "mutual tail call - trampoline"

  (declare is-odd?)
  (defn is-even? [n] (if (= 0 n) true  (is-odd?  (- n 1))))
  (defn is-odd?  [n] (if (= 0 n) false (is-even? (- n 1))))
  (prn (is-even? 1000000))

  ;; tail call - trampoline
  (declare is-odd?)
  (defn is-even? [n] (if (= 0 n) true  (tr is-odd?  (- n 1))))
  (defn is-odd?  [n] (if (= 0 n) false (tr is-even? (- n 1))))
  (prn (eval-tr is-even? 1000000))


  "non-tail recursion - via custom stack!"

  (defn bar [n] (if (= 0 n) 0 (+ n (bar (- n 1)))))
  (prn (bar 10000))

    ;; non-tail call - via custom stack!
  (defn bar [n] (if (= 0 n) 0 (cs + n (bar (- n 1)))))
  (prn (eval-cs bar 10000))


  "tail recursion - also via custom stack!"

  (defn foo [n a] (if (= 0 n) a (cs nil (foo (- n 1) (+ n a)))))
  (prn (eval-cs foo 10000 0))


  "mutual tail call - also via custom stack!"

  (declare is-odd?)
  (defn is-even? [n] (if (= 0 n) true  (cs nil (is-odd?  (- n 1)))))
  (defn is-odd?  [n] (if (= 0 n) false (cs nil (is-even? (- n 1)))))
  (prn (eval-cs is-even? 1000000))


  "non-tail recursion with memoization - via custom stack!"

  ;; fibbonacci
  (defn fib [n] (if (< n 2) n (cs-memo n + (fib (- n 1)) (fib (- n 2)))))
  (prn (eval-cs fib 10))
  (prn (eval-cs fib 30))
  (prn (eval-cs fib 50))

  ;; coin change
  (defn coin-change [s coins]
    (cond (= s 0) 1
          (or (< s 0) (empty? coins)) 0
          :else (cs-memo [s coins]
                         +
                         (coin-change s (rest coins))
                         (coin-change (- s (first coins)) coins))))

  (def coins-list '(1 5 10 25 50))
  (prn (eval-cs coin-change 100    coins-list))
  (prn (eval-cs coin-change 10000  coins-list))

  ;; skyscrappers height
  (defn height [n m]
    (if (or (<= m 0) (<= n 0))
      0
      (cs-memo [n m] + 1 (height n (- m 1)) (height (- n 1) (- m 1)))))

  (prn (eval-cs height 2 14))
  (prn (eval-cs height 5 3000))


  "non-primitive non-tail recursion with memoization - via custom stack!"

  ;; Ackermann
  (defn ack [m n]
    (cond
      (zero? m) (inc n)
      (zero? n) (ack (dec m) 1)
      :else     (ack (dec m) (ack m (dec n)))))

  (prn (ack 4 1))

  (defn ack [m n]
    (cond
      (zero? m) (inc n)
      (zero? n) (cs-memo [m n] nil (ack (dec m) 1))
      :else     (cs-memo [m n]
                         (fn [a b] (cs-memo [a b] nil (ack a b)))
                         (dec m)
                         (ack m (dec n)))))

  (prn (eval-cs ack 4 1))
  (prn (eval-cs ack 3 14))
  
  ;;
  )
