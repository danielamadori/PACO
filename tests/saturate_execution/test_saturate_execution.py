import unittest
import os
from create_custom_tree import create_custom_tree
from saturate_execution.saturate_execution import saturate_execution
from saturate_execution.states import States, states_info, ActivityState
from solver.tree_lib import CTree, CNode, print_sese_custom_tree


class TestSaturateExecution(unittest.TestCase):
    def info(self, custom_tree, states, name):
        print_sese_custom_tree(custom_tree, outfile=self.directory + name + ".png")
        print(states_info(states))

    def setUp(self):
        self.directory = "output_files/saturate_execution/"
        if not os.path.exists(self.directory):
            os.makedirs(self.directory)

# Sequential Tests

    def test_sequential_tasks(self):
        custom_tree = create_custom_tree({
            "expression": "T1, T2",
            "h": 0,
            "impacts": {"T1": [11, 15], "T2": [4, 2]},
            "durations": {"T1": [0, 1], "T2": [0, 2]},
            "impacts_names": ["cost", "hours"],
            "probabilities": {}, "names": {}, "delays": {}, 'loops_prob': {}, 'loops_round': {}
        })
        states, choices_natures, branches = saturate_execution(custom_tree, States())
        self.info(custom_tree, states, "sequential_tasks")

        s1 = CTree(CNode("S1", 0, "", 0, 0, 0, 0, 0))
        t1 = CTree(CNode("T1", 0, "", 1, 0, 0, 0, 0))
        t2 = CTree(CNode("T2", 0, "", 2, 0, 0, 0, 0))

        self.assertEqual(states.activityState[s1.root], ActivityState.COMPLETED_WIHTOUT_PASSING_OVER,
                         "The root should be completed without passing over")
        self.assertEqual(states.executed_time[s1.root], 3,
                         "S1 should be executed with time 3")
        self.assertEqual(states.activityState[t1.root], ActivityState.COMPLETED,
                         "T1 should be completed")
        self.assertEqual(states.executed_time[t1.root], 1,
                         "T1 should be completed at time 1")
        self.assertEqual(states.activityState[t2.root], ActivityState.COMPLETED_WIHTOUT_PASSING_OVER,
                         "T2 should be completed without passing over")
        self.assertEqual(states.executed_time[t2.root], 2,
                         "T2 should be completed at time 2")

    def test_sequential_nature_task(self):
        custom_tree = create_custom_tree({
            "expression": "(T1 ^ [N1] T2), T3",
            "h": 0,
            "impacts": {"T1": [11, 15], "T2": [4, 2], "T3": [1, 20]},
            "durations": {"T1": [0, 1], "T2": [0, 2], "T3": [0, 2]},
            "impacts_names": ["cost", "hours"],
            "probabilities": {"N1": 0.6}, "names": {}, "delays": {}, 'loops_prob': {}, 'loops_round': {}
        })
        states, choices_natures, branches = saturate_execution(custom_tree, States())
        self.info(custom_tree, states, "sequential_nature_task")

        s1 = CTree(CNode("S1", 0, "", 0, 0, 0, 0, 0))
        n1 = CTree(CNode("N1", 0, "", 1, 0, 0, 0, 0))
        t1 = CTree(CNode("T1", 0, "", 2, 0, 0, 0, 0))
        t2 = CTree(CNode("T2", 0, "", 3, 0, 0, 0, 0))
        t3 = CTree(CNode("T3", 0, "", 4, 0, 0, 0, 0))

        self.assertEqual(states.activityState[s1.root], ActivityState.ACTIVE,
                         "The root should be active")
        self.assertEqual(states.executed_time[s1.root], 0,
                         "S1 should be executed with time 0")
        self.assertEqual(states.activityState[n1.root], ActivityState.ACTIVE,
                         "N1 should be active, with two waiting children")
        self.assertEqual(states.executed_time[n1.root], 0,
                         "N1 never increases its executed time")
        self.assertEqual(states.activityState[t1.root], ActivityState.WAITING,
                         "T1 should be waiting, (waiting nature child A)")
        self.assertEqual(states.executed_time[t1.root], 0,
                         "T1 never increases its executed time")
        self.assertEqual(states.activityState[t2.root], ActivityState.WAITING,
                         "T2 should be waiting, (waiting nature child B)")
        self.assertEqual(states.executed_time[t2.root], 0,
                         "T2 never increases its executed time")
        self.assertEqual(states.activityState[t3.root], ActivityState.WAITING,
                         "T3 should be waiting")
        self.assertEqual(states.executed_time[t3.root], 0,
                         "T3 never increases its executed time")

        self.assertEqual(len(choices_natures), 1, "There should be one nature")
        self.assertEqual(choices_natures[0], n1.root, "The nature should be N1")

        multi_decisions = []
        multi_branches = []
        for decisions, branch_states in branches.items():
            multi_decisions.append(decisions)
            multi_branches.append(branch_states)

        self.assertEqual(len(multi_decisions), 2, "There should be two decisions")
        self.assertEqual(multi_decisions[0][0], t1.root, "The first decision should be T1")
        self.assertEqual(multi_decisions[1][0], t2.root, "The second decision should be T2")

        self.assertEqual(len(multi_branches), 2, "There should be two branches")
        self.assertEqual(multi_branches[0].activityState[t1.root], ActivityState.ACTIVE, "T1 should be active")
        self.assertEqual(multi_branches[0].activityState[t2.root], ActivityState.WILL_NOT_BE_EXECUTED, "T2 will not be executed")

        self.assertEqual(multi_branches[1].activityState[t1.root], ActivityState.WILL_NOT_BE_EXECUTED, "T1 will not be executed")
        self.assertEqual(multi_branches[1].activityState[t2.root], ActivityState.ACTIVE, "T2 should be active")

    def test_sequential_task_nature(self):
        custom_tree = create_custom_tree({
            "expression": "T1, (T2 ^ [N1] T3)",
            "h": 0,
            "impacts": {"T1": [11, 15], "T2": [4, 2], "T3": [1, 20]},
            "durations": {"T1": [0, 1], "T2": [0, 2], "T3": [0, 2]},
            "impacts_names": ["cost", "hours"],
            "probabilities": {"N1": 0.6}, "names": {}, "delays": {}, 'loops_prob': {}, 'loops_round': {}
        })
        states, choices_natures, branches = saturate_execution(custom_tree, States())
        self.info(custom_tree, states, "sequential_task_nature")

        s1 = CTree(CNode("S1", 0, "", 0, 0, 0, 0, 0))
        t1 = CTree(CNode("T1", 0, "", 1, 0, 0, 0, 0))
        n1 = CTree(CNode("N1", 0, "", 2, 0, 0, 0, 0))
        t2 = CTree(CNode("T2", 0, "", 3, 0, 0, 0, 0))
        t3 = CTree(CNode("T3", 0, "", 4, 0, 0, 0, 0))

        self.assertEqual(states.activityState[s1.root], ActivityState.ACTIVE,
                         "The root should be active")
        self.assertEqual(states.executed_time[s1.root], 1,
                         "S1 should be executed with time 0")
        self.assertEqual(states.activityState[t1.root], ActivityState.COMPLETED_WIHTOUT_PASSING_OVER,
                         "T1 should be completed without passing over")
        self.assertEqual(states.executed_time[t1.root], 1,
                     "T1 should be completed without passing over at time 1")
        self.assertEqual(states.activityState[n1.root], ActivityState.ACTIVE,
                         "N1 should be active, with two waiting children")
        self.assertEqual(states.executed_time[n1.root], 0,
                         "N1 never increases its executed time")
        self.assertEqual(states.activityState[t2.root], ActivityState.WAITING,
                         "T2 should be waiting, (waiting nature child A)")
        self.assertEqual(states.executed_time[t2.root], 0,
                         "T2 never increases its executed time")
        self.assertEqual(states.activityState[t3.root], ActivityState.WAITING,
                         "T3 should be waiting, (waiting nature child B)")
        self.assertEqual(states.executed_time[t3.root], 0,
                         "T3 never increases its executed time")

        self.assertEqual(len(choices_natures), 1, "There should be one nature")
        self.assertEqual(choices_natures[0], n1.root, "The nature should be N1")

        multi_decisions = []
        multi_branches = []
        for decisions, branch_states in branches.items():
            multi_decisions.append(decisions)
            multi_branches.append(branch_states)

        self.assertEqual(len(multi_decisions), 2, "There should be two decisions")
        self.assertEqual(multi_decisions[0][0], t2.root, "The first decision should be T2")
        self.assertEqual(multi_decisions[1][0], t3.root, "The second decision should be T3")

        self.assertEqual(len(multi_branches), 2, "There should be two branches")
        self.assertEqual(multi_branches[0].activityState[t2.root], ActivityState.ACTIVE, "T2 should be active")
        self.assertEqual(multi_branches[0].activityState[t3.root], ActivityState.WILL_NOT_BE_EXECUTED, "T3 will not be executed")

        self.assertEqual(multi_branches[1].activityState[t2.root], ActivityState.WILL_NOT_BE_EXECUTED, "T2 will not be executed")
        self.assertEqual(multi_branches[1].activityState[t3.root], ActivityState.ACTIVE, "T3 should be active")

    def test_sequential_choice_task(self):
        custom_tree = create_custom_tree({
            "expression": "(T1 / [C1] T2), T3",
            "h": 0,
            "impacts": {"T1": [11, 15], "T2": [4, 2], "T3": [1, 20]},
            "durations": {"T1": [0, 1], "T2": [0, 2], "T3": [0, 2]},
            "impacts_names": ["cost", "hours"],
            "probabilities": {}, "names": {'C1':'C1'}, "delays": {"C1": 1}, 'loops_prob': {}, 'loops_round': {}
        })
        states, choices_natures, branches = saturate_execution(custom_tree, States())
        self.info(custom_tree, states, "sequential_choice_task")

        s1 = CTree(CNode("S1", 0, "", 0, 0, 0, 0, 0))
        c1 = CTree(CNode("C1", 0, "", 1, 0, 0, 0, 0))
        t1 = CTree(CNode("T1", 0, "", 2, 0, 0, 0, 0))
        t2 = CTree(CNode("T2", 0, "", 3, 0, 0, 0, 0))
        t3 = CTree(CNode("T3", 0, "", 4, 0, 0, 0, 0))

        self.assertEqual(states.activityState[s1.root], ActivityState.ACTIVE,
                         "The root should be active")
        self.assertEqual(states.executed_time[s1.root], 1,
                         "S1 should be executed with time 1")
        self.assertEqual(states.activityState[c1.root], ActivityState.ACTIVE,
                         "C1 should be active, with two waiting children")
        self.assertEqual(states.executed_time[c1.root], 1,
                         "C1 should be executed with time 1")
        self.assertEqual(states.activityState[t1.root], ActivityState.WAITING,
                         "T1 should be waiting, (waiting nature child A)")
        self.assertEqual(states.executed_time[t1.root], 0,
                         "T1 never increases its executed time")
        self.assertEqual(states.activityState[t2.root], ActivityState.WAITING,
                         "T2 should be waiting, (waiting nature child B)")
        self.assertEqual(states.executed_time[t2.root], 0,
                         "T2 never increases its executed time")
        self.assertEqual(states.activityState[t3.root], ActivityState.WAITING,
                         "T3 should be waiting")
        self.assertEqual(states.executed_time[t3.root], 0,
                         "T3 never increases its executed time")

        self.assertEqual(len(choices_natures), 1, "There should be one choice")
        self.assertEqual(choices_natures[0], c1.root, "The choice should be C1")

        multi_decisions = []
        multi_branches = []
        for decisions, branch_states in branches.items():
            multi_decisions.append(decisions)
            multi_branches.append(branch_states)

        self.assertEqual(len(multi_decisions), 2, "There should be two decisions")
        self.assertEqual(multi_decisions[0][0], t1.root, "The first decision should be T1")
        self.assertEqual(multi_decisions[1][0], t2.root, "The second decision should be T2")

        self.assertEqual(len(multi_branches), 2, "There should be two branches")
        self.assertEqual(multi_branches[0].activityState[t1.root], ActivityState.ACTIVE, "T1 should be active")
        self.assertEqual(multi_branches[0].activityState[t2.root], ActivityState.WILL_NOT_BE_EXECUTED, "T2 will not be executed")

        self.assertEqual(multi_branches[1].activityState[t1.root], ActivityState.WILL_NOT_BE_EXECUTED, "T1 will not be executed")
        self.assertEqual(multi_branches[1].activityState[t2.root], ActivityState.ACTIVE, "T2 should be active")

    def test_sequential_task_choice(self):
        custom_tree = create_custom_tree({
            "expression": "T1, (T2 / [C1] T3)",
            "h": 0,
            "impacts": {"T1": [11, 15], "T2": [4, 2], "T3": [1, 20]},
            "durations": {"T1": [0, 1], "T2": [0, 2], "T3": [0, 2]},
            "impacts_names": ["cost", "hours"],
            "probabilities": {}, "names": {'C1':'C1'}, "delays": {"C1": 0}, 'loops_prob': {}, 'loops_round': {}
        })
        states, choices_natures, branches = saturate_execution(custom_tree, States())

        self.info(custom_tree, states, "sequential_task_choice")

        s1 = CTree(CNode("S1", 0, "", 0, 0, 0, 0, 0))
        t1 = CTree(CNode("T1", 0, "", 1, 0, 0, 0, 0))
        c1 = CTree(CNode("C1", 0, "", 2, 0, 0, 0, 0))
        t2 = CTree(CNode("T2", 0, "", 3, 0, 0, 0, 0))
        t3 = CTree(CNode("T3", 0, "", 4, 0, 0, 0, 0))

        self.assertEqual(states.activityState[s1.root], ActivityState.ACTIVE,
                         "The root should be active")
        self.assertEqual(states.executed_time[s1.root], 1,
                         "S1 should be executed with time 0")
        self.assertEqual(states.activityState[t1.root], ActivityState.COMPLETED_WIHTOUT_PASSING_OVER,
                         "T1 should be completed without passing over")
        self.assertEqual(states.executed_time[t1.root], 1,
                         "T1 should be completed without passing over at time 1")
        self.assertEqual(states.activityState[c1.root], ActivityState.ACTIVE,
                         "C1 should be active, with two waiting children")
        self.assertEqual(states.executed_time[c1.root], 0,
                         "C1 never increases its executed time")
        self.assertEqual(states.activityState[t2.root], ActivityState.WAITING,
                         "T2 should be waiting, (waiting nature child A)")
        self.assertEqual(states.executed_time[t2.root], 0,
                         "T2 never increases its executed time")
        self.assertEqual(states.activityState[t3.root], ActivityState.WAITING,
                         "T3 should be waiting, (waiting nature child B)")
        self.assertEqual(states.executed_time[t3.root], 0,
                         "T3 never increases its executed time")

        self.assertEqual(len(choices_natures), 1, "There should be one choice")
        self.assertEqual(choices_natures[0], c1.root, "The choice should be C1")

        multi_decisions = []
        multi_branches = []
        for decisions, branch_states in branches.items():
            multi_decisions.append(decisions)
            multi_branches.append(branch_states)

        self.assertEqual(len(multi_decisions), 2, "There should be two decisions")
        self.assertEqual(multi_decisions[0][0], t2.root, "The first decision should be T2")
        self.assertEqual(multi_decisions[1][0], t3.root, "The second decision should be T3")

        self.assertEqual(len(multi_branches), 2, "There should be two branches")
        self.assertEqual(multi_branches[0].activityState[t2.root], ActivityState.ACTIVE, "T2 should be active")
        self.assertEqual(multi_branches[0].activityState[t3.root], ActivityState.WILL_NOT_BE_EXECUTED, "T3 will not be executed")

        self.assertEqual(multi_branches[1].activityState[t2.root], ActivityState.WILL_NOT_BE_EXECUTED, "T2 will not be executed")
        self.assertEqual(multi_branches[1].activityState[t3.root], ActivityState.ACTIVE, "T3 should be active")

