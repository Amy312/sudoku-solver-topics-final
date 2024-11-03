import gradio as gr
import requests
from io import BytesIO
from PIL import Image

port = 3000
API_URL = f"http://127.0.0.1:{port}/solve_sudoku_from_image"

def solve_sudoku_from_image(image):
    if image is None:
        return "⚠️ Error: No image was uploaded. Please upload or capture a Sudoku image to continue."
    
    try:
        img_byte_arr = BytesIO()
        image.save(img_byte_arr, format='PNG')
        img_byte_arr.seek(0)
        
        response = requests.post(API_URL, files={'file': ('image.png', img_byte_arr, 'image/png')})
        
        if response.status_code == 200:
            try:
                solved_image = Image.open(BytesIO(response.content))
                return solved_image
            except Exception:
                return "⚠️ The Sudoku puzzle could not be processed. Please try again with a clearer image."
        else:
            return f"⚠️ The Sudoku puzzle could not be solved. Server response code: {response.status_code}"
    except Exception as e:
        return f"⚠️ An error occurred while processing the image. Please try again. Details: {str(e)}"

interface = gr.Interface(
    fn=solve_sudoku_from_image,
    inputs=gr.Image(
        type="pil", 
        label="Upload or Capture Sudoku Image", 
        source="upload",
        tool="editor",
        mirror_webcam=False
    ),
    outputs="image",
    title="Sudoku Solver - AI-Powered",
    description=(
        "📸 **Upload or capture an image of a Sudoku puzzle** and let our AI-powered solver process and solve it for you! "
        "The solution will be displayed as an image with the completed puzzle.\n\n"
        "Please make sure the Sudoku is clear and well-lit for the best results. "
        "If any issues arise, simply try again with a different image."
    ),
    examples=[["sample_sudoku_image.png"]],
    theme="default",
    allow_flagging="never"
)

if __name__ == "__main__":
    interface.launch()
