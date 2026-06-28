; ============================================================================
; Telos goal module for OmegaClaw  (telos_goals)
; ----------------------------------------------------------------------------
; A REUSABLE goal-understanding layer, written to be loaded into a live OmegaClaw
; runtime (PeTTa / MeTTa-on-SWI-Prolog) — not just a standalone Hyperon demo.
;
; Unlike telos/metta/goal_graph.metta (which hard-codes one example scenario and
; runs its queries at import), this module is SIDE-EFFECT-FREE on load: it only
; defines the schema contract + parameterized derivation rules. The agent (its LLM
; layer) materialises goal atoms from whatever it is reading, then calls these rules
; via the `metta` skill to derive conflicts, collective goals, blocks, and alignment.
;
; Schema (atoms the agent asserts into &self while reading):
;   (goal <id> <scope> <owner> <status>)   scope: individual | collective
;                                          status: active | proposed | achieved | abandoned
;   (rel  <type> <src> <dst>)              type: supports | conflicts | subsumes | depends-on
; ============================================================================

; ---- derivation rules (parameterized; safe to load — nothing runs at import) ----

; All conflict pairs the agent must surface (across ALL goals, not a fixed owner).
(= (telos-conflicts)
   (match &self (rel conflicts $a $b) (conflict-between $a $b)))

; Every collective goal (what the commons wants).
(= (telos-collective-goals)
   (match &self (goal $g collective $owner $status) (collective-goal $g $owner)))

; Goals owned by ANY given stakeholder (individual goal understanding).
(= (telos-goals-of $owner)
   (match &self (goal $g individual $owner $status) (goal-of $owner $g)))

; A goal is ACHIEVED when its status atom says so.
(= (telos-achieved $g)
   (match &self (goal $g $scope $owner achieved) True))

; BLOCKED: a goal that depends-on another goal that is not yet achieved.
(= (telos-blocked)
   (match &self (rel depends-on $g $dep)
      (match &self (goal $dep $s2 $o2 $st2)
         (if (== $st2 achieved) (empty) (blocked $g on $dep)))))

; Cross-level ALIGNMENT: an individual goal that SUPPORTS a collective goal
; (protecting the individual can serve the real collective good).
(= (telos-aligned)
   (match &self (rel supports $i $c)
      (match &self (goal $i individual $o1 $s1)
         (match &self (goal $c collective $o2 $s2)
            (aligns $i with $c)))))

; A full goal reading: run every lens at once. The agent calls (telos-reading)
; after asserting the goal/rel atoms it inferred from the input it is reading.
(= (telos-reading)
   (superpose ((telos-conflicts)
               (telos-collective-goals)
               (telos-blocked)
               (telos-aligned))))
