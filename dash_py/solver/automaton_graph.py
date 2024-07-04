from itertools import zip_longest

import solver.array_operations as array_operations
from solver.view_points import VPChecker
from graphviz import Source
from solver_optimized.states import States


class ANode:
    def __init__(self, states: States, process_ids: list = [], is_final_state: bool = False, is_square_node: bool = False, generator: str = None) -> None:
        self.states = states
        s, _ = self.states.str()
        self.state_id = s
        self.process_ids = str(process_ids)
        self.is_final_state = is_final_state
        self.is_square_node = is_square_node
        self.generator = generator
        self.transitions: dict[str, AGraph] = {}

        self.impacts = []
        if is_final_state:
            self.impacts = self.impacts_evaluation()

    def __str__(self) -> str:
        return self.state_id

    def dot_str(self, full=True, state=True, executed_time=False, previous_node:States=None):
        result = str(self).replace('(', '').replace(')', '').replace(';', '_').replace(':', '_').replace('-', "neg")
        if full:
            result += ' [label=\"'

            s, d = self.states.str(previous_node)

            if state:
                result += "q|s:{" + s
            if state and executed_time:
                result += "},\n"
            if executed_time:
                result += "q|delta:{" + d

            result += "}\"];\n"

        return result

    def add_transition(self, children_graph: 'AGraph'):
        #t_key = self.process_ids + ":" + children_graph.init_node.process_ids
        t_key = children_graph.init_node.process_ids
        self.transitions[t_key] = children_graph

    def remove_transition(self, children_graph: 'AGraph'):
        #t_key = self.process_ids + ":" + children_graph.init_node.process_ids
        t_key = children_graph.init_node.process_ids
        self.transitions.pop(t_key)

    def impacts_evaluation(self):
        impacts = []
        for node, state in self.states.activityState.items():
            if node.type == 'task' and state > 0:
                impacts = [x + y for x, y in zip_longest(impacts, node.impact, fillvalue=0)]

        return impacts




class AGraph:
    def __init__(self, init_node: ANode) -> None:
        self.init_node = init_node

    def __str__(self) -> str:
        result = self.create_dot_graph(self.init_node, True, True)
        return result[0] + result[1]

    def save_dot(self, path, state: bool = True, executed_time: bool = False):
        with open(path, 'w') as file:
            file.write(self.init_dot_graph(state=state, executed_time=executed_time))

    def save_pdf(self, path, state: bool = True, executed_time: bool = False):
        Source(self.init_dot_graph(state=state, executed_time=executed_time), format='pdf').render(path, cleanup=True)

    def init_dot_graph(self, state: bool, executed_time: bool):
        result = "digraph automa {\n"

        node, transition = self.create_dot_graph(self.init_node, state=state, executed_time=executed_time)

        result += node
        result += transition
        result += "__start0 [label=\"\", shape=none];\n"

        result += f"__start0 -> {self.init_node.dot_str(full=False)}  [label=\"{self.init_node.process_ids[:-1]}\"];\n" + "}"
        return result

    def create_dot_graph(self, root: ANode, state: bool, executed_time: bool, previous_node: States = None):
        nodes_id = root.dot_str(state=state, executed_time=executed_time, previous_node=previous_node)

        transitions_id = ""

        for transition in root.transitions.keys():
            next_node = root.transitions[transition].init_node
            transitions_id += f"{root.dot_str(full=False)} -> {next_node.dot_str(full=False)} [label=\"{transition.replace(":", "->")[:-1]}\"];\n"

            ids = self.create_dot_graph(next_node, state=state, executed_time=executed_time, previous_node=root.states)
            nodes_id += ids[0]
            transitions_id += ids[1]

        return nodes_id, transitions_id


