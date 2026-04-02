# Encoding SPIN plays into PRISM

In this section, we present a direct translation from BPMN+CPI models to [PRISM](https://www.prismmodelchecker.org/), available at [the project repository](https://anonymous.4open.science/r/PACO-D1D0/README.md).
The repository includes the presentation of the extended validation results,
the BPMN+CPI to SPIN and the SPIN to PRISM translations, together with their visual representations. As we will see in this section, we need to create more intermediate MDP states due to the simple and restrictive structure of the PRISM program, in order to correctly map the SPIN into the PRISM framework. Because of this, we had to carefully craft a method that compacts all these intermediate states into those corresponding to the SPIN places. 

The following translation preserves the synchronous semantics and temporal behavior of the original formalism.
This translation addresses the strategy synthesis problem by encoding it as a multi-objective bounded reachability problem in PRISM, enabling cross-validation of our specialized algorithms against the general-purpose PRISM model checker.

## PRISM Module System and Translation Overview

PRISM uses a state-based formalism where systems are composed of modules that interact through synchronized actions. We illustrate this with a comprehensive example showing the key PRISM mechanisms in [Listing 1](#lst-prism-basic-example).

<a id="lst-prism-basic-example"></a>

**Listing 1 - Basic PRISM example**

```prism
global x : [0..3] init 0;
global y : [0..2] init 0;
global stage : [0..2] init 0;

formula psi_ready = x>0 & y=0;
formula psi_active = x=3 & y>0;

module mod1
    s1 : [0..2] init 0;
    // Guard with psi condition
    [] psi_ready & s1=0 -> (s1'=1);
    // Action synchronization
    [sync] s1=1 -> (s1'=2) & (x'=x+1);
endmodule

module mod2
    s2 : [0..1] init 0;
    // Synchronized action
    [sync] psi_active & s2=0 -> (s2'=1);
    // Probabilistic choice
    [] s2=1 -> 0.6: (s2'=0) & (y'=1) + 0.4: (s2'=0) & (y'=2);
endmodule
```

The example in [Listing 1](#lst-prism-basic-example) demonstrates the four key mechanisms: *guards* use conditions such as `psi_ready` and `psi_active` to coordinate module interactions based on global state. *Updates* modify local state variables such as `s1'=1` and `s1'=2`, together with global variables such as `x'=x+1`. *Action synchronization* through labeled actions such as `[sync]` ensures coordinated execution across modules. *Probabilistic choice* provides explicit probability distributions for non-deterministic outcomes.

## Variable Encoding and State Representation

The SPIN to PRISM translation employs a systematic variable encoding scheme that captures both the discrete state of places and the coordination requirements of synchronous execution. The encoding consists of three primary variable categories that work together to preserve SPIN semantics:

**Place State Variables:** Each SPIN place $p \in P$ with duration $d = Duration(p)$ is encoded using two global PRISM variables. The *place value variable* `p_value : [-1..d]` directly encodes the SPIN state function $q(p)$, where `p_value = -1` corresponds to $q(p) = \epsilon$ (no token present) and `p_value = n` for $n \geq 0$ corresponds to $q(p) = n$ (token present for $n$ time units). The initial value is set to 0 for the initial place and -1 for all others. Additionally, each place has a *coordination variable* `p_updated : [0..1]` that ensures deterministic processing order during time advancement phases, preventing race conditions in the parallel execution environment.

**Transition State Variables:** Each SPIN transition becomes a PRISM module containing a local state variable `transitionName_state : [-1..1]`. This variable encodes the transition readiness within each execution cycle: state -1 indicates the transition is deactivated (input places do not meet duration requirements), state 0 represents idle status (ready for evaluation), and state 1 signifies the transition is ready to fire (all input places have satisfied their duration constraints). This three-state encoding allows the system to distinguish between transitions that cannot fire due to timing constraints or absence of tokens in one of the incoming places versus those that are eligible for activation.

**Execution Control Variables:** The global `STAGE : [0..5]` variable orchestrates the six-phase execution protocol that replicates the SPIN
synchronous semantics. Stage 0 handles state activation decisions, stage 1 resets coordination flags, stage 2 represents termination, stage 3 manages time advancement, stage 4 executes non-nature transitions, and stage 5 handles probabilistic nature transitions. This staged approach ensures that the complex interactions between multiple transitions and places occur in a deterministic, reproducible manner that preserves the temporal relationships inherent in the original SPIN model while avoiding the state explosion that would result from naive parallel composition.

## Place Encoding and Time Advancement

Each SPIN place $p \in P$ with duration $d = Duration(p)$ is encoded using two global PRISM variables that work together to maintain both state information and execution coordination. The *place value variable* `p_value : [-1..d]` directly encodes the SPIN state function $q(p)$, where `p_value = -1` corresponds to $q(p) = \epsilon$ (no token present) and `p_value = n` for $n \geq 0$ corresponds to $q(p) = n$ (token present for $n$ time units). The *coordination variable* `p_updated : [0..1]` ensures deterministic processing order during time advancement phases, preventing race conditions in the parallel execution environment.

The stage-based execution protocol is controlled by the manager module, which orchestrates the six-stage cycle that replicates SPIN synchronous semantics, as shown in [Listing 2](#lst-stage-operations).

<a id="lst-stage-operations"></a>

**Listing 2 - Stage operations**

```prism
module manager
    // Stage 0 -> 3: Time advancement (when no transitions can fire)
    [] STAGE=0 & psi_step -> (STAGE'=3);

    // Stage 0 -> 2: Termination (no transitions active, no time can advance)
    [] STAGE=0 & !psi_step & psi_noone_idle & !psi_atleastone_active -> (STAGE'=2);

    // Stage 0 -> 4: Transition firing (at least one transition is active)
    [] STAGE=0 & !psi_step & psi_noone_idle & psi_atleastone_active -> (STAGE'=4);

    // Stage 3 -> 1: All places updated, move to reset phase
    [] STAGE=3 & psi_all_step_updated -> (STAGE'=1);

    // Stage 1 -> 0: All coordination flags reset, return to analysis
    [] STAGE=1 & psi_all_step_not_updated -> (STAGE'=0);

    // Stage 4 -> 5: All non-nature transitions processed, handle nature
    [] STAGE=4 & psi_all_idle_but_nature -> (STAGE'=5);

    // Stage 5 -> 0: All nature transitions processed, return to analysis
    [] STAGE=5 & psi_all_idle_nature -> (STAGE'=0);
    ...
endmodule
```

The time advancement transition in [Listing 2](#lst-stage-operations) occurs when no transitions can fire (`psi_step` condition), while the termination condition is checked when no transitions are active and no time advancement is possible. Transition firing is triggered when at least one transition is active, and the return to analysis phase occurs after processing non-nature transitions and nature transitions.
During Stage 3 (time advancement), each place follows a three-case update protocol that directly implements the $\emptyset$ transition semantics from SPIN, as illustrated in [Listing 3](#lst-place-update).

<a id="lst-place-update"></a>

**Listing 3 - Place update rules**

```prism
// Place p0 with duration=2, time advancement rules
module manager
    ...
    // Case 1: Place has no token (value=-1), just mark as updated
    [] STAGE=3 & step_updated_p0 & p0_value=-1 -> (p0_updated'=1);

    // Case 2: Place has token but hasn't reached duration limit
    [] STAGE=3 & step_updated_p0 & p0_value>=0 & p0_value<2 -> (p0_value'=p0_value+1) & (p0_updated'=1);

    // Case 3: Place has reached duration limit, just mark as updated
    [] STAGE=3 & step_updated_p0 & p0_value=2 -> (p0_updated'=1);

    // Similar rules for other places...
    [] STAGE=3 & step_updated_p1 & p1_value=-1 -> (p1_updated'=1);
    [] STAGE=3 & step_updated_p1 & p1_value>=0 & p1_value<1 -> (p1_value'=p1_value+1) & (p1_updated'=1);
    [] STAGE=3 & step_updated_p1 & p1_value=1 -> (p1_updated'=1);
endmodule
```

Case 1 (lines 5-6 in [Listing 3](#lst-place-update)) handles places without tokens by only updating the coordination flag, Case 2 (lines 8-10) manages time advancement for active tokens by incrementing both the time value and coordination flag, and Case 3 (lines 12-13) processes tokens that have reached their duration limit by only updating the coordination flag.
The deterministic ordering is enforced through coordination formulas that ensure places are processed in lexicographic order, as shown in [Listing 4](#lst-place-coordination). This systematic approach prevents race conditions and ensures that exactly one place updates per step within each stage cycle.

<a id="lst-place-coordination"></a>

**Listing 4 - Place coordination formulas**

```prism
// Coordination formulas for deterministic place update ordering
formula step_updated_p0 = p0_updated=0;
formula step_updated_p1 = p1_updated=0 & p0_updated=1;
formula step_updated_p2 = p2_updated=0 & p0_updated=1 & p1_updated=1;

// Global coordination for stage transition
formula psi_all_step_updated = p0_updated=1 & p1_updated=1 & p2_updated=1;

// Stage transition rule
[] STAGE=3 & psi_all_step_updated -> (STAGE'=1);
```

The coordination formulas (lines 2-4 in [Listing 4](#lst-place-coordination)) establish the lexicographic ordering where each place can only update after all preceding places have been processed. The global coordination check (`psi_all_step_updated` at line 6) determines when all places have completed their updates, triggering the stage transition (line 9) from Stage 3 to Stage 1.

Places without tokens (`p_value = -1`) simply mark themselves as updated without state change. Places with tokens that have not yet met their duration requirement (`p_value < d`) increment their time counter and mark themselves as updated. Places that have already satisfied their duration constraint (`p_value = d`) remain unchanged but still participate in the coordination protocol. This systematic approach guarantees that the PRISM time advancement phase produces exactly the same state transitions as the corresponding $\emptyset$ transitions in the original SPIN model, maintaining semantic equivalence while providing the coordination necessary for deterministic execution in the PRISM framework.

## Transition Module Encoding

Each SPIN transition is mapped to a PRISM module according to its type and connectivity pattern. The encoding distinguishes between modules that represent single transitions and those that represent paired transitions with shared input places. Single transition modules are used for task transitions, parallel splits, parallel merges, and simple single transitions, where each module corresponds to exactly one SPIN transition. Paired transition modules are employed for choice and nature gateways, where one PRISM module handles both alternative transitions that share the same input place, representing the two possible execution paths with their respective output places labeled as `p_true` and `p_false`.

The module structure follows a consistent pattern regardless of transition type: each module contains a local state variable `transitionName_state` that tracks the transition readiness throughout the execution cycle, and the module logic handles both the activation analysis phase (determining whether the transition can fire) and the actual execution phase (updating place values according to the transition semantics). This unified approach ensures that all transition types integrate seamlessly into the stage-based execution protocol while maintaining their distinct behavioral characteristics.

The following listings illustrate the generated PRISM code for each transition type.

**Single Transition (Task/Simple):** one input place, one output place, visible in [Listing 5](#lst-single-transition).
The module structure contains a local state variable (line 2 in [Listing 5](#lst-single-transition)) that tracks the transition readiness throughout the execution cycle. The activation analysis occurs during Stage 0 through two rules: the first rule (lines 4-5) sets the transition state to 1 when duration requirements are met, while the second rule (lines 6-7) sets the state to -1 when requirements are not satisfied. The actual execution phase updates place values during Stage 4 (lines 9-12), where enabled transitions consume input tokens and produce output tokens.

<a id="lst-single-transition"></a>

**Listing 5 - Single transition module**

```prism
module t_task
  t_task_state : [-1..1] init 0;
  // Stage 0: Activation check
  [fire_t_task] STAGE=0 & psi_idle_t_task & (p_in_value >= dur_p_in) -> (t_task_state'=1);
  [] STAGE=0 & psi_idle_t_task & !(p_in_value >= dur_p_in) -> (t_task_state'=-1);
  // Stage 4: Execution
  [] STAGE=4 & psi_first_but_nature_not_idle_t_task & t_task_state=1 ->
  (t_task_state'=0) & (p_in_value'=-1) & (p_out_value'=0);
  [] STAGE=4 & psi_first_but_nature_not_idle_t_task & t_task_state=-1 -> (t_task_state'=0);
endmodule
```

**Parallel Split:** one input place, two output places, shown in [Listing 6](#lst-parallel-split).
The parallel split demonstrates how one input place (checked at line 4 in [Listing 6](#lst-parallel-split)) can produce tokens in multiple output places simultaneously (line 10), where tokens are placed in both output places by setting `p_out1_value'=0` and `p_out2_value'=0` in the same update operation.

<a id="lst-parallel-split"></a>

**Listing 6 - Parallel split module**

```prism
module t_split
  t_split_state : [-1..1] init 0;
  // Stage 0: Activation check
  [] STAGE=0 & psi_idle_t_split & (p_in_value >= dur_p_in) -> (t_split_state'=1);
  [] STAGE=0 & psi_idle_t_split & !(p_in_value >= dur_p_in) -> (t_split_state'=-1);
  // Stage 4: Execution
  [] STAGE=4 & psi_first_but_nature_not_idle_t_split & t_split_state=1
    -> (t_split_state'=0) & (p_in_value'=-1) & (p_out1_value'=0) & (p_out2_value'=0);
  [] STAGE=4 & psi_first_but_nature_not_idle_t_split & t_split_state=-1 -> (t_split_state'=0);
endmodule
```

**Parallel Merge:** two input places, one output place, visible in [Listing 7](#lst-parallel-merge).
The merge module shows the coordination required for multiple input places (lines 4-5 in [Listing 7](#lst-parallel-merge)) to synchronize before proceeding, where both duration conditions must be satisfied simultaneously, and the execution phase (line 9) consumes tokens from both input places.

<a id="lst-parallel-merge"></a>

**Listing 7 - Parallel merge module**

```prism
module t_merge
  t_merge_state : [-1..1] init 0;
  // Stage 0: Activation check
  [] STAGE=0 & psi_idle_t_merge & (p_in1_value >= dur_p_in1) & (p_in2_value >= dur_p_in2) -> (t_merge_state'=1);
  [] STAGE=0 & psi_idle_t_merge & !((p_in1_value >= dur_p_in1) & (p_in2_value >= dur_p_in2)) -> (t_merge_state'=-1);
  // Stage 4: Execution
  [] STAGE=4 & psi_first_but_nature_not_idle_t_merge & t_merge_state=1
    -> (t_merge_state'=0) & (p_in1_value'=-1) & (p_in2_value'=-1) & (p_out_value'=0);
  [] STAGE=4 & psi_first_but_nature_not_idle_t_merge & t_merge_state=-1 -> (t_merge_state'=0);
endmodule
```

**Choice Split Module:** one input place, two alternative output places (non-deterministic), as shown in [Listing 8](#lst-choice-split).
Choice transitions provide non-deterministic alternatives through multiple execution rules (lines 9-12 in [Listing 8](#lst-choice-split)), where the first alternative (line 10) places the token in `p_true` by setting `p_true_value'=0` and the second alternative (line 12) places it in `p_false` by setting `p_false_value'=0`.

<a id="lst-choice-split"></a>

**Listing 8 - Choice split module**

```prism
module t_choice
  t_choice_state : [-1..1] init 0;
  // Stage 0: Activation check
  [] STAGE=0 & psi_idle_t_choice & (p_in_value >= dur_p_in) -> (t_choice_state'=1);
  [] STAGE=0 & psi_idle_t_choice & !(p_in_value >= dur_p_in) -> (t_choice_state'=-1);
  // Stage 4: Execution (two non-deterministic alternatives)
  [] STAGE=4 & psi_first_but_nature_not_idle_t_choice & t_choice_state=1
    -> (t_choice_state'=0) & (p_in_value'=-1) & (p_true_value'=0);
  [] STAGE=4 & psi_first_but_nature_not_idle_t_choice & t_choice_state=1
    -> (t_choice_state'=0) & (p_in_value'=-1) & (p_false_value'=0);
  [] STAGE=4 & psi_first_but_nature_not_idle_t_choice & t_choice_state=-1 -> (t_choice_state'=0);
endmodule
```

**Nature Split Module:** one input place, two alternative output places (probabilistic) as shown in [Listing 9](#lst-nature-split).
Nature transitions implement probabilistic branching with explicit probability distributions (lines 9-11 in [Listing 9](#lst-nature-split)), where the 0.7 probability (line 10) places the token in `p_true` by setting `p_true_value'=0` and the 0.3 probability (line 11) places the token in `p_false` by setting `p_false_value'=0`.

<a id="lst-nature-split"></a>

**Listing 9 - Nature split module**

```prism
module t_nature
  t_nature_state : [-1..1] init 0;
  // Stage 0: Activation check
  [] STAGE=0 & psi_idle_t_nature & (p_in_value >= dur_p_in) -> (t_nature_state'=1);
  [] STAGE=0 & psi_idle_t_nature & !(p_in_value >= dur_p_in) -> (t_nature_state'=-1);
  // Stage 5: Execution (probabilistic choice)
  [] STAGE=5 & psi_first_nature_not_idle_t_nature & t_nature_state=1
    -> 0.7: (t_nature_state'=0) & (p_true_value'=0) & (p_in_value'=-1) +
       0.3: (t_nature_state'=0) & (p_false_value'=0) & (p_in_value'=-1);
  [] STAGE=5 & psi_first_nature_not_idle_t_nature & t_nature_state=-1 -> (t_nature_state'=0);
endmodule
```

## Stage-Based Execution Protocol

The synchronous execution semantics of SPIN are replicated through a deterministic six-stage protocol, where each stage has specific activation conditions and operational invariants that ensure correct temporal ordering and state consistency. Each firing of a synchronized set $t$ corresponds to a specific stage traversal pattern: for empty transition sets ($t = \emptyset$), the system follows Stage 0 $\rightarrow$ Stage 3 $\rightarrow$ Stage 1 $\rightarrow$ Stage 0 to advance time and return to a new SPIN state; for non-empty synchronized transition sets ($t \neq \emptyset$), the traversal follows Stage 0 $\rightarrow$ Stage 4 $\rightarrow$ Stage 5 $\rightarrow$ Stage 0 to execute transitions and reach the resulting SPIN state; finally, the path Stage 0 $\rightarrow$ Stage 2 represents system termination when no further evolution is possible. Crucially, the `p_value` variables of all places whenever the system is at Stage 0 directly encode the current state of the corresponding SPIN model, establishing a bijective correspondence between PRISM states at Stage 0 and SPIN states.

In the detailed stage descriptions that follow, we assume that both places and transitions are ordered lexicographically by name. This lexicographic ordering is essential for eliminating useless non-determinism that would otherwise arise from arbitrary processing sequences, thereby preventing unnecessary state space explosion in the chain of variable updates. The deterministic ordering ensures that equivalent SPIN states are reached through unique PRISM execution paths, maintaining semantic consistency while optimizing verification performance.

**Stage 0 - State Activation Analysis:** It is important to note that each PRISM module represents either one transition (for task, parallel split, parallel merge, and single transitions) or two transitions (for choice and nature modules, where one module handles both possible alternative transitions). At the beginning of execution and whenever the system returns to Stage 0, all place coordination variables `p_updated` are set to 0 and all transition state variables `transitionName_state` are set to 0, establishing a clean initial state for the activation analysis phase. The system then evaluates whether transitions can fire based on their input place requirements. For each transition with name `transitionName`, we define the formula `is_active_transitionName = \bigwedge_{p \in \text{input_places}(\texttt{transitionName})} (\texttt{p_value} \geq Duration(p))`, which is true when all incoming places have satisfied their duration constraints, making the transition ready to fire.

Conversely, `\neg\texttt{is_active_transitionName}` indicates that at least one incoming place fails to meet the requirements, preventing the transition from firing. We can then determine whether all transitions are inactive using the formula `\texttt{psi_noone_active} = \bigwedge_{\texttt{transitionName} \in \mathcal{T}} \neg\texttt{is_active_transitionName}`, which indicates that no transitions are ready to fire. Additionally, we define the formula `\texttt{psi_at_least_one_remaining_duration} = \bigvee_{p \in P} (\texttt{p_value} \geq 0 \land \texttt{p_value} < Duration(p))`, which indicates that there exists at least one place with a token that has not yet met its duration requirement. This formula is essential for distinguishing between time advancement scenarios and terminal conditions.
Stage 0 operates based on the evaluation of these formulas. If `\texttt{psi_noone_active}` is false, indicating that at least one transition has all its incoming places with durations met, then transition modules activate in lexicographical order by means of a formula that determines whether all previous transition modules in the ordering are not idle. When a module becomes active, it checks as a precondition whether its related transition is active: if the transition is not active (incoming places have not met duration requirements), the module sets its state to -1; otherwise, if the incoming places have met their duration requirements, it sets its state to 1. After all transition state updates are complete, there is a formula `\texttt{psi_noone_idle} = \bigwedge_{\texttt{transitionName} \in \mathcal{T}} (\texttt{transitionName_state} \neq 0)` that checks if all transition states are not idle. When this formula is true (which occurs only at the end of all transition state updates) and `\texttt{psi_noone_active}` is false and we are in Stage 0, the system transitions to Stage 4.

If `\texttt{psi_noone_active}` is true and `\texttt{psi_at_least_one_remaining_duration}` is true, the system moves directly to Stage 3 for time advancement. If both `\texttt{psi_noone_active}` and `\texttt{psi_at_least_one_remaining_duration}` are false, the system moves directly to Stage 2 for termination, with no state modifications occurring in this case.

**Stage 3 - Time Advancement Phase:** When the system enters Stage 3, all transition states are in idle mode (`transitionName_state = 0`) and all place coordination variables are reset (`p_updated = 0` for all places $p \in P$). The system then systematically advances time by processing places in lexicographical order to ensure deterministic execution. The coordination formula `step_updated_p = p_updated = 0 \land \bigwedge_{p' < p} p'_updated = 1` ensures that each place $p$ is processed only after all lexicographically preceding places have been updated. For each place $p$ in this deterministic order, three distinct update rules apply based on the current token state: (i) if `p_value = -1` (no token present), only the coordination flag is updated using `p_updated' = 1`; (ii) if 0 $\leq$ `p_value` < $Duration(p)$ (token present but duration not yet met), both the time value and coordination flag are updated through `p_value' = p_value + 1 \land p_updated' = 1`; and (iii) if `p_value = Duration(p)` (token has reached maximum duration), only the coordination flag is updated since further time advancement is unnecessary. These update rules, implemented in the manager module Stage 3 transitions, ensure that time progresses uniformly across all active places while respecting duration constraints. Once all places have been processed, indicated by the global coordination formula $\psi_{\text{all\_step\_updated}} = \bigwedge_{p \in P}$ `p_updated = 1` evaluating to true, the manager transitions to Stage 1 through `STAGE = 3 \land \psi_{\text{all_step_updated}} \Rightarrow STAGE' = 1`. During Stage 1, the coordination variables are systematically reset to their initial state through the lexicographically ordered formula `step_not_updated_p = p_updated = 1 \land \bigwedge_{p' < p} p'_updated = 0`, which ensures each place coordination flag is reset only after all preceding places have been reset. When all coordination variables have been cleared, as determined by $\psi_{\text{all\_step\_not\_updated}} = \bigwedge_{p \in P}$ `p_updated = 0`, the manager returns to Stage 0 to begin a new execution cycle, completing the time advancement protocol and maintaining the synchronized semantics essential for faithful SPIN representation.

**Stage 4 - Non-Nature Transition Firing Phase:** Stage 4 is entered when all place coordination variables have been reset (`p_updated = 0` for all places $p \in P$) and at least one transition state is not idle (indicated by $\psi_{\text{noone\_idle}}$ being true). The system processes non-nature transitions in lexicographical order using a coordination mechanism similar to the place ordering in Stage 3. The coordination formula $\psi_{\text{first\_but\_nature\_not\_idle}_t} = t\texttt{\_state} \neq 0 \land \bigwedge_{\substack{t' < t \\ t' \notin \mathcal{t}_{\text{nature}}}} t'\texttt{\_state} = 0$ ensures that each non-nature transition $t$ is processed only after all lexicographically preceding non-nature transitions have been reset to idle state. For each transition in this deterministic order, two distinct processing rules apply: (i) if the transition state equals -1 (transition was not enabled during state activation), the rule `STAGE = 4 \land \psi_{\text{first_but_nature_not_idle}_t} \land t_state = -1 \Rightarrow t_state' = 0` resets the transition to idle without further action; and (ii) if the transition state equals 1 (transition was enabled and ready to fire), the transition executes by consuming tokens from input places and producing tokens in output places according to its type-specific semantics. A notable case occurs with choice transitions, where the firing rule `STAGE = 4 \land \psi_{\text{first_but_nature_not_idle}_t} \land t_state = 1` provides two non-deterministic alternatives: the first rule $\Rightarrow (t\_state' = 0) \land (p_{\text{in}}\texttt{\_value'} = -1) \land (p_{\text{true}}\texttt{\_value'} = 0)$ places the token in the true output place by setting `p_true_value'=0`, while the second rule $\Rightarrow (t\_state' = 0) \land (p_{\text{in}}\texttt{\_value'} = -1) \land (p_{\text{false}}\texttt{\_value'} = 0)$ places the token in the false output place by setting `p_false_value'=0`. Whenever either alternative is selected, the choice module simultaneously resets to idle state (0), preventing any additional actions by this module during the current Stage 4 phase and ensuring the module cannot be visited again until the system cycles through Stage 0. The completion of Stage 4 is determined by the formula $\psi_{\text{all\_idle\_but\_nature}} = \bigwedge_{t \notin \mathcal{t}_{\text{nature}}} t\texttt{\_state} = 0$, which verifies that all non-nature transitions have returned to idle state. When this condition is satisfied, the manager transitions to Stage 5 through `STAGE = 4 \land \psi_{\text{all_idle_but_nature}} \Rightarrow STAGE' = 5` to process any remaining nature transitions.

**Stage 5 - Nature Transition Firing Phase:** When Stage 5 is entered, the system maintains specific state guarantees: all place coordination variables remain reset (`p_updated = 0` for all places $p \in P$), all nature transition states are either enabled (1) or disabled (-1), and all non-nature transitions have been reset to idle state (0) during the preceding Stage 4 processing. Stage 5 operates exclusively on nature split transitions using a coordination mechanism analogous to Stage 4. The lexicographical ordering formula $\psi_{\text{first\_nature\_not\_idle}_t} = t\texttt{\_state} \neq 0 \land \bigwedge_{\substack{t' < t \\ t' \in \mathcal{t}_{\text{nature}}}} t'\texttt{\_state} = 0$ ensures that each nature transition $t$ is processed only after all lexicographically preceding nature transitions have been reset to idle state. For each nature transition in this deterministic order, two processing rules apply: (i) if the transition state equals -1 (transition was not enabled during state activation), the rule `STAGE = 5 \land \psi_{\text{first_nature_not_idle}_t} \land t_state = -1 \Rightarrow t_state' = 0` resets the transition to idle without further action; and (ii) if the transition state equals 1 (transition was enabled and ready to fire), the nature transition executes through the probabilistic rule `STAGE = 5 \land \psi_{\text{first_nature_not_idle}_t} \land t_state = 1 \Rightarrow \pi: (t_state' = 0) \land (p_{\text{true}}\texttt{_value'} = 0) \land (p_{\text{in}}\texttt{_value'} = -1) + (1-\pi): (t_state' = 0) \land (p_{\text{false}}\texttt{_value'} = 0) \land (p_{\text{in}}\texttt{_value'} = -1)`, which probabilistically places the token in either the true output place by setting `p_true_value'=0` with probability $\pi$ or in the false output place by setting `p_false_value'=0` with probability $(1-\pi)`. It should be noted that loop constructs are managed using the identical module structure with different connectivity arrangements.
In both probabilistic outcomes, the nature transition state is simultaneously reset to idle (0) within the same update operation, preventing the module from being visited again during the current Stage 5 phase and ensuring proper phase isolation.
The completion of Stage 5 is determined by the formula $\psi_{\text{all_idle_nature}} = \bigwedge_{t \in \mathcal{t}_{\text{nature}}} t\texttt{_state} = 0$,
which verifies that all nature transitions have returned to idle state. When this condition is satisfied, combined with the guarantee that all non-nature transitions were already reset to idle during Stage 4, the manager returns to Stage 0 through `STAGE = 5 \land \psi_{\text{all_idle_nature}} \Rightarrow STAGE' = 0`, completing the full execution cycle and preparing the system for the next synchronized step.

## Impact Vector Encoding Through Reward Structures

The PRISM encoding captures the multi-dimensional impact vectors from SPIN tasks through a carefully designed reward structure system that ensures each task contribution is counted exactly once during execution. The reward assignment mechanism relies on action labeling during the crucial decision point when task transitions become enabled.

**Definition (Task Transition Action Labeling)**

For each task transition $t \in t$ with associated place $p_t$ having non-zero impact vector $Impact(p_t) \neq {\mathbf{0}}$, the PRISM encoding assigns an action label `[fire_t]` to the transition from `t_state = 0` to `t_state = 1` during Stage 0 state activation analysis. This labeling occurs precisely when the strategic decision to activate the task is made, rather than during the mechanical execution phases.

The reward structures are generated systematically for each impact dimension (as visible in [Listing 10](#lst-reward-structures)), creating separate reward streams that can be analyzed independently or in combination for multi-objective verification:

<a id="lst-reward-structures"></a>

**Listing 10 - Reward structures**

```prism
rewards "impact_0"
  [fire_task1] true : 10;
  [fire_task3] true : 5;
  [fire_task7] true : 40;
endrewards

rewards "impact_1"
  [fire_task1] true : 1;
  [fire_task3] true : 4;
  [fire_task7] true : 1;
endrewards
```

The reward assignment mechanism operates on several key principles that ensure correctness and prevent double-counting. First, action labels are triggered exclusively during Stage 0 when strategic decisions about task activation are made (as seen with `[fire_task1]` at line 2 in [Listing 10](#lst-reward-structures)), ensuring that rewards reflect actual task executions rather than mechanical state transitions. Second, the guard condition `true` (lines 2, 3, 4, 7, 8, 9) applies universally since the action label itself provides sufficient specificity about which task is being activated. Third, the reward values correspond directly to the impact vector components from the original SPIN model (e.g., values 10, 5, 40 for impact dimension 0 and values 1, 4, 1 for impact dimension 1), maintaining quantitative fidelity across the translation.

The temporal separation between reward assignment (Stage 0) and task execution (Stages 4-5) provides important semantic clarity: rewards are accumulated when the strategic decision to execute a task is made, not when the task mechanically completes. This design choice aligns with the SPIN semantics where impact accumulation occurs when tokens are placed in task places, corresponding to task activation rather than task completion.

For multi-objective strategy synthesis verification, PRISM property specifications can reference these reward structures to formulate bounded reachability queries that directly correspond to the strategy synthesis problem discussed in the paper:

<a id="lst-propertyspec"></a>

**Listing 11 - Property specification**

```prism
multi(R{"impact_0"}<=135 [C], R{"impact_1"}<=9 [C])
```

This property specification ([Listing 11](#lst-propertyspec)) verifies whether there exists a strategy that reaches a terminal state while keeping the expected cumulative reward for impact dimension 0 below 135 and impact dimension 1 below 9, providing direct cross-validation capability for our specialized strategy synthesis algorithms against the general-purpose PRISM verification framework.

The comprehensive PRISM encoding presented in this section establishes a faithful translation from SPIN
models to the PRISM probabilistic model checker framework while mimicking the synchronous
semantics and temporal behavior essential for accurate verification.

The stage-based execution protocol presented above faithfully reproduces the synchronous semantics of SPIN through two critical ordering principles. First, the precedence of temporal transitions over time passage is enforced by the stage transition logic: when transitions are enabled (Stage 0 $\rightarrow$ Stage 4/5), the system processes all active transitions before allowing time to advance, whereas time advancement (Stage 0 $\rightarrow$ Stage 3) occurs only when no transitions are immediately available for firing. This ordering ensures that the PRISM encoding captures the same causality relationships as SPIN, where enabled transitions must fire before time can progress. Second, when choice and nature transitions are simultaneously enabled, the sequential processing through Stage 4 (non-nature transitions including choices) followed by Stage 5 (nature transitions) implements the deterministic resolution order specified in SPIN semantics, where strategic choices are resolved before probabilistic nature outcomes are determined. This separation prevents information leakage from nature decisions to strategic choices and maintains the clean separation of concerns essential for strategy synthesis. Through these carefully orchestrated stage transitions and coordination formulas, the PRISM encoding preserves not only the structural properties of SPIN models but also their precise temporal and probabilistic execution semantics, enabling faithful cross-validation between our specialized synthesis algorithms and general-purpose probabilistic model checking approaches.
