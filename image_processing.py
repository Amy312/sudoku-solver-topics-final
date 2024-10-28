import cv2
import numpy as np
from yolo import detect_sudoku
from PIL import Image, ImageDraw, ImageFont

def process_image(image_bytes):
    np_arr = np.frombuffer(image_bytes, np.uint8)
    image = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

    sudoku_coords = detect_sudoku(image)

    if sudoku_coords:
        corners = adjust_perspective(image, sudoku_coords)
        processed_image = apply_filters(corners)
        board = extract_numbers(processed_image)
        return processed_image, board
    else:
        raise ValueError("Sudoku not found in the image")

def board_to_image(board: list[list[int]], cell_size=50, line_thickness=2):
    board_size = cell_size * 9
    img = Image.new("RGB", (board_size, board_size), "white")
    draw = ImageDraw.Draw(img)

    try:
        font = ImageFont.truetype("arial.ttf", cell_size // 2)
    except IOError:
        font = ImageFont.load_default()

    for row in range(9):
        for col in range(9):
            x0, y0 = col * cell_size, row * cell_size
            x1, y1 = x0 + cell_size, y0 + cell_size

            if row % 3 == 0:
                draw.line([(0, y0), (board_size, y0)], fill="black", width=line_thickness * 2)
            if col % 3 == 0:
                draw.line([(x0, 0), (x0, board_size)], fill="black", width=line_thickness * 2)

            if board[row][col] != 0:
                text = str(board[row][col])
                text_width, text_height = draw.textsize(text, font=font)
                text_x = x0 + (cell_size - text_width) / 2
                text_y = y0 + (cell_size - text_height) / 2
                draw.text((text_x, text_y), text, fill="black", font=font)

    draw.line([(0, board_size - 1), (board_size - 1, board_size - 1)], fill="black", width=line_thickness * 2)
    draw.line([(board_size - 1, 0), (board_size - 1, board_size - 1)], fill="black", width=line_thickness * 2)

    return img

def adjust_perspective(image, corners):
    # Implementar lógica para ajustar la perspectiva
    pass

def apply_filters(image):
    # Implementar lógica de filtros para mejorar la visualización
    pass

def extract_numbers(image):
    # Utilizar el modelo para identificar números y casillas vacías
    pass
