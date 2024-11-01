from fastapi import FastAPI, UploadFile, File
from fastapi.responses import StreamingResponse
from solver import solve_sudoku
from gradio_interface import launch_gradio_interface
from image_processing import process_image, board_to_image
from utils.json_formater import json_formater
from segmentation.sudoku_bound_detector import SudokuBoundDetector
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

@app.post("/display-original/")
async def display_original_image(file: UploadFile = File(...)):
    try:
        image = await file.read()
        with open("temp_image.png", "wb") as f:
            f.write(image)
        img = detector.read_img("temp_image.png")
        detector.display_img(img)
        return json_formater("Original image displayed successfully.")
    except Exception as err:
        return json_formater(f"Error displaying original image: {err}", is_err=True)

@app.post("/get-detection/")
async def get_detection(file: UploadFile = File(...)):
    try:
        image = await file.read()
        with open("temp_image.png", "wb") as f:
            f.write(image)
        detection = detector.get_detection("temp_image.png")
        box_coordinates = detection.boxes.xyxy.tolist()
        return json_formater("Bounding box coordinates detected.", data=box_coordinates)
    except Exception as err:
        return json_formater(f"Error getting detection: {err}", is_err=True)

@app.post("/get-crop-box/")
async def get_crop_box(file: UploadFile = File(...)):
    try:
        image = await file.read()
        with open("temp_image.png", "wb") as f:
            f.write(image)
        cropped_image = detector.get_crop_box("temp_image.png")
        _, encoded_image = cv2.imencode(".png", cropped_image)
        return StreamingResponse(io.BytesIO(encoded_image.tobytes()), media_type="image/png")
    except Exception as err:
        return json_formater(f"Error cropping Sudoku box: {err}", is_err=True)

@app.post("/display-crop-box/")
async def display_crop_box(file: UploadFile = File(...)):
    try:
        image = await file.read()
        with open("temp_image.png", "wb") as f:
            f.write(image)
        detector.show_crop_box("temp_image.png")
        return json_formater("Cropped Sudoku box displayed successfully.")
    except Exception as err:
        return json_formater(f"Error displaying cropped box: {err}", is_err=True)

@app.post("/correct-sudoku-area/")
async def correct_sudoku_area(file: UploadFile = File(...)):
    try:
        image = await file.read()
        with open("temp_image.png", "wb") as f:
            f.write(image)
        prediction = detector.get_detection("temp_image.png")
        orig_img = prediction.orig_img
        contour = prediction.masks.xy[0]
        corrected_image = detector.correct_area(orig_img, contour)
        _, encoded_image = cv2.imencode(".png", corrected_image)
        return StreamingResponse(io.BytesIO(encoded_image.tobytes()), media_type="image/png")
    except Exception as err:
        return json_formater(f"Error correcting Sudoku area: {err}", is_err=True)

@app.post("/display-corrected-sudoku/")
async def display_corrected_sudoku(file: UploadFile = File(...)):
    try:
        image = await file.read()
        with open("temp_image.png", "wb") as f:
            f.write(image)
        detector.display_corrected_sudoku("temp_image.png")
        return json_formater("Corrected and cleaned Sudoku box displayed successfully.")
    except Exception as err:
        return json_formater(f"Error displaying corrected Sudoku box: {err}", is_err=True)

@app.post("/get-final-image/")
async def get_final_image(file: UploadFile = File(...)):
    try:
        image = await file.read()
        with open("temp_image.png", "wb") as f:
            f.write(image)
        img_bytes = detector.process_and_return_corrected_image("temp_image.png")
        return StreamingResponse(img_bytes, media_type="image/png")
    except Exception as err:
        return json_formater(f"Error processing final image: {err}", is_err=True)

@app.post("/get_jpg_processed_image")
async def detect_sudoku_from_image(file: UploadFile = File(...)):
    try:
        img_bytes = await file.read()
        with open("temp_image.png", "wb") as temp_file:
            temp_file.write(img_bytes)

        img_bytes = detector.process_and_return_corrected_image("temp_image.png")

        headers = {
            'Content-Disposition': 'attachment; filename="corrected_sudoku.png"'
        }
        return StreamingResponse(img_bytes, media_type="image/png", headers=headers)

    except Exception as err:
        print('detect_sudoku_from_image:', err)
        return json_formater(
            message='Error while detecting sudoku from image',
            is_err=True,
            code_err=500
        )

if __name__ == "__main__":
    # LAUNCH GRADIO
    # launch_gradio_interface()
    
    # LAUNCH API
    import uvicorn
    port = 3000
    print(f'Proyect running, test on: http://127.0.0.1:{port}/docs')
    uvicorn.run("main:app", reload=True, port=3000)
