import pandas as pd

import matplotlib.pyplot as plt

import numpy as np

import yfinance as yf

import matplotlib.ticker as mtick

import streamlit as st

from matplotlib.figure import Figure

import plotly.graph_objects as go


# streamlit run "c:/Users/Mike Souroullas/Desktop/Personal/Finance_project/Python/stock_analysis_function.py"

#setting a streamline tittle
st.markdown(
    """
    <div style='text-align: center; padding-top: 10px;'>
        <h4 style='margin-bottom: 0; font-family: Arial; color: #333333;'>
            🚀 The 2 stock comparison analysis 🚀
        </h4>
    </div>
    """,
    unsafe_allow_html=True
)

# Sidebar inputs to streamline
with st.sidebar.form(key = 'input_form'):
    x = st.text_input("Enter first stock ticker:", "AAPL")
    y = st.text_input("Enter second stock ticker:", "TSLA")
    years = st.slider("Years to look back:", 1, 20, 10)
    submit = st.form_submit_button(label = 'Submit')
    placeholder_for_radio = st.empty()

if years < 5:
    volatility_window = 21 #rolling window size in days for daily volatility calculation - short term investing
    annualisation_factor = 1
    rolling_window = 21
    subplot_title = f'Short Term Analysis of {years} years, {x} vs {y}'
elif years >=5:
    volatility_window = 252 #rolling window size in days for daily volatility calculation - short term investing
    annualisation_factor = 252**0.5
    rolling_window = 252
    subplot_title = f'Long Term Analysis of {years} years, {x} vs {y}'  

# if submit:  
#     #store inputs in session state on form submit
#     st.session_state['ticker1'] = x
#     st.session_state['ticker2'] = y
#     st.session_state['years'] = years

