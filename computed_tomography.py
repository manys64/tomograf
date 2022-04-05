import math

import matplotlib.pyplot as plt
import numpy as np
import skimage.draw as draw
import skimage.io as io
from skimage.color import gray2rgb


# plik z matematyka i obliczeniami

class Tomograph:
    def scanner(self, img_name, num_detectors, num_scans, beam_extent, use_filter):
        # img = io.imread(img_name, as_gray=True)
        img = img_name

        # Getting the bigger side of the image
        s = max(img.shape[0:2])
        # Creating a dark square with NUMPY
        f = np.zeros((s, s), np.float64)
        # Getting the centering position
        ax, ay = (s - img.shape[1]) // 2, (s - img.shape[0]) // 2
        # Pasting the 'image' in a centering position
        f[ay:img.shape[0] + ay, ax:ax + img.shape[1]] = img
        side_len = f.shape[0]

        if img_name == 'SADDLE_PE.jpg' or img_name == 'Shepp_logan.jpg':
            # if side_len > 900:
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
            # print(all_scans_angles[scan])

            detector_points = self.calc_detector_points(all_scans_angles[scan], beam_extent, num_detectors,
                                                        circle_radius, circle_center)
            emitter_points = self.calc_emitter_points(all_scans_angles[scan], beam_extent, num_detectors, circle_radius,
                                                      circle_center)
            sino_row = self.get_sinogram_row(detector_points, emitter_points, f, use_filter)
            sino.append(sino_row)

            if use_filter == True:
                print("todo")
                # convolve(sino[i, :], kernel, mode='same')
            self.tomograph_reconstruction(detector_points, emitter_points, f, tomograph_image_empty, use_filter)
            if scan == process_indexes[process_index]:
                process_scans_images.append(tomograph_image_empty)
                process_index += 1

        self.draw_sinogram(sino, False)
        tomograph_image = tomograph_image_empty
        process_scans_images.append(gray2rgb(tomograph_image))
        # self.draw_tomograph_image(sino,f.shape[0],False)
        return process_scans_images

    def pad_with(self, vector, pad_width, iaxis, kwargs):
        pad_value = kwargs.get('padder', 10)
        vector[:pad_width[0]] = pad_value
        vector[-pad_width[1]:] = pad_value

    def calc_detector_points(self, alpha, angle_range, point_amount, circle_radius, circle_center):
        angle_shift = math.radians(alpha - angle_range / 2)
        angle_range = math.radians(angle_range)
        angles = np.linspace(0, angle_range, point_amount) + angle_shift
        cx, cy = circle_center
        x = circle_radius * np.cos(angles) - cx
        y = circle_radius * np.sin(angles) - cy
        points = np.array(list(zip(x, y)))
        return points

    def calc_emitter_points(self, alpha, angle_range, point_amount, circle_radius, circle_center):
        angle_shift = math.radians(alpha - angle_range / 2 + 180)
        angle_range = math.radians(angle_range)
        angles = np.linspace(0, angle_range, point_amount) + angle_shift
        cx, cy = circle_center
        x = circle_radius * np.cos(angles) - cx
        y = circle_radius * np.sin(angles) - cy
        points = np.array(list(zip(x, y)))
        return points

    def get_sinogram_row(self, detector_points, emitter_points, image, use_filter):
        sinogram_row = []
        #  print("column x --------------")
        for j in range(len(detector_points)):
            line = draw.line_nd(emitter_points[len(emitter_points) - 1 - j], detector_points[j])
            # for each detector calc avg of values in emitter-detector line
            sinogram_row.append(np.average(image[line]))
        # print(sinogram_row)
        return sinogram_row

    def draw_sinogram(self, sinogram, use_filter):
        # print(sinogram)
        imgplot = plt.imshow(sinogram, cmap='gray')
        plt.show()

    def draw_tomograph_image(self, sinogram, side_len, use_filter):
        # print(sinogram)
        tomograph_image = np.zeros((side_len, side_len))
        print(len(sinogram))
        # plt.imshow(tomograph_image, cmap='gray')
        # plt.show()

    def tomograph_reconstruction(self, detector_points, emitter_points, image, output_image, use_filter):
        # 1 i 3 etap combined
        sinogram_row = []

        # plt.imshow(tomograph_image, cmap='gray')
        # plt.show()
        #  print("column x --------------")
        for j in range(len(detector_points)):
            line = draw.line_nd(emitter_points[len(emitter_points) - 1 - j], detector_points[j])
            # for each detector calc avg of values in emitter-detector line
            sinogram_row.append(np.average(image[line]))
            # print(image[line])
            # print("---------")
            output_image[line] += np.average(image[line])
        # print(tomograph_image[line])

    # 180 detektorow i 90 skanow da w 1 etapie:


