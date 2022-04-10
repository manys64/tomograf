import copy
import math
import numpy as np
import skimage.draw as draw


class Tomograph:
    def scanner(self, img_data, num_detectors, num_scans, beam_extent, use_filter):
        img = img_data

        # Getting the bigger side of the image
        s = max(img.shape[0:2])
        # Creating a dark square with NUMPY
        f = np.zeros((s, s), np.float64)
        # Getting the centering position
        ax, ay = (s - img.shape[1]) // 2, (s - img.shape[0]) // 2
        # Pasting the 'image' in a centering position
        f[ay:img.shape[0] + ay, ax:ax + img.shape[1]] = img
        side_len = f.shape[0]

        if side_len > 900:
            pad_size = 200
            f = np.pad(f, pad_size, self.pad_with, padder=0)
            side_len = f.shape[0]

        circle_radius = f.shape[0] // 2
        circle_center = np.floor(np.array(f.shape) / 2).astype(int)

        all_scans_angles = np.linspace(0, 180, num_scans).astype(int)
        tomograph_image_empty = np.zeros((side_len, side_len))
        sino = []

        process_scans_images_amount = num_scans // 5
        if (process_scans_images_amount >= 10):
            process_scans_images_amount = num_scans // 9
        process_index = 0
        process_scans_images = []
        process_indexes = np.linspace(0, num_scans, process_scans_images_amount).astype(int)
        for scan in range(num_scans):

            detector_points = self.calc_detector_points(all_scans_angles[scan], beam_extent, num_detectors,
                                                        circle_radius, circle_center)
            emitter_points = self.calc_emitter_points(all_scans_angles[scan], beam_extent, num_detectors, circle_radius,
                                                      circle_center)

            if use_filter == True:
                sino_row = self.tomograph_reconstruction_filter(detector_points, emitter_points, f, tomograph_image_empty)
            else:
                sino_row = self.tomograph_reconstruction(detector_points, emitter_points, f, tomograph_image_empty)
            sino.append(sino_row)

            if scan == process_indexes[process_index]:
                process_scans_images.append(copy.copy(tomograph_image_empty))
                process_index += 1

        process_scans_images.append(copy.copy(tomograph_image_empty))
        return process_scans_images, sino

    def pad_with(self, vector, pad_width, iaxis, kwargs):
        pad_value = kwargs.get('padder', 10)
        vector[:pad_width[0]] = pad_value
        vector[-pad_width[1]:] = pad_value

    def calc_detector_points(self, alpha, angle_range, point_amount, circle_radius, circle_center):
        angle_shift = math.radians(alpha - angle_range / 2)
        angle_range = math.radians(angle_range)
        angles = np.linspace(0, angle_range, point_amount) + angle_shift

        points = self.get_points_for_angles(angles, circle_center, circle_radius)
        return points

    def calc_emitter_points(self, alpha, angle_range, point_amount, circle_radius, circle_center):
        angle_shift = math.radians(alpha - angle_range / 2 + 180)
        angle_range = math.radians(angle_range)
        angles = np.linspace(0, angle_range, point_amount) + angle_shift

        points = self.get_points_for_angles(angles,circle_center,circle_radius)
        return points

    def get_points_for_angles(self,angles,circle_center,circle_radius):
        cx, cy = circle_center
        x = circle_radius * np.cos(angles) - cx
        y = circle_radius * np.sin(angles) - cy
        points = np.array(list(zip(x, y)))
        return points

    def get_sinogram_row(self, detector_points, emitter_points, image, use_filter):
        sinogram_row = []
        for j in range(len(detector_points)):
            line = draw.line_nd(emitter_points[len(emitter_points) - 1 - j], detector_points[j])

            sinogram_row.append(np.average(image[line]))
        return sinogram_row


    def tomograph_reconstruction(self, detector_points, emitter_points, image, output_image):
        sinogram_row = []
        #step 1 & 3 combined
        for j in range(len(detector_points)):
            line = draw.line_nd(emitter_points[len(emitter_points) - 1 - j], detector_points[j])
            # for each detector calc avg of values in emitter-detector line
            sino =  np.average(image[line])
            sinogram_row.append(sino)
            output_image[line] += sino

        return sinogram_row

    def tomograph_reconstruction_filter(self, detector_points, emitter_points, image, output_image):
        sinogram_row = []
        #step 1
        for j in range(len(detector_points)):
            line = draw.line_nd(emitter_points[len(emitter_points) - 1 - j], detector_points[j])
            # for each detector calc avg of values in emitter-detector line
            sino = np.average(image[line])
            sinogram_row.append(sino)
        #step 2
        kernel = self.get_kernel()
        sinogram_row = np.convolve(sinogram_row, kernel, mode='same')

        #step 3
        for k in range(len(detector_points)):
            line_reconstruction = draw.line_nd(emitter_points[len(emitter_points) - 1 - k], detector_points[k])
            output_image[line_reconstruction] += sinogram_row[k]

        return sinogram_row

    def get_kernel(self):
        right_part = np.zeros(11)
        for i in range(0, len(right_part)):
            if i % 2 == 0:
                right_part[i] = 0
            else:
                right_part[i] = (-4 / math.pow(math.pi, 2)) / math.pow(i, 2)
        right_part[0] = 1
        left_part = np.flip(right_part[1:])
        kernel = np.concatenate((left_part, right_part))
        return kernel
