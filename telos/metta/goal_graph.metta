; ============================================================================
; Telos goal graph — AtomSpace representation for OmegaClaw
; ----------------------------------------------------------------------------
; This mirrors telos/schema.py in MeTTa so a goal reading materialises as atoms
; in OmegaClaw's AtomSpace, where its NAL/PLN engines can reason over it. It is
; runnable on a Hyperon MeTTa interpreter (pip install hyperon; `metta goal_graph.metta`)
; and is exercised by tests/test_metta.py when hyperon is installed.
;
; Representation
;   (goal <id> <scope> <owner> <status>)     scope: individual | collective
;   (rel  <type> <src> <dst>)                type: supports | conflicts
;                                                  | subsumes | depends-on
; ============================================================================

; ---- example goals (from scenario ic-01 "GPU hog" + co-01 "manipulated majority") ----
(goal alice-train      individual alice  active)
(goal dao-fair-access  collective dao    active)
(goal jo-due-process   individual jo     active)
(goal community-govern collective dao    active)

; ---- example relations ----
(rel conflicts alice-train     dao-fair-access)   ; individual vs collective
(rel supports  jo-due-process  community-govern)  ; protecting the individual serves the real collective good

; ---- a dependency example (gp-01 "blocked on finance") ----
(goal grant-proposal individual user     active)
(goal budget-table   individual finance  proposed)   ; not achieved
(rel depends-on grant-proposal budget-table)

; ============================================================================
; Queries / rules — the goal-understanding an agent runs over the graph
; ============================================================================

; 1) all conflicts the agent must surface
!(match &self (rel conflicts $a $b) (conflict-between $a $b))

; 2) all collective goals (what the commons wants)
!(match &self (goal $g collective $owner $status) (collective-goal $g $owner))

; 3) goals owned by a given stakeholder (individual goal understanding)
!(match &self (goal $g individual alice $status) (alice-goal $g))

; 4) a goal is ACHIEVED when its status atom says so
(= (achieved $g)
   (match &self (goal $g $scope $owner achieved) True))

; 5) BLOCKED: a goal that depends-on a goal that is not yet achieved.
;    (We list the dependency edges; the agent treats an unmet dependency as a block.)
!(match &self (rel depends-on $g $dep) (depends $g on $dep))

; 6) cross-level alignment edge: an individual goal that SUPPORTS a collective goal
!(match &self (rel supports $i $c)
   (match &self (goal $i individual $o1 $s1)
     (match &self (goal $c collective $o2 $s2)
       (aligns $i with $c))))
