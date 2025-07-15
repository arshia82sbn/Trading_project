#!/usr/bin/env python
# coding: utf-8

# In[1]:
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from numba import njit

symbol_info = {
    "EURUSD": {
        "digits": 5,
        "point": 0.00001,
        "tick_value": 10,
        "tick_size": 0.0001,
        "min_volume": 0.01,
        "max_volume": 100.0,
        "volume_step": 0.01,
    },
    "USDJPY": {
        "digits": 3,
        "point": 0.001,
        "tick_value": 1000,
        "tick_size": 0.01,
        "min_volume": 0.1,
        "max_volume": 50.0,
        "volume_step": 0.1,
    },
    "GBPUSD": {
        "digits": 5,
        "point": 0.00001,
        "tick_value": 10,
        "tick_size": 0.0001,
        "min_volume": 0.01,
        "max_volume": 200.0,
        "volume_step": 0.01,
    },
    "AUDUSD": {
        "digits": 5,
        "point": 0.00001,
        "tick_value": 7,
        "tick_size": 0.0001,
        "min_volume": 0.01,
        "max_volume": 150.0,
        "volume_step": 0.01,
    },
}


def process_and_plot(csv_path, analysis_params):
    global inputs
    inputs = analysis_params  # Ensure analysis_params is set globally for use in generating signals
    print("processing...")

    # Load data
    df = pd.read_csv(csv_path)
    df['Time'] = pd.to_datetime(df['Time'])
    print('file read')
    # Apply selected indicators (Moving Average, MACD, Stochastic)
    indicator_counting = 1
    print('ma')
    # Moving Averages
    if 'moving_average1' in analysis_params:
        df = calculate_moving_averages(df, analysis_params['moving_average1'])
    if 'moving_average2' in analysis_params:
        df = calculate_moving_averages(df, analysis_params['moving_average2'])
    print('macd')
    # MACD
    if 'macd' in analysis_params:
        macd_config = analysis_params['macd']
        df = calculate_macd(df, macd_config['short_period'], macd_config['long_period'], macd_config['signal_period'])
    print('stochastic')
    # Stochastic
    if 'stochastic' in analysis_params:
        stochastic_config = analysis_params['stochastic']
        df = calculate_stochastic(df, stochastic_config['k_period'], stochastic_config['d_period'], stochastic_config['smoothing_factor'])
    print('get month and balance')
    # Parameters for trade signals
    year = 2023
    month = analysis_params['month']
    balance = analysis_params['balance']
    print('generate_signals')    
    df_with_signals = generate_signals(df, year, month, indicator_counting, balance)

    print('manage_signals')
    positions_df = manage_signals(df_with_signals, balance, risk=0.01)
    check_df = check(df_with_signals, positions_df)
    trades_df = calculate_balance_and_volume(check_df, balance, risk=0.01).dropna()

    print('ploting...')
    plot(trades_df, df_with_signals)
    print('plot done')
    return trades_df, df_with_signals
# In[2]:


def calculate_moving_averages(df, period):
    df[f'MA {period}'] = df['Close'].rolling(window=period).mean()
    return (df)

def calculate_macd(df, short_period, long_period, signal_period):
    EMA_short = df['Close'].ewm(span=short_period, adjust=False).mean()
    EMA_long = df['Close'].ewm(span=long_period, adjust=False).mean()

    df['MACD'] = EMA_short - EMA_long
    df['MACD_signal'] = df['MACD'].ewm(span=signal_period, adjust=False).mean()
    df['MACD_Histogram'] = df['MACD'] - df['MACD_signal']
    
    return (df)
def calculate_stochastic(df, k_period, d_period, smoothing_factor):

    low_min = df['Low'].rolling(window=k_period).min()
    high_max = df['High'].rolling(window=k_period).max()

    df['Stochastic %K'] = ((df['Close'] - low_min) / (high_max - low_min)) * 100
    df['Stochastic %K_smooth'] = df['Stochastic %K'].rolling(window=smoothing_factor).mean()
    df['Stochastic %D'] = df['Stochastic %K_smooth'].rolling(window=d_period).mean()
    return (df)


