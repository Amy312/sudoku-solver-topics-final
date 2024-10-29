from fastapi import FastAPI, UploadFile, File
from fastapi.responses import StreamingResponse
from solver import solve_sudoku
from gradio_interface import launch_gradio_interface
from image_processing import process_image, board_to_image
from utils.json_formater import json_formater
import io

app = FastAPI(title="sudoku solver")

'''
Sample Board:
INPUT:
[
  [5, 3, 0, 0, 7, 0, 0, 0, 0],
  [6, 0, 0, 1, 9, 5, 0, 0, 0],
  [0, 9, 8, 0, 0, 0, 0, 6, 0],
  [8, 0, 0, 0, 6, 0, 0, 0, 3],
  [4, 0, 0, 8, 0, 3, 0, 0, 1],
  [7, 0, 0, 0, 2, 0, 0, 0, 6],
  [0, 6, 0, 0, 0, 0, 2, 8, 0],
  [0, 0, 0, 4, 1, 9, 0, 0, 5],
  [0, 0, 0, 0, 8, 0, 0, 7, 9]
]

OUTPUT:
[
    [ 5, 3, 4, 6, 7, 8, 9, 1, 2 ],
    [ 6, 7, 2, 1, 9, 5, 3, 4, 8 ],
    [ 1, 9, 8, 3, 4, 2, 5, 6, 7 ],
    [ 8, 5, 9, 7, 6, 1, 4, 2, 3 ],
    [ 4, 2, 6, 8, 5, 3, 7, 9, 1 ],
    [ 7, 1, 3, 9, 2, 4, 8, 5, 6 ],
    [ 9, 6, 1, 5, 3, 7, 2, 8, 4 ],
    [ 2, 8, 7, 4, 1, 9, 6, 3, 5 ],
    [ 3, 4, 5, 2, 8, 6, 1, 7, 9 ]
]
'''
@app.post("/solve")
async def solve_sudoku_manual(board: list[list[int]]):
    try:
        solved_board = solve_sudoku(board)
        if(len(solved_board) == 0):
            return json_formater(
                message='Sudoku does not have a solution',
                is_err=True,
                code_err=500
            )
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
        headers = {
            'Content-Disposition': 'attachment; filename="sudoku_board.png"'
        }
        return [json_formater(
            data={
                'board_gotten': board,
            },
            message='Image processed correctly'
        ), StreamingResponse(processed_image, media_type="image/png", headers=headers)]
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

@app.post("/solve_from_board_to_image")
async def solve_from_board_to_image(board: list[list[int]]):
    try:
        solved_board = solve_sudoku(board)
        
        if(len(solved_board) == 0):
            return json_formater(
                message='Sudoku does not have a solution',
                is_err=True,
                code_err=500
            )
        
        img = board_to_image(solved_board)
        
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
    try:
        _, board = process_image(await file.read())
        solved_board = solve_sudoku(board)
        
        img = board_to_image(solved_board)
        
        img_bytes = io.BytesIO()
        img.save(img_bytes, format="PNG")
        img_bytes.seek(0)
        
        headers = {
            'Content-Disposition': 'attachment; filename="sudoku_board.png"'
        }
        
        return [json_formater(
            data={
                'solve_sudoku': board,
            },
            message='Sudoku from image solved correctly'
        ), StreamingResponse(img_bytes, media_type="image/png", headers=headers)]
    except Exception as err:
        print('solve_sudoku_from_image: ',err)
        return json_formater(
            message='Error while solving sudoku from image',
            is_err=True,
            code_err=500
        )

if __name__ == "__main__":
    # LAUNCH GRADIO
    # launch_gradio_interface()
    
    # LAUNCH API
    import uvicorn
    uvicorn.run("main:app", reload=True, port=3000)
