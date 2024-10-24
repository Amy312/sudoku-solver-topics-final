from fastapi import FastAPI, UploadFile, File
from solver import solve_sudoku
from gradio_interface import launch_gradio_interface
from image_processing import process_image

app = FastAPI()

@app.post("/solve")
async def solve_sudoku_manual(board: list[list[int]]):
    solved_board = solve_sudoku(board)
    return {"solved_board": solved_board}

@app.post("/solve_from_image")
async def solve_sudoku_from_image(file: UploadFile = File(...)):
    # Procesar imagen con OpenCV
    processed_image, board = process_image(await file.read())
    solved_board = solve_sudoku(board)
    # Aquí puedes añadir la función que dibuja los resultados en la imagen original
    return {"solved_board": solved_board}

if __name__ == "__main__":
    launch_gradio_interface()