# In[3]:


def generate_signals(df_org, year, month, indicator_counting, balance,analysis_params):
    df_year = df_org[df_org['Time'].dt.year == year].copy()
    df_month = df_year[df_year['Time'].dt.month == month].copy()
    df = df_month.reset_index(drop= True).copy()
    
# بررسی موجود بودن کلیدهای مربوط به Moving Average
    if 'moving_average1' in analysis_params and 'moving_average2' in analysis_params:
        ma1 = analysis_params['moving_average1']
        ma2 = analysis_params['moving_average2']
    else:
        raise ValueError("Missing 'moving_average1' or 'moving_average2' in analysis_params")
    
    df['MA_Signal'] = 0

    # Fast from down cross slow
    MA_buy_signal = (df[f'MA {ma1}'] > df[f'MA {ma2}']) & \
                    (df[f'MA {ma1}'].shift(1) <= df[f'MA {ma2}'].shift(1))
    
    # Fast from up cross slow
    MA_sell_signal = (df[f'MA {ma1}'] < df[f'MA {ma2}']) & \
                     (df[f'MA {ma1}'].shift(1) >= df[f'MA {ma2}'].shift(1))

    df.loc[MA_buy_signal, 'MA_Signal'] = 1
    df.loc[MA_sell_signal, 'MA_Signal'] = -1
    df['MA_Signal'] = df['MA_Signal'].replace(0, None).ffill().fillna(0)

    # MACD or Stochastic Signals
    trade_lock = False
    macd_state = 1
    stoch_state = 1
    df['MACD_Signal'] = 0
    df['Stoch_Signal'] = 0

    for i in range(1, len(df)):
        if df['MA_Signal'].iloc[i] == 1 and not trade_lock:
            if macd_state == 1 and df['MACD_Histogram'].iloc[i] > 0:
                macd_state = 2
            elif macd_state == 2 and df['MACD_Histogram'].iloc[i] < 0:
                df.loc[i, 'MACD_Signal'] = 1
                trade_lock = True
                macd_state = 1

            if stoch_state == 1 and df['Stochastic %K'].iloc[i] > 50:
                stoch_state = 2
            elif stoch_state == 2 and df['Stochastic %K'].iloc[i] < 50:
                df.loc[i, 'Stoch_Signal'] = 1
                trade_lock = True
                stoch_state = 1

        elif df['MA_Signal'].iloc[i] == -1 and not trade_lock:
            if macd_state == 1 and df['MACD_Histogram'].iloc[i] < 0:
                macd_state = 2
            elif macd_state == 2 and df['MACD_Histogram'].iloc[i] > 0:
                df.loc[i, 'MACD_Signal'] = -1
                trade_lock = True
                macd_state = 1

            if stoch_state == 1 and df['Stochastic %K'].iloc[i] > 50:
                stoch_state = 2
            elif stoch_state == 2 and df['Stochastic %K'].iloc[i] < 50:
                df.loc[i, 'Stoch_Signal'] = -1
                trade_lock = True
                stoch_state = 1

        if df['MA_Signal'].iloc[i] != df['MA_Signal'].iloc[i - 1]:
            trade_lock = False

    return df
    
    
    
    
    


# In[4]:


def pips_to_double(symbol, pips):
    digits = symbol_info.get(symbol, {}).get('digits', 0)
    if digits == 3 or digits == 5:
        pips = pips * 10
    point = symbol_info.get(symbol, {}).get('point', 0)
    value = pips * point
    return value


# In[5]:


