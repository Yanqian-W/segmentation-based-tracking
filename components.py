import cv2
import numpy as np

# ========== Color Space ==========
class ColorSpace:
    def __init__(self, mode="HSV"):
        self.mode = mode

    def apply(self, image):
        if self.mode == "HSV":
            converted = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        elif self.mode == "LAB":
            converted = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
        elif self.mode == "GRAY":
            converted = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            converted = image  # default: no change
        # cv2.imshow(f"ColorSpace-{self.mode}", converted)
        return converted


# ========== Pre Processing ==========
class PreProcessing:
    def __init__(self, method="gaussian", kernel_size=5):
        self.method = method
        self.k_size = kernel_size

    def apply(self, image):
        # image = cv2.normalize(image, None, alpha=0, beta=255, norm_type=cv2.NORM_MINMAX)

        if self.method == "gaussian":
            processed = cv2.GaussianBlur(image, (self.k_size, self.k_size), 0)
        elif self.method == "bilateral":
            processed = cv2.bilateralFilter(image, 9, 75, 75)
        elif self.method == "median":
            processed = cv2.medianBlur(image, self.k_size)
        
        # Morphology Opening (remove small noise)
        elif self.method == "opening":
            # The larger the kernel, the stronger the smoothing effect, 
            # but it may swallow small targets
            kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (self.k_size, self.k_size))
            processed = cv2.morphologyEx(image, cv2.MORPH_OPEN, kernel)
        # Morphology Closing (fill small holes in objects)
        elif self.method == "closing":
            kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (self.k_size, self.k_size))
            processed = cv2.morphologyEx(image, cv2.MORPH_CLOSE, kernel)
        # Morphology Opening + Closing combined
        elif self.method == "open_close":
            kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (self.k_size, self.k_size))
            temp = cv2.morphologyEx(image, cv2.MORPH_OPEN, kernel)
            processed = cv2.morphologyEx(temp, cv2.MORPH_CLOSE, kernel)

        else:
            processed = image  # default: no preprocessing
        # cv2.imshow(f"PreProcessing-{self.method}", processed)
        return processed


# ========== Segmentation ==========
class Segmentation:
    def __init__(self, method="threshold"):
        self.method = method

    def apply(self, image):
        if self.method == "threshold":
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if len(image.shape) == 3 else image
            _, mask = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        elif self.method == "canny":
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if len(image.shape) == 3 else image
            mask = cv2.Canny(gray, 100, 120, L2gradient=False)
        elif self.method == "kmeans":
            Z = image.reshape((-1, 3))
            Z = np.float32(Z)
            criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 10, 1.0)
            _, labels, centers = cv2.kmeans(Z, 2, None, criteria, 10, cv2.KMEANS_RANDOM_CENTERS)
            mask = labels.reshape((image.shape[0], image.shape[1])).astype(np.uint8) * 255
        else:
            mask = np.zeros(image.shape[:2], dtype=np.uint8)
        # cv2.imshow(f"Segmentation-{self.method}", mask)
        return mask
    

