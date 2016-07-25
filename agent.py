import random
from environment import Agent, Environment
from planner import RoutePlanner
from simulator import Simulator

class LearningAgent(Agent):
    """An agent that learns to drive in the smartcab world."""
    
    n_trials  =0

    def __init__(self, env):
        super(LearningAgent, self).__init__(env)  # sets self.env = env, state = None, next_waypoint = None, and a default color
        self.color = 'red'  # override color
        self.planner = RoutePlanner(self.env, self)  # simple route planner to get next_waypoint

        # TODO: Initialize any additional variables here
        self.next_waypoint = None
        # self.total_reward = 0
        # Set number of trials
        self.trial =0
        # Set all avaiable action
        self.actions = ['forward', 'left', 'right',None]
        self.total_reward = 0
        self.numBadMoves = 0
        self.lastReward = 0

        #learning rate of 0.9 *scratch*
        # updated the learning rate function Alpha = 1 / (c+(t/b))
        # where c is constant and b is a tuning parameter, t is self.trial
        # self.alpha = 0.9

        # set Gamma / Discount factor in Bellman equation
        # self.gamma = 0.33
        # self.epsilon = 0.1 
   
        # Initialize Q table(light, oncoming, next_waypoint)
        # intialize Q table per state and action
        self.Q = {}
        self.valid_actions = Environment.valid_actions
        for light in ['green','red']:  
          for oncoming in self.valid_actions:  
            for waypoint in Environment.valid_actions[1:]:
                   self.Q[(light,oncoming,waypoint)] = [1] * len(self.actions)  

    def reset(self, destination=None):
        self.planner.route_to(destination)
        # TODO: Prepare for a new trip; reset any variables here, if required

    def update(self, t):
        # Gather inputs
        self.next_waypoint = self.planner.next_waypoint()  # from route planner, also displayed by simulator
        inputs = self.env.sense(self)
        deadline = self.env.get_deadline(self)

        # TODO: Update state
        self.state = (inputs['light'],inputs['oncoming'], self.next_waypoint)

        # TODO: Select action according to your policy
        #action = None
        #action = random.choice(self.env.valid_actions) # random action
        
        ## Find the max Q value for the current state
        max_Q = self.Q[self.state].index(max(self.Q[self.state]))

        ## assign action 
        p = random.uniform(0.1,1)
        if p<self.epsilon:
            action = random.choice(self.env.valid_actions)
        else:
            action = self.actions[max_Q]

        # Execute action and get reward
        reward = self.env.act(self, action)

        # TODO: Learn policy based on state, action, reward
        # Do Learning rate update function
        # http://www.cse.unsw.edu.au/~cs9417ml/RL1/algorithms.html
        
        # self.tune_alpha =1000
        self.total_reward = reward + 1
        
        #Learning rate
        # self.alpha = 1/(1.1+self.trial/self.tune_alpha)
        self.trial = self.trial+1

        ## get the next state,action Q(s',a')
        next_inputs = self.env.sense(self)
        next_next_waypoint = self.planner.next_waypoint()
        next_state = (next_inputs['light'],next_inputs['oncoming'], next_next_waypoint)

        ## update Q table
        self.Q[self.state][self.actions.index(action)] = \
            (1-self.alpha)*self.Q[self.state][self.actions.index(action)] + \
            (self.alpha * (reward + self.gamma * max(self.Q[next_state])))

        #print "LearningAgent.update(): deadline = {}, inputs = {}, action = {}, reward = {}".format(deadline, inputs, action, reward)  # [debug]


def run():
    """Run the agent for a finite number of trials."""

    # Set up environment and agent
    # e = Environment()  # create environment (also adds some dummy traffic)
    # a = e.create_agent(LearningAgent)  # create agent
    # e.set_primary_agent(a, enforce_deadline=False)  # set agent to track
    # e.set_primary_agent(a, enforce_deadline=True)
    # Now simulate it
    # sim = Simulator(e, update_delay=0.01)  # reduce update_delay to speed up simulation
    # sim.run(n_trials=100)  # press Esc or close pygame window to quit
    
    ## print Q table
    #for key in a.Q:
    #    print key,
    #    print ["%0.2f" % i for i in a.Q[key]]
    
    ntrials_range = 100
    filename = 'Test training 100, testing 1000_2.csv'
    f = open(filename,'w')
    f.write("n_trials,epsilon,alpha,gamma,epsilon discount,successful_trials,sum(total_rewards.values()),total_badMoves,total_trialsNoPenalty,trials_sinceFailure, trials_sincePenalty\n")
    f.close()

    epsilon_range = {1.0}
    alpha_range = {0.9,0.8,0.7}
    gamma_range = {1}
    epsilon_discount = {0.9999,0.999,0.99}
    ntrials_range = {1,2,3,4,5,6,7,8,9,10}

    for ntrials in ntrials_range:
        for ep in epsilon_range:
            for al in alpha_range:
                for ga in gamma_range:
                    for epdi in epsilon_discount:
                        #a = e.create_agent(LearningAgent)
                        #e.set_primary_agent(a, enforce_deadline=True)

                        e = Environment()  # create environment (also adds some dummy traffic)
                        a = e.create_agent(LearningAgent)  # create agent
                        e.set_primary_agent(a, enforce_deadline=True) 

                        a.epsilon = ep
                        a.alpha = al
                        a.gamma = ga
                        a.epdi = epdi

                        sim = Simulator(e, update_delay=0.0)
                        sim.run(n_trials=100)

                        #e.set_primary_agent(a, enforce_deadline=True)
                        #sim = Simulator(e, update_delay=0.0)
                        a.alpha = 0
                        a.epsilon = 0
                        
                        successful_trials = 0
                        total_rewards = {}
                        total_badMoves = 0
                        total_trialsNoPenalty = 0
                        trials_sincePenalty = 0
                        trials_sinceFailure = 0
                        for count in range(0,1000):
                            sim.run(n_trials=1)
                            total_rewards[len(total_rewards)] = a.total_reward
                            total_badMoves += a.numBadMoves
                            if a.lastReward == 12:
                                successful_trials += 1
                                trials_sinceFailure += 1
                            else:
                                trials_sinceFailure = 0
                            if a.numBadMoves == 0:
                                trials_sincePenalty += 1
                                total_trialsNoPenalty += 1
                            else:
                                trials_sincePenalty = 0
                        
                        #print "{},{},{},{},{},{},{}".format(ep,al,ga,epdi,total_rewards.values())

                        print "{},{},{},{},{},{},{}".format(ep,al,ga,epdi,successful_trials,sum(total_rewards.values()),total_badMoves)
                        f = open(filename,'a')
                        #f.write("%d,%f,%f,%f,%f,%f,%f,%f,%f,%f,%f\n" % (n_trials,ep,al,ga,epdi,successful_trials))
                        f.close()
                        f.write("%d,%f,%f,%f,%f,%f,%f,%f,%f,%f,%f\n" % (n_trials,ep,al,ga,epdi,successful_trials,sum(total_rewards.values()),total_badMoves,total_trialsNoPenalty,trials_sinceFailure, trials_sincePenalty))
                        

if __name__ == '__main__':
    run()
