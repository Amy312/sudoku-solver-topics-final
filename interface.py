import gradio as gr
import requests
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
import tempfile

port = 3000
API_IMAGE_URL = f"http://127.0.0.1:{port}/get_solved_sudoku_image_from_image"
API_MATRIX_URL = f"http://127.0.0.1:{port}/get_solved_board_matrix_from_image"
API_SOLVE_MATRIX_URL = f"http://127.0.0.1:{port}/get_solved_sudoku_image_from_board_matrix"

def get_sudoku_solution_image(image):
    if image is None:
        return "⚠️ Error: No image was uploaded. Please upload or capture a Sudoku image to continue."

    try:
        img_byte_arr = BytesIO()
        image.save(img_byte_arr, format='PNG')
        img_byte_arr.seek(0)

        response = requests.post(API_IMAGE_URL, files={'file': ('image.png', img_byte_arr, 'image/png')})

        if response.status_code == 200:
            solved_image = Image.open(BytesIO(response.content))
            return solved_image
        else:
            return f"⚠️ The Sudoku puzzle could not be solved. Server response code: {response.status_code}"
    except Exception as e:
        return f"⚠️ An error occurred while processing the image. Please try again. Details: {str(e)}"

def solve_edited_sudoku(matrix):
    try:
        matrix = [[int(cell) if cell not in ("", None) else 0 for cell in row] for row in matrix]
        payload = matrix
        response = requests.post(API_SOLVE_MATRIX_URL, json=payload)

        if response.status_code == 200:
            img_byte_arr = BytesIO(response.content)
            solved_image = Image.open(img_byte_arr)
            return solved_image
        else:
            return f"⚠️ The Sudoku puzzle could not be solved. Server response code: {response.status_code}"
    except Exception as e:
        return f"⚠️ An error occurred while processing the matrix. Details: {str(e)}"

def get_sudoku_solution_matrix(image):
    if image is None:
        return None, "⚠️ Error: No image was uploaded."

    try:
        img_byte_arr = BytesIO()
        image.save(img_byte_arr, format='PNG')
        img_byte_arr.seek(0)

        response = requests.post(API_MATRIX_URL, files={'file': ('image.png', img_byte_arr, 'image/png')})

        if response.status_code == 200:
            data = response.json().get('data')
            if data and len(data) == 9 and all(len(row) == 9 for row in data):
                return data, None
            else:
                return None, "⚠️ Error: Invalid matrix format received. Ensure the solution is a 9x9 grid."
        else:
            return None, f"⚠️ Error retrieving matrix. Server response code: {response.status_code}"
    except Exception as e:
        return None, f"⚠️ An error occurred. Details: {str(e)}"

with gr.Blocks() as interface:
    sudoku_image = gr.Image(type="pil", label="Upload or Capture Sudoku Image")

    solve_button = gr.Button("Solve Sudoku")
    solution_image = gr.Image(label="Solved Sudoku Image")
    solution_matrix = gr.Matrix(label="Solved Sudoku Matrix", interactive=True, value=[[0] * 9 for _ in range(9)])
    error_message = gr.Textbox(label="Error Message", visible=False)

    solve_edited_button = gr.Button("Solve Edited Sudoku")
    solved_edited_image = gr.Image(label="Solved Edited Sudoku Image")

    def handle_solution(image):
        matrix, error = get_sudoku_solution_matrix(image)
        if error:
            return None, error, gr.update(visible=True)
        return matrix, None, gr.update(visible=False)

    solve_button.click(
        fn=lambda image: (get_sudoku_solution_image(image), *handle_solution(image)),
        inputs=sudoku_image,
        outputs=[solution_image, solution_matrix, error_message]
    )

    solve_edited_button.click(
        fn=solve_edited_sudoku,
        inputs=solution_matrix,
        outputs=solved_edited_image
    )

if __name__ == "__main__":
    interface.launch()
