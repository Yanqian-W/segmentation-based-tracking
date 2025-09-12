# Tracking the outlines of moving objects in the camera

## Objective
This project aims to develop an algorithm to detect moving solid objects in a video, trace their outlines, and locate their centers. 
The algorithm can be applied to videos with complex backgrounds (e.g., grassy surfaces) and is robust to background and object colors. Furthermore, given the camera's intrinsic parameters, the algorithm can display object positions in the 3D camera coordinate system.

## Algorithm Pipeline
- Convert frames to different **color spaces** (GRAY and HSV) and apply **preprocessing** to enhance object features.
- Apply **segmentation** methods (thresholding) to detect object regions.
- Use **background subtraction** (MOG2) to extract moving areas.
- **Post-process** masks to remove noise and filter out small areas.
- **Visualize** object contours, centers, and 3D coordinates relative to the camera.
- Optional operations are to save the processed video or display the processing in real time.

## How to Run
1. Install dependencies:
  ```
  pip install opencv-python numpy
  ```
2. Update input and output video paths in main.py:
  ```
  INPUT_VIDEO_PATH = "trace_objects_3d/resources/PennAir 2024 App Dynamic Hard.mp4"
  OUTPUT_VIDEO_PATH = "trace_objects_3d/output/dynamic_hard_result_3d.mp4"
  ```
3. Tunable parameters for each component:
  - PreProcessing: `method` (options: gaussian, bilateral, median, opening, closing, open_close), `kernel_size`
  - Background Subtractor (MOG2)**: `history`, `varThreshold`, `detectShadows`
  - Segmentation: `method` (options: threshold, canny, kmeans)
  - PostProcessing: `kernel_open`, `kernel_close`, `area_ratio` (for contour filtering)
4. Optional parameters:
  - `VISUALIZE=True` to display results in real time.
  - `SAVE_VIDEO=True` to save the output video in the target OUTPUT_VIDEO_PATH.
  - `FRAME_SKIP` controls the frame interval for processing, 1 means frame-by-frame processing. 
5. Run the main program.
6. Press 'q' to quit during the running process.

After processing, the program outputs the processed video, FPS information, and optionally shows the tracked objects on screen.

Note: This README provides a high-level overview and usage instructions. For detailed explanations of individual components, evaluations, and demo test results, see the [evaluation report](docs/evaluation.md).



