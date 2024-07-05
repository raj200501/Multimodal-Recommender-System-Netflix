import torch
import torchvision.models as models
from torchvision import transforms
from PIL import Image

class CVModel:
    def __init__(self):
        self.model = models.resnet50(pretrained=True)
        self.model.eval()
        self.preprocess = transforms.Compose([
            transforms.Resize(256),
            transforms.CenterCrop(224),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
        ])

    def predict(self, image_path):
        image = Image.open(image_path)
        image = self.preprocess(image)
        image = image.unsqueeze(0)
        with torch.no_grad():
            output = self.model(image)
        return output.argmax().item()

if __name__ == "__main__":
    cv_model = CVModel()
    prediction = cv_model.predict('sample_image.jpg')
    print(f"Predicted Class: {prediction}")
