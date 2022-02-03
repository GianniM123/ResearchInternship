from fsm import FSM, Transition, State, FSM_Diff


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
 

if __name__ == "__main__": 
    FSM_Diff().algorithm(bowling_fsm,pong_fsm,0.5)