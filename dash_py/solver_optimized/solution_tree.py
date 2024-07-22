import math
import numpy as np
import solver.array_operations as array_operations
from graphviz import Source
from solver.tree_lib import CNode
from solver_optimized.states import States, ActivityState


class SolutionNode:
    def __init__(self, states: States, decisions: tuple[CNode], choices_natures: tuple, parent: 'SolutionTree', is_final_state: bool):

        self.states = states
        s, _ = self.states.str()
        self.state_id = s
        self.decisions = decisions
        self.choices_natures = choices_natures
        self.parent = parent
        self.is_final_state = is_final_state
        self.transitions: dict[tuple, SolutionTree] = {}
        self.probability = None
        self.impacts = None
        self.impacts_evaluation()
        self.cei_top_down = np.zeros(len(self.impacts), dtype=np.float64)
        self.cei_bottom_up = np.zeros(len(self.impacts), dtype=np.float64)

    def __str__(self) -> str:
        return str(self.states)

    def __hash__(self):
        return hash(str(self))

    @staticmethod
    def text_format(text: str, line_length: int):
        parts = []
        current_part = ""
        char_count = 0

        for char in text:
            current_part += char
            char_count += 1
            if char == ';' and char_count >= line_length:
                parts.append(current_part)
                current_part = ""
                char_count = 0

        if current_part:
            parts.append(current_part)

        return "\\n".join(parts)

    def dot_str(self, full: bool = True, state: bool = True, executed_time: bool = False, previous_node: States = None):
        result = str(self).replace('(', '').replace(')', '').replace(';', '_').replace(':', '_').replace('-', "neg")

        if full:
            result += ' [label=\"'

            s, d = self.states.str(previous_node)
            s = "q|s:{" + s + "}"
            d = "q|delta:{" + d + "}"

            label = ""
            if state:
                label += s
            if state and executed_time:
                label += ",\n"
            if executed_time:
                label += d

            line_length = int(1.3 * math.sqrt(len(label)))
            result += self.text_format(label, line_length) + "\"];\n"

        return result

    def add_child(self, subTree: 'SolutionTree'):
        transition = []
        for i in range(len(self.choices_natures)):
            transition.append((self.choices_natures[i], subTree.root.decisions[i], ))

        self.transitions[tuple(transition)] = subTree

    def impacts_evaluation(self):
        self.probability = 1.0
        for node, state in self.states.activityState.items():
            if (node.type == 'natural' and state > ActivityState.WAITING
                and (self.states.activityState[node.childrens[0].root] > ActivityState.WAITING
                or self.states.activityState[node.childrens[1].root] > ActivityState.WAITING)):

                p = node.probability
                if self.states.activityState[node.childrens[1].root] > 0:
                    p = 1 - p
                self.probability *= p

            if node.type == 'task':
                if self.impacts is None:
                    self.impacts = np.array(node.impact, dtype=np.float64)
                elif state > 0:
                    self.impacts += node.impact

    def dot_cei_str(self):
        return (self.dot_str(full=False) + "_impact",
                f" [label=\"(cei_td: {self.cei_top_down}, cei_bu: {self.cei_bottom_up})\", shape=rect];\n")


class SolutionTree:
    def __init__(self, root: SolutionNode):
        self.root = root

    def __str__(self) -> str:
        result = self.create_dot_graph(self.root, True, True, True)
        return result[0] + result[1]

    def save_dot(self, path, state: bool = True, executed_time: bool = False, all_states: bool = False):
        with open(path, 'w') as file:
            file.write(self.init_dot_graph(state=state, executed_time=executed_time, all_states=all_states))

    def save_pdf(self, path, state: bool = True, executed_time: bool = False, all_states: bool = False):
        Source(self.init_dot_graph(state=state, executed_time=executed_time, all_states=all_states), format='pdf').render(path, cleanup=True)

    def init_dot_graph(self, state: bool, executed_time: bool, all_states: bool):
        result = "digraph automa {\n"

        node, transition = self.create_dot_graph(self.root, state=state, executed_time=executed_time, all_states=all_states)

        result += node
        result += transition
        result += "__start0 [label=\"\", shape=none];\n"

        starting_node_ids = ""
        for n in self.root.decisions:
            starting_node_ids += str(n.id) + ";"

        starting_node_ids = starting_node_ids[:-1] + "->"
        for n in self.root.choices_natures:
            starting_node_ids += str(n.id) + ";"

        result += f"__start0 -> {self.root.dot_str(full=False)}  [label=\"{starting_node_ids[:-1]}\"];\n" + "}"
        return result

    def create_dot_graph(self, root: SolutionNode, state: bool, executed_time: bool, all_states: bool, previous_node: States = None):
        if all_states:
            previous_node = None

        nodes_id = root.dot_str(state=state, executed_time=executed_time, previous_node=previous_node)
        transitions_id = ""

        impact_id, impact_label = root.dot_cei_str()
        transitions_id += f"{root.dot_str(full=False)} -> {impact_id} [label=\"\" color=red];\n" #style=invis
        nodes_id += impact_id + impact_label

        for transition in root.transitions.keys():
            next_node = root.transitions[transition].root
            x = ""
            for t in transition:
                x += str(t[0].id) + '->' + str(t[1].id) + ';'
                #x += str(t)[1:-1].replace(',', '->') + ";"

            transitions_id += f"{root.dot_str(full=False)} -> {next_node.dot_str(full=False)} [label=\"{x[:-1]}\"];\n"

            ids = self.create_dot_graph(next_node, state=state, executed_time=executed_time, all_states=all_states, previous_node=root.states)
            nodes_id += ids[0]
            transitions_id += ids[1]

        return nodes_id, transitions_id
