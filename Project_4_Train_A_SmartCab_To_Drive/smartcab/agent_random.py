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
        self.success = 0  # How many times agent able to reach the target for given trials?

        self.penalties = 0
        self.total_rewards = 0

    def reset(self, destination=None):
        self.planner.route_to(destination)

        # TODO: Prepare for a new trip; reset any variables here, if required
        self.penalties = 0
        self.total_rewards = 0

    def update(self, t):
        # Gather inputs
        self.next_waypoint = self.planner.next_waypoint()  # from route planner, also displayed by simulator
        inputs = self.env.sense(self)
        deadline = self.env.get_deadline(self)

        # TODO: Update state
        # self.state = inputs
        self.state = (inputs['light'], inputs['oncoming'], inputs['left'])
        # self.state = (inputs['light'], inputs['oncoming'], inputs['left'], self.next_waypoint)

        # TODO: Select action according to your policy
        action = random.choice(self.env.valid_actions)  # Initial random movement / random action

        # Execute action and get reward
        reward = self.env.act(self, action)

        # TODO: Learn policy based on state, action, reward

        print "LearningAgent.update(): deadline = {}, inputs = {}, action = {}, reward = {}".\
            format(deadline, inputs, action, reward)  # [debug]

        # Statistics
        self.total_rewards += reward

        if reward < 0:
            self.penalties += 1

        if reward > 5:
            self.success += 1
            print "\nTrial info: Number of Penalties =  {}, Net rewards: {}. \nTotal success/trials: {}/{}. \n".\
                format(self.penalties, self.total_rewards, self.success, self.trials)


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