# ========== Post Processing ==========
class PostProcessing:
    def __init__(self, kernel_open=7, kernel_close=5, area_ratio=0.01):
        # different kernels for open and close
        self.kernel_open = np.ones((kernel_open, kernel_open), np.uint8)
        self.kernel_close = np.ones((kernel_close, kernel_close), np.uint8)
        self.area_ratio = area_ratio

    def apply(self, mask):
        h, w = mask.shape[:2]
        mask_clean = mask.copy()

        # Open calculation to remove small noise
        mask_clean = cv2.morphologyEx(mask_clean, cv2.MORPH_OPEN, self.kernel_open)

        # Contour Filtering
        contours, _ = cv2.findContours(mask_clean, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        mask_filtered = np.zeros_like(mask_clean)
        for cnt in contours:
            if cv2.contourArea(cnt) >= self.area_ratio*h*w:
                cv2.drawContours(mask_filtered, [cnt], -1, 255, -1)

        # Closing operation, smoothing the edge of the target and filling small holes
        mask_final = cv2.morphologyEx(mask_filtered, cv2.MORPH_CLOSE, self.kernel_close)

        return mask_final


# =============== Visualization ===============
# class Visualization:
#     def __init__(self, draw_contours=True):
#         self.draw_contours = draw_contours

#     def apply(self, image, mask):
#         h, w = image.shape[:2]
#         center_x, center_y = w // 2, h // 2  # image center

#         kernel = np.ones((5, 5), np.uint8)
#         mask_clean = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
#         mask_clean = cv2.morphologyEx(mask_clean, cv2.MORPH_CLOSE, kernel)

#         result = image.copy()
#         cv2.circle(result, (center_x, center_y), 5, (255, 255, 255), -1)  # Origin point
    
#         if self.draw_contours:
#             contours, _ = cv2.findContours(mask_clean, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
#             for cnt in contours:
#                 cv2.drawContours(result, [cnt], -1, (0, 128, 255), 2)
#                 M = cv2.moments(cnt)
#                 if M["m00"] > 0:
#                     cx = int(M["m10"] / M["m00"])
#                     cy = int(M["m01"] / M["m00"])
#                     cv2.circle(result, (cx, cy), 4, (255, 255, 255), -1)
#                     cv2.putText(result, f"coords: [{cx-center_x},{cy-center_y}]", (cx - 150, cy + 120),
#                                 cv2.FONT_HERSHEY_SIMPLEX, 1.0, (255, 255, 255), 2) # center-based coordinates

#         return result

class Visualization:
    def __init__(self):
        # Camera intrinsics
        self.fx = 2564.3186869
        self.fy = 2569.70273111
        self.cx = 0
        self.cy = 0
        self.radius_in = 10.0  # known radius in inches

    def apply(self, image, mask):
        h, w = image.shape[:2]
        result = image.copy()

        kernel = np.ones((5, 5), np.uint8)
        mask_clean = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
        mask_clean = cv2.morphologyEx(mask_clean, cv2.MORPH_CLOSE, kernel)

        contours, _ = cv2.findContours(mask_clean, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        for cnt in contours:
            cv2.drawContours(result, [cnt], -1, (0, 128, 255), 2)
            M = cv2.moments(cnt)
            if M["m00"] > 0:
                cx_img = int(M["m10"] / M["m00"])
                cy_img = int(M["m01"] / M["m00"])
                cv2.circle(result, (cx_img, cy_img), 4, (255, 255, 255), -1)

                # === Estimate object size in pixels ===
                (x, y), r_px = cv2.minEnclosingCircle(cnt)
                if r_px > 1:  # avoid division by zero
                    # Depth estimation
                    Z = (self.fx * self.radius_in) / r_px
                    X = (cx_img - self.cx) * Z / self.fx
                    Y = (cy_img - self.cy) * Z / self.fy

                    # Display 3D coordinates
                    coord_text = f"coords: [{X:.1f}, {Y:.1f}, {Z:.1f}]"
                    cv2.putText(result, coord_text,
                                (cx_img - 200, cy_img + 140),
                                cv2.FONT_HERSHEY_SIMPLEX, 1.0,
                                (255, 255, 255), 2)

        return result
    

# ========== Image Pipeline ==========
if __name__ == "__main__":
    # Load image
    image = cv2.imread("trace_objects_3d/resources/test.png")

    # Color space
    color = ColorSpace("HSV").apply(image)
    # Preprocessing
    pre = PreProcessing("open_close").apply(color)
    # Segmentation
    mask = Segmentation("canny").apply(pre)
    # Postprocessing
    post = PostProcessing(area_ratio=0.002, kernel_size=7).apply(mask)
    result = Visualization().apply(image, post)

    scale = 0.5  # rescale display
    disp_frame = cv2.resize(mask, None, fx=scale, fy=scale, interpolation=cv2.INTER_AREA)
    cv2.imshow("Pipeline-Result", disp_frame)
    # cv2.imwrite("trace_objects_3d/output/test_result.png", result)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
