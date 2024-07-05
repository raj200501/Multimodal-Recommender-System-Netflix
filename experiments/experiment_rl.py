from models.rl_model import RLModel

def run_experiment():
    rl_model = RLModel()
    rl_model.train()
    state = rl_model.env.reset()
    action = rl_model.predict(state)
    print(f"Predicted Action: {action}")

if __name__ == "__main__":
    run_experiment()
