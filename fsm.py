from dataclasses import dataclass
from typing import List, Tuple, Dict
from time import time

from debug import write_smtlib_no_daggify

from pysmt.shortcuts import Symbol, And, GE, Plus, Minus, Times, Equals, Real, get_model, write_smtlib, read_smtlib, to_smtlib
from pysmt.typing import REAL
from pysmt.smtlib.script import SmtLibScript

SMT_SOLVERS = ["msat","cvc4","z3","yices","btor","picosat","bdd"]

current_solver = "z3"
debug = False
timing = False

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
                if t1[2]["input"] == t2[2]["input"] and t1[2]["output"] == t2[2]["output"]:
                    state_compare.matching_trans.append((t1,t2))
                    matched = True
            if not matched:
                state_compare.non_matching_trans[0].append(t1)
        for t2 in used_trans2:
            matched = False
            for t1 in used_trans1:
                if t1[2]["input"] == t2[2]["input"] and t1[2]["output"] == t2[2]["output"]:
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
            write_smtlib_no_daggify(formula)
        if timing:
            start_time = time()
        model = get_model(formula, solver_name=current_solver)
        if timing:
            print("%s seconds" % (time() - start_time))
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
    
        return k_pairs
        


