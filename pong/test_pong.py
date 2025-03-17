import torch
import numpy as np
from pong import PongEnv
from train_pong import DQN

def select_action(state):
    state = torch.FloatTensor(state).unsqueeze(0)
    with torch.no_grad():
        q_values = model(state)
    return torch.argmax(q_values).item()


if __name__ == '__main__':
    env = PongEnv()
    state_dim = len(env.reset())
    n_actions = env.action_space.n

    model = DQN(state_dim, n_actions)
    model.load_state_dict(torch.load("pong_best.pth"))
    model.eval()

    state = env.reset()
    done = False
    total_reward = 0

    while not done:
        action = select_action(state)

        next_state, reward, done, _ = env.step(action)
        total_reward += reward

        env.check_event()
        env.render()

        state = next_state
    
    print(f"Score final: {total_reward}")

    env.close()