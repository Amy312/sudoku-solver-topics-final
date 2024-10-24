import gradio as gr
import requests

def solve_sudoku_manual(board):
    response = requests.post("http://127.0.0.1:8000/solve", json={"board": board})
    return response.json().get("solved_board")

def solve_sudoku_image(image):
    files = {'file': image}
    response = requests.post("http://127.0.0.1:8000/solve_from_image", files=files)
    return response.json().get("solved_board")

def launch_gradio_interface():
    sudoku_interface = gr.Interface(
        fn=solve_sudoku_manual,
        inputs=gr.Textbox(label="Enter Sudoku values (9x9 matrix)"),
        outputs="json",
    )

    image_interface = gr.Interface(
        fn=solve_sudoku_image,
        inputs="image",
        outputs="json",
    )

    gr.TabbedInterface([sudoku_interface, image_interface], ["Manual Entry", "Upload Image"]).launch()
