# Evaluation

This document explains how the segmentation based tracking algorithm work.

## Static Image Segmentation

The algorithm follows the work pipeline:

- **Convert frames to different color spaces (GRAY and HSV):** Practice has shown that a certain color space is usually unable to detect all graphics, which means a single color space may be sensitive to some targets but almost blind to others. Therefore, multi-color space fusion is used to enhance detection capabilities. 

- **Apply preprocessing to enhance object features:** Since the background is noisy, if the segmentation algorithm is used directly, the gaps between the background grass will be considered as foreground. The morphological operation opening and closing is used to remove small noise and fill small holes in objects.

- **Apply segmentation methods to detect object regions:** Both Otsu thresholding and Canny edge detection offer near-real-time detection performance. The images in this task have distinct colors, so the thresholding method is more suitable. In addition, kmeans was tried, but its accuracy and time efficiency were poor. After performing Otsu threshold segmentation in different color spaces, the results are fused using the OR operation.

- Post-process masks to remove noise and filter out small areas.
- Visualize object contours, centers, and 2D coordinates.

The detection results on the grassy background are shown below. The segmentation results agree well with the object outlines, demonstrating the high accuracy of the detection algorithm on still images.

![static image test result](output\static_result.png)



## Dynamic Video Segmentation

Next, the algorithm needs to be extended to video. Video is viewed as a stream with images as each frame. The main improvements are as follows:

- Each frame is processed in the Frame loop to ensure that all objects are tracked in the video.
- **Post-processing is used to remove large noise points:** In some frames, a large amount of background is mistakenly identified as foreground. After removing the noise using a large kernel open operation, area_radio is used to filter out foreground areas smaller than a certain threshold. Then, a slightly smaller kernel close operation is used to fill in small holes. This post-processing ensures a relatively clean and accurate video segmentation.
- Display the processing results in real time or save the processed video as needed.
- Print video processing time and FPS for easy efficiency analysis.

The detection results on the grassy background are shown below:

<video src="output\dynamic_result_compressed.mp4" controls width="600">
  Your browser does not support the video tag.
</video>

Evaluation:
- **Near real-time processing speed**: Processed 1837 frames in 61.11 sec; FPS: 30.06.
- High accuracy and efficiency.



## Background Agnostic

Next, the algorithm tries to handle backgrounds with different textures and graphics with complex colors. The main changes are as follows:
- **Use background subtraction (MOG2) to extract moving areas:** If segmentation is based solely on color space, different colored parts of the same object will be identified as separate objects. However, temporal and motion information can be leveraged to enhance edge detection. The key idea is that while a single frame's color may not be able to distinguish between the target and background, the target moves across consecutive frames, and the same target has similar movement trends, while the background is static or changes slowly.
- **Add the FRAME_SKIP parameter to control processing speed**: To achieve near real-time processing speed, it is usually acceptable to detect every few frames. The video below is the result of processing every 2 frames.

<video src="output\dynamic_hard_result_compressed.mp4" controls width="600">
  Your browser does not support the video tag.
</video>

Evaluation:
- Efficiency: Processed 1841 frames in 72.61 sec; FPS: 25.35 (FRAME_SKIP=2).
- Accuracy: Initially, the pentagon was mistakenly identified as two objects, and the two corners of the trapezoid were identified as background. However, as they began to move, MOG2 helped the algorithm correct the foreground. MOG2 is more effective for fast-moving objects.
- Robustness: The algorithm can also recognize objects of different colors on backgrounds of different textures, showing a certain degree of robustness.



## 3D Camera

Given the camera’s intrinsic matrix K=[[2564.3186869,0,0],[0,2569.70273111,0],[0, 0, 1]], and that the circle has a 
radius of 10 in. The algorithm can mark the depth, x, and y coordinates of the centers w.r.t the camera.

<video src="output\dynamic_hard_result_3d_compressed.mp4" controls width="600">
  Your browser does not support the video tag.
</video>


## Potential improvements