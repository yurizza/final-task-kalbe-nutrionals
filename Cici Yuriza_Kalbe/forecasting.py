# -*- coding: utf-8 -*-
"""forecasting.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1kX0Ec1qSxdSzygdV4oofZo0VIfa1eIhC

## Time Series Forecasting

**Problem Statement:**
As a Data Scientist at Kalbe Nutritionals, you have been tasked by the inventory teams to assist in predicting the sales quantity of the entire range of Kalbe products.

**Objective:**
The goal of this project is to develop a forecasting model that can predict the daily sales quantity of Kalbe products. This model will be utilized to generate estimates of the quantity of products that will be sold in the future.

### 1. Load Dataset
"""

pip install pmdarima

import pandas as pd
import matplotlib.pyplot as plt

from statsmodels.tsa.arima.model import ARIMA
from statsmodels.tsa.stattools import adfuller
from statsmodels.graphics.tsaplots import plot_acf, plot_pacf

from sklearn.metrics import mean_squared_error
import numpy as np

import warnings

# Disable all warnings
warnings.filterwarnings("ignore")

# Or, only disable specific warnings based on category
# Example: Disabling DeprecationWarning
warnings.filterwarnings("ignore", category=DeprecationWarning)

from google.colab import drive
drive.mount('/content/drive')

folder_path = '/content/drive/MyDrive/rakamin/kalbe/'

df = pd.read_csv(folder_path+'df_merged.csv')

df.head()

df.info()

# Convert the "Date" column to datetime data type with the specified format
df['Date'] = pd.to_datetime(df['Date'], format='%Y-%m-%d')

"""### 2. Calculate Total Quantity per day"""

df_totalquantity = df.groupby('Date')["Qty"].sum().reset_index()

df_totalquantity.info()

df_totalquantity.set_index('Date', inplace=True)

from pylab import rcParams
rcParams['figure.figsize'] = 20, 7
df_totalquantity.plot(marker='o')
plt.show()

# Assuming df_totalquantity is your DataFrame with 'Date' as the index
df_totalquantity.boxplot()
plt.title('Boxplot of Total Quantity')
plt.ylabel('Total Quantity')
plt.xlabel('Date')
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()

"""### 3. Stationary Test

H0: It is non-stationary

H1: It is stationary

p-value <= 0.05 so H0 rejected.

p-value >0.05 so H0 accepted.
"""

def adfuller_test(sales):
    result=adfuller(sales)
    labels = ['ADF Test Statistic','p-value','#Lags Used','Number of Observations']
    for value,label in zip(result,labels):
        print(label+' : '+str(value) )

    if result[1] <= 0.05:
        print("strong evidence against the null hypothesis(Ho), reject the null hypothesis. Data is stationary")
    else:
        print("weak evidence against null hypothesis,indicating it is non-stationary ")

adfuller_test(df_totalquantity['Qty'])

"""data is already stationary.

Now looking the p, d and q value for ARIMA

### 4. Chose best p, d and q
"""

# Create ACF and PACF plots
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8))
plot_acf(df_totalquantity['Qty'], lags=30, ax=ax1)
plot_pacf(df_totalquantity['Qty'], lags=30, ax=ax2)

plt.tight_layout()
plt.show()

"""p = 4
q = 4
d = 0
"""

aic_scores = []
# Fit the ARIMA model
model = ARIMA(df_totalquantity['Qty'], order=(4,0,4))
model_fit = model.fit()
# Add AIC score to the list
aic_scores.append({'par': '(4,0,4)', 'aic': model_fit.aic})

aic_scores

"""#### grid search hyperparameter tuning"""

from itertools import product

# Define ranges for p, d, and q
p = range(0, 5)  # 0 to 7
d = range(0, 3)  # 0 to 2
q = range(0, 5)  # 0 to 7

# Use the product function from itertools
# to create combinations of p, d, and q
pdq = list(product(p, d, q))
print(pdq)

"""Manual grid search to find the optimal combination of parameters (p, d, q) for an ARIMA model based on the lowest AIC score."""

# Splitting data into training and testing with ratio 8 : 2
data_train = df_totalquantity[:292]["Qty"]
data_test = df_totalquantity[292:]['Qty']

