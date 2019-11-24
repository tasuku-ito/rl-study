import sys
import os
import numpy as np

class TicTacToeField:
    """
    3x3 field
      0  1  2 y
    0   |  |
      ーーーー
    1   |  |
      ーーーー
    2   |  |
    x

    z
    0: Brank
    1: o
    2: x
    states[x][y] = z
    基本的にoが自分
    先行後攻は外から操作する
    """ 
    def __init__(self):
        self.states = [[0]*3 for i in range(3)]
        self.blanks = [(x, y) for x in range(3) for y in range(3)]
        self.now_turn = 0

    def initialize(self):
        self.states = [[0]*3 for i in range(3)]
        self.blanks = [(x, y) for x in range(3) for y in range(3)]
        self.now_turn = 0
    
    def is_win(self, x, y, mark_number):
        """
        arguments: x,y,mark_numnber(o=1, x=2)
        return: r
        """ 
        r=0
        win = False

        for x in range(3):
            if self.states[x][0]==self.states[x][1]==self.states[x][2]==mark_number:
                win = True
                r=10
        for y in range(3):
            if self.states[0][y]==self.states[1][y]==self.states[2][y]==mark_number:
                win = True
                r=10

        if self.states[0][0]==self.states[1][1]==self.states[2][2]==mark_number:
            win = True
            r=10
            
        if self.states[0][2]==self.states[1][1]==self.states[2][0]==mark_number:
            win = True
            r=10
        
        return win, r
    
    def put_mark(self, x, y, mark):
        """
        arguments: x,y,mark(o or x)
        return: states, r
        """
        r=0
        self.now_turn += 1

        put_mark = 0
        if mark=="o":
            put_mark=1
        else:
            put_mark=2
        
        self.states[x][y]=1
        self.delete_blanks(x, y)
        win, r = self.is_win(x, y, put_mark)
        s = self.states

        if win:
            self.initialize()
            return win, s, r
        
        if self.now_turn==9:
            r=1
            self.initialize()
        
        return win, s, r
    
    def delete_blanks(self, x, y):
        self.blanks.remove((x, y))
    
    def show(self):
        """
        o|x|o
        -----
        o|x|o
        -----
        x|o|o
        """
        dump = []
        dump.append(" ")
        dump.append("o")
        dump.append("x")

        print(dump[self.states[0][0]] + "|" + dump[self.states[0][1]] + "|" + dump[self.states[0][2]])
        print("-----")
        print(dump[self.states[1][0]] + "|" + dump[self.states[1][1]] + "|" + dump[self.states[1][2]])
        print("-----")
        print(dump[self.states[2][0]] + "|" + dump[self.states[2][1]] + "|" + dump[self.states[2][2]])
        print()
        return

class TicTacToeBrain:
    def __init__(self, field):
        self.field = field
        self.states = [i for i in range(3**9)]
        self.value = [0]*(3**9)
        self.policy = {}
        for s in range(3**9):
            actions = self.get_actions_from_state(s)
            for a in actions:
                self.policy[(s,a)] = 1/len(actions)
    
    def get_now_state_value(self):
        now_states = self.field.states
        state_number = self.conv_state(now_states)
        #print(state_number)
        return state_number, self.value[state_number]

    def get_now_actions(self):
        blanks = self.field.blanks
        actions = []
        for a in blanks:
            x, y = a
            actions.append(3*x+y)
        return actions

    def do(self, action_number, mark):
        """
        0|1|2
        -----
        3|4|5
        -----
        6|7|8
        a: action_number
        """
        actions = self.get_now_actions()
        if action_number in actions:
            x = action_number//3
            y = action_number-x*3
            #print("{}({}, {})".format(mark, x, y))
            win, states, r = self.field.put_mark(x, y, mark)
            return win, self.conv_state(states), r
        else:
            raise ValueError("{} is not blank".format(a))

    def get_actions_from_state(self, state_number):
        actions = []
        states = self.decode_state(state_number)
        for x in range(3):
            for y in range(3):
                if states[x][y] == 0:
                    actions.append(3*x+y)
        return actions   

    def conv_state(self,field_states):
        """
        arguments: field_states=[
            [0, 0, 0], 
            [0, 0, 0], 
            [0, 0, 0]]
        return single number (0<= <=19682)
        """
        ret = 0
        for x in range(3):
            for y in range(3):
                ret += field_states[x][y]*(3**(x*3+y))  
        return ret

    def decode_state(self, number):
        states = [[0]*3 for i in range(3)]
        for x in range(2, -1, -1):
            for y in range(2, -1, -1):
                states[x][y] = number//(3**(x*3+y))
                number = number - states[x][y]*(3**(x*3+y))
        return states

    def show_values(self, start, end):
        if start<0 or end>3**9-1:
            raise ValueError("Incorrect numbers")
        for i in range(start, end, 1):
            print("State number: {}, State value: {}".format(i, self.value[i]))
            st = self.decode_state(i)
            print(st)

        return

