import torch
import cv2
import numpy as np
from torchvision import transforms

def load_digit_model():
    # Cargar el modelo entrenado
    model = torch.load("models/digit_best_model.pth")
    model.eval()
    return model

def recognize_digits(image):
    model = load_digit_model()
    transform = transforms.Compose([
        transforms.Grayscale(),
        transforms.Resize((28, 28)),
        transforms.ToTensor(),
        transforms.Normalize((0.5,), (0.5,))
    ])

    # Divide la imagen en 9x9 celdas y reconoce los números
    digits = np.zeros((9, 9), dtype=int)
    cell_height, cell_width = image.shape[0] // 9, image.shape[1] // 9

    for row in range(9):
        for col in range(9):
            cell = image[row * cell_height:(row + 1) * cell_height, col * cell_width:(col + 1) * cell_width]
            cell = transform(cell).unsqueeze(0)  # Añadir batch dimension
            with torch.no_grad():
                output = model(cell)
                predicted_digit = output.argmax(dim=1).item()
                digits[row, col] = predicted_digit

    return digits
