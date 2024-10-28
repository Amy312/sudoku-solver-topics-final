from fastapi import FastAPI, UploadFile, File
from fastapi.responses import StreamingResponse
from solver import solve_sudoku
from gradio_interface import launch_gradio_interface
from image_processing import process_image, board_to_image
from utils.json_formater import json_formater
import io

app = FastAPI()

@app.post("/solve")
async def solve_sudoku_manual(board: list[list[int]]):
    try:
        solved_board = solve_sudoku(board)
        print('solve_sudoku_manual: Sudoku solved')
        return json_formater(
            data={
                "solved_board": solved_board
            },
            message='Sudoku solved'
        )
    except Exception as err:
        print('solve_sudoku_manual:', err)
        return json_formater(
            message='Sudoku can not be solved',
            is_err=True,
            code_err=err
        )

@app.post("/process_sent_image")
async def process_sent_image(file: UploadFile = File(...)):
    try:
        processed_image, board = process_image(await file.read())
        print('process_sent_image: Image processed correctly')
        return json_formater(
            data={
                'board_gotten': board,
                'processed_image': processed_image,
            },
            message='Image processed correctly'
        )
    except Exception as err:
        print('process_sent_image: ',err)
        return json_formater(
            message='Error while processing image',
            is_err=True,
            code_err=500
        )

@app.post("/board_to_image")
async def create_board_to_image(board: list[list[int]]):
    try:
        img = board_to_image(board)
        
        img_bytes = io.BytesIO()
        img.save(img_bytes, format="PNG")
        img_bytes.seek(0)
        
        headers = {
            'Content-Disposition': 'attachment; filename="sudoku_board.png"'
        }
        return StreamingResponse(img_bytes, media_type="image/png", headers=headers)

    except Exception as err:
        print('board_to_image: ',err)
        return json_formater(
            message='Error while processing board',
            is_err=True,
            code_err=500
        )

@app.post("/solve_from_image")
async def solve_sudoku_from_image(file: UploadFile = File(...)):
    processed_image, board = process_image(await file.read())
    solved_board = solve_sudoku(board)
    return {"solved_board": solved_board}

if __name__ == "__main__":
    launch_gradio_interface()
