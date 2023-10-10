from google.colab import drive
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from tensorflow.keras.preprocessing.text import Tokenizer
from keras.layers import Input, Embedding, LSTM, Dense
from keras.models import Model
import keras.backend as K
from keras.layers import Layer

# Mount Google Drive
drive.mount('/content/drive/')

# Load sample data (replace with your own data)
corpus = pd.read_csv('/content/drive/My Drive/Colab Notebooks/data.csv')
train1 = pd.read_csv('/content/drive/My Drive/Colab Notebooks/data1.csv')
train2 = pd.read_csv('/content/drive/My Drive/Colab Notebooks/data2.csv')

# Tokenize the text data
t = Tokenizer()
t.fit_on_texts(corpus)
text_matrix = t.texts_to_sequences(corpus)
text_pad = pad_sequences(text_matrix, maxlen=32, padding='post')
features = 2
vocab_length = len(t.word_index)  # Use the vocabulary size from the tokenizer

# Split data into train and test sets
train_x, test_x, train_y, test_y = train_test_split(train1, train2, test_size=0.2, random_state=42)

# Define the attention layer
class Attention(Layer):
    def __init__(self, **kwargs):
        super(Attention, self).__init__(**kwargs)

    def build(self, input_shape):
        self.W = self.add_weight(name="att_weight", shape=(input_shape[-1], 1), initializer="normal")
        self.b = self.add_weight(name="att_bias", shape=(input_shape[1], 1), initializer="zeros")
        super(Attention, self).build(input_shape)

    def call(self, x):
        et = K.squeeze(K.tanh(K.dot(x, self.W) + self.b), axis=-1)
        at = K.softmax(et)
        at = K.expand_dims(at, axis=-1)
        output = x * at
        return K.sum(output, axis=1)

    def compute_output_shape(self, input_shape):
        return (input_shape[0], input_shape[-1])

# Define the model architecture
inputs = Input(shape=(features,))
x = Embedding(input_dim=vocab_length + 1, output_dim=32, input_length=features, embeddings_regularizer=keras.regularizers.l2(0.001))(inputs)
att_in = LSTM(100, dropout=0.3, recurrent_dropout=0.2, return_sequences=True)(x)
att_out = Attention()(att_in)
outputs = Dense(1, activation='sigmoid', trainable=True)(att_out)

model = Model(inputs, outputs)
model.compile(loss='binary_crossentropy', optimizer='adam', metrics=['accuracy'])
model.summary()

# Train the model on the sample data
model.fit(x=train_x, y=train_y, batch_size=100, epochs=10, verbose=1, shuffle=True, validation_split=0.2)

# Evaluate the model on test data
test_loss, test_accuracy = model.evaluate(x=test_x, y=test_y)
print("Test Loss:", test_loss)
print("Test Accuracy:", test_accuracy)

# Make predictions on new data (you can replace 'new_data' with your own data)
new_data = np.array(["Your new text data goes here"])
new_data_matrix = t.texts_to_sequences(new_data)
new_data_pad = pad_sequences(new_data_matrix, maxlen=32, padding='post')
predictions = model.predict(new_data_pad)
print("Predictions:", predictions)
