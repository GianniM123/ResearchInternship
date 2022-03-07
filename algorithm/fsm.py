from cProfile import label
from dataclasses import dataclass

from typing import List, Tuple, Dict
from time import time

from debug import print_smtlib

from pysmt.shortcuts import Symbol, And, GE, Plus, Minus, Times, Equals, Real, get_model, write_smtlib, read_smtlib, to_smtlib
from pysmt.typing import REAL

import networkx as nx
import string

SMT_SOLVERS = ["msat","cvc4","z3","yices","btor","picosat","bdd"]

current_solver = "z3"
debug = False
timing = False
performance = False
logging = False

@dataclass
class ComparingStates:
    states: Tuple[str,str]
    matching_trans: List[Tuple[Dict,Dict]]
    non_matching_trans: Tuple[List[Dict],List[Dict]]

class Singleton(type):
    _instances = {}
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]

class FSM_Diff(metaclass=Singleton):

    def pair_matching_transition(self,fsm_1,fsm_2,s1,s2,out):
        used_trans1 = []
        used_trans2 = []
        state_compare = ComparingStates((s1,s2),[],([],[]))
        for t1 in fsm_1.edges.data():
            if (t1[0] == s1 and out) or (t1[1] == s1 and not out):
                used_trans1.append(t1)
        for t2 in fsm_2.edges.data():
            if (t2[0] == s2 and out) or (t2[1] == s2 and not out):
                used_trans2.append(t2)

        for t1 in used_trans1:
            matched = False
            for t2 in used_trans2:
                if t1[2]["label"] == t2[2]["label"]:
                    state_compare.matching_trans.append((t1,t2))
                    matched = True
            if not matched:
                state_compare.non_matching_trans[0].append(t1)
        for t2 in used_trans2:
            matched = False
            for t1 in used_trans1:
                if t1[2]["label"] == t2[2]["label"]:
                    matched = True
            if not matched:
                state_compare.non_matching_trans[1].append(t2)
        
        return (state_compare)

    def matching_transitions(self,fsm_1,fsm_2,out):
        outcome = []
        for s1 in fsm_1.nodes:
            for s2 in fsm_2.nodes:
                outcome.append(self.pair_matching_transition(fsm_1,fsm_2,s1,s2,out))
        return outcome
                    
    def linear_equation_solver(self, state_pairs, k, out):
        names = []
        variables = []
        domain = []
        equations = []
        
        for state_pair in state_pairs:
            names.append(state_pair.states)
            variable = Symbol("(" + state_pair.states[0] + "," + state_pair.states[1] + ")", REAL)
            variables.append(variable)
            domain.append(GE(variable,Real(0.0)))
            denominator = 2 * (len(state_pair.matching_trans) + len(state_pair.non_matching_trans[0]) + len(state_pair.non_matching_trans[1]))
            reached_states_vars = [Symbol("(" + (t1[1] if out else t1[0]) + "," + (t2[1] if out else t2[0])  + ")", REAL) for t1, t2 in state_pair.matching_trans]
            times = Real(0) if len(reached_states_vars) < 1 else Plus([i for i in reached_states_vars])
            equation = Equals(Minus(Times(Real(denominator), variable), Times(Real(k), times)), Real(len(state_pair.matching_trans)))
            equations.append(equation)
        formula = And(And( (i for i in domain)), And( (i for i in equations)))
        if(debug):
            print_smtlib(formula)
        start_time = time()
        model = get_model(formula, solver_name=current_solver)
        if out:
            self.out_time = (time() - start_time)
        else:
            self.in_time = (time() - start_time)
        if timing:
            print("%s seconds SMT execution for " % self.out_time if out else self.in_time, end="")
            print("outgoing transitions" if out else "incoming transitions")
        return_dict = {}
        for i in range(0,len(variables)):
            return_dict[names[i]] = eval(str(model.get_value(variables[i])))
        return return_dict
            
    def compute_scores(self,fsm_1, fsm_2, k):
        out_match_trans = self.matching_transitions(fsm_1,fsm_2,True)
        outcome_out = self.linear_equation_solver(out_match_trans, k, True)

        in_match_trans = self.matching_transitions(fsm_1,fsm_2,False)
        outcome_in = self.linear_equation_solver(in_match_trans, k, False)

        result_dict = {}
        for var in outcome_out:
            result_dict[var] = (outcome_out[var] + outcome_in[var]) / 2
        return result_dict

    def identify_landmarks(self, pairs_to_scores,t,r, matching_pair = None):
        filtered_dict = {}
        vars = []
        for var in pairs_to_scores:
            vars.append(var)
            if (pairs_to_scores[var] >= t):
                filtered_dict[var] = pairs_to_scores[var]
        landmarks = set()
        if matching_pair is not None:
            landmarks.add(matching_pair)
        for var in vars:
            filtered_vars = list(filter(lambda v: v[0] ==var[0] and not v == var, vars))
            is_landmark = True
            for f_var in filtered_vars:
                if not (pairs_to_scores[var] >= (pairs_to_scores[f_var] * r) and var in filtered_dict):
                    is_landmark = False
            if is_landmark:
                landmarks.add(var)
        return landmarks        


    def surrounding_pairs(self, fsm_1,fsm_2,pair):
        s1 = pair[0]
        s2 = pair[1]

        n_pair = set()
        out_matching = self.pair_matching_transition(fsm_1,fsm_2,s1,s2,True)
        for t_out1, t_out2 in out_matching.matching_trans:
            n_pair.add(  (t_out1[1] , t_out2[1]))
        in_matching = self.pair_matching_transition(fsm_1,fsm_2,s1,s2,False)
        for t_in1, t_in2 in in_matching.matching_trans:
            n_pair.add( (t_in1[0], t_in2[0]))
        return n_pair

    def pick_highest(self, n_pairs, pairs_to_scores):
        highest =  ("", -0.0)
        for pair in n_pairs:
            if pairs_to_scores[pair] >= highest[1]:
                highest = (pair, pairs_to_scores[pair])
        return highest[0]

    def remove_conflicts(self,n_pairs, pair):
        new_n_pairs = set()
        for n_pair in n_pairs:
            if pair[0] != n_pair[0] and pair[1] != n_pair[1]:
                new_n_pairs.add(n_pair)
        return new_n_pairs

    def added_transitions(self, fsm_1, fsm_2, k_pairs):
        added_transitions = []
        for edge2 in fsm_2.edges.data():
            exists = False
            for edge1 in fsm_1.edges.data():
                if (edge1[0],edge2[0]) in k_pairs and (edge1[1],edge2[1]) in k_pairs and edge2[2]["label"] == edge1[2]["label"]:
                    exists = True
            if not exists:
                added_transitions.append(edge2)
        return added_transitions

    def removed_transitions(self, fsm_1, fsm_2, k_pairs):
        removed_transitions = []
        for edge1 in fsm_1.edges.data():
            exists = False
            for edge2 in fsm_2.edges.data():
                if (edge1[0],edge2[0]) in k_pairs and (edge1[1],edge2[1]) in k_pairs and edge2[2]["label"] == edge1[2]["label"]:
                    exists = True
            if not exists:
                removed_transitions.append(edge1)
        return removed_transitions

    def fresh_var(self,index):
        letters = string.ascii_lowercase
        value = 1
        if index >= len(letters):
            value = int(index / len(letters)) + 1
        return (letters[index] * value)

    
    def annotade_edges(self,graph,k_pairs,set,color, index, nr_of_states):
        
        added_dict = {}
        for add in set:
            from_state = None
            for k in k_pairs:
                if k[index] == add[0]:
                    from_state = self.fresh_var(k_pairs.index(k))
            if from_state is None and add[0] in added_dict.keys():
                from_state = self.fresh_var(added_dict[add[0]])
            elif from_state is None:
                num = nr_of_states + len(added_dict)
                from_state = self.fresh_var(num)
                added_dict[add[0]] = num
                graph.add_node(from_state,color=color)
            
            to_state = None
            for k in k_pairs:
                if k[index] == add[1]:
                    to_state = self.fresh_var(k_pairs.index(k))
            if to_state is None and add[1] in added_dict.keys():
                to_state = self.fresh_var(added_dict[add[1]])
            elif to_state is None:
                num = nr_of_states + len(added_dict)
                to_state = self.fresh_var(num)
                added_dict[add[1]] = num
                graph.add_node(to_state,color=color)
            
            graph.add_edge(from_state,to_state,color=color,label=add[2]["label"])
        
        return nr_of_states + len(added_dict)
    
    def matched_k_pairs_transitions(self, fsm_1, fsm_2, k_pairs):
        edges = []
        k_pairs = list(k_pairs)
        for edge1 in fsm_1.edges.data():
            for edge2 in fsm_2.edges.data():
                if (edge1[0],edge2[0]) in k_pairs and (edge1[1],edge2[1]) in k_pairs and edge2[2]["label"] == edge1[2]["label"]:
                    from_state = self.fresh_var(k_pairs.index((edge1[0],edge2[0])))
                    to_state = self.fresh_var(k_pairs.index((edge1[1],edge2[1])))
                    edges.append((from_state,to_state,edge2[2]["label"]))
        return edges

    def annotade_graph(self, k_pairs, added, removed, matched):
        graph = nx.MultiDiGraph()
        k_pairs = list(k_pairs)
        for i in range(0,len(k_pairs)):
            graph.add_node(self.fresh_var(i))

        for i in matched:
            graph.add_edge(i[0],i[1], label=i[2])
        
        nr_of_states = self.annotade_edges(graph,k_pairs,added,"green",1,len(graph.nodes))
        self.annotade_edges(graph,k_pairs,removed,"red",0,nr_of_states)
        return graph

    def performance_matrix(self, fsm_1, FP, FN, dict):
        TP = []
        for edge in fsm_1.edges.data():
            found = False
            for rem in FN:
                if edge[0] == rem[0] and edge[1] == rem[1] and edge[2] == rem[2]:
                    found = True
            if not found:
                TP.append(edge)

        dict["precision"] = len(TP) / (len(TP) + len(FP)) # FP is guaranteed to be not in TP, so can just be added
        dict["recall"] = len(TP) / (len(TP) + len(FN)) # FN is guarenteeed to be not in TP, so can just be added
        dict["f-measure"] = (2 * dict["precision"] * dict["recall"]) / (dict["precision"] + dict["recall"])

        
    def statistics_graph(self, graph):
        return {"States": len(graph.nodes), "Transitions": len(graph.edges)}
    
    def logging(self, fsm_1, fsm_2, added, removed, graph, dict):
        self.performance_matrix(fsm_1,added,removed,dict)
        dict["Reference"] = self.statistics_graph(fsm_1)
        dict["Updated"] = self.statistics_graph(fsm_2)
        dict["Output"] = self.statistics_graph(graph)
        dict["Outgoing time"] = "%s" % self.out_time
        dict["Incoming time"] = "%s" % self.in_time
        dict["Solver"] = current_solver

    def algorithm(self, fsm_1, fsm_2, k, t, r, matching_pair = None):
        if matching_pair is not None:
            if (matching_pair[0] not in fsm_1.nodes or matching_pair[1] not in fsm_2.nodes):
                print("Given pairs do not exists in the FSM's")
                return

        # line 1
        pairs_to_scores = self.compute_scores(fsm_1,fsm_2,k)
        
        # line 2
        k_pairs = self.identify_landmarks(pairs_to_scores,t,r,matching_pair)
        # line 3-5
        key = (list(fsm_1.nodes)[0], list(fsm_2.nodes)[0])
        if not k_pairs and pairs_to_scores[key] >= 0:
            k_pairs.add(key)
        # line 6
        n_pairs = set()
        for pair in k_pairs:
            n_pairs = n_pairs.union(self.surrounding_pairs(fsm_1,fsm_2,pair))
        for k in k_pairs:
            n_pairs = self.remove_conflicts(n_pairs,k)
        
        # line 7 - 14
        while n_pairs:
            while n_pairs:
                # line 9
                pair = self.pick_highest(n_pairs,pairs_to_scores)
                # line 10
                k_pairs.add(pair)
                # line 11
                n_pairs = self.remove_conflicts(n_pairs,pair)
            # line 13
            for pair in k_pairs:
                n_pairs = n_pairs.union(self.surrounding_pairs(fsm_1,fsm_2,pair))
            for k in k_pairs:
                n_pairs = self.remove_conflicts(n_pairs,k)
    
        added = self.added_transitions(fsm_1,fsm_2,k_pairs)
        removed = self.removed_transitions(fsm_1,fsm_2,k_pairs)
        matched = self.matched_k_pairs_transitions(fsm_1,fsm_2,k_pairs)
        graph = self.annotade_graph(k_pairs,added,removed,matched)

        if logging:
            self.logging(fsm_1,fsm_2,added,removed,graph,graph.graph)

        if performance and logging:
            print(graph.graph)
        elif performance and not logging:
            dict = {}
            self.logging(fsm_1,fsm_2,added,removed,graph,dict)
            print (dict)


        return graph
        


