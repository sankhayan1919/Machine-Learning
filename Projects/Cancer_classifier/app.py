import gradio as gr
import numpy as np
import pandas as pd
import sklearn.datasets
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
import tensorflow as tf
from tensorflow import keras

# Load and prepare dataset
ds = sklearn.datasets.load_breast_cancer()
data_frame = pd.DataFrame(ds.data, columns=ds.feature_names)
data_frame['label'] = ds.target

x = data_frame.drop(columns='label', axis=1)
y = data_frame['label']

x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.2, random_state=2)

# Standardization
scaler = StandardScaler()
x_train_std = scaler.fit_transform(x_train)
x_test_std = scaler.transform(x_test)

# Build and train the model
tf.random.set_seed(3)
model = keras.Sequential([
    keras.layers.Flatten(input_shape=(30,)),
    keras.layers.Dense(20, activation='relu'),
    keras.layers.Dense(2, activation='sigmoid')
])

model.compile(optimizer='adam', loss='sparse_categorical_crossentropy', metrics=['accuracy'])
model.fit(x_train_std, y_train, validation_data=(x_test_std, y_test), epochs=10)

# Define prediction function for Gradio
def predict_tumor_radius(
    mean_radius, mean_texture, mean_perimeter, mean_area, mean_smoothness,
    mean_compactness, mean_concavity, mean_concave_points, mean_symmetry, mean_fractal_dimension,
    radius_error, texture_error, perimeter_error, area_error, smoothness_error,
    compactness_error, concavity_error, concave_points_error, symmetry_error, fractal_dimension_error,
    worst_radius, worst_texture, worst_perimeter, worst_area, worst_smoothness,
    worst_compactness, worst_concavity, worst_concave_points, worst_symmetry, worst_fractal_dimension
):
    input_data = (
        mean_radius, mean_texture, mean_perimeter, mean_area, mean_smoothness,
        mean_compactness, mean_concavity, mean_concave_points, mean_symmetry, mean_fractal_dimension,
        radius_error, texture_error, perimeter_error, area_error, smoothness_error,
        compactness_error, concavity_error, concave_points_error, symmetry_error, fractal_dimension_error,
        worst_radius, worst_texture, worst_perimeter, worst_area, worst_smoothness,
        worst_compactness, worst_concavity, worst_concave_points, worst_symmetry, worst_fractal_dimension
    )

    input_data_np = np.asarray(input_data).reshape(1, -1)
    input_data_std = scaler.transform(input_data_np)
    prediction = model.predict(input_data_std)
    prediction_label = np.argmax(prediction)

    if prediction_label == 1:
        return "🟢 The tumor is *benign*."
    else:
        return "🔴 The tumor is *malignant*."

# Gradio interface
feature_names = ds.feature_names
inputs = [gr.Number(label=label) for label in feature_names]
iface = gr.Interface(fn=predict_tumor_radius, inputs=inputs, outputs="text", title="Breast Cancer Prediction")

iface.launch()