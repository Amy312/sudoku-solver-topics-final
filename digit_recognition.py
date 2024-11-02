import cv2
import numpy as np
from PIL import Image
import os
import timm
import torch
from torchvision import transforms
import matplotlib.pyplot as plt

def load_digit_model():
    classes = [str(i) for i in range(10)]
    num_classes = len(classes)
    model = timm.create_model("rexnet_150", pretrained=False, num_classes=num_classes)
    model.load_state_dict(torch.load("./models/digits_best_model.pth", map_location=torch.device('cpu')))
    model.eval()
    return model

def preprocess_sudoku_image(image_path):
    image = cv2.imread(image_path)
    if image is None:
        print(f"Error al cargar la imagen desde {image_path}")
        return None

    max_dim = 1000
    if max(image.shape) > max_dim:
        scale = max_dim / max(image.shape)
        image = cv2.resize(image, (int(image.shape[1]*scale), int(image.shape[0]*scale)), interpolation=cv2.INTER_AREA)

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray, (5, 5), 0)
    thresh = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                   cv2.THRESH_BINARY_INV, 11, 2)
    return thresh

def recognize_digits(image):
    model = load_digit_model()
    transform = transforms.Compose([
        transforms.Resize((224, 224)),  
        transforms.ToTensor(),
        transforms.Normalize([0.485, 0.456, 0.406], 
                             [0.229, 0.224, 0.225])
    ])
    digits = np.zeros((9, 9), dtype=int)
    height, width = image.shape
    cell_height = height // 9
    cell_width = width // 9

    for row in range(9):
        for col in range(9):
            y_start = row * cell_height
            x_start = col * cell_width
            y_end = y_start + cell_height
            x_end = x_start + cell_width
            cell = image[y_start:y_end, x_start:x_end]

            margin = int(cell_height * 0.161)  
            cell = cell[margin:-margin, margin:-margin]

            cell = clean_cell_image(cell)

            if is_cell_empty(cell):
                digits[row, col] = 0  # Celda vacía
                print(f'Celda ({row}, {col}) vacía')
                # Mostrar la celda vacía
                #plt.imshow(cell, cmap='gray')
                #plt.title(f'Celda ({row}, {col}) - Vacía')
                #plt.axis('off')
                #plt.show()
            else:
                cell_rgb = cv2.cvtColor(cell, cv2.COLOR_GRAY2RGB)
                cell_pil = Image.fromarray(cell_rgb)
                cell_transformed = transform(cell_pil).unsqueeze(0)

                with torch.no_grad():
                    output = model(cell_transformed)
                    probabilities = torch.nn.functional.softmax(output, dim=1)
                    predicted_digit = output.argmax(dim=1).item()
                    confidence = probabilities[0, predicted_digit].item()

                digits[row, col] = predicted_digit
                print(f'Celda ({row}, {col}) predicción: {predicted_digit} con confianza: {confidence:.2f}')
                # Mostrar la celda preprocesada y la predicción
                #plt.imshow(cell, cmap='gray')
                #plt.title(f'Celda ({row}, {col}) - Pred: {predicted_digit}\nConfianza: {confidence:.2f}')
                #plt.axis('off')
                #plt.show()

    return digits

def clean_cell_image(cell):
    kernel = np.ones((3, 3), np.uint8)
    cell = cv2.morphologyEx(cell, cv2.MORPH_OPEN, kernel)
    cell = cv2.morphologyEx(cell, cv2.MORPH_CLOSE, kernel)
    cell = cv2.GaussianBlur(cell, (3, 3), 0)
    return cell

def is_cell_empty(cell):
    non_zero_pixels = cv2.countNonZero(cell)
    total_pixels = cell.shape[0] * cell.shape[1]
    ratio = non_zero_pixels / total_pixels
    if ratio < 0.1:  # Ajusta este umbral según tus necesidades
        return True
    else:
        return False


image_path = "./assets/s1.jpeg"
processed_image = preprocess_sudoku_image(image_path)
if processed_image is not None:
    recognized_digits = recognize_digits(processed_image)
    print("Dígitos Reconocidos:")
    print(recognized_digits)
else:
    print("No se pudo procesar la imagen del Sudoku.")