# sinogram 90 wierszy tego co doszlo do emiterow
# 180 kolumn dla kazdego detektora

# skimage.draw.line_nd  da wszystkie punkty wchodzace w sklad linii pomiedzy
# dwoma punktami: mimejscem detektora a miejscem emitera

# dostajemy liste list [rows,cols]
# Mzona uproscic kod nie isc po petli z draw nd tylko dwie listy nimi indeksowac tablice numpy
# Agregujemy srednia ze wspolrzednych punktiw
# Nd zwraca lsite list. musimy odwiedzic te punkty na obrazie
# patrzymy co przechowuja te pixele
# Mozna indeksowac po line ktore jest wynikiem line nd
# i np.mean mozna przez to
# i taki wynik zapisujemy w odpowiednim iejscu sinogramu
# pierwszy w 0 wierszu 0 kolumnie
# Kolejny detektor wyzn linie, agregujemy
# i zapisujemy 0 wiersz 1 kolumna

# petla for liczba skanow
# todo 1 etap
# zapisuj SREDNIA (nie suma) jasnosc krechy miedzy punktami
# dla kazdej pary emiter detektor
# zapis do tablicy zwyklej lub numpy kazdego z wierszy sinogramu
# te wartosci da sie jako obrazek wyswietlic tez
# a mozna tez pojedyncze wiersz jako wykres w ktorym wartosci Y to punkty poj. detektora dla widoku
# a ilosc detektorow to X i dzieki temu wykresy jak slajdy.sprawdz dla kropki

# todo 2 etap if use_filter = true
# filtracja: convolve(sino[i, :], kernel, mode=’same’)
# po filtracji da sie obrazek wyswietlic tez
# pojedyncze wykresy potem zobaczyc czy jak na slajdzie sie zmieniaja

# todo 3 etap: dalej ta sama petla potem dla optymalizacji
# obraz wynikowy na poczatku te same wymiary co pocz. tylko pusty caly czarny (same 0 lub 1?)
# wzmacniamy wynikowy wartosciami z sinogramu: wczesniejsze wiersze sino[], just dodajemy?
# liczba wzmocnien to liczba skanow = wierszy
# chyba trzeba co iteracje dodawac do calego obrazka
# finalny obrazek wyswietlamy
# zeby polaczyc z 1 etapem zapisz sobie wszystkie linie dla wszystkich detektorow
# W danym View (obrocie)
# chyba na tej samej linii na ktorej skanowales dodanie na wspolrzednych img tej linii wartosci
# z sino
# Generujemy linie od 1 detektora do 1 emitera
# Te same 2 punkty, ta sama linia miedzy nimi
# Tym samym pikselom z line nd Wszystkim podbijamy o jedna wartosc

# inny przypadek 360 det i 180 skanow


# kwestie techniczne:
'''
podzielic obrazek na piksele punkty emiterow
tak samo punkty detektorow
pomiedzy nimi robi linie
Punkty linii jakos da sie porownac z punktami img czy cos?
    i na nich liczyc srednia/sume
    
    POZBYC SIE ARTEFAKTOW ===> wyznaczenie średniej jasności (a nie sumy) na promieniu, 
    inaczej artefakty na sinogramie

    
    
pytanie jak potem te dodawanie do pustego obrazu tych rzeczy
znow po tych liniach czy co 
od ===> Następnie dla każdej pary emiter/detektor, dodajemy wartość odpowiadającego punktu
sinogramu do pikseli leżących na linii pomiędzy nimi.

'''