with st.container():

    #Fetch data    
    df = yf.Ticker(x).history(period= f'{years}y')
    df = df.reset_index() #Yahoo imports date as an index and has to become a collumn

    df1 = yf.Ticker(y).history(period= f'{years}y') 
    df1 = df1.reset_index() #Yahoo imports date as an index and has to become a collumn

    # #store fetched data
    # st.session_state['df'] = df
    # st.session_state['df1'] = df1

    # if 'df' in st.session_state and 'df1' in st.session_state:
    #     st.write(f"Data for {st.session_state['Enter first stock ticker:']} and {st.session_state['Enter second stock ticker:']} over {st.session_state['years']} years loaded.")
    #     df = st.session_state['df']
    #     df1 = st.session_state['df1']
   
    # else:
    #     st.write("Submit the form to load data.")

    #variables
    risk_free_rate_daily = 0 #daily risk-free ratio, set to 0 if unknown


    #calculating daily returns: [Price(t)/Price(t-1)] -1
        #Stock 1

    df['daily_return'] = df['Close'].pct_change()
    df_returns = df.dropna(subset=['daily_return'])[['Date','daily_return']]

        #Stock 2

    df1['daily_return'] = df1['Close'].pct_change()
    df1_returns = df1.dropna(subset=['daily_return'])[['Date','daily_return']]

        #setting date as the index to be plotted on the x-axis
            #setting date as the index to plot the Close to date for stock 1
    df['Date'] = pd.to_datetime(df['Date'],yearfirst=True)
    df.set_index('Date', inplace=True)
            #setting date as the index to plot the Close to date for stock 2
    df1['Date'] = pd.to_datetime(df1['Date'],yearfirst=True)
    df1.set_index('Date',inplace=True)

        #moving average on a monthly window moving(approx 21 trading days) average to smooth out the noice (trend line)
    df['moving_average_21'] = df['Close'].rolling(window=21).mean()
    df1['moving_average_21'] = df1['Close'].rolling(window=21).mean()

    #Plotting the Close price over time
        #axes[0].plt.figure(figsize=(12,6))
    fig0 = go.Figure()

    # Plot raw Close prices for x and y
    fig0.add_trace(go.Scatter(
    x=df.index, 
    y=df['Close'], 
    mode='lines', 
    name=f'{x} Close',
    line=dict(color='blue')
    ))

    fig0.add_trace(go.Scatter(
    x=df1.index, 
    y=df1['Close'], 
    mode='lines', 
    name=f'{y} Close',
    line=dict(color='orange')
    ))

    # Plot moving averages with dashed lines
    fig0.add_trace(go.Scatter(
    x=df.index,
    y=df['moving_average_21'],
    mode='lines',
    name=f'{x} 21-Day MA',
    line=dict(color='green', dash='dash')
    ))

    fig0.add_trace(go.Scatter(
    x=df1.index,
    y=df1['moving_average_21'],
    mode='lines',
    name=f'{y} 21-Day MA',
    line=dict(color='purple', dash='dash')
    ))

    # Layout titles and axis labels
    fig0.update_layout(
    width = 2000,
    height = 500,
    title=f"{x} vs {y} Adjusted Closing Prices",
    xaxis_title='Year',
    yaxis_title='Close Price',
    legend_title='Legend',
    hovermode='x unified',  # better hover info on x axis
    template='plotly_white', # clean white background
    legend=dict(
        orientation='h',       # horizontal layout
        x=0.5,                 # center of the plot horizontally
        y=-0.2,                # push it below the x-axis
        xanchor='center',
        yanchor='top'
    )
    )


    #Calculating yearly return
        #Function to calculate yearly return
    def calculate_yearly_return(df):
        #resample =get first and last Close prices for each year
        yearly = df['Close'].resample('YE').agg(['first','last'])
        yearly['yearly_return'] = yearly['last']/yearly['first'] - 1
        return yearly['yearly_return']

        #calculating the yearly returns for stock1 and stock2
    stock1_yearly_returns = calculate_yearly_return(df)
    stock2_yearly_returns = calculate_yearly_return(df1)

        #calculating the average of stock yearly 
    stock1_mean_yearly_returns = calculate_yearly_return(df).mean()
    stock2_mean_yearly_returns = calculate_yearly_return(df1).mean()
    both_stocks_mean_yearly_returns = (stock1_mean_yearly_returns + stock2_mean_yearly_returns)/2

        #combining yearly returns into one data frame to be plotted as a bar chart
    combined_yearly_returns = pd.DataFrame({ x : stock1_yearly_returns, y : stock2_yearly_returns})

        #converting the dates to 2022 instead of 2022-12-31
    combined_yearly_returns.index = combined_yearly_returns.index.year

    fig1 = go.Figure()

    # Actual bars for yearly returns
    fig1.add_trace(go.Bar(
    x=combined_yearly_returns.index.astype(str),
    y=combined_yearly_returns[x],
    name=f"{x} Yearly Return",
    marker_color='blue'
    ))
    fig1.add_trace(go.Bar(
    x=combined_yearly_returns.index.astype(str),
    y=combined_yearly_returns[y],
    name=f"{y} Yearly Return",
    marker_color='orange'
    ))

    # Add invisible scatter traces to show average yearly returns in legend
    fig1.add_trace(go.Scatter(
    x=[None],
    y=[None],
    mode='markers',
    marker=dict(color='rgba(0,0,0,0)'),
    showlegend=True,
    name=f"{x} Avg yearly return: {stock1_mean_yearly_returns*100:.2f}%"
    ))
    fig1.add_trace(go.Scatter(
    x=[None],
    y=[None],
    mode='markers',
    marker=dict(color='rgba(0,0,0,0)'),
    showlegend=True,
    name=f"{y} Avg yearly return: {stock2_mean_yearly_returns*100:.2f}%"
    ))
    fig1.add_trace(go.Scatter(
    x=[None],
    y=[None],
    mode='markers',
    marker=dict(color='rgba(0,0,0,0)'),
    showlegend=True,
    name=f"Combined Avg yearly Return: {both_stocks_mean_yearly_returns*100:.2f}%"
    ))

    fig1.update_layout(
    title=f"{x} vs {y} Yearly Returns",
    xaxis_title='Year',
    yaxis_title='Yearly Return',
    barmode='group',
    template='plotly_white',
    legend_title_text='Stocks & Averages',
    legend=dict(
    orientation='h',       # horizontal layout
    x=0.5,                 # center of the plot horizontally
    y=-0.2,                # push it below the x-axis
    xanchor='center',
    yanchor='top'
    ))

    #Volatility calculation

        #calculating the natural logarithm return of each day (Log Retruns)
    df['log_return'] = np.log(df['Close']/df['Close'].shift(1))
    df1['log_return'] = np.log(df1['Close']/df1['Close'].shift(1))

        #calculating rolling standard deviation of log return for every day and multiplying it by the annualisation_factor - Long term analysis

    df['log_volatility'] = (df['log_return'].rolling(window=volatility_window).std(ddof=1)) * annualisation_factor

    df1['log_volatility'] = (df1['log_return'].rolling(window=volatility_window).std(ddof=1)) * annualisation_factor

        #Plotting the volatility

    fig2 = go.Figure()

    fig2.add_trace(go.Scatter(
    x=df.index,
    y=df['log_volatility'],
    mode='lines',
    name=x,
    line=dict(color='blue')
    ))

    fig2.add_trace(go.Scatter(
    x=df1.index,
    y=df1['log_volatility'],
    mode='lines',
    name=y,
    line=dict(color='orange')
    ))

    fig2.update_layout(
    title=f'Annualised Rolling Log Volatility ({volatility_window}-Day Window)',
    xaxis_title='Date',
    yaxis_title='Annualised Log Volatility',
    legend_title='Legend',
    template='plotly_white',
    hovermode='x unified',
    legend=dict(
    orientation='h',       # horizontal layout
    x=0.5,                 # center of the plot horizontally
    y=-0.2,                # push it below the x-axis
    xanchor='center',
    yanchor='top'
    ))
    

    #calculating annualised rolling sharpe ratio

    df['rolling_mean'] = df['log_return'].rolling(window=rolling_window).mean()
    df['rolling_std']= df['log_return'].rolling(window=rolling_window ).std(ddof=1)

    df['rolling_sharpe'] = ((df['rolling_mean'] - risk_free_rate_daily) / df['rolling_std']) * annualisation_factor

    df1['rolling_mean'] = df1['log_return'].rolling(window=rolling_window).mean()
    df1['rolling_std']= df1['log_return'].rolling(window=rolling_window ).std(ddof=1)

    df1['rolling_sharpe'] = ((df1['rolling_mean'] - risk_free_rate_daily) / df1['rolling_std']) * annualisation_factor


    fig3 = go.Figure()

    fig3.add_trace(go.Scatter(
    x=df.index,
    y=df['rolling_sharpe'],
    mode='lines',
    name=x,
    line=dict(color='blue')
    ))

    fig3.add_trace(go.Scatter(
    x=df1.index,
    y=df1['rolling_sharpe'],
    mode='lines',
    name=y,
    line=dict(color='orange')
    ))

    fig3.update_layout(
    title=f'Annualised Sharpe Ratio ({rolling_window}-Day Window)',
    xaxis_title='Date',
    yaxis_title='Annualised Sharpe Ratio',
    legend_title='Legend',
    template='plotly_white',
    hovermode='x unified',
    legend=dict(
    orientation='h',       # horizontal layout
    x=0.5,                 # center of the plot horizontally
    y=-0.2,                # push it below the x-axis
    xanchor='center',
    yanchor='top'
    ))


    #creating a subplot for the 2nd window

    #Calculating Cumulative return
    df['cumulative_return'] = df['Close']/df['Close'].iloc[0] -1
    df1['cumulative_return'] = df1['Close']/df1['Close'].iloc[0] -1

        #calculating the return from the first day of the 10 years to today
    total_return_stock1 = (df['Close'].iloc[-1] / df['Close'].iloc[0] -1) * 100
    total_return_stock2 = (df1['Close'].iloc[-1] / df1['Close'].iloc[0] -1) * 100

    fig4 = go.Figure()

    fig4.add_trace(go.Scatter(
    x=df.index,
    y=df['cumulative_return']*100,
    mode='lines',
    name=f'{x}, Total Return = {total_return_stock1:.2f}%',
    line=dict(color='blue')
    ))

    fig4.add_trace(go.Scatter(
    x=df1.index,
    y=df1['cumulative_return']*100,
    mode='lines',
    name=f'{y}, Total Return = {total_return_stock2:.2f}%',
    line=dict(color='orange')
    ))

    fig4.update_layout(
    title='cumulative Return',
    xaxis_title='Date',
    yaxis_title='cumulative Return (%)',
    legend_title='Legend',
    template='plotly_white',
    hovermode='x unified',
    legend=dict(
    orientation='h',       # horizontal layout
    x=0.5,                 # center of the plot horizontally
    y=-0.2,                # push it below the x-axis
    xanchor='center',
    yanchor='top'
    ))
    

    #cumulative return if invested 1000£

    money_invested = 1000;

    df['cumulative_return_money'] = (df['Close']/df['Close'].iloc[0]) * money_invested
    df1['cumulative_return_money'] = (df1['Close']/df1['Close'].iloc[0])* money_invested

        #calculating the return from the first day of the 10 years to today
    total_return_money_stock1 = (df['Close'].iloc[-1] / df['Close'].iloc[0]) * money_invested
    total_return_money_stock2 = (df1['Close'].iloc[-1] / df1['Close'].iloc[0]) * money_invested

    #plotting cumulative return with money example
    fig5 = go.Figure()

    fig5.add_trace(go.Scatter(
    x=df.index,
    y=df['cumulative_return_money'],
    mode='lines',
    name=f'{x}, Total Return = £{total_return_money_stock1:.2f}',
    line=dict(color='blue')
    ))

    fig5.add_trace(go.Scatter(
    x=df1.index,
    y=df1['cumulative_return_money'],
    mode='lines',
    name=f'{y}, Total Return = £{total_return_money_stock2:.2f}',
    line=dict(color='orange')
    ))

    fig5.update_layout(
    title=f'Return if £{money_invested} were invested {years} years ago today',
    xaxis_title='Date',
    yaxis_title='Return (£)',
    yaxis=dict(tickprefix='£', separatethousands=True),
    legend_title='Legend',
    hovermode='x unified',
    template='plotly_white',
    legend=dict(
    orientation='h',       # horizontal layout
    x=0.5,                 # center of the plot horizontally
    y=-0.2,                # push it below the x-axis
    xanchor='center',
    yanchor='top'
    ))
    

    #Drawdown and Max Drawdown calculation

        #calculating running peak (cumulative max)
    df['Current_peak'] = df['Close'].cummax()
    df1['Current_peak'] = df1['Close'].cummax()
        #calculating drawdown
    df['Drawdown'] = (df['Close'] - df['Current_peak']) / df['Current_peak']
    df1['Drawdown'] = (df1['Close'] - df1['Current_peak']) / df1['Current_peak']
        #calculating max drawdown
    max_drawdown1 = (df['Drawdown'].min())
    max_drawdown_date1 = df['Drawdown'].idxmin()
    max_drawdown_date1 = str(max_drawdown_date1)[:10]

    max_drawdown2 = (df1['Drawdown'].min())
    max_drawdown_date2 = df1['Drawdown'].idxmin()
    max_drawdown_date2 = str(max_drawdown_date2)[:10]


    #plotting the drowdown
    fig6 = go.Figure()

    fig6.add_trace(go.Scatter(
    x=df.index,
    y=df['Drawdown'],
    mode='lines',
    name=f'{x}, Max Drawdown = {max_drawdown1*100:.2f}%, {max_drawdown_date1}',
    line=dict(color='blue')
    ))

    fig6.add_trace(go.Scatter(
    x=df1.index,
    y=df1['Drawdown'],
    mode='lines',
    name=f'{y}, Max Drawdown = {max_drawdown2*100:.2f}%, {max_drawdown_date2}',
    line=dict(color='orange')
    ))

    fig6.update_layout(
    title=f'Drawdown the past {years} years',
    xaxis_title='Date',
    yaxis_title='Drawdown',
    legend_title='Legend',
    hovermode='x unified',
    template='plotly_white',
    legend=dict(
    orientation='h',       # horizontal layout
    x=0.5,                 # center of the plot horizontally
    y=-0.2,                # push it below the x-axis
    xanchor='center',
    yanchor='top'
    ))
    

    #calculating rolling correlation of the 2 stocks

    rolling_correlation = df['log_return'].rolling(window=volatility_window).corr(df1['log_return'])

    #plotting the drowdown
    fig7 = go.Figure()

    fig7.add_trace(go.Scatter(
    x=rolling_correlation.index,
    y=rolling_correlation,
    mode='lines',
    name='Rolling correlation',
    line=dict(color='purple')
    ))

    fig7.update_layout(
    title=f'Rolling correlation of {x} & {y}',
    xaxis_title='Date',
    yaxis_title='Rolling correlation',
    yaxis=dict(range=[-1.2, 1.2]),
    legend_title='Legend',
    hovermode='x unified',
    template='plotly_white',
    legend=dict(
    orientation='h',       # horizontal layout
    x=0.5,                 # center of the plot horizontally
    y=-0.2,                # push it below the x-axis
    xanchor='center',
    yanchor='top'
    ))
    
    
    #chooseing plot to be shown
    chart_options = ["Closing Prices", "Yearly returns (%)", "Rolling Volatility", "Sharpe Ratio", "Cumulative Return", "What if I invested £1000", "Drawdown", "Rolling Correlation"]

    #Sidebar radio button

    selected_chart = st.sidebar.radio("Please choose a chart", chart_options)

    if selected_chart == 'Closing Prices':
        st.plotly_chart(fig0)
        st.markdown("**<u>Notes:</u>**", unsafe_allow_html=True)
        st.write(f"The plot above represents the closing price of each stock every day for the past {years} years, even though it is not a good metric to compare stocks, it is good to gain a first understanding of how the stocks have been behaving in the given timeframe.")
        st.write("For the best user experience please view the plot in full-screen")
        st.write("Oh! And the plot is fully interactive!😀")
    elif selected_chart == 'Yearly returns (%)':
        st.plotly_chart(fig1)
        st.markdown("**<u>Notes:</u>**", unsafe_allow_html=True)
        st.write("The bar chart above indicates the yearly percentage (%) return of each stock per year! ")
        st.write(f"We can see that the percentage yearly return of **{x}** was **{stock1_mean_yearly_returns*100:.2f}%** through the past {years} years, while **{y}** had a yealy return of **{stock2_mean_yearly_returns*100:.2f}%** ")
        st.write(f"Owning both stocks in the pre-defined duration, would return an average yeatly return of **{both_stocks_mean_yearly_returns*100:.2f}%**")
        st.write("For the best user experience please view the plot in full-screen")
        st.write("Oh! And the plot is fully interactive!😀")
    
    elif selected_chart == 'Rolling Volatility':
        st.plotly_chart(fig2)
        st.markdown("**<u>Notes:</u>**", unsafe_allow_html=True)
        st.write("The rolling volatility plot shows how a stock’s risk or price fluctuations change over time. It helps us spot periods of higher or lower uncertainty, so we can better understand the market's mood and adjust our strategies accordingly.")
        st.write("When the rolling volatility plot **peaks**, it means the asset’s price is experiencing higher fluctuations or risk, the market is more uncertain or volatile. When the plot **troughs** (goes down), it shows periods of lower price movement and calmer, more stable market conditions.")
        st.write("Rolling Volatility is calcualted as the **Standard Deviation of log Returns** over a time window (21 days for short-term analyis & 251 days for long term analysis) and then it is **annualised** by multiplying it by √252. This gives a smoothed, time-varying measure of how much the stock returns fluctuate on an annual basis." )
        st.write("For the best user experience please view the plot in full-screen")
        st.write("Oh! And the plot is fully interactive!😀")

    elif selected_chart == 'Sharpe Ratio':
        st.plotly_chart(fig3)
        st.markdown("**<u>Notes:</u>**", unsafe_allow_html=True)
        st.write("The Sharpe ratio measures how much **return** an investment generates for each unit of **risk** taken. A higher Sharpe ratio means you’re getting more reward for the risk you’re taking, helping you compare how well different investments are performing on a risk-adjusted basis.")
        st.write("When the Sharpe ratio **peaks**, it means the investment is delivering **strong returns relative to its risk**, a good time in terms of risk-adjusted performance, while when it **troughs** or goes low, it means returns aren’t compensating well for the risk taken, indicating **less efficient or more unfavorable performance**.")
        st.write("The rolling Sharpe ratio is calculated by dividing the **rolling average of excess returns** (log return minus the daily risk-free rate) by the **rolling standard deviation of log returns**, which is also known as **rolling volatility**. To make it comparable on an annual basis, the result is multiplied by an annualisation factor of √252 ")
        st.write("For the best user experience please view the plot in full-screen")
        st.write("Oh! And the plot is fully interactive!😀")

    elif selected_chart == 'Cumulative Return':
        st.plotly_chart(fig4)
        st.markdown("**<u>Notes:</u>**", unsafe_allow_html=True)
        st.write("The cumulative return plot shows how much an investment has **grown** or **shrunk** over time, combining all daily returns up to each point. It gives a clear, visual picture of the total performance of the asset from the starting point, expressed as a percentage gain or loss.")
        st.write("When the cumulative return plot peaks, it means the investment has gained value and is at a local high point in its growth. When it troughs, the value has declined, reflecting a period of negative performance. Overall, upward trends show compounding growth, while downward trends indicate losses.")
        st.write("Cumulative return is calculated by taking the current price and dividing it by the initial price, then subtracting 1. This gives the total return relative to the starting point. The result is multiplied by 100 to express it as a percentage")
        st.write("For the best user experience please view the plot in full-screen")
        st.write("Oh! And the plot is fully interactive!😀")

    elif selected_chart == 'What if I invested £1000':
        st.plotly_chart(fig5)
        st.write("The what if I invested £1000 graph is more to help us understand the impact of growth using a metric we are all familiar with.")
        st.write(f"How crazy is it that if you invested £1000 in **{x} {years}** years ago you would now have **£{total_return_money_stock1:.2f}**, while if you invested the £1000 in **{y}** you would now have **£{total_return_money_stock2:.2f}**")
        st.write("For the best user experience please view the plot in full-screen")
        st.write("Oh! And the plot is fully interactive!😀")

    elif selected_chart == 'Drawdown':
        st.plotly_chart(fig6)
        st.write("The drawdown plot shows the percentage **loss** from the investment’s **highest** value up to that point. It highlights the **worst declines over time**, helping to visualise how deep and how long the investment stayed below its peak — a key insight into downside risk and recovery patterns.")
        st.write("A peak (near 0%) in the drawdown plot means the investment is at or close to its historical maximum value. A trough (more negative) indicates a period where the price has fallen significantly from its peak — the deeper the trough, the larger the drawdown. Rising slopes show recovery from losses, while falling slopes reflect worsening declines.")
        st.write(f"**{x}** had a **Max Drawdown** of **{max_drawdown1*100:.2f}%** on **{max_drawdown_date1}** while **{y}** had a **Max Drawdown** of **{max_drawdown2*100:.2f}%** on **{max_drawdown_date2}**")
        st.write("For the best user experience please view the plot in full-screen")
        st.write("Oh! And the plot is fully interactive!😀")
        
    elif selected_chart == 'Rolling Correlation':
        st.plotly_chart(fig7)
        st.write("The rolling correlation plot shows how the **relationship between two investment's returns** changes over time. It helps reveal whether they tend to **move together** (positive correlation), move in **opposite** directions (negative correlation), or behave **independently**. It's a great way to monitor changing co-movement patterns.")
        st.write("A **peak (close to +1)** indicates a strong positive correlation — the two stocks have been moving **together**. A **trough (close to -1)** suggests strong negative correlation — they’ve been moving in **opposite** directions. Values near **0** indicate little to **no consistent relationship**. Changes in the plot highlight shifts in how the two assets interact over time.")
        st.write(f"Rolling correlation is calculated by taking the **correlation coefficient** between two sets of returns (e.g., log returns of {x} and {y}) over a moving window. For each point in time, the correlation is computed based on the past n days of returns")
        st.write("For the best user experience please view the plot in full-screen")
        st.write("Oh! And the plot is fully interactive!😀")
