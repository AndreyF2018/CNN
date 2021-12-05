import numpy as np
import sys
import os

from tensorflow import keras
from keras.preprocessing import image
from PySide2.QtGui import QPixmap
from PySide2.QtWidgets import QWidget, QApplication, QPushButton, QFileDialog, QGraphicsScene

from CNNForm_ui import  Ui_Dialog

def Image_select():
    global selected_image_file #выбранное для предсказания изображение
    # Открытие окна выбора изображения:
    fileName = QFileDialog.getOpenFileName(filter="*.png *.jpg *.bmp")
    image = QPixmap(fileName[0])
    #Изменение размера выбранного изображения под размер graphicsView:
    pixmap = image.scaled(295, 220)
    scene = QGraphicsScene()
    scene.addPixmap(pixmap)
    ui.graphicsView.setScene(scene)
    # Замена в пути изображения слэша на двойной обратный слэш:
    selected_image_file = str(fileName[0]).replace("/", "\\\\")
    return selected_image_file

def Load_models():
    global gender_model
    global age_model
    gender_model = keras.models.load_model('Gender_recognition.h5')
    gender_model.compile(loss='binary_crossentropy',
                         optimizer='adam',
                         metrics=['accuracy'])

    age_model = keras.models.load_model('Age_category_recognition.h5')
    age_model.compile(loss='categorical_crossentropy',
                      optimizer='SGD',
                      metrics=['accuracy'])

def GenderPredict(model, image_file):
    label_names = ["Female", "Male"]
    # Метод для загрузки изображения:
    img = image.load_img(image_file, target_size=(150, 150))
    img_arr = np.expand_dims(img, axis=0) / 255.0
    result = model.predict_classes(img_arr) #метод для предсказания
    return label_names[result[0][0]]

def AgePredict(model, image_file):
    label_names = ["Adult", "Child", "Oldman"]
    # Метод для загрузки изображения:
    img = image.load_img(image_file, target_size=(150, 150))
    img_arr = np.expand_dims(img, axis=0) / 255.0
    result = model.predict_classes(img_arr) #метод для предсказания
    return label_names[result[0]]

def Predict():
    gender = GenderPredict(gender_model, selected_image_file)
    age = AgePredict(age_model, selected_image_file)
    ui.lineEdit.setText(gender)
    ui.lineEdit_3.setText(age)

def Stat():
    directory = QFileDialog.getExistingDirectory() # выбор директории
    # Замена в пути директории слэша на двойной обратный слэш:
    directory = str(directory).replace("/", "\\\\")
    gender_count = []
    age_count = []

    # Создание исключения:
    if len(os.listdir(directory)) > 100:
        ui.textBrowser.setVisible(True)
        ui.pushButton_4.setVisible(True)
        raise ValueError("The number of images should not exceed 100")

    else:
        # Цикл для обхода выбранной директории
        for filename in os.listdir(directory):
            # Метод для загрузки изображения:
            image_file = image.load_img(directory + "\\" + filename, target_size=(150, 150))
            img_arr = np.expand_dims(image_file, axis=0) / 255.0
            gender = gender_model.predict_classes(img_arr)
            age = age_model.predict_classes(img_arr)
            age_count.append(age)
            gender_count.append(gender)
        # Расчёт процента пола и возрастный катгеорий:
        females_part = round(gender_count.count(0) / len(gender_count), 2) * 100
        males_part = 100 - females_part
        adults_part = round(age_count.count(0) / len(age_count), 2) * 100
        childs_part = round(age_count.count(1) / len(age_count), 2) * 100
        oldmans_part = 100 - (adults_part + childs_part)
        # Запись рассчитанных процентов в поля:
        ui.lineEdit_2.setText(str(males_part) + "%")
        ui.lineEdit_4.setText(str(females_part) + "%")
        ui.lineEdit_5.setText(str(oldmans_part) + "%")
        ui.lineEdit_6.setText(str(adults_part) + "%")
        ui.lineEdit_7.setText(str(childs_part) + "%")

def Ecxep():
    ui.textBrowser.setVisible(False)
    ui.pushButton_4.setVisible(False)

if __name__ == '__main__':
    Load_models()
    app = QApplication(sys.argv)
    Form = QWidget()
    ui = Ui_Dialog()
    ui.setupUi(Form)
    Form.show()

    # Кнопка для выбора изображения:
    ui.pushButton.clicked.connect(Image_select)

    # Кнопка предсказания
    ui.pushButton_2.clicked.connect(Predict)

    #Кнопка статистика
    ui.pushButton_3.clicked.connect(Stat)

    #Кнопка закрытия исключения
    ui.pushButton_4.clicked.connect(Ecxep)

    sys.exit(app.exec_())
