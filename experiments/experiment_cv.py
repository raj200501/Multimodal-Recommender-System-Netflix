from models.cv_model import CVModel

def run_experiment():
    cv_model = CVModel()
    prediction = cv_model.predict('sample_image.jpg')
    print(f"Predicted Class: {prediction}")

if __name__ == "__main__":
    run_experiment()