def battle(brain_ml, brain_you, gamma=0.9):
    num_battles = 100
    count_ml_win = 0
    for n in range(100):
        delta = 0
        # 先攻
        for i in range(9):
            if i%2==0:
                actions = brain_ml.get_now_actions()
                a_number = random.randint(0, len(actions)-1)
                a = actions[a_number]
                win, new_s, r = brain_ml.do(a, "o")
                if win:
                    count_ml_win+=1
            else:
                actions = brain_ml.get_now_actions()
                a_number = random.randint(0, len(actions)-1)
                a = actions[a_number]
                win, ns, r = brain_you.do(a, "x")

            delta = max(delta, abs(v-v_new))

            if win:
                break

        # 後攻
        for i in range(9):
            if i%2==1:
                actions = brain_ml.get_now_actions()
                a_number = random.randint(0, len(actions)-1)
                a = actions[a_number]
                win, new_s, r = brain_ml.do(a, "o")
                if win:
                    count_ml_win+=1
            else:
                actions = brain_ml.get_now_actions()
                a_number = random.randint(0, len(actions)-1)
                a = actions[a_number]
                win, ns, r = brain_you.do(a, "x")

            delta = max(delta, abs(v-v_new))
            
            if win:
                break

    print("Win rate {}".format(count_ml_win/(num_battles*2)))




def policy_eval(brain_ml, brain_you, gamma=0.9, theta=0.001):
    import random
    while True:
        delta = 0
        # 先攻
        for i in range(9):
            if i%2==0:
                s, v = brain_ml.get_now_state_value()
                actions = brain_ml.get_now_actions()
                a_number = random.randint(0, len(actions)-1)
                a = actions[a_number]
                win, new_s, r = brain_ml.do(a, "o")
                v_new = brain_ml.policy[(s,a)]*(r + gamma*brain_ml.value[new_s])
                brain_ml.value[new_s] = v_new
            else:
                actions = brain_ml.get_now_actions()
                a_number = random.randint(0, len(actions)-1)
                a = actions[a_number]
                win, ns, r = brain_you.do(a, "x")

            delta = max(delta, abs(v-v_new))

            if win:
                break

        # 後攻
        for i in range(9):
            if i%2==1:
                s, v = brain_ml.get_now_state_value()
                actions = brain_ml.get_now_actions()
                a_number = random.randint(0, len(actions)-1)
                a = actions[a_number]
                win, new_s, r = brain_ml.do(a, "o")
                v_new = brain_ml.policy[(s,a)]*(r + gamma*brain_ml.value[new_s])
                brain_ml.value[new_s] = v_new
            else:
                actions = brain_ml.get_now_actions()
                a_number = random.randint(0, len(actions)-1)
                a = actions[a_number]
                win, ns, r = brain_you.do(a, "x")

            delta = max(delta, abs(v-v_new))
            
            if win:
                break
        if delta < theta:
            break

if __name__ == '__main__':
    tictactoe_field = TicTacToeField()
    ml_brain = TicTacToeBrain(tictactoe_field)
    you_brain = TicTacToeBrain(tictactoe_field)
    policy_eval(ml_brain, you_brain)
    
