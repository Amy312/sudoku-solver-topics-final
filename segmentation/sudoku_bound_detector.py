import cv2
from matplotlib import pyplot as plt
import numpy as np
import torch
from ultralytics import YOLO
import io
from PIL import Image

class SudokuBoundDetector:
    def __init__(self, model_path):
        # Initialize the YOLO model
        self.model = YOLO(model_path)

    def read_img(self, path):
        """Reads an image in grayscale format."""
        return cv2.imread(path, cv2.IMREAD_GRAYSCALE)
    
    def display_img(self, img):
        """Displays an image using matplotlib."""
        plt.imshow(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
        plt.axis('off')
        plt.show()

    def get_detection(self, img_path):
        """Gets the first prediction from the model for a given image path."""
        predictions = self.model.predict(img_path)
        return predictions[0]

    def get_crop_box(self, img_path):
        """Crops the detected sudoku box area from the image."""
        prediction = self.get_detection(img_path)
        orig_img = prediction.orig_img
        coord_crop = torch.tensor([
            [int(box[0]), int(box[1]), int(box[2]), int(box[3])]
            for box in prediction.boxes.xyxy
        ])
        cropped_image = orig_img[
            coord_crop[0][1]: coord_crop[0][3],
            coord_crop[0][0]: coord_crop[0][2]
        ]
        return cropped_image

    def show_crop_box(self, img_path):
        """Displays the cropped box."""
        cropped_box = self.get_crop_box(img_path)
        self.display_img(cropped_box)

    def correct_area(self, orig_img, contour):
        """Corrects the detected sudoku area using perspective transformation."""
        x, y, w, h = cv2.boundingRect(contour)
        side_length = max(w, h)

        epsilon = 0.02 * cv2.arcLength(contour, True)
        approx = cv2.approxPolyDP(contour, epsilon, True)

        if len(approx) != 4:
            src_points = np.array([[x, y], [x + w, y], [x + w, y + h], [x, y + h]], dtype=np.float32)
        else:
            src_points = np.array([point[0] for point in approx], dtype=np.float32)

        src_points = src_points[np.argsort(src_points[:, 1])]
        if src_points[0][0] > src_points[1][0]:
            src_points[[0, 1]] = src_points[[1, 0]]
        if src_points[2][0] < src_points[3][0]:
            src_points[[2, 3]] = src_points[[3, 2]]

        dst_points = np.array([[0, 0], [side_length - 1, 0], 
                               [side_length - 1, side_length - 1], [0, side_length - 1]], dtype=np.float32)

        matrix = cv2.getPerspectiveTransform(src_points, dst_points)
        warped_square = cv2.warpPerspective(orig_img, matrix, (side_length, side_length))
        
        return warped_square

    def display_sudoku(self, img_path):
        """Detects and displays the corrected sudoku area."""
        prediction = self.get_detection(img_path)
        orig_img = prediction.orig_img
        contour = prediction.masks.xy[0]
        final_img = self.correct_area(orig_img, contour)
        self.display_img(final_img)

    def clean_image(self, img):
        """Applies cleaning steps to enhance the sudoku image."""
        proc = cv2.cvtColor(img.copy(), cv2.COLOR_BGR2GRAY)
        proc = cv2.GaussianBlur(proc, (9, 9), 0)
        proc = cv2.adaptiveThreshold(proc, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)
        proc = cv2.bitwise_not(proc, proc)

        kernel = np.array([[0., 1., 0.], [1., 1., 1.], [0., 1., 0.]], np.uint8)
        proc = cv2.erode(proc, kernel, iterations=2)
        proc = cv2.dilate(proc, kernel, iterations=3)
        proc = cv2.morphologyEx(proc, cv2.MORPH_CLOSE, kernel)
        proc = cv2.bitwise_not(proc, proc)

        return proc

    def display_corrected_sudoku(self, img_path):
        """Displays the cleaned and corrected sudoku area."""
        prediction = self.get_detection(img_path)
        orig_img = prediction.orig_img
        contour = prediction.masks.xy[0]
        corrected_img = self.correct_area(orig_img, contour)
        final_img = self.clean_image(corrected_img)
        self.display_img(final_img)

    def process_and_return_corrected_image(self, img_path):
        """Processes the image to detect, correct, and clean the sudoku area, returning the final image as bytes."""
        prediction = self.get_detection(img_path)
        orig_img = prediction.orig_img
        contour = prediction.masks.xy[0]
        corrected_img = self.correct_area(orig_img, contour)
        final_img = self.clean_image(corrected_img)
        
        img_bytes = io.BytesIO()
        final_img = cv2.cvtColor(final_img, cv2.COLOR_GRAY2RGB)
        Image.fromarray(final_img).save(img_bytes, format="PNG")
        img_bytes.seek(0)
        
        return img_bytes

    def process_and_return_image(self, img_path):
        """Processes the image to detect, correct, and clean the sudoku area, returning the final image as bytes."""
        prediction = self.get_detection(img_path)
        orig_img = prediction.orig_img
        contour = prediction.masks.xy[0]
        corrected_img = self.correct_area(orig_img, contour)
        
        img_bytes = io.BytesIO()
        # final_img = cv2.cvtColor(corrected_img, cv2.COLOR_GRAY2RGB)
        Image.fromarray(corrected_img).save(img_bytes, format="PNG")
        img_bytes.seek(0)
        
        return img_bytes

    def return_sudoku(self, img_path):
        """Detects and displays the corrected sudoku area."""
        prediction = self.get_detection(img_path)
        orig_img = prediction.orig_img
        contour = prediction.masks.xy[0]
        final_img = self.correct_area(orig_img, contour)
        return final_img
