from flask import request, render_template, jsonify, Flask
import yfinance as yf
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import datetime as dt

from sklearn.preprocessing import MinMaxScaler
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Dropout, LSTM

app = Flask(__name__,template_folder='templates')

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/get_stock_data', methods =['POST'])
def get_stock_data():
    ticker = request.get_json()['ticker']
    data = yf.Ticker(ticker).history(period = '1y')
    return jsonify({'currentPrice':data.iloc[-1].Close,'openPrice': data.iloc[-1].Open})


@app.route('/get_prediction', methods =['POST'])
def get_prediction():
    ticker = request.get_json()['ticker']
    company = ticker

    start = dt.datetime(2012, 1, 1)
    end = dt.datetime(2024, 1, 1)

    # Use yfinance to fetch the data
    data = yf.download(company, start=start, end=end)

    # Prepare data
    scaler = MinMaxScaler(feature_range=(0, 1))
    scaled_data = scaler.fit_transform(data['Close'].values.reshape(-1, 1))

    prediction_days = 60

    x_train = []
    y_train = []

    for x in range(prediction_days, len(scaled_data)):
        x_train.append(scaled_data[x - prediction_days:x, 0])
        y_train.append(scaled_data[x, 0])

    x_train = np.array(x_train)
    y_train = np.array(y_train)

    x_train = np.reshape(x_train, (x_train.shape[0], x_train.shape[1], 1))

    # Build the model
    model = Sequential()
    model.add(LSTM(units=60, return_sequences=True, input_shape=(x_train.shape[1], 1)))
    model.add(Dropout(0.3))
    model.add(LSTM(units=60, return_sequences=True))
    model.add(Dropout(0.3))
    model.add(LSTM(units=60))
    model.add(Dropout(0.3))
    model.add(Dense(units=1))

    model.compile(optimizer='adam', loss='mean_absolute_error')
    model.fit(x_train, y_train, epochs=10, batch_size=32)

    '''Testing model accuracy'''

    # Load test data
    test_start = dt.datetime(2020, 1, 1)
    test_end = dt.datetime.now()

    test_data = yf.download(company, start=test_start, end=test_end)
    actual_prices = test_data['Close'].values

    total_dataset = pd.concat((data['Close'], test_data['Close']), axis=0)

    model_inputs = total_dataset[len(total_dataset) - len(test_data) - prediction_days:].values
    model_inputs = model_inputs.reshape(-1, 1)
    model_inputs = scaler.transform(model_inputs)

    # Make predictions on test data
    x_test = []

    for x in range(prediction_days, len(model_inputs)):
        x_test.append(model_inputs[x - prediction_days:x, 0])

    x_test = np.array(x_test)
    x_test = np.reshape(x_test, (x_test.shape[0], x_test.shape[1], 1))

    predicted_prices = model.predict(x_test)
    predicted_prices = scaler.inverse_transform(predicted_prices)
    real_data = model_inputs[len(model_inputs) - prediction_days:]

    real_data = np.reshape(real_data, (1, real_data.shape[0], 1))


    prediction = model.predict(real_data)

    prediction = scaler.inverse_transform(prediction)

    return jsonify({'prediction': float(prediction[0][0])})


if __name__ == '__main__':
    app.run(debug=True)


