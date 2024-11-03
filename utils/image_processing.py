import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

def board_to_image(board: list[list[int]], cell_size=50, line_thickness=2):
    board_size = cell_size * 9
    img = Image.new("RGB", (board_size, board_size), "white")
    draw = ImageDraw.Draw(img)

    font_size = int(cell_size * 2)
    try:
        font = ImageFont.truetype("arial.ttf", font_size)
    except IOError:
        font = ImageFont.load_default()

    for row in range(9):
        for col in range(9):
            x0, y0 = col * cell_size, row * cell_size
            x1, y1 = x0 + cell_size, y0 + cell_size
            
            draw.rectangle([x0, y0, x1, y1], outline="gray", width=line_thickness)

            if row % 3 == 0:
                draw.line([(0, y0), (board_size, y0)], fill="black", width=line_thickness * 2)
            if col % 3 == 0:
                draw.line([(x0, 0), (x0, board_size)], fill="black", width=line_thickness * 2)

            if board[row][col] != 0:
                text = str(board[row][col])
                bbox = font.getbbox(text)
                text_width, text_height = bbox[2] - bbox[0], bbox[3] - bbox[1]
                text_x = x0 + (cell_size - text_width) / 2
                text_y = y0 + (cell_size - text_height) / 2
                draw.text((text_x, text_y), text, fill="black", font=font)

    draw.line([(0, board_size - 1), (board_size - 1, board_size - 1)], fill="black", width=line_thickness * 2)
    draw.line([(board_size - 1, 0), (board_size - 1, board_size - 1)], fill="black", width=line_thickness * 2)

    return img
