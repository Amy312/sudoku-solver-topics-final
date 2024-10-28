from fastapi import HTTPException
from typing import Any, Union

def json_formater(message: str, data=None, is_err=False, code_err=500):
  """Format the data into a JSON format."""
  if not is_err and data != None:
    return {
      'message': message,
      'data': data or None
    }
  else:
    raise HTTPException(status_code=code_err, detail=message)
