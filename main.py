from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.responses import StreamingResponse, JSONResponse
from utils.solver import solve_sudoku
from utils.image_processing import board_to_image
from utils.json_formater import json_formater, convert_ndarray_to_list, get_final_matrix, board_formater
from segmentation.sudoku_bound_detector import SudokuBoundDetector
from digits.digit_recognition import detect_digits_from_image
from PIL import Image
import cv2
import io

app = FastAPI(title="sudoku solver")

detector = SudokuBoundDetector(model_path="models/sudoku_bound_detector_30e.pt")

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
@app.post("/solve_sudoku_by_number_matrix")
async def solve_sudoku_by_number_matrix(board: list[list[int]]):
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
                "message": 'Sudoku solved',
                "data": solved_board
            },
        )
    except Exception as err:
        print('solve_sudoku_manual:', err)
        return json_formater(
            message='Sudoku can not be solved',
            is_err=True,
            code_err=err
        )

@app.post("/get_solved_board_matrix_from_image")
async def get_solved_board_matrix_from_image(file: UploadFile = File(...)):
    try:
        image = await file.read()
        with open("temp_image.png", "wb") as f:
            f.write(image)
        
        img_bytes = detector.process_and_return_corrected_image("temp_image.png")
        
        processed_image = img_bytes.getvalue()
        
        with open("processed_image.png", "wb") as f:
            f.write(processed_image)
        
        path_processed_image = './processed_image.png'
        
        board = detect_digits_from_image(path=path_processed_image)
        
        if len(board) == 0 or len(board[0]) == 0:
            return json_formater(
                    message='Could not detect digits',
                    is_err=True,
                    code_err=500
                )
        
        print('process_sent_image: Image processed correctly')

        return json_formater(
                data={
                    "message": "Image processed correctly to board",
                    "data": board
                },
            )

    except Exception as err:
        print('process_sent_image:', err)
        return json_formater(
                message='Error while processing image',
                is_err=True,
                code_err=500
            )

@app.post("/process_sent_image_to_sudoku_image")
async def process_sent_image_to_sudoku_image(file: UploadFile = File(...)):
    try:
        image = await file.read()
        with open("temp_image.png", "wb") as f:
            f.write(image)
        
        img_bytes = detector.process_and_return_corrected_image("temp_image.png")
        
        processed_image = img_bytes.getvalue()
        
        with open("processed_image.png", "wb") as f:
            f.write(processed_image)
        
        path_processed_image = './processed_image.png'
        
        board = detect_digits_from_image(path=path_processed_image)
        
        board = convert_ndarray_to_list(board)
        
        if len(board) == 0 or len(board[0]) == 0:
            return json_formater(
                    message='Could not detect digits',
                    is_err=True,
                    code_err=500
                )
        
        print('process_sent_image: Image processed correctly')

        board = get_final_matrix(board)
        return board_formater(board)

    except Exception as err:
        print('process_sent_image:', err)
        return json_formater(
                message='Error while processing image',
                is_err=True,
                code_err=500
            )

@app.post("/solve_sudoku_from_board_matrix")
async def solve_from_board_to_image(board: list[list[int]]):
    try:
        solved_board = solve_sudoku(board)
        
        if(len(solved_board) == 0):
            return json_formater(
                message='Sudoku does not have a solution',
                is_err=True,
                code_err=500
            )
        
        return board_formater(solved_board)

    except Exception as err:
        print('board_to_image: ',err)
        return json_formater(
            message='Error while processing board',
            is_err=True,
            code_err=500
        )

@app.post("/solve_sudoku_from_image")
async def solve_sudoku_from_image(file: UploadFile = File(...)):
    try:
        image = await file.read()
        with open("temp_image.png", "wb") as f:
            f.write(image)
        
        img_bytes = detector.process_and_return_image("temp_image.png")
        
        processed_image = img_bytes.getvalue()
        
        with open("processed_image.png", "wb") as f:
            f.write(processed_image)
        
        path_processed_image = './processed_image.png'
        
        board = detect_digits_from_image(path=path_processed_image)
        
        board = get_final_matrix(board)
        
        solved_board = solve_sudoku(board)
        
        if len(solved_board) == 0:
            raise HTTPException(status_code=500, detail="Sudoku does not have a solution")
        img = board_to_image(solved_board)
        img_bytes = io.BytesIO()
        img.save(img_bytes, format="PNG")
        img_bytes.seek(0)
        
        print('solve_sudoku_from_image: BOARD SOLVED')
        
        return StreamingResponse(img_bytes, media_type="image/png")
        
    except Exception as err:
        print('solve_sudoku_from_image:', err)
        return json_formater(
            message='Error while solving sudoku from image',
            is_err=True,
            code_err=500
        )

if __name__ == "__main__":
    import uvicorn
    port = 3000
    print(f'Proyect running, test on: http://127.0.0.1:{port}/docs')
    uvicorn.run("main:app", reload=True, port=3000)
