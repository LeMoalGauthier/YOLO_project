import torch
import torch.nn as nn
import torch.optim as optim
import random
import numpy as np
from collections import deque
from pong_env import PongEnv  # Assurez-vous d'utiliser la version corrigée

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# Hyperparamètres optimisés
BATCH_SIZE = 128
LEARNING_RATE = 5e-5
GAMMA = 0.99
EPSILON_START = 1.0
EPSILON_END = 0.01
EPSILON_DECAY = 0.9999
TARGET_UPDATE_FREQ = 5_000
REPLAY_MEMORY_SIZE = 500_000
EVAL_FREQ = 10

class DQN(nn.Module):
    def __init__(self, input_dim, output_dim):
        super(DQN, self).__init__()
        self.fc1 = nn.Linear(input_dim, 512)
        self.fc2 = nn.Linear(512, 512)
        self.fc3 = nn.Linear(512, 256)
        self.value = nn.Linear(256, 1)
        self.advantage = nn.Linear(256, output_dim)

    def forward(self, x):
        x = torch.relu(self.fc1(x))
        x = torch.relu(self.fc2(x))
        x = torch.relu(self.fc3(x))
        value = self.value(x)
        advantage = self.advantage(x)
        return value + (advantage - advantage.mean(dim=1, keepdim=True))

def preprocess_state(state):
    return np.clip(state, 0, 1).astype(np.float32)

def epsilon_greedy(state, epsilon, net):
    if random.random() < epsilon:
        return random.randint(0, n_actions-1)
    else:
        state_tensor = torch.FloatTensor(state).unsqueeze(0).to(device)
        with torch.no_grad():
            return net(state_tensor).argmax().item()

def evaluate_agent(net, env, n_episodes=5):
    total_reward = 0
    for _ in range(n_episodes):
        state = preprocess_state(env.reset())
        done = False
        while not done:
            action = epsilon_greedy(state, 0.0, net)
            next_state, reward, done, _ = env.step(action)
            state = preprocess_state(next_state)
            total_reward += reward
    return total_reward / n_episodes

if __name__ == '__main__':
    env = PongEnv()
    n_actions = env.action_space.n
    state_dim = len(preprocess_state(env.reset()))
    
    policy_net = DQN(state_dim, n_actions).to(device)
    target_net = DQN(state_dim, n_actions).to(device)
    target_net.load_state_dict(policy_net.state_dict())
    target_net.eval()

    optimizer = optim.Adam(policy_net.parameters(), lr=LEARNING_RATE)
    memory = deque(maxlen=REPLAY_MEMORY_SIZE)
    
    epsilon = EPSILON_START
    best_reward = -float('inf')
    step_count = 0

    for episode in range(1, 1001):
        state = preprocess_state(env.reset())
        done = False
        total_reward = 0
        
        while not done:
            action = epsilon_greedy(state, epsilon, policy_net)
            next_state, reward, done, _ = env.step(action)
            next_state = preprocess_state(next_state)
            
            memory.append((state, action, reward, next_state, done))
            state = next_state
            total_reward += reward
            step_count += 1
            epsilon = max(EPSILON_END, epsilon * EPSILON_DECAY)

            # Entraînement
            if len(memory) >= BATCH_SIZE:
                batch = random.sample(memory, BATCH_SIZE)
                states, actions, rewards, next_states, dones = zip(*batch)
                
                states = torch.FloatTensor(np.array(states)).to(device)
                next_states = torch.FloatTensor(np.array(next_states)).to(device)
                actions = torch.LongTensor(actions).to(device)
                rewards = torch.FloatTensor(rewards).to(device)
                dones = torch.BoolTensor(dones).to(device)

                current_q = policy_net(states).gather(1, actions.unsqueeze(1))
                
                with torch.no_grad():
                    next_q = target_net(next_states).max(1)[0]
                    target_q = rewards + (GAMMA * next_q * ~dones)

                loss = nn.SmoothL1Loss()(current_q.squeeze(), target_q)
                optimizer.zero_grad()
                loss.backward()
                torch.nn.utils.clip_grad_norm_(policy_net.parameters(), 1.0)
                optimizer.step()

            # Mise à jour du réseau cible
            if step_count % TARGET_UPDATE_FREQ == 0:
                target_net.load_state_dict(policy_net.state_dict())

        # Évaluation et logging
        if episode % EVAL_FREQ == 0:
            eval_reward = evaluate_agent(policy_net, env)
            print(f"Episode {episode} | Train Reward: {total_reward:.1f} | Eval Reward: {eval_reward:.1f} | Epsilon: {epsilon:.3f}")
            
            if eval_reward > best_reward:
                print("Saved")
                torch.save(policy_net.state_dict(), f"pong_best.pth")
                best_reward = eval_reward

    env.close()