class AutomatonGraph():
    def __init__(self, aalpy_automaton, sul) -> None:
        active_states = self.prune_no_transition_states(aalpy_automaton.states)
        self.final_states, self.impacts = self.get_final_states_with_impacts(active_states, sul)
        self.graph = graph_to_be_processed = self.generate_graph_from_automaton(active_states[0])
        self.processed_graph = self.process_graph(graph_to_be_processed, sul)

    def prune_no_transition_states(self, states):
        pruned_states = []
        for s in states:
            if len(s.transitions) > 0:
                pruned_states.append(s)
        return pruned_states
    
    def get_final_states_with_impacts(self, active_states, sul: VPChecker):
        final_states = []
        impacts = []
        for s in active_states:
            for k in s.output_fun.keys():
                if s.output_fun[k] == 1:
                    final_states.append(s.state_id)
                    k_str = k.replace(" ", "")
                    k_tuple = tuple(map(int, k_str[1:-1].split(',')))
                    executed_tasks = [i for i in range(sul.number_of_nodes) if k_tuple[i] == 2 and sul.types[i] == sul.TASK]
                    naturals_activated = [i for i in range(sul.number_of_nodes) if k_tuple[i] == 2 and sul.types[i] == sul.NATURAL]
                    impact = []
                    p = 1
                    for t in executed_tasks:
                        impact = array_operations.sum(impact, sul.task_dict[t])
                    for n in naturals_activated:
                        left_child = sul.nature_dict[n][0]
                        left_c_prob = sul.nature_dict[n][1]
                        if k_tuple[left_child] == 2:
                            p = p * left_c_prob
                        else:
                            p = p * (1-left_c_prob)
                    impact = array_operations.product(impact, p)
                    impacts.append(impact.copy())
        return final_states, impacts                 

    def generate_graph_from_automaton(self, aalpy_automaton_state):
        is_final_state = True if aalpy_automaton_state.state_id in self.final_states else False
        tmp_node = ANode(states=aalpy_automaton_state,
                         is_final_state=is_final_state)
        if not is_final_state: # qui devo sistemare, se ho uno stato in loop non finisco più
            for kt in aalpy_automaton_state.transitions.keys():
                if aalpy_automaton_state.transitions[kt].state_id != aalpy_automaton_state.state_id:
                    tmp_node.add_transition(self.generate_graph_from_automaton(aalpy_automaton_state.transitions[kt]))
        return AGraph(tmp_node)
    
    def process_graph(self, graph: AGraph, sul: VPChecker):
        self.process_graph_rec(graph.init_node, tuple([0 for _ in range(sul.number_of_nodes)]), sul)
        return graph

    def process_graph_rec(self, node: ANode, in_char: tuple[int], sul: VPChecker):
        if node.is_final_state: return
        for nt_keys in node.transitions.keys():
            self.process_graph_rec(node.transitions[nt_keys].init_node, tuple(map(int, (nt_keys.replace(" ", ""))[1:-1].split(','))), sul)
        active_choices, active_naturals, traceroutes_dict = self.activated_choices_and_naturals(in_char, list(node.transitions.keys()), sul)
        if active_choices == 0 and active_naturals > 0:
            node.is_square_node = True
        elif active_choices > 0 and active_naturals > 0:
            for tk in traceroutes_dict.keys():
                tmp_node = ANode(states=node.states,
                                 is_square_node=True, generator=node.state_id)
                for out_char in traceroutes_dict[tk]:
                    print("out_char:" + out_char)
                    #tmp_node.add_transition(out_char, node.transitions[out_char])
                    tmp_node.add_transition(node.transitions[out_char])
                    #node.remove_transition(out_char)
                    node.remove_transition(node.transitions[out_char])

                print("tk:" + tk)
                node.add_transition(AGraph(tmp_node))

    def activated_choices_and_naturals(self, in_char, out_chars, sul: VPChecker):
        if len(out_chars) == 0:
            return 0,0,{}
        list_of_activated_choices = []
        list_of_activated_naturals = []
        tmp_out_char = tuple(map(int, (out_chars[0].replace(" ", ""))[1:-1].split(',')))
        for id, c in enumerate(in_char):
            if sul.types[id] == sul.CHOICE:
                icl = in_char[sul.childrens[id][0]]
                icr = in_char[sul.childrens[id][1]]
                ocl = tmp_out_char[sul.childrens[id][0]]
                ocr = tmp_out_char[sul.childrens[id][1]]
                if tmp_out_char[id] == 1:
                    if [ocl,ocr] == [1,-1] or [ocl,ocr] == [-1,1]:
                        if c == 0 or [c, icl, icr] == [1, 0, 0]:
                            list_of_activated_choices.append(id)         
            elif sul.types[id] == sul.NATURAL:
                if c == 0:
                    if tmp_out_char[id] == 1:
                        list_of_activated_naturals.append(id)

        traceroutes_dict = {}
        if len(list_of_activated_choices) != 0 and len(list_of_activated_naturals) != 0:
            for ok in out_chars:
                ok_tuple = tuple(map(int, (ok.replace(" ", ""))[1:-1].split(',')))
                traces_dict_key = []
                for ac in list_of_activated_choices:
                    [lc,rc] = sul.childrens[ac]
                    if ok_tuple[lc] == -1:
                        traces_dict_key.append(1)
                    else:
                        traces_dict_key.append(0)
                traces_dict_key_def = str(tuple(traces_dict_key))
                if traces_dict_key_def in traceroutes_dict.keys():
                    traceroutes_dict[traces_dict_key_def].append(ok)
                else:
                    traceroutes_dict[traces_dict_key_def] = [ok]


        return len(list_of_activated_choices), len(list_of_activated_naturals), traceroutes_dict
