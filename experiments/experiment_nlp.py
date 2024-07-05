from models.nlp_model import NLPModel

def run_experiment():
    nlp_model = NLPModel()
    prompt = "Once upon a time"
    generated_text = nlp_model.generate_text(prompt)
    print(f"Generated Text: {generated_text}")

if __name__ == "__main__":
    run_experiment()
