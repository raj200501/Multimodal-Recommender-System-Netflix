import transformers
from transformers import GPT2Tokenizer, GPT2LMHeadModel

class NLPModel:
    def __init__(self, model_name='gpt2'):
        self.tokenizer = GPT2Tokenizer.from_pretrained(model_name)
        self.model = GPT2LMHeadModel.from_pretrained(model_name)

    def generate_text(self, prompt, max_length=50):
        inputs = self.tokenizer(prompt, return_tensors="pt")
        outputs = self.model.generate(inputs["input_ids"], max_length=max_length, num_return_sequences=1)
        return self.tokenizer.decode(outputs[0], skip_special_tokens=True)

if __name__ == "__main__":
    nlp_model = NLPModel()
    prompt = "Once upon a time"
    generated_text = nlp_model.generate_text(prompt)
    print(f"Generated Text: {generated_text}")
