import torch
import torch.nn as nn
import torch.optim as optim
import numpy as np
from collections import deque, namedtuple
import random
from data_preprocessing import load_and_preprocess_data

# Define experience tuple structure
Experience = namedtuple('Experience', ['state', 'action', 'reward', 'next_state', 'done'])

class ThreatScoringDQN(nn.Module):
    def __init__(self, state_size, action_size):
        super(ThreatScoringDQN, self).__init__()
        
        self.network = nn.Sequential(
            nn.Linear(state_size, 128),
            nn.ReLU(),
            nn.Linear(128, 64),
            nn.ReLU(),
            nn.Linear(64, action_size)
        )
    
    def forward(self, x):
        return self.network(x)

class ThreatScoringAgent:
    def __init__(self, state_size, action_size):
        self.state_size = state_size
        self.action_size = action_size
        
        # DQN network
        self.dqn = ThreatScoringDQN(state_size, action_size)
        self.target_dqn = ThreatScoringDQN(state_size, action_size)
        self.target_dqn.load_state_dict(self.dqn.state_dict())
        
        # Training parameters
        self.memory = deque(maxlen=10000)
        self.batch_size = 64
        self.gamma = 0.95
        self.epsilon = 1.0
        self.epsilon_min = 0.01
        self.epsilon_decay = 0.995
        self.optimizer = optim.Adam(self.dqn.parameters())
        
    def remember(self, state, action, reward, next_state, done):
        self.memory.append(Experience(state, action, reward, next_state, done))
    
    def act(self, state):
        if random.random() < self.epsilon:
            return random.randrange(self.action_size)
        
        with torch.no_grad():
            state_tensor = torch.FloatTensor(state).unsqueeze(0)
            q_values = self.dqn(state_tensor)
            return q_values.argmax().item()
    
    def replay(self):
        if len(self.memory) < self.batch_size:
            return
        
        # Sample batch from memory
        batch = random.sample(self.memory, self.batch_size)
        
        # Prepare batch data
        states = torch.FloatTensor([e.state for e in batch])
        actions = torch.LongTensor([e.action for e in batch])
        rewards = torch.FloatTensor([e.reward for e in batch])
        next_states = torch.FloatTensor([e.next_state for e in batch])
        dones = torch.FloatTensor([e.done for e in batch])
        
        # Current Q values
        current_q = self.dqn(states).gather(1, actions.unsqueeze(1))
        
        # Next Q values
        with torch.no_grad():
            next_q = self.target_dqn(next_states).max(1)[0]
        
        # Target Q values
        target_q = rewards + (1 - dones) * self.gamma * next_q
        
        # Compute loss and update
        loss = nn.MSELoss()(current_q.squeeze(), target_q)
        self.optimizer.zero_grad()
        loss.backward()
        self.optimizer.step()
        
        # Update epsilon
        self.epsilon = max(self.epsilon_min, self.epsilon * self.epsilon_decay)
    
    def update_target_network(self):
        self.target_dqn.load_state_dict(self.dqn.state_dict())

def train_rl_model(episodes=1000):
    # Load preprocessed data
    X_train, X_test, y_train, y_test, _ = load_and_preprocess_data()
    
    if X_train is None:
        return None
    
    # Initialize agent
    state_size = X_train.shape[1]
    action_size = 4  # Different mitigation actions
    agent = ThreatScoringAgent(state_size, action_size)
    
    # Training loop
    for episode in range(episodes):
        total_reward = 0
        
        # Sample a batch of traffic data
        batch_indices = np.random.choice(len(X_train), size=100)
        batch_X = X_train.iloc[batch_indices].values
        batch_y = y_train.iloc[batch_indices]
        
        for state, label in zip(batch_X, batch_y):
            # Get action from agent
            action = agent.act(state)
            
            # Simulate environment response
            is_attack = label != 'BENIGN'
            
            # Define rewards
            if is_attack and action > 0:  # Correct detection and appropriate action
                reward = 1.0
            elif not is_attack and action == 0:  # Correct normal traffic
                reward = 0.5
            else:  # Incorrect classification
                reward = -1.0
            
            # Create next state (simplified)
            next_state = state + np.random.normal(0, 0.1, state.shape)
            
            # Store experience
            agent.remember(state, action, reward, next_state, False)
            
            # Train agent
            agent.replay()
            
            total_reward += reward
        
        # Update target network periodically
        if episode % 10 == 0:
            agent.update_target_network()
        
        if (episode + 1) % 50 == 0:
            print(f"Episode: {episode + 1}, Total Reward: {total_reward:.2f}, Epsilon: {agent.epsilon:.2f}")
    
    return agent

if __name__ == "__main__":
    agent = train_rl_model()
    if agent is not None:
        # Save the model
        torch.save({
            'dqn_state_dict': agent.dqn.state_dict(),
            'target_dqn_state_dict': agent.target_dqn.state_dict(),
            'epsilon': agent.epsilon
        }, r"d:\CyberProject\V2\backend\models\threat_scorer_rl.pt")