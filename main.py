import cv2
import time
import os
from components import ColorSpace, PreProcessing, Segmentation, \
                       PostProcessing, Visualization

INPUT_VIDEO_PATH = "trace_objects_3d/resources/PennAir 2024 App Dynamic Hard.mp4"
OUTPUT_VIDEO_PATH = "trace_objects_3d/output/dynamic_hard_result_3d.mp4"
VISUALIZE = True
SAVE_VIDEO = False
FRAME_SKIP = 2

# Video reader
cap = cv2.VideoCapture(INPUT_VIDEO_PATH)
if not cap.isOpened():
    raise IOError("Cannot open video file")

# Video writer
out = None
if SAVE_VIDEO:
    os.makedirs(os.path.dirname(OUTPUT_VIDEO_PATH), exist_ok=True)
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(
        OUTPUT_VIDEO_PATH,
        fourcc,
        cap.get(cv2.CAP_PROP_FPS),
        (int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)), int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)))
    )

frame_count = 0
start_time = time.time()

# ===== Initialize pipeline modules =====
pre = PreProcessing(method="open_close", kernel_size=7)
seg = Segmentation(method="threshold")
post = PostProcessing(kernel_open=11, kernel_close=9, area_ratio=0.004)
vis = Visualization()

# Background Subtractor (MOG2)
fgbg = cv2.createBackgroundSubtractorMOG2(history=50, varThreshold=12, detectShadows=False)


# ===== Frame loop =====
while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    if frame_count % FRAME_SKIP == 0:
        # Color space conversion
        gray = ColorSpace(mode="GRAY").apply(frame)
        hsv = ColorSpace(mode="HSV").apply(frame)

        # Pre prcessing
        pre_gray = pre.apply(gray)
        pre_hsv = pre.apply(hsv)

        # Segmentation
        mask_gray = seg.apply(pre_gray)
        mask_hsv = seg.apply(pre_hsv)
        seg_mask = cv2.bitwise_or(mask_gray, mask_hsv)

        # motion mask (MOG2)
        motion_mask = fgbg.apply(frame)
        combined_mask = cv2.bitwise_or(seg_mask, motion_mask)

        # Post processing and visualization (draw contours, centers, axes)
        mask_post = post.apply(combined_mask)
        final_frame = vis.apply(frame, mask_post)


    # ===== Display & Save =====
    if VISUALIZE:
        scale = 0.5  # rescale display
        disp_frame = cv2.resize(final_frame, None, fx=scale, fy=scale, interpolation=cv2.INTER_AREA)
        cv2.imshow("Pipeline-Result", disp_frame)
    if SAVE_VIDEO:
        out.write(final_frame)

    frame_count += 1

    # Press 'q' to quit
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

# ===== Done =====
end_time = time.time()
print(f"Processed {frame_count} frames in {end_time - start_time:.2f} sec")
print(f"FPS: {frame_count / (end_time - start_time):.2f}")

cap.release()
if SAVE_VIDEO:
    out.release()
cv2.destroyAllWindows()
