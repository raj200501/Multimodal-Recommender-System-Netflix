import gym
import numpy as np

class RLModel:
    def __init__(self, env_name='CartPole-v1'):
        self.env = gym.make(env_name)
        self.state = self.env.reset()
        self.q_table = np.zeros([self.env.observation_space.shape[0], self.env.action_space.n])
        self.alpha = 0.1
        self.gamma = 0.99
        self.epsilon = 0.1

    def train(self, episodes=1000):
        for _ in range(episodes):
            state = self.env.reset()
            done = False
            while not done:
                if np.random.uniform(0, 1) < self.epsilon:
                    action = self.env.action_space.sample()
                else:
                    action = np.argmax(self.q_table[state])
                next_state, reward, done, _ = self.env.step(action)
                old_value = self.q_table[state, action]
                next_max = np.max(self.q_table[next_state])
                new_value = (1 - self.alpha) * old_value + self.alpha * (reward + self.gamma * next_max)
                self.q_table[state, action] = new_value
                state = next_state

    def predict(self, state):
        return np.argmax(self.q_table[state])

if __name__ == "__main__":
    rl_model = RLModel()
    rl_model.train()
    state = rl_model.env.reset()
    action = rl_model.predict(state)
    print(f"Predicted Action: {action}")
