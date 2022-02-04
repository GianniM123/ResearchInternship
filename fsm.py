from dataclasses import dataclass
from typing import List


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
                    


    def simularity_score(self,fsm_1, fsm_2, k):
        out_match_trans = self.matching_transitions(fsm_1,fsm_2, True)
        print(out_match_trans[0].non_matching_trans)
        
        in_match_trans = self.matching_transitions(fsm_1,fsm_2,False)
        print(in_match_trans[0].matching_trans)


    def algorithm(self, fsm_1, fsm_2, k):
        self.simularity_score(fsm_1,fsm_2,k)

