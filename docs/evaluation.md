# Evaluation

This document explains how the segmentation-based tracking algorithm works.

## Static Image Segmentation

The algorithm follows the pipeline:

- **Convert frames to different color spaces (GRAY and HSV):** A single color space is often insufficient to detect all targets. Some spaces are sensitive to certain objects while ignoring others. Therefore, fusing multiple color spaces enhances detection capabilities.

- **Apply preprocessing to enhance object features:** Since the background is noisy, applying segmentation directly would misclassify background gaps (grass) as foreground. Morphological operations (opening and closing) are applied to remove small noise and fill small holes.

- **Apply segmentation methods to detect object regions:** Both Otsu thresholding and Canny edge detection offer near real-time detection performance. Given that the images in this task have distinct colors, thresholding is more suitable. K-means clustering was also tested but performed poorly in both accuracy and speed. Results from thresholding across different color spaces are fused using the OR operation.

- **Post-process masks** to remove noise and filter out small areas.
- **Visualize** object contours, centers, and 2D coordinates of detected objects.

Results on static images show good alignment between segmentation output and true outlines, confirming high accuracy.

<img src="../output/static_result.png" width="600">



## Dynamic Video Segmentation

To extend the algorithm to video, each frame is processed in a loop:

- **Frame-wise segmentation and tracking** ensures that all objects are detected across time.
- **Post-processing removes large false detections:** In some frames, large noisy patches are mistakenly classified as objects. A large-kernel opening operation combined with an area ratio filter removes small irrelevant components, followed by a smaller-kernel closing to fill in gaps.
- Display or save video results, depending on requirements.
- Measure processing time and FPS for efficiency analysis.

Evaluation:
- **Near real-time processing speed**: Processed 1837 frames in 61.11 sec; FPS: 30.06. (VISUALIZE=SAVE_VIDEO=False)
- High accuracy and efficiency maintained across frames.

<video src="../output/dynamic_result_compressed.mp4" controls width="600">
  Your browser does not support the video tag.
</video>



## Background Agnostic

To generalize beyond specific textures and object colors:
- **Background subtraction (MOG2) is used to extract moving regions:** If segmentation is based solely on color space, different colored parts of the same object will be identified as separate objects. However, temporal and motion information can be leveraged to enhance edge detection. The key idea is that while a single frame's color may not be able to distinguish between the target and background, motion consistency across frames provides stronger cues, correcting errors in challenging cases.
- **Frame skipping (FRAME_SKIP)** allows processing every n frames, balancing speed and accuracy for near real-time results. The video below is the result of processing every 2 frames.

<video src="../output/dynamic_hard_result_compressed.mp4" controls width="600">
  Your browser does not support the video tag.
</video>

Evaluation:
- Efficiency: Processed 1841 frames in 72.61 sec; FPS: 25.35 (FRAME_SKIP=2, VISUALIZE=SAVE_VIDEO=False).
- Accuracy: Initially, the pentagon was mistakenly identified as two objects, and the two corners of the trapezoid were identified as background. However, as they began to move, MOG2 helped the algorithm correct the foreground. MOG2 proves especially effective for fast-moving targets.
- Robustness: The method adapts to objects of different colors and complex backgrounds, demonstrating resilience.



## 3D Camera

The algorithm is extended to estimate object positions in camera coordinates $(X, Y, Z)$ using the given intrinsic matrix:

$$
K = \begin{bmatrix}
2564.32 & 0 & 0 \\
0 & 2569.70 & 0 \\
0 & 0 & 1
\end{bmatrix}
$$

For a detected object center at pixel coordinates $(u, v)$, the mapping to camera coordinates is:  

$$
\begin{bmatrix}
X \\
Y \\
Z
\end{bmatrix}
= Z \cdot K^{-1} 
\begin{bmatrix}
u \\
v \\
1
\end{bmatrix}
$$

where $Z$ is the estimated depth.  

### Depth from circle radius

If an object is known to be a circle of real-world radius $r$ (10 in in this task), and it appears in the image with pixel radius $r_p$, then depth can be recovered by the pinhole camera model:

$$
r_p = \frac{f \cdot r}{Z}
$$

where $f$ is the focal length (in pixels) from the intrinsic matrix $K$. Solving for $Z$:

$$
Z = \frac{f \cdot r}{r_p}
$$

Once $Z$ is estimated, the full 3D coordinates of the circle center are obtained by the previous back-projection formula. 

This allows the algorithm to display $(X, Y, Z)$ relative to the camera frame.

<video src="../output/dynamic_hard_result_3d_compressed.mp4" controls width="600">
  Your browser does not support the video tag.
</video>



## Potential improvements

To further enhance accuracy and robustness:  
 
- **Adaptive segmentation**: Use learning-based methods (e.g., lightweight deel learning models) for improved generalization.  
- **Robust tracking**: Incorporate Kalman filters to stabilize trajectories.
- **Shape priors**: Apply geometric constraints (e.g. known pentagons and trapezoids) to improve detection accuracy.
