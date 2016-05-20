import random
from environment import Agent, Environment
from planner import RoutePlanner
from simulator import Simulator


class LearningAgent(Agent):
    """An agent that learns to drive in the smartcab world."""

    def __init__(self, env, trials):
        super(LearningAgent, self).__init__(env)  # sets self.env = env, state = None, next_waypoint = None, and a default color
        self.color = 'red'  # override color
        self.planner = RoutePlanner(self.env, self)  # simple route planner to get next_waypoint

        # TODO: Initialize any additional variables here
        self.trials = trials
        self.success = 0  # How many times agent was able to reach the destination for given trials?
        self.penalties = 0
        self.total_rewards = 0

        # QLearning parameters
        self.QTable = {}  # Q(state,action)- Empty QTable
        self.epsilon = 0  # exploration probability of making a random move. The larger epsilon is, the more likely it is to pick random action.
        self.gamma = 0.90  # discount rate
        self.last_action = None
        self.last_state = None
        self.last_reward = None
        self.state = None

    def reset(self, destination=None):
        self.planner.route_to(destination)

        # TODO: Prepare for a new trip; reset any variables here, if required
        self.penalties = 0
        self.total_rewards = 0

        self.last_state = None
        self.last_action = None
        self.last_reward = None
        self.epsilon = 0

    def update(self, t):
        # Gather inputs
        self.next_waypoint = self.planner.next_waypoint()  # from route planner, also displayed by simulator
        inputs = self.env.sense(self)
        deadline = self.env.get_deadline(self)

        # TODO: Update state
        self.state = (inputs['light'], inputs['oncoming'], inputs['left'], self.next_waypoint)
        t += 1

        alpha = get_decay_rate(t)  # learning rate - how much of q-value depends on estimated future versus seen past
        self.epsilon = get_decay_rate(t)

        # TODO: Select action according to your policy
        # action = random.choice(self.env.valid_actions)  # Initial random movement / random action
        Q, action = self.get_qmax(self.state)  # policy

        # Execute action and get reward
        reward = self.env.act(self, action)

        # TODO: Learn policy based on state, action, reward

        # print "LearningAgent.update(): deadline = {}, inputs = {}, action = {}, reward = {}".\
        #    format(deadline, inputs, action, reward)  # [debug]

        if self.last_state is not None:
            if (self.last_state, self.last_action) not in self.QTable:
                self.QTable[(self.last_state, self.last_action)] = 1.0  # set to 1 if state,action pair not in QTable values

            print alpha, " - ", self.gamma

        # Update Q Table Values(state,action)
            self.QTable[(self.last_state, self.last_action)] = \
                ((1 - alpha) * self.QTable[(self.last_state, self.last_action)]) + \
                alpha * (self.last_reward +
                         self.gamma * (self.get_qmax(self.state)[0] - self.QTable[(self.last_state, self.last_action)]))

        # Store previous action, used to update QTable for next iteration time step
        self.last_state = self.state
        self.last_action = action
        self.last_reward = reward

        # Statistics
        self.total_rewards += reward

        if reward < 0:
            self.penalties += 1

        if reward > 5:
            self.success += 1
            print "\nTrial info: Number of Penalties =  {}, Net rewards: {}. " \
                  "\nTotal success/trials: {}/{}. \n".\
                format(self.penalties, self.total_rewards, self.success, self.trials)

    # Epsilon Greedy Exploration
    def get_qmax(self, state):

        # Returns: max Q value and best action
        best_action = None

        if random.random() < self.epsilon:
            # Chooses random action / add randomness to the choice
            best_action = random.choice(Environment.valid_actions)
            q_max = self.getqvalue(state, best_action)
        else:
            # Choose action based on policy
            q_max = float('-inf')

            for action in Environment.valid_actions:
                q = self.getqvalue(state, action)
                if q > q_max:
                    q_max = q
                else:
                    q = [self.getqvalue(state, a) for a in Environment.valid_actions]
                    q_max = max(q)
                    count_options = q.count(q_max)

                    # if more than 1 q_max, choose randomly among the q_max
                    if count_options > 1:
                        best = [i for i in range(len(Environment.valid_actions)) if q[i] == q_max]
                        i = random.choice(best)
                    else:
                        i = q.index(q_max)

                    best_action = Environment.valid_actions[i]

        return q_max, best_action

    def getqvalue(self, state, action):
        # Returns Q(state,action)
        if (state, action) not in self.QTable:
            self.QTable[(state, action)] = 1.0  # initialize Q-Values to 1.0
        return self.QTable[(state, action)]


def get_decay_rate(t):  # Decay rate for alpha and epsilon
        return 1.0 / float(t)


def run():
    """Run the agent for a finite number of trials."""
    trials = 100  # number of trials

    # Set up environment and agent
    e = Environment()  # create environment (also adds some dummy traffic)
    a = e.create_agent(LearningAgent, trials)  # create agent
    e.set_primary_agent(a, enforce_deadline=True)  # set agent to track

    # Now simulate it
    sim = Simulator(e, update_delay=0.000001)  # reduce update_delay to speed up simulation
    sim.run(n_trials=trials)  # press Esc or close pygame window to quit


if __name__ == '__main__':
    run()
