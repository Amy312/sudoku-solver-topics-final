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

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    # Puedes agregar más pasos de preprocesamiento si es necesario
    return gray

def recognize_digits(image):
    model = load_digit_model()

    transform = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize([0.485, 0.456, 0.406],
                             [0.229, 0.224, 0.225])
    ])

    digits = np.zeros((9, 9), dtype=int)
    cell_height = image.shape[0] // 9
    cell_width = image.shape[1] // 9

    for row in range(9):
        for col in range(9):
            cell = image[row * cell_height:(row + 1) * cell_height,
                         col * cell_width:(col + 1) * cell_width]

            # La celda ya está en escala de grises
            cell_gray = cell

            # Aplicar umbralización para resaltar el dígito
            _, thresh = cv2.threshold(cell_gray, 128, 255, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)
            cell_preprocessed = thresh

            # Comprobar si la celda está vacía basándose en los píxeles no negros
            if is_cell_empty(cell_preprocessed):
                digits[row, col] = 0  # Representa una celda vacía
                print(f'Celda ({row}, {col}) vacía (por píxeles)')
                # Mostrar la imagen preprocesada de la celda vacía
                #plt.imshow(cell_preprocessed, cmap='gray')
                #plt.title(f'Celda ({row}, {col}) - Vacía')
                #plt.axis('off')
                #plt.show()
            else:
                # Convertir de escala de grises a RGB
                cell_rgb = cv2.cvtColor(cell_preprocessed, cv2.COLOR_GRAY2RGB)
                cell_pil = Image.fromarray(cell_rgb)
                cell_transformed = transform(cell_pil).unsqueeze(0)

                with torch.no_grad():
                    output = model(cell_transformed)
                    probabilities = torch.nn.functional.softmax(output, dim=1)
                    predicted_digit = output.argmax(dim=1).item()
                    confidence = probabilities[0, predicted_digit].item()

                # Si la confianza es menor a 0.98, consideramos la celda como vacía
                if confidence < 0.99:
                    digits[row, col] = 0
                    print(f'Celda ({row}, {col}) vacía (baja confianza: {confidence:.2f})')
                    # Mostrar la imagen preprocesada de la celda vacía
                    #plt.imshow(cell_preprocessed, cmap='gray')
                    #plt.title(f'Celda ({row}, {col}) - Vacía\nConfianza: {confidence:.2f}')
                    #plt.axis('off')
                    #plt.show()
                else:
                    digits[row, col] = predicted_digit
                    print(f'Celda ({row}, {col}) predicción: {predicted_digit} con confianza: {confidence:.2f}')
                    # Mostrar la imagen preprocesada junto con la predicción y confianza
                    #plt.imshow(cell_preprocessed, cmap='gray')
                    #plt.title(f'Celda ({row}, {col}) - Pred: {predicted_digit}\nConfianza: {confidence:.2f}')
                    #plt.axis('off')
                    #plt.show()

    return digits

def is_cell_empty(cell):
    # Contar los píxeles blancos (valor 255) después de la umbralización inversa
    non_zero_pixels = cv2.countNonZero(cell)
    if non_zero_pixels < (cell.shape[0] * cell.shape[1]) * 0.01:  # Ajusta el umbral según sea necesario
        return True
    else:
        return False

# Uso del código para reconocer los dígitos en una imagen de Sudoku

image_path = "./assets/s2.jpeg"
processed_image = preprocess_sudoku_image(image_path)
if processed_image is not None:
    recognized_digits = recognize_digits(processed_image)
    print("Dígitos Reconocidos:")
    print(recognized_digits)
else:
    print("No se pudo procesar la imagen del Sudoku.")
