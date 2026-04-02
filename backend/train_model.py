from rl_threat_scorer import train_rl_model

if __name__ == "__main__":
    print("Starting model training...")
    agent = train_rl_model(episodes=1000)
    print("Training completed!")