def manage_signals(df, balance, risk=0.01):
    buy_signals = df[(df['MA_Signal'] == 1) & ((df['MACD_Signal'] == 1) | (df['Stoch_Signal'] == 1))]
    sell_signals = df[(df['MA_Signal'] == -1) & ((df['MACD_Signal'] == -1) | (df['Stoch_Signal'] == -1))]
     
    trades_df = pd.DataFrame(columns=['time', 'symbol', 'type', 'price', 'volume', 'sl', 'tp', 'magic', 'comment'])
    magic_number = 0
    
    for i in range(len(buy_signals)):

        time = buy_signals.iloc[i]['Time']
        symbol = 'EURUSD'
        trade_type = 'buy'
        price = buy_signals.iloc[i]['Close']
        comment = f'buy {i}'
        tp, sl = calc_tp_sl(symbol, trade_type, price)
         
        row = {
            'time': time,
            'symbol': symbol,
            'type': trade_type,
            'price': price,
            #'volume': trade.iloc[i]['volume'],
            'sl': sl,
            'tp': tp,
            #'magic': trade.iloc[i]['magic'],
            'comment': comment
        }
        trades_df.loc[len(trades_df)] = pd.Series(row)
        # Process sell signals
    for j in range(len(sell_signals)):
        
        time = sell_signals.iloc[j]['Time']
        symbol = 'EURUSD'
        trade_type = 'sell'
        price = sell_signals.iloc[j]['Close']
        comment = f'sell {j}'
        tp, sl = calc_tp_sl(symbol, trade_type, price)
        #magic_number = trade.iloc[i]['magic']
        row = {
            'time': time,
            'symbol': symbol,
            'type': trade_type,
            'price': price,
            #'volume': trade.iloc[i]['volume'],
            'sl': sl,
            'tp': tp,
            #'magic': trade.iloc[i]['magic'],
            'comment': comment
        }
        trades_df.loc[len(trades_df)] = pd.Series(row)

    return trades_df
    


# In[7]:


def calc_tp_sl(symbol,trade_type, price):
    stoploss = 50 
    RR = 2

    sl = price - pips_to_double(symbol, stoploss) if trade_type == "buy" else price + pips_to_double(symbol, stoploss)
    tp = price + RR * (price - sl) if trade_type == "buy" else price - RR * (sl - price)
    
    return round(tp, 5), round(sl, 5)

def check(df_with_signals, positions_df):
    positions_df = positions_df.sort_values(by='time').reset_index(drop=True)
    print('wait...')
    for i, trade in positions_df.iterrows():
        trade_type = trade['type']  # buy یا sell
        open_time = trade['time']
        tp = trade['tp']
        sl = trade['sl']
        trade_data = df_with_signals[df_with_signals['Time'] > open_time]

        close_time = None
        close_price = None
        status = "open"
        for j, row in trade_data.iterrows():
            price = row['Close']

            # چک کردن کراس مووینگ اورج
            if 'MA_Signal' in row and ((trade_type == 'buy' and row['MA_Signal'] == -1) or
                                       (trade_type == 'sell' and row['MA_Signal'] == 1)):
                status = "closed_ma_cross"
                close_price = price
                close_time = row['Time']
                break

            # چک کردن TP یا SL
            if trade_type == 'buy':
                if price >= tp:
                    status = "closed_tp"
                    close_price = tp
                    close_time = row['Time']
                    break
                elif price <= sl:
                    status = "closed_sl"
                    close_price = sl
                    close_time = row['Time']
                    break
            elif trade_type == 'sell':
                if price <= tp:
                    status = "closed_tp"
                    close_price = tp
                    close_time = row['Time']
                    break
                elif price >= sl:
                    status = "closed_sl"
                    close_price = sl
                    close_time = row['Time']
                    break

        # به‌روزرسانی وضعیت معامله
        positions_df.at[i, 'status'] = status
        positions_df.at[i, 'close_time'] = close_time
        positions_df.at[i, 'close_price'] = close_price

    return positions_df
