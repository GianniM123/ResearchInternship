from dataclasses import dataclass

from pysmt.shortcuts import Symbol, And, GE, LT, Plus, Minus, Times, Equals, Real, Int, get_model
from pysmt.typing import REAL
from pysmt.oracles import get_logic

@dataclass
class State:
    name: str


@dataclass
class Transition:
    from_state: State
    to_state: State
    input: str
    output: str

@dataclass
class FSM:
    states: list[State]
    initial_state: State
    transitions: list[Transition]

@dataclass
class ComparingStates:
    states: tuple[State,State]
    matching_trans: list[tuple[Transition,Transition]]
    non_matching_trans: tuple[list[Transition],list[Transition]]

class Singleton(type):
    _instances = {}
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]

class FSM_Diff(metaclass=Singleton):

    # Transitions match if output is equal for a input
    def matching_transitions(self,fsm_1,fsm_2,out):
        outcome = []
        for s1 in fsm_1.states:
            for s2 in fsm_2.states:
                used_trans1 = []
                used_trans2 = []
                state_compare = ComparingStates((s1,s2),[],([],[]))
                for t1 in fsm_1.transitions:
                    if (t1.from_state == s1 and out) or (t1.to_state == s1 and not out):
                        used_trans1.append(t1)
                for t2 in fsm_2.transitions:
                    if (t2.from_state == s2 and out) or (t2.to_state == s2 and not out):
                        used_trans2.append(t2)

                for t1 in used_trans1:
                    matched = False
                    for t2 in used_trans2:
                        if t1.input == t2.input and t1.output == t2.output:
                            state_compare.matching_trans.append((t1,t2))
                            matched = True
                    if not matched:
                        state_compare.non_matching_trans[0].append(t1)
                
                for t2 in used_trans2:
                    matched = False
                    for t1 in used_trans1:
                        if t1.input == t2.input and t1.output == t2.output:
                            matched = True
                    if not matched:
                        state_compare.non_matching_trans[1].append(t2)
            
                outcome.append(state_compare)
        return outcome
                    
    def linear_equation_solver(self, state_pairs, k, out):
        variables = []
        domain = []
        equations = []
        
        for state_pair in state_pairs:
            variable = Symbol("(" + state_pair.states[0].name + "," + state_pair.states[1].name + ")", REAL)
            variables.append(variable)
            domain.append(GE(variable,Real(0.0)))
            denominator = 2 * (len(state_pair.matching_trans) + len(state_pair.non_matching_trans[0]) + len(state_pair.non_matching_trans[1]))
            reached_states_vars = [Symbol("(" + (t1.to_state.name if out else t1.from_state.name) + "," + (t2.to_state.name if out else t2.from_state.name)  + ")", REAL) for t1, t2 in state_pair.matching_trans]
            times = Real(0) if len(reached_states_vars) < 1 else Plus([i for i in reached_states_vars])
            equation = Equals(Minus(Times(Real(denominator), variable), Times(Real(k), times)), Real(len(state_pair.matching_trans)))
            equations.append(equation)
        formula = And(And( (i for i in domain)), And( (i for i in equations)))
        model = get_model(formula, solver_name="z3")
        return_dict = {}
        for var in variables:
            return_dict[var] = model.get_value(var)
        return return_dict
            

    def simularity_score(self,fsm_1, fsm_2, k):
        out_match_trans = self.matching_transitions(fsm_1,fsm_2,True)
        outcome_out = self.linear_equation_solver(out_match_trans, k, True)
        
        in_match_trans = self.matching_transitions(fsm_1,fsm_2,False)
        outcome_in = self.linear_equation_solver(in_match_trans, k, False)
        result_dict = {}
        for key in outcome_out:
            result_dict[key] = (outcome_out[key] + outcome_in[key]) / 2
        return result_dict


    def algorithm(self, fsm_1, fsm_2, k):
        self.simularity_score(fsm_1,fsm_2,k)

