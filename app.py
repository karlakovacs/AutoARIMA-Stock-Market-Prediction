import streamlit as st
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import yfinance as yf
import plotly.graph_objs as go
import pmdarima as pm
from sklearn.metrics import mean_squared_error


def root_mean_squared_error(y_true, y_pred):
    return np.sqrt(mean_squared_error(y_true, y_pred))


def auto_arima(df, test_percentage, num_predictions):
    test_size = int(test_percentage / 100 * len(df))
    train_data = df[:-test_size]
    test_data = df[-test_size:]
    model = pm.auto_arima(train_data, error_action='warn', trace=True, suppress_warnings=True, stepwise=True,
                          random_state=42, n_fits=100)
    model.fit(train_data)
    forecast = model.predict(n_periods=len(test_data))
    rmse = root_mean_squared_error(test_data, forecast)
    model.fit(df)
    auto_arima_predictions = model.predict(n_periods=num_predictions)
    return rmse, auto_arima_predictions


def main():
    st.set_page_config(page_title="AutoARIMA Stock Market Prediction", page_icon=":moneybag:")
    st.sidebar.title("📈AutoARIMA Stock Market Prediction💸")
    st.sidebar.write("Harness the value of AutoARIMA to get the most accurate stock market predictions!🤖")
    ticker = st.sidebar.text_input("Enter a stock ticker symbol🏛️:")
    ticker = ticker.upper()
    option = st.sidebar.checkbox(
        "Specify your custom date range (default: data from the earliest available date to the current day)⌛")
    if ticker and option:
        start_date = st.sidebar.date_input("Select a start date🕘:", datetime.today())
        end_date = st.sidebar.date_input("Select an end date🕔:", datetime.today())
        df = yf.download(ticker, start=start_date, end=end_date)
        df = df['Adj Close']
    elif ticker:
        df = yf.download(ticker)
        df = df['Adj Close']
    num_predictions = st.sidebar.slider("Select the duration of days for which you would like to receive predictions🔮:",
                                        min_value=1, max_value=30, step=1, value=1)
    test_percentage = st.sidebar.slider("Select the percentage of data to be allocated for testing💯:", min_value=1,
                                        max_value=100, step=1, value=20)
    if st.sidebar.button("Get predictions!") and ticker:
        st.header(f"Graph of the {ticker} stock")
        st.write(df)
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=df.index, y=df, mode='lines', name='Actual', line=dict(color='blue')))
        fig.update_layout(title="Stock Data",
                          xaxis_title="Date",
                          yaxis_title="Adj Close Price ($)")
        st.plotly_chart(fig)

        rmse, auto_arima_predictions = auto_arima(df, test_percentage, num_predictions)
        st.header("AutoARIMA Predictions")
        st.write(f"**RMSE:** {rmse}")

        auto_arima_predictions_df = pd.DataFrame(auto_arima_predictions, columns=['Prediction'])

        if option:
            dates = [end_date + timedelta(days=i) for i in range(1, num_predictions + 1)]
        else:
            yesterday = datetime.now() - timedelta(days=1)
            yesterday_start = yesterday.replace(hour=0, minute=0, second=0, microsecond=0)
            dates = [yesterday_start + timedelta(days=i) for i in range(1, num_predictions + 1)]

        auto_arima_predictions_df['Date'] = dates
        auto_arima_predictions_df.set_index('Date', inplace=True)
        st.write(auto_arima_predictions_df)

        trace_actual = go.Scatter(x=df.index, y=df, mode='lines', name='Actual', line=dict(color='blue'))
        trace_predicted = go.Scatter(x=auto_arima_predictions_df.index, y=auto_arima_predictions_df['Prediction'],
                                     mode='lines', name='Predicted', line=dict(color='green'))
        fig = go.Figure([trace_actual, trace_predicted])
        fig.update_layout(title="Actual and Predicted Stock Prices",
                          xaxis_title="Date",
                          yaxis_title="Adj Close Price ($)")
        st.plotly_chart(fig)

    with st.expander("Notes"):
        st.write(
            "**Disclaimer⚠️**: This app is provided for educational and informational purposes only. The forecasts generated by this app are based on historical data and statistical algorithms, and they should not be considered as financial, investment, or trading advice.")
        st.write("AutoARIMA libraries are used for automated time series forecasting and model selection.")
        st.write("**pmdarima🩷** is a Python library for autoARIMA model selection and forecasting.")
        st.write("Evaluation metrics are used to assess the performance of forecasting models.")
        st.write(
            "**RMSE✅** (Root Mean Squared Error) measures the average deviation of the predicted values from the actual values. Lower RMSE indicates better model performance.")
    st.sidebar.markdown("---")
    st.sidebar.markdown("Made with ❤️ by Karla Kovacs")


if __name__ == "__main__":
    main()