@njit
def calculate_balance_and_volume(trades_df, initial_balance, risk=0.01):
    """
    Calculate profit/loss, update balance, and compute volume for each trade.
    
    Args:
        trades_df (pd.DataFrame): The trades dataframe containing all trade details.
        initial_balance (float): The initial balance at the start.
        risk (float): The risk percentage per trade (default: 0.01).

    Returns:
        pd.DataFrame: The updated dataframe with calculated columns.
    """
    # مرتب‌سازی معاملات براساس زمان باز شدن
    trades_df = trades_df.sort_values(by="time").reset_index(drop=True)

    balance = initial_balance
    updated_trades = []  # برای ذخیره داده‌های جدید معاملات

    for i, trade in trades_df.iterrows():
        try:
            # فاصله SL (برای محاسبه والیوم)
            sl_distance = abs(trade['price'] - trade['sl'])

            # محاسبه والیوم
            volume = round((risk * balance) / sl_distance, 2)

            # محاسبه سود/زیان
            if trade['type'] == 'buy':
                profit_loss = round((trade['close_price'] - trade['price']) * volume, 2)
            elif trade['type'] == 'sell':
                profit_loss = round((trade['price'] - trade['close_price']) * volume, 2)
            else:
                raise ValueError(f"Invalid trade type: {trade['type']}")

            # آپدیت بالانس
            balance += profit_loss

            # اضافه کردن داده‌های جدید به معامله
            updated_trades.append({
                "time": trade['time'],
                "close_time": trade['close_time'],
                "price": trade['price'],
                "close_price": trade['close_price'],
                "type": trade['type'],
                "status": trade['status'],
                "tp": trade['tp'],
                "sl": trade['sl'],
                "profit_loss": profit_loss,
                "volume": volume,
                "balance_after_trade": balance
            })

        except KeyError as e:
            print(f"Missing column in trade: {e}")
        except Exception as e:
            print(f"Error processing trade {i}: {e}")

    # تبدیل معاملات به DataFrame
    updated_trades_df = pd.DataFrame(updated_trades)
    return updated_trades_df

# In[8]:
def plot(trades_df, df_month):

# General settings
    fig = make_subplots(
        rows=3, cols=1, shared_xaxes=True,
        vertical_spacing=0.1, subplot_titles=('Candlestick', 'MACD', 'Stochastic'),
        row_heights=[0.6, 0.2, 0.2])
    
# Candlestick chart
    fig.add_trace(go.Candlestick(
        x=df_month['Time'],
        open=df_month['Open'], high=df_month['High'],
        low=df_month['Low'], close=df_month['Close'],
        name='Candlestick'), row=1, col=1)
# Add Indicators if they exist

# MA
    i=0
    for col in df_month.columns:

        if 'MA ' in col:
            i+=1
            if i == 1:
                color = 'blue'
            else :
                color = 'black'

            fig.add_trace(go.Scattergl(x=df_month['Time'], y=df_month[col],
                mode='lines', name=col,
                line=dict(color=color, width=1.5)), row=1,col=1)
# MACD
        if 'MACD_signal' in col:
            fig.add_trace(go.Scattergl(
                x=df_month['Time'], y=df_month['MACD'],
                mode='lines', name='MACD',
                line=dict(color='blue', width=1.5)), row=2, col=1)

            fig.add_trace(go.Scattergl(
                x=df_month['Time'], y=df_month['MACD_signal'],
                mode='lines', name='MACD Signal',
                line=dict(color='orange', width=1.5)),
                row=2, col=1)
            fig.add_trace(
                go.Bar(
                    x=df_month['Time'],
                    y=df_month['MACD_Histogram'],
                    name="MACD Histogram",
                    marker=dict(
                        color=np.where(df_month['MACD_Histogram'] > 0, 'green', 'red')  # تعیین رنگ بر اساس مقدار
                    )
                ),
                row=2, col=1
            )
# Stochastic
        if 'Stochastic %D' in col:
            fig.add_trace(go.Scattergl(
                x=df_month['Time'], y=df_month['Stochastic %D'],
                mode='lines', name='Stochastic %D', line=dict(color='blue', width=1.5)
            ), row=3, col=1)

            fig.add_trace(go.Scattergl(
                x=df_month['Time'], y=df_month['Stochastic %K_smooth'],
                mode='lines', name='Stochastic %K', line=dict(color='orange', width=1.5)
            ), row=3, col=1)

    buy_signals = df_month[(df_month['MA_Signal'] == 1) & ((df_month['MACD_Signal'] == 1) | (df_month['Stoch_Signal'] == 1))]
    fig.add_trace(go.Scattergl(
        x=buy_signals['Time'],
        y=buy_signals['Close'],
        mode='markers',
        marker=dict(size=10, color='green', symbol='triangle-up'),
        name='Buy Signal'
    ))

    # نقاط سیگنال‌های فروش (Sell)
    sell_signals = df_month[(df_month['MA_Signal'] == -1) & ((df_month['MACD_Signal'] == -1) | (df_month['Stoch_Signal'] == -1))]
    fig.add_trace(go.Scattergl(
        x=sell_signals['Time'],

        y=sell_signals['Close'],
        mode='markers',
        marker=dict(size=10, color='red', symbol='triangle-down'),
        name='Sell Signal'
    ))
