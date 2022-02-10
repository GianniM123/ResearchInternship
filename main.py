from fsm import FSM, Transition, State, FSM_Diff, SMT_SOLVERS
import fsm
import getopt, sys



BowlingS0 = State("Start Game")
BowlingS1 = State("Bowling Game")
BowlingS2 = State("Pause")

bowling_fsm = FSM([BowlingS0,BowlingS1,BowlingS2], BowlingS0, [
                        Transition(BowlingS0,BowlingS1,"Start","1"),
                        Transition(BowlingS0,BowlingS0,"Exit","1"),
                        Transition(BowlingS0,BowlingS2,"Pause", "1"),
                        Transition(BowlingS1,BowlingS1,"Start","0"),
                        Transition(BowlingS1,BowlingS1,"Exit","0"),
                        Transition(BowlingS1,BowlingS2,"Pause","1"),
                        Transition(BowlingS2,BowlingS1,"Start","1"),
                        Transition(BowlingS2,BowlingS0,"Exit","1"),
                        Transition(BowlingS2,BowlingS2,"Pause","0")
                        ]
                    )

PongS0 = State("Start Game")
PongS1 = State("Pong Game")
PongS2 = State("Pause")

pong_fsm = FSM([PongS0,PongS1,PongS2], PongS0, [
                        Transition(PongS0,PongS1,"Start","1"),
                        Transition(PongS0,PongS0,"Exit","0"),
                        Transition(PongS0,PongS0,"Pause", "0"),
                        Transition(PongS1,PongS1,"Start","0"),
                        Transition(PongS1,PongS0,"Exit","1"),
                        Transition(PongS1,PongS2,"Pause","1"),
                        Transition(PongS2,PongS1,"Start","1"),
                        Transition(PongS2,PongS0,"Exit","1"),
                        Transition(PongS2,PongS2,"Pause","0")
                        ]
                    )
 
b0 = State("b0")
b1 = State("b1")
b2 = State("b2")
b3 = State("b3")

b_fsm = FSM([b0,b1,b2,b3],b0,[
                        Transition(b2,b0,"b","0"),
                        Transition(b3,b0,"b","0"),
                        Transition(b0,b1,"a","0")
])

a0 = State("a0")
a1 = State("a1")
a2 = State("a2")
a3 = State("a3")
a4 = State("a4")

a_fsm = FSM([a0,a1,a2,a3,a4],a0,[
                        Transition(a3,a0,"b","0"),
                        Transition(a0,a1,"a","0"),
                        Transition(a0,a2,"a","0"),
                        Transition(a0,a4,"b","0")
])


def main():
    try:
        arguments = getopt.getopt(sys.argv[1:],"hs:",["help","smt"])

        for current_arg, current_val in arguments[0]:
            if current_arg in ("-s", "--smt"):
                if current_val in SMT_SOLVERS:
                    fsm.current_solver = current_val
                else:
                    print("invalid smt-solver")
                    return
            elif current_arg in ("-h", "--help"):
                print("Usage: main.py [-s <smt-solver>]")
                print("<smt-solver> options:")
                for solver in SMT_SOLVERS:
                    print('\t' + solver)
                return
    except getopt.error as err:
        print(str(err))

    matching_pairs = FSM_Diff().algorithm(bowling_fsm,pong_fsm,0.5,0.8,1)

    print(matching_pairs)

if __name__ == "__main__":
    main()
