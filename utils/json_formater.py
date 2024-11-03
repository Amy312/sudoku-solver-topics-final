import numpy as np
from fastapi import HTTPException
from fastapi.responses import JSONResponse, StreamingResponse
from typing import Union, List
from image_processing import board_to_image
import io

def convert_ndarray_to_list(data: Union[np.ndarray, List[np.ndarray]]):
  """Recursively convert NumPy ndarrays to lists."""
  if isinstance(data, np.ndarray):
    return data.tolist()
  elif isinstance(data, list):
    return [convert_ndarray_to_list(item) for item in data]
  return data

def get_final_matrix(data: Union[np.ndarray, List[np.ndarray]]):
  data = convert_ndarray_to_list(data)
  return data[0]

def json_formater(data=None, is_err=False, code_err=500, message=None):
  """Format the data into a JSON format."""
  if not is_err and data != None:
    if isinstance(data['data'], np.ndarray) or isinstance(data['data'][0], np.ndarray):
      data['data'] = convert_ndarray_to_list(data['data'])
      data['data'] = data['data'][0]
    print('type list: ', type(data['data']))
    print('data: ', data['data'])
    return JSONResponse(content=data, status_code=200)
  else:
    raise HTTPException(status_code=code_err, detail=message)

def board_formater(board: list[list[int]]):
  img = board_to_image(board)
    
  img_bytes = io.BytesIO()
  img.save(img_bytes, format="PNG")
  img_bytes.seek(0)
  
  headers = {
      'Content-Disposition': 'attachment; filename="sudoku_board.png"'
  }
  return StreamingResponse(img_bytes, media_type="image/png", headers=headers)
