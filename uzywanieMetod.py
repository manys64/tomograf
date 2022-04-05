import computed_tomography as ct

img_name = 'SADDLE_PE.jpg'
tomograph = ct.Tomograph()

angle_range = 100  # zakres katow na ktorych beda proste do tych rownoleglych
detectors = 180
number_of_scans = 90

tomograph.scanner(img_name, detectors, number_of_scans, angle_range, False)