# Rectangles
    for i in range(len(df_month)):
        if (df_month['MA_Signal'].iloc[i] != df_month['MA_Signal'].iloc[i - 1]):

            fig.add_shape(
                type="line",
                x0=df_month.iloc[i]['Time'],  
                x1=df_month.iloc[i]['Time'],  
                y0=df_month['Close'].min()-0.01,  
                y1=df_month['Close'].max()+0.01,  
                line=dict(color="blue", width=1.3, dash="dot"),
                xref="x",
                yref="y1"
            )

    for i in range(len(trades_df)):
        fig.add_shape(
            type="rect",
            x0=trades_df.iloc[i,0],  # نقطه شروع محور x
            x1=trades_df.iloc[i,1],  # نقطه پایان محور x
            y0=trades_df.iloc[i,2],          # نقطه شروع محور y
            y1=trades_df.iloc[i,3],          # نقطه پایان محور y
            line=dict(color="green") if trades_df.iloc[i,4]== 'buy' else dict(color="red"),  # رنگ حاشیه
            fillcolor="green" if pd.notna(trades_df.iat[i, -3]) and trades_df.iat[i, -3] > 0 else "red",  # رنگ پس‌زمینه
            opacity=0.3                    # شفافیت
        )
        hover_text = (
                f"Open Time: {trades_df.iloc[i]['time']}<br>"
                f"Close Time: {trades_df.iloc[i]['close_time']}<br>"
                f"Open Price: {trades_df.iloc[i]['price']}<br>"
                f"Close Price: {trades_df.iloc[i]['close_price']}<br>"
                f"Type: {trades_df.iloc[i]['type']}<br>"
                f"Volume: {trades_df.iloc[i]['volume']}<br>"
                f"Status: {trades_df.iloc[i]['status']}<br>"
                f"Profit_Loss: {trades_df.iloc[i]['profit_loss']}<br>"
                f"Balance: {trades_df.iloc[i]['balance_after_trade']}<br>"
                
            )
        fig.add_trace(go.Scattergl(
                x=[trades_df.iloc[i]['close_time']],  # قرار دادن نقطه در محل مستطیل
                y=[trades_df.iloc[i]['price']],
                mode="markers",
                marker=dict(size=10, color="rgba(0,0,0,0)"),  # نقطه نامرئی
                hovertext=hover_text,
                hoverinfo="text",
                showlegend=False
            ))
        fig.add_shape(
            type="line",
            x0=trades_df.iloc[i]['time'],
            x1=trades_df.iloc[i]['time'],
            y0=-0.0005,
            y1=0.0005,
            line=dict(color="blue", width=1.3, dash="dot"),
            xref="x",
            yref="y2"  # محور y ساب‌پلات دوم
        )

        # ساب‌پلات سوم: بین 0 و 100
        fig.add_shape(
            type="line",
            x0=trades_df.iloc[i]['time'],
            x1=trades_df.iloc[i]['time'],
            y0=0,
            y1=100,
            line=dict(color="blue", width=1.3, dash="dot"),
            xref="x",
            yref="y3"  # محور y ساب‌پلات سوم
        )
        

# Final setting
    fig.update_layout(
        title="EUR/USD 1m Candlestick Chart with MACD and Stochastic",
        xaxis_title="Date",
        yaxis_title="Price",
        xaxis_rangeslider_visible=False
    )
    fig.show()

