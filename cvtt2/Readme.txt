Backtest Simulation
====================

=====================================================
Backtest Sim Module = 
                   Backtest Trader  
                  + Backtest Risk Manager 
                  +  Simulated Market Data
=====================================================
Backtest Connector  < == > Backtest Sim Module
-----------------------------------------------------------------------------

- - always in-proc
- all events are delivered to the application by Exchange Instrument event queue
  - Order Status Updates (from Backtest Trader)
  - Position Updates (from Backtest RiskManager)

--------------------------
BacktestTrader
--------------------------
- gets orders - maintains its own order book
- listens to simulated market data (trades)
- matches the trades to existing orders
- supports order status requests
- supports order cancel requests

Backtest Risk Manager
-------------------------------------
- gets notified on position update events: fills and deposits.
- dispatches PositionChange events

Backtest Connector
-------------------------------
- implements mkt_data, connector and account interfaces

Simulated Market Data
-------------------------------------
- accepts subscriptions 
- sets application time (see timeutils.py and app.py in this directory)

