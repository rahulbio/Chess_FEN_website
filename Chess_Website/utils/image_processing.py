import cv2
import numpy as np
import re
import matplotlib as plt
piece_symbols = 'prbnkqPRBNKQ'

def preprocess_image(img_path):
    height = 240
    width = 240

    # Change to grayscale
    img = cv2.imread(img_path, cv2.COLOR_BGR2GRAY)

    # Resize the image to the desired size
    gray_image = cv2.resize(img, (width, height))

    # Normalize the image
    gray_image = (gray_image - np.min(gray_image)) / (np.max(gray_image) - np.min(gray_image))

    squares = image_to_squares(gray_image, height, width)
    return squares

def image_to_squares(img, heights, widths):
    squares = []
    for i in range(0, 8):
        for j in range(0, 8):
            squares.append(img[i * heights // 8:i * heights // 8 + heights // 8, j * widths // 8:j * widths // 8 + widths // 8])
    return np.array(squares)

def onehot_from_fen(fen):
    eye = np.eye(13)
    output = np.empty((0, 13))
    fen = re.sub('[-]', '', fen)

    for char in fen:
        if char in '12345678':
            output = np.append(output, np.tile(eye[12], (int(char), 1)), axis=0)
        else:
            if char in piece_symbols:
                idx = piece_symbols.index(char)
                output = np.append(output, eye[idx].reshape((1, 13)), axis=0)
            else:
                # Handle the case when char is not found in piece_symbols
                # For example, you might want to skip this character or handle it differently.
                pass

    return output

def fen_from_onehot(one_hot):
    output = ''
    for j in range(8):
        for i in range(8):
            if one_hot[j][i] == 12:
                output += ' '
            else:
                output += piece_symbols[one_hot[j][i]]
        if j != 7:
            output += '-'

    for i in range(8, 0, -1):
        output = output.replace(' ' * i, str(i))

    return output

def display_with_predicted_fen(image_path, model):
    pred = model.predict(preprocess_image(image_path)).argmax(axis=1).reshape(-1, 8, 8)
    fen = fen_from_onehot(pred[0])
    return fen