# Sequential Sequential Tests

    def test_sequential_sequential_nature(self):
        custom_tree = create_custom_tree({
            "expression": "T1, T2,(T3 ^ [N1] T4)",
            "h": 0,
            "impacts": {"T1": [1, 2], "T2": [3, 4], "T3": [5, 6], "T4": [7, 8]},
            "durations": {"T1": [0, 0], "T2": [0, 1], "T3": [0, 2], "T4": [0, 3]},
            "impacts_names": ["a", "b"],
            "probabilities": {"N1": 0.6}, "names": {}, "delays": {}, 'loops_prob': {}, 'loops_round': {}
        })
        states, choices_natures, branches = saturate_execution(custom_tree, States())
        self.info(custom_tree, states, "sequential_sequential_nature")

        s1 = CTree(CNode("S1", 0, "", 0, 0, 0, 0, 0))
        t1 = CTree(CNode("T1", 0, "", 2, 0, 0, 0, 0))
        t2 = CTree(CNode("T2", 0, "", 3, 0, 0, 0, 0))
        n1 = CTree(CNode("N1", 0, "", 4, 0, 0, 0, 0))
        t3 = CTree(CNode("T3", 0, "", 5, 0, 0, 0, 0))
        t4 = CTree(CNode("T4", 0, "", 6, 0, 0, 0, 0))

        self.assertEqual(states.activityState[s1.root], ActivityState.ACTIVE, "The root should be active")
        self.assertEqual(states.executed_time[s1.root], 1, "S1 should be executed with time 1")

        self.assertEqual(states.activityState[t1.root], ActivityState.COMPLETED, "T1 should be completed")
        self.assertEqual(states.executed_time[t1.root], 0, "T1 should be completed at time 0")
        self.assertEqual(states.activityState[t2.root], ActivityState.COMPLETED_WIHTOUT_PASSING_OVER, "T2 should be completed without passing over")
        self.assertEqual(states.executed_time[t2.root], 1, "T2 should be completed at time 1")

        self.assertEqual(states.activityState[n1.root], ActivityState.ACTIVE, "N1 should be active, with two waiting children")
        self.assertEqual(states.executed_time[n1.root], 0, "N1 never increases its executed time")
        self.assertEqual(states.activityState[t3.root], ActivityState.WAITING, "T3 should be waiting")
        self.assertEqual(states.activityState[t4.root], ActivityState.WAITING, "T4 should be waiting")
        self.assertEqual(states.executed_time[t3.root], 0, "T3 never increases its executed time")
        self.assertEqual(states.executed_time[t4.root], 0, "T4 never increases its executed time")

        self.assertEqual(len(choices_natures), 1, "There should be one nature")
        self.assertEqual(choices_natures[0], n1.root, "The nature should be N1")

        multi_decisions = []
        multi_branches = []
        for decisions, branch_states in branches.items():
            multi_decisions.append(decisions)
            multi_branches.append(branch_states)

        self.assertEqual(len(multi_decisions), 2, "There should be two decisions")
        self.assertEqual(multi_decisions[0][0], t3.root, "The first decision should be T3")
        self.assertEqual(multi_decisions[1][0], t4.root, "The second decision should be T4")

        self.assertEqual(len(multi_branches), 2, "There should be two branches")
        self.assertEqual(multi_branches[0].activityState[t3.root], ActivityState.ACTIVE, "T3 should be active")
        self.assertEqual(multi_branches[0].activityState[t4.root], ActivityState.WILL_NOT_BE_EXECUTED, "T4 should be waiting")

        self.assertEqual(multi_branches[1].activityState[t3.root], ActivityState.WILL_NOT_BE_EXECUTED, "T3 should be waiting")
        self.assertEqual(multi_branches[1].activityState[t4.root], ActivityState.ACTIVE, "T4 should be active")

    def test_sequential_sequential_choice(self):
        custom_tree = create_custom_tree({
            "expression": "T1, T2,(T3 / [C1] T4)",
            "h": 0,
            "impacts": {"T1": [1, 2], "T2": [3, 4], "T3": [5, 6], "T4": [7, 8]},
            "durations": {"T1": [0, 0], "T2": [0, 1], "T3": [0, 2], "T4": [0, 3]},
            "impacts_names": ["a", "b"],
            "probabilities": {}, "names": {'C1':'C1'}, "delays": {"C1": 0}, 'loops_prob': {}, 'loops_round': {}
        })
        states, choices_natures, branches = saturate_execution(custom_tree, States())
        self.info(custom_tree, states, "sequential_sequential_choice")

        s1 = CTree(CNode("S1", 0, "", 0, 0, 0, 0, 0))
        t1 = CTree(CNode("T1", 0, "", 2, 0, 0, 0, 0))
        t2 = CTree(CNode("T2", 0, "", 3, 0, 0, 0, 0))
        c1 = CTree(CNode("C1", 0, "", 4, 0, 0, 0, 0))
        t3 = CTree(CNode("T3", 0, "", 5, 0, 0, 0, 0))
        t4 = CTree(CNode("T4", 0, "", 6, 0, 0, 0, 0))

        self.assertEqual(states.activityState[s1.root], ActivityState.ACTIVE, "The root should be active")
        self.assertEqual(states.executed_time[s1.root], 1, "S1 should be executed with time 1")

        self.assertEqual(states.activityState[t1.root], ActivityState.COMPLETED, "T1 should be completed")
        self.assertEqual(states.executed_time[t1.root], 0, "T1 should be completed at time 0")
        self.assertEqual(states.activityState[t2.root], ActivityState.COMPLETED_WIHTOUT_PASSING_OVER, "T2 should be completed without passing over")
        self.assertEqual(states.executed_time[t2.root], 1, "T2 should be completed at time 1")
        self.assertEqual(states.activityState[c1.root], ActivityState.ACTIVE, "C1 should be active, with two waiting children")
        self.assertEqual(states.executed_time[c1.root], 0, "C1 not increases its executed time")
        self.assertEqual(states.activityState[t3.root], ActivityState.WAITING, "T3 should be waiting")
        self.assertEqual(states.activityState[t4.root], ActivityState.WAITING, "T4 should be waiting")
        self.assertEqual(states.executed_time[t3.root], 0, "T3 never increases its executed time")
        self.assertEqual(states.executed_time[t4.root], 0, "T4 never increases its executed time")

        self.assertEqual(len(choices_natures), 1, "There should be one choice")
        self.assertEqual(choices_natures[0], c1.root, "The nature should be N1")

        multi_decisions = []
        multi_branches = []
        for decisions, branch_states in branches.items():
            multi_decisions.append(decisions)
            multi_branches.append(branch_states)

        self.assertEqual(len(multi_decisions), 2, "There should be two decisions")
        self.assertEqual(multi_decisions[0][0], t3.root, "The first decision should be T3")
        self.assertEqual(multi_decisions[1][0], t4.root, "The second decision should be T4")

        self.assertEqual(len(multi_branches), 2, "There should be two branches")
        self.assertEqual(multi_branches[0].activityState[t3.root], ActivityState.ACTIVE, "T3 should be active")
        self.assertEqual(multi_branches[0].activityState[t4.root], ActivityState.WILL_NOT_BE_EXECUTED, "T4 should be waiting")

        self.assertEqual(multi_branches[1].activityState[t3.root], ActivityState.WILL_NOT_BE_EXECUTED, "T3 should be waiting")
        self.assertEqual(multi_branches[1].activityState[t4.root], ActivityState.ACTIVE, "T4 should be active")

        # Considering choice delay
        custom_tree = create_custom_tree({
            "expression": "T1, T2,(T3 / [C1] T4)",
            "h": 0,
            "impacts": {"T1": [1, 2], "T2": [3, 4], "T3": [5, 6], "T4": [7, 8]},
            "durations": {"T1": [0, 0], "T2": [0, 1], "T3": [0, 2], "T4": [0, 3]},
            "impacts_names": ["a", "b"],
            "probabilities": {}, "names": {'C1':'C1'}, "delays": {"C1": 1}, 'loops_prob': {}, 'loops_round': {}
        })
        states, choices_natures, branches = saturate_execution(custom_tree, States())
        self.info(custom_tree, states, "sequential_sequential_choice_delay")

        self.assertEqual(states.activityState[s1.root], ActivityState.ACTIVE, "The root should be active")
        self.assertEqual(states.executed_time[s1.root], 2, "S1 should be executed with time 2")

        self.assertEqual(states.activityState[t1.root], ActivityState.COMPLETED, "T1 should be completed")
        self.assertEqual(states.executed_time[t1.root], 0, "T1 should be completed at time 0")

        self.assertEqual(states.activityState[t2.root], ActivityState.COMPLETED, "T2 should be completed because of the choice delay")
        self.assertEqual(states.executed_time[t2.root], 1, "T2 should be completed at time 1")

        self.assertEqual(states.activityState[c1.root], ActivityState.ACTIVE, "C1 should be active, with two waiting children")
        self.assertEqual(states.executed_time[c1.root], 1, "C1 increases its executed time to 1")
        self.assertEqual(states.activityState[t3.root], ActivityState.WAITING, "T3 should be waiting")
        self.assertEqual(states.activityState[t4.root], ActivityState.WAITING, "T4 should be waiting")
        self.assertEqual(states.executed_time[t3.root], 0, "T3 never increases its executed time")
        self.assertEqual(states.executed_time[t4.root], 0, "T4 never increases its executed time")

        self.assertEqual(len(choices_natures), 1, "There should be one choice")
        self.assertEqual(choices_natures[0], c1.root, "The nature should be N1")

        multi_decisions = []
        multi_branches = []
        for decisions, branch_states in branches.items():
            multi_decisions.append(decisions)
            multi_branches.append(branch_states)

        self.assertEqual(len(multi_decisions), 2, "There should be two decisions")
        self.assertEqual(multi_decisions[0][0], t3.root, "The first decision should be T3")
        self.assertEqual(multi_decisions[1][0], t4.root, "The second decision should be T4")

        self.assertEqual(len(multi_branches), 2, "There should be two branches")
        self.assertEqual(multi_branches[0].activityState[t3.root], ActivityState.ACTIVE, "T3 should be active")
        self.assertEqual(multi_branches[0].activityState[t4.root], ActivityState.WILL_NOT_BE_EXECUTED, "T4 should be waiting")

        self.assertEqual(multi_branches[1].activityState[t3.root], ActivityState.WILL_NOT_BE_EXECUTED, "T3 should be waiting")
        self.assertEqual(multi_branches[1].activityState[t4.root], ActivityState.ACTIVE, "T4 should be active")

