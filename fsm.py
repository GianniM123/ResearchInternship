from dataclasses import dataclass
from re import T


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
class StatePair:
    state: State
    matched_trans: list[Transition]
    unmatched_trans: list[Transition]

class Singleton(type):
    _instances = {}
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]

class FSM_Diff(metaclass=Singleton):

    # Transitions match if output is equal for a input
    def matching_transitions(self,fsm_1,fsm_2):
        matching_trans = []
        for s1 in fsm_1.states:
            for s2 in fsm_2.states:
                pair = (StatePair(s1,[],[]),StatePair(s2,[],[]))
                for t1 in fsm_1.transitions:
                    if t1.from_state == s1:
                        matched = False # check for transitions that don't have the same input
                        for t2 in fsm_2.transitions:
                            if t2.from_state == s2 and t1.input == t2.input:
                                if t1.output == t2.output:
                                    pair[0].matched_trans.append(t1)
                                    pair[1].matched_trans.append(t2)
                                else:
                                    pair[0].unmatched_trans.append(t1)
                                    pair[1].unmatched_trans.append(t2)
                                matched = True
                        if matched == False:
                            pair[0].unmatched_trans.append(t1) 
                
                for t2 in fsm_2.transitions:
                    if t2.from_state == s2:
                        matched = False
                        for t1 in fsm_1.transitions:
                            if t1.from_state == s1 and t1.input == t2.input:
                                matched = True
                        if matched == False:
                            pair[1].unmatched_trans.append(t1) 

                matching_trans.append(pair)
        return matching_trans
                        
                
                
        


    def simularity_score(self,fsm_1, fsm_2, k):
        out_match_trans = self.matching_transitions(fsm_1,fsm_2)
        print(out_match_trans[0][0].matched_trans)
        print(out_match_trans[0][1].matched_trans)
        


    def algorithm(self, fsm_1, fsm_2, k):
        self.simularity_score(fsm_1,fsm_2,k)

