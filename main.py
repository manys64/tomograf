import matplotlib.pyplot as plt
import numpy as np
import math
from skimage.color import gray2rgb


# ///////////////////initial
def process_image(img, alpha, angle_range, detectors):
    # Getting the bigger side of the image
    s = max(img.shape[0:2])

    # Creating a dark square with NUMPY
    f = np.zeros((s, s), np.float64)

    # Getting the centering position
    ax, ay = (s - img.shape[1]) // 2, (s - img.shape[0]) // 2

    # Pasting the 'image' in a centering position
    f[ay:img.shape[0] + ay, ax:ax + img.shape[1]] = img

    # //////////////////////////// padding

    circle_radius = f.shape[0] // 2
    circle_center = np.floor(np.array(f.shape) / 2).astype(int)

    # def detector_coords(alpha, angle_range, count, radius=1, center=(0, 0)):
    #    return circle_points(radians(alpha - angle_range / 2), radians(angle_range), count, radius, center)
    # (alpha=90, angle_range=180, detectors=15)

    # PUNKTY DLA DETEKTOROW
    # alpha = 90  # alfa to obkrecenie co widac przy liniach
    # angle_range = 40  # zakres katow na ktorych beda proste do tych rownoleglych
    # detectors = 15
    detector_amount = detectors
    angle_shift = math.radians(alpha - angle_range / 2)
    angle_range = math.radians(angle_range)
    angles = np.linspace(0, angle_range, detector_amount) + angle_shift
    cx, cy = circle_center
    x = circle_radius * np.cos(angles) - cx
    y = circle_radius * np.sin(angles) - cy
    points = np.array(list(zip(x, y)))

    radius, center = circle_radius, circle_center
    fig, ax = plt.subplots(1)

    emitters = np.floor(points).astype(int)
    # emitters = emitter_coords(alpha, angle_range, detectors, radius, center)
    # detectors = detector_coords(alpha, angle_range, detectors, radius, center)
    # lines = radon_lines(emitters, detectors)
    img = gray2rgb(f)
    for x, y in emitters:
        img[x - 2:x + 2, y - 2:y + 2] = (0, 1, 0)
        # zeby byly kreski nie pojedyncze pixele
    # for x, y in detectors:
    #         img[x - 2:x + 2, y - 2:y + 2] = (1, 0, 0)
    # for line in lines:
    #         img[tuple(line)] = (0, 0, 1)
    # ////////////////////rysowanie okregu na obrazie

    return img
