# YOLO SÉ: Reconocimiento y Solución de Sudokus mediante Visión Artificial

## Descripción
Este proyecto, desarrollado como parte de la asignatura "Tópicos Selectos en Inteligencia Artificial" en la Universidad Privada Boliviana, explora la aplicación de visión por computadora para la identificación y resolución automática de Sudokus. Utilizando redes neuronales avanzadas y técnicas de segmentación, el sistema detecta una cuadrícula de Sudoku en una imagen, identifica los dígitos en cada celda y resuelve el rompecabezas, mostrando el resultado en tiempo real.

## Equipo
- **Ander Michael Cayllan Mamani** - 63428
- **Ambar Mónica Rojas Morales** - 61375
- **José Samuel Carrasco Encinas** - 63003

**Docente:** Ing. José Eduardo Laruta Espejo
**Fecha:** 4 de noviembre de 2024  
**Ubicación:** La Paz, Bolivia

## Objetivos
### Objetivo General
Desarrollar un sistema basado en visión por computadora capaz de reconocer y resolver Sudokus a partir de imágenes, utilizando técnicas de detección de objetos y segmentación.

### Objetivos Específicos
1. **Implementación de detección y segmentación**: Usar modelos como YOLOv11 y OpenCV para detectar y segmentar la cuadrícula de Sudoku.
2. **Pipeline de procesamiento de imágenes**: Extraer la cuadrícula, identificar dígitos y preparar datos para la resolución del Sudoku.
3. **Resolución automática**: Integrar un algoritmo que genere la solución en tiempo real.

## Descripción Técnica
### Técnicas Empleadas
- **Detección de objetos**: Utiliza bounding boxes para localizar la cuadrícula del Sudoku en la imagen.
- **Segmentación de imágenes**: Divide la cuadrícula en celdas individuales, lo cual permite identificar y procesar cada dígito.
  
### Modelos y Herramientas
- **YOLOv11**: Modelo avanzado de detección de objetos, ajustado con un dataset de imágenes de Sudokus para segmentar correctamente la cuadrícula.
- **ReXNet_150**: Modelo para la identificación de dígitos, adaptado para clasificar dígitos de 0 a 9, con pesos preentrenados en ImageNet.

### Preparación y Entrenamiento de Modelos
- **Dataset**: Imágenes de Sudokus segmentadas y etiquetadas con Roboflow.
- **Entrenamiento de ReXNet_150**: Adaptación de la capa de salida para detectar 10 clases (0-9) y entrenado con un optimizador Adam y función de pérdida CrossEntropyLoss.
- **Detección de dígitos**: Aplicación de procesamiento de imagen (filtros, binarización y morfología) para mejorar la precisión en la detección de dígitos individuales en cada celda.

## API y Endpoints
El sistema incluye una API que permite la interacción a través de los siguientes endpoints:

1. **`get_solved_sudoku_from_number_matrix`**  
   - Recibe una matriz de números y devuelve la solución del Sudoku en forma de matriz.

2. **`get_solved_board_matrix_from_image`**  
   - Recibe una imagen del Sudoku y devuelve una matriz de números con la solución.

3. **`get_solved_sudoku_image_from_board_matrix`**  
   - Recibe una matriz numérica y devuelve la imagen del Sudoku resuelto.

4. **`get_solved_sudoku_image_from_image`**  
   - Recibe una imagen del Sudoku y devuelve la solución en formato de imagen.

## Estructura del Proyecto
El proyecto está organizado en los siguientes directorios:
- **assets**: Contiene ejemplos para validar la funcionalidad de la API.
- **digits**: Código de detección de dígitos, devolviendo la matriz de números.
- **digits-train**: Archivos de entrenamiento del modelo de dígitos.
- **models**: Modelos de detección y segmentación.
- **segmentation**: Configuración de segmentación de la cuadrícula.
- **utils**: Funciones adicionales para el manejo de datos de entrada y salida.

## Aplicaciones
1. **Aplicación de Sudoku**: Genera la solución de un Sudoku a partir de una imagen o matriz de entrada.
2. **Proyecto Educativo**: Ejemplo práctico para enseñar cómo se detectan números en una imagen.
3. **Micro-servicio**: Implementable en otras APIs para resolver Sudokus u otros puzzles similares.

## Interfaz Gráfica
Para facilitar el uso, se ha desarrollado una interfaz gráfica con Gradio, que permite visualizar y probar los endpoints de la API de manera sencilla.

## Requerimientos del Proyecto
- **Python** >= 3.11.10
- **Bibliotecas**: OpenCV, PyTorch, timm, Gradio, entre otras.

## Instalación
1. Clona este repositorio:
   ```bash
   git clone https://github.com/Amy312/sudoku-solver-topics-final.git
   ```
2. Crea un entorno virtual de python
   ```bash
    conda create -n yolose_solver python=3.11.10
    conda activate yolose_solver
    ```
3. Instala las dependencias:
    ```bash
    pip install -r requirements.txt
    ```
4. Corre el servidor de la API:
    ```bash
    python -m main
    ```
5. Corre la interfaz gráfica:
    ```bash
    python -m interface
    ```   
## Uso
Accede a los endpoints de la API para cargar y resolver Sudokus.
Para interactuar con la interfaz gráfica, abre el archivo ``interface.py`` en Gradio.
