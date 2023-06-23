import os
from typing import Optional
from skimage import io
from skimage.filters import threshold_otsu
import numpy as np
from skimage.transform import resize
from skimage import measure
from skimage.measure import regionprops
import matplotlib.patches as patches
from skimage import io
import joblib
from pydantic import BaseModel

class PlateRecognitionConfig(BaseModel):
    
    threashold: Optional[int] = 84
    plate_dimension_factors: Optional[list] = [0, 0.09, 0, 0.07]
    character_dimension_factors: Optional[list] = [0.1, 1, 0.05, 0.25]
    area_lower_bound:Optional[int] = 4000
    area_upper_bound:Optional[int] = 10000
    
    model_path:Optional[str] = './svc/svc.pkl'
    model_path_relative:Optional[bool] = True

class PlateRecognition():
    
    image:any = None
    binary_image:any = None
    model: any = None
    
    current_conf: PlateRecognitionConfig = PlateRecognitionConfig()

    threashold:int = 84
    plate_dimension_factors: int = [0, 0.09, 0, 0.07]
    character_dimension_factors: list = [0.1, 1, 0.05, 0.25]
    area_lower_bound:int = 4000
    area_upper_bound:int = 10000
    
    model_path:str = '/svc/svc.pkl'
    model_path_relative:bool = True

    def __init__(self):
        # todo: clean the config stuff
        self.load_config(self.current_conf, True)
        # self.__load_model()

    def __load_model(self):
        if self.model_path_relative:
            current_dir = os.path.dirname(os.path.realpath(__file__))
            model_dir = os.path.join(current_dir, self.model_path)
            self.model = joblib.load(model_dir)
        else:
            self.model = joblib.load(self.model_path)

    def __pre_process_image(self, path:str):
        # first we need some preprocess
        # first we read the car image in grayscale mode and then mutiply the image by 255 to get pixels in range of(0,255)

        car = io.imread('0.jpg', as_gray=True)
        car_gray = car *255

        threshold = threshold_otsu(car_gray)
        # using threshold value to creat binary image from grayscale image
        car_binary = car_gray > self.threashold

        # we use connected component analysis
        # this gets all the connected regions and groups them together
        label_image = measure.label(car_binary)

        # getting the maximum width, height and minimum width and height that a license plate can be
        plate_dimensions = (self.plate_dimension_factors[0]*label_image.shape[0],
                            self.plate_dimension_factors[1]*label_image.shape[0],
                            self.plate_dimension_factors[2]*label_image.shape[1],
                            self.plate_dimension_factors[3]*label_image.shape[1])

        min_height, max_height, min_width, max_width = plate_dimensions

        plate_objects_cordinates = []
        plate_like_objects = []

        # regionprops creates a list of properties of all the labelled regions
        for region in regionprops(label_image):
            if region.area < 4000 or region.area>10000:
                continue

            # the bounding box coordinates
            min_row, min_col, max_row, max_col= region.bbox
            region_height = max_row - min_row
            region_width = max_col - min_col
            # ensuring that the region identified satisfies the condition of a typical license plate
            if region_height >= min_height and region_height <= max_height and region_width >= min_width and region_width <= max_width and region_width > region_height:
                plate_like_objects.append(car_binary[min_row:max_row, min_col:max_col])
                plate_objects_cordinates.append((min_row, min_col, max_row, max_col))

                rectBorder = patches.Rectangle((min_col, min_row), max_col-min_col, max_row-min_row, edgecolor="red", linewidth=3, fill=False)
                # ax1.add_patch(rectBorder) #todo: check this with the main code to see if its just for show


        license_plate = np.invert(plate_like_objects[0])
        license_plate = resize(license_plate,(110,600))
        labelled_plate = measure.label(license_plate)

        character_dimensions = (self.character_dimension_factors[0]*license_plate.shape[0],
                                self.character_dimension_factors[1]*license_plate.shape[1],
                                self.character_dimension_factors[2]*license_plate.shape[1],
                                self.character_dimension_factors[3]*license_plate.shape[1])

        min_height, max_height, min_width, max_width = character_dimensions
        characters = []
        column_list = []

        for regions in regionprops(labelled_plate):
            y0, x0, y1, x1 = regions.bbox
            region_height = y1 - y0
            region_width = x1 - x0

            if region_height > min_height and region_height < max_height and region_width > min_width and region_width < max_width:
                roi = license_plate[y0:y1, x0:x1]

                # draw a red bordered rectangle over the character.
                rect_border = patches.Rectangle((x0, y0), x1 - x0, y1 - y0, edgecolor="red",
                                            linewidth=1, fill=False)
                # ax1.add_patch(rect_border)

                # resize the characters to 100X60 and then append each character into the characters list
                resized_char = resize(roi, (100, 60))
                characters.append(resized_char)
            
                # keeping order
                column_list.append(x0)

        return (characters, column_list)

    def __predict_plate(self, characters, column_list):
        classification_result = []
        for each_character in characters:
            # to a 1D array
            each_character = each_character.reshape(1, -1)
            result = self.model.predict(each_character)
            classification_result.append(result)

        plate_string = ''
        for eachPredict in classification_result:

            plate_string += eachPredict[0]

        # sorting letters in correct order

        column_list_copy = column_list[:]
        column_list.sort()
        rightplate_string = ''
        for each in column_list:
            rightplate_string += plate_string[column_list_copy.index(each)]

        return rightplate_string

    def load_config(self, conf:PlateRecognitionConfig, model_reload:bool):
        
        self.current_conf = conf

        if conf.area_lower_bound is not None:
            self.area_lower_bound = conf.area_lower_bound

        if conf.area_upper_bound is not None:
            self.area_upper_bound = conf.area_upper_bound

        if conf.plate_dimension_factors is not None:
            self.plate_dimension_factors = conf.plate_dimension_factors

        if conf.character_dimension_factors is not None:
            self.character_dimension_factors = conf.character_dimension_factors
            
        if conf.threashold is not None:
            self.threashold = conf.threashold

        if conf.model_path is not None:
            self.model_path = conf.model_path

        if conf.model_path_relative is not None:
            self.model_path_relative = conf.model_path_relative

        if model_reload:
            self.__load_model()

    def get_config(self) -> PlateRecognitionConfig :
        return self.current_conf

    def recognize_plate(self, image_path:str) -> str:
        characters, column_list = self.__pre_process_image(path=image_path)
        plate_string = self.__predict_plate(characters=characters, column_list=column_list)
        return plate_string

    