# Creating a list to store AIC scores
aic_scores = []

# Performing manual grid search to find optimal p, d, q
for param in pdq:
    # Fitting the ARIMA model
    model = ARIMA(data_train, order=param)
    model_fit = model.fit()
    # Adding AIC score to the list
    aic_scores.append({'par': param, 'aic': model_fit.aic})

# Finding the smallest AIC score
best_aic = min(aic_scores, key=lambda x: x['aic'])

print(best_aic)

# Creating an ARIMA model with the best p, d, and q from grid search
model = ARIMA(data_train, order=(best_aic['par']))
model_fit = model.fit()

# Making predictions for the next 73 days (testing data)
preds = model_fit.forecast(73)

preds.plot()

"""#### auto arima
Choose p, d and q automatic
"""

import pmdarima as pm

auto_arima = pm.auto_arima(data_train,stepwise=False, seasonal=False)
forecast = auto_arima.predict(n_periods=73)

auto_arima.summary()

# ploting
forecast.plot(label='auto arima')
preds.plot(label='grid search')

data_train.plot(label='train')
data_test.plot(label='test')
plt.legend()

"""While both methods, Auto ARIMA and grid search, are useful in selecting optimal parameters for the ARIMA model, in this case, the use of **grid search seems more appropriate.**

### 5. evaluate model
"""

# Calculate RMSE for training data
train_predictions = model_fit.predict(start=data_train.index[0], end=data_train.index[-1])
train_rmse = np.sqrt(mean_squared_error(data_train, train_predictions))

# Calculate RMSE for testing data
test_rmse = np.sqrt(mean_squared_error(data_test, preds))

print(f"RMSE for Training Data: {train_rmse:.2f}")
print(f"RMSE for Testing Data: {test_rmse:.2f}")

df_totalquantity.plot(figsize=(15, 6), alpha=0.5, marker="o")
preds.plot(linewidth=2, marker="o", legend=True)

"""The parameter values p = 2, d = 1, and q = 3 resulted in an RMSE value of 14.07 dan RMSE for Training Data is 16.89.

The difference between the RMSE values for training (16.89) and testing (14.07) is not too large suggests that the model is not overfitting. A smaller difference indicates that the model is generalizing reasonably well to unseen data.

### 6. forecasting 30 days using p = 2, d = 1 and q=3
"""

from pandas.tseries.offsets import DateOffset

future_dates=[df_totalquantity.index[-1]+ DateOffset(days=x)for x in range(0,31)]
future_dates_df=pd.DataFrame(index=future_dates[1:],columns=df_totalquantity.columns)

future_df = pd.concat([df_totalquantity,future_dates_df])

model=ARIMA(df_totalquantity['Qty'], order=(2,1,3))
model_fit=model.fit()

future_df['forecast'] = model_fit.predict(start = 0, end = 395, dynamic = False)
future_df[['Qty', 'forecast']].plot(figsize=(12, 8))

future_df.tail(30).mean()

"""### 7. Saving Model"""

import pickle

# Creating an ARIMA model with the best p, d, and q from grid search
model = ARIMA(df_totalquantity['Qty'], order=best_aic['par'])
model_fit = model.fit()

# Save the model to a file using pickle
model_filename = 'arima_model.pkl'
with open(folder_path+model_filename, 'wb') as model_file:
    pickle.dump(model_fit, model_file)

print("Model saved successfully!")

import pickle
# Load the ARIMA model from the file
model_filename = 'arima_model.pkl'
with open(folder_path + model_filename, 'rb') as model_file:
    loaded_model_fit = pickle.load(model_file)

# Number of days for prediction
num_days = 30

# Forecast the next 30 days
forecast = loaded_model_fit.forecast(steps=num_days)

print("Forecasted quantities for the next", num_days, "days:")
print(forecast)

forecast.plot()

"""### Conclusion
1. The ARIMA parameters, namely p, d, and q, are set to 2, 1, and 3, respectively.
2. The RMSE values for the training and testing datasets are 17.41 and 13.47, respectively.
3. No Overfitting Detected: The model is not exhibiting overfitting.
4. Exploring Alternative Time Series Algorithms: Let's try utilizing different time series algorithms.
"""