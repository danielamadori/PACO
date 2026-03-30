# Encoding BPMN+CPI into PRISM

In this section, we describe the transformation from BPMN+CPI models to [PRISM](https://www.prismmodelchecker.org/), a well-established probabilistic model checker. This encoding enables validation of our approach and provides a foundation for comparative analysis. We explain the mapping between \spin\ semantics and PRISM modules, how time progression is handled, the formula-based coordination mechanisms, and strategies for managing unnecessary state space explosion. 

Before discussing the specific encoding, it is helpful to understand how the PRISM module system works. PRISM uses a state-based formalism where systems are composed of modules that interact through synchronized actions. Each module in PRISM has the following structure:

```prism
module module_name
 var1 : [min..max] init initial_value;
 var2 : [min..max] init initial_value;

 [action_name] guard_condition -> probability1:(update1) + probability2:(update2);
    ...
endmodule
```

The key mechanism in PRISM that makes it particularly suitable for encoding BPMN+CPI processes is the handling of guards and updates:

1. **Guards**: These are boolean conditions that determine when transitions are enabled. Importantly, guards can reference variables from any module in the system as well as global formulas. This allows modules to condition their behavior on the state of other modules, essential for encoding correctly activations between parent-child in \CPI.

2. **Updates**: These define how variables change when transitions occur. A crucial restriction is that each module can only update its own variables, not those of other modules. This encapsulation aligns well with the localized behavior of BPMN+CPI components.

3. **Action Synchronization**: Transitions with the same action name across multiple modules are synchronized, meaning they must occur simultaneously. This provides a powerful mechanism for coordinating behavior across the system.

4. **Probabilistic Choice**: PRISM allows transitions to have probabilistic outcomes, directly supporting the nature gateways in the BPMN+CPI formalism.

This combination of global visibility in guards with local modification in updates creates a flexible yet controlled framework for encoding complex process behaviors.


The transformation maps the hierarchical structure of BPMN+CPI processes into a flat collection of interacting PRISM modules. Each region in the BPMN+CPI process becomes a separate module with carefully crafted variables and transitions:


Each module maintains a state variable tracking progression through discrete execution phases:

- **0: EXCLUDED** - The component will not execute in the current path
- **1: OPEN** - The component is ready but has not yet started
- **2: STARTED** - The component has just begun execution
- **3: RUNNING** - The component is in progress for at least one time unit
- **4: COMPLETED** - The component has just finished execution
- **5: EXPIRED** - The component completed at least one time unit ago

For task modules, an additional step counter is maintained, tracking progress from 0 to the task duration, modeling the passage of time within activities.


The transition system is carefully designed to enforce the same execution semantics as the \spin\ formalism. A key aspect of this mapping is how the `[step]` action in PRISM directly corresponds to the empty transitions $\emptyset$ in \spin:

```prism
module task{id}
 state{id} : [0..5] init 1;
 step{id} : [0..{duration}] init 0;

 [open_to_started_task{id}] ActiveReadyPending_task{id} -> (state{id}'=2);

 [step] StepAvailable & state{id}=2 -> (step{id}'=1) & (state{id}'=3);
 [step] StepAvailable & state{id}=3 & step{id}<{duration-1} -> (step{id}'=step{id}+1);
 [step] StepAvailable & state{id}=3 & step{id}={duration-1} -> (step{id}'=step{id}+1) & (state{id}'=4);
 [step] StepAvailable & state{id}=4 -> (state{id}'=5);
 [step] StepAvailable & (state{id}=0 | state{id}=1 | state{id}=5) -> true;
endmodule
```

In this encoding, each PRISM `[step]` action maps directly to an $\emptyset$ transition in the \spin\ formalism. The $\emptyset$ transitions in \spin\ represent the passage of time when no transitions occur, and similarly, the `[step]` action in PRISM represents a global clock tick that advances time across all modules when no state-changing transitions are possible. This correspondence is critical for preserving the temporal semantics of BPMN+CPI processes.

Key aspects of this transformation include:

1. **Synchronized Time Progression**: The `[step]` action synchronizes all modules, ensuring that time advances consistently across the entire system, just as $\emptyset$ transitions do in \spin.

2. **Task Duration Modeling**: For tasks each `[step]` increments the `step{id}` counter, modeling the passage of time within the task, directly mirroring how $\emptyset$ transitions increment time in \spin.

3. **State Transition Sequencing**: The transition from STARTED (2) to RUNNING (3) to COMPLETED (4) to EXPIRED (5) through successive `[step]` actions precisely captures the time-dependent state progression in the \spin\ model.

This direct mapping between `[step]` actions and $\emptyset$ transitions ensures that the temporal and causal relationships between process elements are preserved in the transformation, validating that the specialized algorithm and the general-purpose PRISM verification operate on equivalent semantic models.


A key challenge in the encoding is coordinating the behavior of multiple modules to faithfully represent the semantics of \CPI. The PRISM formula mechanism is instrumental in this regard. A sophisticated network of formulas is used to manage the complex interdependencies between process components:

1. **ReadyPending Formula**:

```prism
formula ReadyPending_sequence{id} = state{id}=1 & (parent_condition);
```

2. **ClosingPending Formula**:

```prism
formula ClosingPending_parallel{id} = state{id}=3 & state{child1_id} >= 4 & state{child2_id} >= 4;
```

3. **StepAvailable Formula**:

```prism
formula StepAvailable = ReadyPendingCleared & ClosingPendingCleared & (StepReady_task1 | StepReady_task2 | ... );
```

4. **Prioritization Formulas**:

```prism
formula ActiveReadyPending_typeid = ReadyPending_typeid & !ReadyPending_type1id1 & !ReadyPending_type2id2 & ... ;
```

The power of this formula-based approach lies in its ability to create complex coordination patterns while maintaining the principle that each module only updates its own variables. The formulas encode the global coordination logic, while the updates remain strictly local.


The BPMN+CPI impact vectors are naturally mapped to PRISM reward structures. Each dimension of the impact vectors becomes a separate reward structure:

```prism
rewards "energy_consumption"
 [running_to_completed_{root_type}{root_id}] state{task_id}!=0 & state{task_id}!=1 : 10;
 [running_to_completed_{root_type}{root_id}] state{task_id2}!=0 & state{task_id2}!=1 : 15;
    ...
endrewards

rewards "worker_hours"
 [running_to_completed_{root_type}{root_id}] state{task_id}!=0 & state{task_id}!=1 : 2;
 [running_to_completed_{root_type}{root_id}] state{task_id2}!=0 & state{task_id2}!=1 : 4;
    ...
endrewards
```

The guard conditions `state{task_id}!=0 & state{task_id}!=1` ensure that rewards are only accumulated for tasks that were actually executed in a particular process path.

With these reward structures in place, PRISM multi-objective property specification can be leveraged to verify whether processes meet multiple impact bounds simultaneously:

```prism
multi(R{"energy_consumption"}<=135 [C], R{"worker_hours"}<=9 [C])
```

This directly corresponds to the bound verification problem from Chapter~\ref{chap:strategy}, allowing cross-validation of the specialized algorithm against PRISM general-purpose verification capabilities.


A significant challenge in transforming BPMN+CPI to PRISM is managing state space explosion, particularly for processes with parallel execution. In a naive encoding, the number of states would grow factorially with the number of concurrent activities due to all possible interleavings of their executions.

To address this challenge, several sophisticated state space reduction techniques are employed:

1. **Deterministic Activation Ordering**: When multiple modules could activate simultaneously, a deterministic ordering based on module IDs is enforced.

2. **Two-Phase Execution Model**: The execution is separated into distinct phases.

These techniques effectively implement a form of partial order reduction tailored to process models.

It should be noted that validation via PRISM transformation is performed only on acyclic processes. However, the encoding can be extended to handle loops as well as described in the paper.
