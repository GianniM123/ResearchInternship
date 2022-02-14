from fsm import FSM_Diff, SMT_SOLVERS
import fsm
import getopt, sys
import networkx as nx

bowling = nx.MultiDiGraph()
bowling.add_node("Start Game")
bowling.add_node("Bowling Game")
bowling.add_node("Pause")

bowling.add_edge("Start Game",      "Bowling Game", input="Start",  output="1")
bowling.add_edge("Start Game",      "Start Game",   input="Exit",   output="1")
bowling.add_edge("Start Game",      "Pause",        input="Pause",  output="1")
bowling.add_edge("Bowling Game",    "Bowling Game", input="Start",  output="0")
bowling.add_edge("Bowling Game",    "Bowling Game", input="Exit",   output="0")
bowling.add_edge("Bowling Game",    "Pause",        input="Pause",  output="1")
bowling.add_edge("Pause",           "Bowling Game", input="Start",  output="1")
bowling.add_edge("Pause",           "Start Game",   input="Exit",   output="1")
bowling.add_edge("Pause",           "Pause",        input="Pause",  output="0")

pong = nx.MultiDiGraph()
pong.add_node("Start Game")
pong.add_node("Pong Game")
pong.add_node("Pause")

pong.add_edge("Start Game",     "Pong Game",    input="Start",  output="1"),
pong.add_edge("Start Game",     "Start Game",   input="Exit",   output="0"),
pong.add_edge("Start Game",     "Start Game",   input="Pause",  output="0"),
pong.add_edge("Pong Game",      "Pong Game",    input="Start",  output="0"),
pong.add_edge("Pong Game",      "Start Game",   input="Exit",   output="1"),
pong.add_edge("Pong Game",      "Pause",        input="Pause",  output="1"),
pong.add_edge("Pause",          "Pong Game",    input="Start",  output="1"),
pong.add_edge("Pause",          "Start Game",   input="Exit",   output="1"),
pong.add_edge("Pause",          "Pause",        input="Pause",  output="0")

b = nx.MultiDiGraph()
b.add_node("b0")
b.add_node("b1")
b.add_node("b2")
b.add_node("b3")

b.add_edge("b2","b0",input="b",output="0")
b.add_edge("b3","b0",input="b",output="0")
b.add_edge("b0","b1",input="a",output="0")


a = nx.MultiDiGraph()
a.add_node("a0")
a.add_node("a1")
a.add_node("a2")
a.add_node("a3")
a.add_node("a4")

a.add_edge("a3","a0",input="b",output="0")
a.add_edge("a0","a1",input="a",output="0")
a.add_edge("a0","a2",input="a",output="0")
a.add_edge("a0","a4",input="b",output="0")



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

    matching_pairs = FSM_Diff().algorithm(bowling,pong,0.5,0.2,1)

    print(matching_pairs)

if __name__ == "__main__":
    main()