# Parallel Tests

    def test_parallel_tasks(self):
        custom_tree = create_custom_tree({
            "expression": "T1 || T2",
            "h": 0,
            "impacts": {"T1": [11, 15], "T2": [4, 2]},
            "durations": {"T1": [0, 1], "T2": [0, 1]},
            "impacts_names": ["cost", "hours"],
            "probabilities": {}, "names": {}, "delays": {}, 'loops_prob': {}, 'loops_round': {}
        })
        states, choices_natures, branches = saturate_execution(custom_tree, States())
        self.info(custom_tree, states, "parallel_task1_eq_task2")

        p1 = CTree(CNode("P1", 0, "", 0, 0, 0, 0, 0))
        t1 = CTree(CNode("T1", 0, "", 1, 0, 0, 0, 0))
        t2 = CTree(CNode("T2", 0, "", 2, 0, 0, 0, 0))

        self.assertEqual(states.activityState[p1.root], ActivityState.COMPLETED_WIHTOUT_PASSING_OVER,
                         "The root should be completed without passing over")
        self.assertEqual(states.executed_time[p1.root], 1,
                         "P1 should be executed with time 1")
        self.assertEqual(states.activityState[t1.root], ActivityState.COMPLETED_WIHTOUT_PASSING_OVER,
                         "T1 should be completed without passing over")
        self.assertEqual(states.executed_time[t1.root], 1,
                         "T1 should be completed at time 1")
        self.assertEqual(states.activityState[t2.root], ActivityState.COMPLETED_WIHTOUT_PASSING_OVER,
                         "T2 should be completed without passing over")
        self.assertEqual(states.executed_time[t2.root], 1,
                         "T2 should be completed at time 1")


        custom_tree = create_custom_tree({
            "expression": "T1 || T2",
            "h": 0,
            "impacts": {"T1": [11, 15], "T2": [4, 2]},
            "durations": {"T1": [0, 1], "T2": [0, 2]},
            "impacts_names": ["cost", "hours"],
            "probabilities": {}, "names": {}, "delays": {}, 'loops_prob': {}, 'loops_round': {}
        })
        states, choices_natures, branches = saturate_execution(custom_tree, States())
        self.info(custom_tree, states, "parallel_task1_lt_task2")

        p1 = CTree(CNode("P1", 0, "", 0, 0, 0, 0, 0))
        t1 = CTree(CNode("T1", 0, "", 1, 0, 0, 0, 0))
        t2 = CTree(CNode("T2", 0, "", 2, 0, 0, 0, 0))

        self.assertEqual(states.activityState[p1.root], ActivityState.COMPLETED_WIHTOUT_PASSING_OVER,
                         "The root should be completed without passing over")
        self.assertEqual(states.executed_time[p1.root], 2,
                         "P1 should be executed with time 2")
        self.assertEqual(states.activityState[t1.root], ActivityState.COMPLETED,
                         "T1 should be completed")
        self.assertEqual(states.executed_time[t1.root], 1,
                         "T1 should be completed at time 1")
        self.assertEqual(states.activityState[t2.root], ActivityState.COMPLETED_WIHTOUT_PASSING_OVER,
                         "T2 should be completed without passing over")
        self.assertEqual(states.executed_time[t2.root], 2,
                         "T2 should be completed at time 2")

        custom_tree = create_custom_tree({
            "expression": "T1 || T2",
            "h": 0,
            "impacts": {"T1": [11, 15], "T2": [4, 2]},
            "durations": {"T1": [0, 2], "T2": [0, 1]},
            "impacts_names": ["cost", "hours"],
            "probabilities": {}, "names": {}, "delays": {}, 'loops_prob': {}, 'loops_round': {}
        })
        states, choices_natures, branches = saturate_execution(custom_tree, States())
        self.info(custom_tree, states, "parallel_task1_gt_task2")

        p1 = CTree(CNode("P1", 0, "", 0, 0, 0, 0, 0))
        t1 = CTree(CNode("T1", 0, "", 1, 0, 0, 0, 0))
        t2 = CTree(CNode("T2", 0, "", 2, 0, 0, 0, 0))

        self.assertEqual(states.activityState[p1.root], ActivityState.COMPLETED_WIHTOUT_PASSING_OVER,
                         "The root should be completed without passing over")
        self.assertEqual(states.executed_time[p1.root], 2,
                         "P1 should be executed with time 2")
        self.assertEqual(states.activityState[t1.root], ActivityState.COMPLETED_WIHTOUT_PASSING_OVER,
                         "T1 should be completed without passing over")
        self.assertEqual(states.executed_time[t1.root], 2,
                         "T1 should be completed at time 2")
        self.assertEqual(states.activityState[t2.root], ActivityState.COMPLETED,
                         "T2 should be completed")
        self.assertEqual(states.executed_time[t2.root], 1,
                         "T2 should be completed at time 1")

    # TODO parallel_choice_tasks, parallel_nature_tasks (=, <, >)

    # TODO parallel_natures (=)

    # TODO parallel_choices (=, <, >)

    # TODO parallel_nature_choice (=)

    # TODO parallel_parallel choice_nature_nature (=)



    #Old
    def test_parallel_sequential_nature(self):
        # 3 test, parallel: T1 = T2, T1 < T2, T1 > T2

        # T1 T2 ended and N1 start at the same time
        custom_tree = create_custom_tree({
            "expression": "T1 || T2,(T3 ^ [N1] T4)",
            "h": 0,
            "impacts": {"T1": [1, 2], "T2": [3, 4], "T3": [5, 6], "T4": [7, 8]},
            "durations": {"T1": [0, 1], "T2": [0, 1], "T3": [0, 2], "T4": [0, 3]},
            "impacts_names": ["a", "b"],
            "probabilities": {"N1": 0.6}, "names": {}, "delays": {}, 'loops_prob': {}, 'loops_round': {}
        })
        states, choices_natures, branches = saturate_execution(custom_tree, States())
        self.info(custom_tree, states, "parallel_sequential_nature")

        p1 = CTree(CNode("P1", 0, "", 0, 0, 0, 0, 0))
        t1 = CTree(CNode("T1", 0, "", 1, 0, 0, 0, 0))
        t2 = CTree(CNode("T2", 0, "", 3, 0, 0, 0, 0))
        n1 = CTree(CNode("N1", 0, "", 4, 0, 0, 0, 0))
        t3 = CTree(CNode("T3", 0, "", 5, 0, 0, 0, 0))
        t4 = CTree(CNode("T4", 0, "", 6, 0, 0, 0, 0))

        self.assertEqual(states.activityState[p1.root], ActivityState.ACTIVE, "The root should be active")
        self.assertEqual(states.executed_time[p1.root], 1, "P1 should be executed with time 1")

        self.assertEqual(states.activityState[t1.root], ActivityState.COMPLETED_WIHTOUT_PASSING_OVER, "T1 should be completed without passing over")
        self.assertEqual(states.executed_time[t1.root], 1, "T1 should be completed at time 0")

        self.assertEqual(states.activityState[t2.root], ActivityState.COMPLETED_WIHTOUT_PASSING_OVER, "T2 should be completed without passing over")
        self.assertEqual(states.executed_time[t2.root], 1, "T2 should be completed at time 1")

        self.assertEqual(states.activityState[n1.root], ActivityState.ACTIVE, "N1 should be active, with two waiting children")
        self.assertEqual(states.executed_time[n1.root], 0, "N1 never increases its executed time")
        self.assertEqual(states.activityState[t3.root], ActivityState.WAITING, "T3 should be waiting")
        self.assertEqual(states.activityState[t4.root], ActivityState.WAITING, "T4 should be waiting")
        self.assertEqual(states.executed_time[t3.root], 0, "T3 never increases its executed time")
        self.assertEqual(states.executed_time[t4.root], 0, "T4 never increases its executed time")

        self.assertEqual(len(choices_natures), 1, "There should be one nature")
        self.assertEqual(choices_natures[0], n1.root, "The nature should be N1")

        multi_decisions = []
        multi_branches = []
        for decisions, branch_states in branches.items():
            multi_decisions.append(decisions)
            multi_branches.append(branch_states)

        self.assertEqual(len(multi_decisions), 2, "There should be two decisions")
        self.assertEqual(multi_decisions[0][0], t3.root, "The first decision should be T3")
        self.assertEqual(multi_decisions[1][0], t4.root, "The second decision should be T4")

        self.assertEqual(len(multi_branches), 2, "There should be two branches")
        self.assertEqual(multi_branches[0].activityState[t3.root], ActivityState.ACTIVE, "T3 should be active")
        self.assertEqual(multi_branches[0].activityState[t4.root], ActivityState.WILL_NOT_BE_EXECUTED, "T4 should be waiting")

        self.assertEqual(multi_branches[1].activityState[t3.root], ActivityState.WILL_NOT_BE_EXECUTED, "T3 should be waiting")
        self.assertEqual(multi_branches[1].activityState[t4.root], ActivityState.ACTIVE, "T4 should be active")

        # T1 ended first
        custom_tree = create_custom_tree({
            "expression": "T1 || T2,(T3 ^ [N1] T4)",
            "h": 0,
            "impacts": {"T1": [1, 2], "T2": [3, 4], "T3": [5, 6], "T4": [7, 8]},
            "durations": {"T1": [0, 1], "T2": [0, 2], "T3": [0, 2], "T4": [0, 3]},
            "impacts_names": ["a", "b"],
            "probabilities": {"N1": 0.6}, "names": {}, "delays": {}, 'loops_prob': {}, 'loops_round': {}
        })
        states, choices_natures, branches = saturate_execution(custom_tree, States())
        self.info(custom_tree, states, "parallel_sequential_nature")

        self.assertEqual(states.activityState[p1.root], ActivityState.ACTIVE, "The root should be active")
        self.assertEqual(states.executed_time[p1.root], 2, "P1 should be executed with time 2")

        self.assertEqual(states.activityState[t1.root], ActivityState.COMPLETED, "T1 should be completed")
        self.assertEqual(states.executed_time[t1.root], 1, "T1 should be completed at time 0")

        self.assertEqual(states.activityState[t2.root], ActivityState.COMPLETED_WIHTOUT_PASSING_OVER, "T2 should be completed without passing over")
        self.assertEqual(states.executed_time[t2.root], 2, "T2 should be completed at time 1")

        self.assertEqual(states.activityState[n1.root], ActivityState.ACTIVE, "N1 should be active, with two waiting children")
        self.assertEqual(states.executed_time[n1.root], 0, "N1 never increases its executed time")
        self.assertEqual(states.activityState[t3.root], ActivityState.WAITING, "T3 should be waiting")
        self.assertEqual(states.activityState[t4.root], ActivityState.WAITING, "T4 should be waiting")
        self.assertEqual(states.executed_time[t3.root], 0, "T3 never increases its executed time")
        self.assertEqual(states.executed_time[t4.root], 0, "T4 never increases its executed time")

        self.assertEqual(len(choices_natures), 1, "There should be one nature")
        self.assertEqual(choices_natures[0], n1.root, "The nature should be N1")

        multi_decisions = []
        multi_branches = []
        for decisions, branch_states in branches.items():
            multi_decisions.append(decisions)
            multi_branches.append(branch_states)

        self.assertEqual(len(multi_decisions), 2, "There should be two decisions")
        self.assertEqual(multi_decisions[0][0], t3.root, "The first decision should be T3")
        self.assertEqual(multi_decisions[1][0], t4.root, "The second decision should be T4")

        self.assertEqual(len(multi_branches), 2, "There should be two branches")
        self.assertEqual(multi_branches[0].activityState[t3.root], ActivityState.ACTIVE, "T3 should be active")
        self.assertEqual(multi_branches[0].activityState[t4.root], ActivityState.WILL_NOT_BE_EXECUTED, "T4 should be waiting")

        self.assertEqual(multi_branches[1].activityState[t3.root], ActivityState.WILL_NOT_BE_EXECUTED, "T3 should be waiting")
        self.assertEqual(multi_branches[1].activityState[t4.root], ActivityState.ACTIVE, "T4 should be active")

        # T2 ended first
        custom_tree = create_custom_tree({
            "expression": "T1 || T2,(T3 ^ [N1] T4)",
            "h": 0,
            "impacts": {"T1": [1, 2], "T2": [3, 4], "T3": [5, 6], "T4": [7, 8]},
            "durations": {"T1": [0, 2], "T2": [0, 1], "T3": [0, 2], "T4": [0, 3]},
            "impacts_names": ["a", "b"],
            "probabilities": {"N1": 0.6}, "names": {}, "delays": {}, 'loops_prob': {}, 'loops_round': {}
        })
        states, choices_natures, branches = saturate_execution(custom_tree, States())
        self.info(custom_tree, states, "parallel_sequential_nature")

        self.assertEqual(states.activityState[p1.root], ActivityState.ACTIVE, "The root should be active")
        self.assertEqual(states.executed_time[p1.root], 1, "P1 should be executed with time 1")

        self.assertEqual(states.activityState[t1.root], ActivityState.ACTIVE, "T1 should be active")
        self.assertEqual(states.executed_time[t1.root], 1, "T1 should be completed at time 0")

        self.assertEqual(states.activityState[t2.root], ActivityState.COMPLETED_WIHTOUT_PASSING_OVER, "T2 should be completed without passing over")
        self.assertEqual(states.executed_time[t2.root], 1, "T2 should be completed at time 1")

        self.assertEqual(states.activityState[n1.root], ActivityState.ACTIVE, "N1 should be active, with two waiting children")
        self.assertEqual(states.executed_time[n1.root], 0, "N1 never increases its executed time")
        self.assertEqual(states.activityState[t3.root], ActivityState.WAITING, "T3 should be waiting")
        self.assertEqual(states.activityState[t4.root], ActivityState.WAITING, "T4 should be waiting")
        self.assertEqual(states.executed_time[t3.root], 0, "T3 never increases its executed time")
        self.assertEqual(states.executed_time[t4.root], 0, "T4 never increases its executed time")

        self.assertEqual(len(choices_natures), 1, "There should be one nature")
        self.assertEqual(choices_natures[0], n1.root, "The nature should be N1")

        multi_decisions = []
        multi_branches = []
        for decisions, branch_states in branches.items():
            multi_decisions.append(decisions)
            multi_branches.append(branch_states)

        self.assertEqual(len(multi_decisions), 2, "There should be two decisions")
        self.assertEqual(multi_decisions[0][0], t3.root, "The first decision should be T3")
        self.assertEqual(multi_decisions[1][0], t4.root, "The second decision should be T4")

        self.assertEqual(len(multi_branches), 2, "There should be two branches")
        self.assertEqual(multi_branches[0].activityState[t3.root], ActivityState.ACTIVE, "T3 should be active")
        self.assertEqual(multi_branches[0].activityState[t4.root], ActivityState.WILL_NOT_BE_EXECUTED, "T4 should be waiting")

        self.assertEqual(multi_branches[1].activityState[t3.root], ActivityState.WILL_NOT_BE_EXECUTED, "T3 should be waiting")
        self.assertEqual(multi_branches[1].activityState[t4.root], ActivityState.ACTIVE, "T4 should be active")


if __name__ == '__main__':
    unittest.main()
