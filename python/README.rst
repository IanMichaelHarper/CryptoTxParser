Parse crypto currency transactions to figure out short term and long term gains

Requirements
~~~~~~~~~~~~

- python 3.6+ (https://www.python.org/downloads/)

- python-dateutil

.. code:: shell

  pip install python-dateutil

Warning
~~~~~~~
The use of this script is not a substitute for using a certified public accountant (CPA) to determine your gains and losses on your tax return. Use at your own discretion. I am not responsible for any errors.

Usage
~~~~~
Background
----------

This script will parse an input file that is in CSV format with the following columns:

- date

  * The following date formats styles are acceptable:
  
    + 1/1/2017 1:00:00
    + 1/1/2017 13:00:00
    + 01/01/2017 01:00:00 AM
    + 01/01/2017 01:00:00 PM
  * make sure these are in UTC!
  * make sure no commas, ie- "Dec 27, 2017 01:00:00"
- transaction type

  * transaction types:
  
    + buy- when you are buying the destination currency with the source currency. Valid values:
    
      - buy
      - b
    + sell- when you are selling the source currency for the destination currency. Valid values:
    
      - sell
      - s
    + transfer (source/destination currency should be the same)- This is when you are transferring the currency from the source wallet to the destination wallet. Valid values:
    
      - transfer
      - xfer
      - x
    + outbound (source/destination currency should be the same)- This is when you are making a payment using crypto-currency. Valid values:
    
      - outbound
      - out
      - o
    + inbound (source/destination currency should be the same)- This is when you are receiving crypto-currency. Valid values:
    
      - inbound
      - in
      - i



- source currency

  * Can be crypto-currency or fiat, ie- "USD", "BTC", "ETH", etc.
- destination currency

  * Can be crypto-currency or fiat, ie- "USD", "BTC", "ETH", etc.
- source wallet

  * Wallet name to group transactions together. 
  * Will typically be an exchange name, but can be a hardware/software wallet.
  * Make sure you keep the names consistent for the same logical wallet
- destination wallet

  * Wallet name to group transactions together. 
  * Will typically be an exchange name, but can be a hardware/software wallet.
  * Make sure you keep the names consistent for the same logical wallet
- source value

  * Make sure no commas in values!
- destination value

  * Make sure no commas in values!
- notes (optional)

  * Make sure no commas in notes!

Things to note-

- The order does not matter much, as the script will sort these in chronological order prior to processing. 
- It's easier to maintain these transactions in Excel, Google Sheets, etc and just export to CSV.

Running the Script
------------------
.. code:: shell

  python CryptoTxParser.py -f [input csv file]
  
Optional parameters

- -c [fiat currency]

  * default is "USD"
- -l [days]

  * days to consider gains as long-term
- -y [year]

  * Year to evaluate gains for. If not set, will process all transactions for all years.
- -s

  * Will print wallet summaries
- -H
  
  * If your input data CSV file does not include a header, please turn this flag on
 
Examples
--------

sample.csv

.. code:: shell
  
  date,tx type,src currency,dst currency,src wallet,dst wallet,src value,dst value,notes
  1/1/2016 1:00 AM,buy,USD,ETH,fiat,gdax,.92,1,initial buy ETH (~.92) on gdax
  1/2/2017 1:00 AM,sell,ETH,USD,gdax,fiat,1,8.33,sell ETH (~8.33) this will be a long term gain
  2/1/2017 1:00 AM,buy,USD,ETH,fiat,gdax,10.71,1,buy ETH (~10.71)
  3/1/2017 1:00 AM,xfer,ETH,ETH,gdax,gatehub,1,1,transfer ETH (~17.55) to gatehub
  4/1/2017 1:00 AM,buy,ETH,XRP,gatehub,gatehub,1,2530,convert ETH (~50.6) to XRP (~.02)
  7/1/2017 1:00 AM,sell,XRP,ETH,gatehub,gatehub,1265,1.16,convert half XRP (~.24) back to ETH (~261)
  8/1/2017 1:00 AM,xfer,ETH,ETH,gatehub,gdax,1.16,1.16,transfer ETH (~226) to gatehub
  9/1/2017 1:00 AM,sell,ETH,USD,gdax,fiat,.58,227,sell half ETH (~391) on gdax

Command:

.. code:: shell

   python CryptoTxParser.py -f sample.csv -s
   
Output:

.. code:: shell

  Wallet Info:
  Wallet Name ... gdax
  Currency Name ... ETH
  Related Transactions:
     timestamp:              01-01-2016 01:00:00 (1451631600)
     transaction type:       buy
     source currency:        USD
     destination currency:   ETH
     source wallet:          fiat
     destination wallet:     gdax
     source value:           0.92000000
     destination value:      1.00000000
     notes:                  initial buy ETH (~.92) on gdax

     timestamp:              01-02-2017 01:00:00 (1483340400)
     transaction type:       sell
     source currency:        ETH
     destination currency:   USD
     source wallet:          gdax
     destination wallet:     fiat
     source value:           1.00000000
     destination value:      8.33000000
     notes:                  sell ETH (~8.33) this will be a long term gain

     timestamp:              02-01-2017 01:00:00 (1485932400)
     transaction type:       buy
     source currency:        USD
     destination currency:   ETH
     source wallet:          fiat
     destination wallet:     gdax
     source value:           10.71000000
     destination value:      1.00000000
     notes:                  buy ETH (~10.71)

     timestamp:              03-01-2017 01:00:00 (1488351600)
     transaction type:       transfer
     source currency:        ETH
     destination currency:   ETH
     source wallet:          gdax
     destination wallet:     gatehub
     source value:           1.00000000
     destination value:      1.00000000
     notes:                  transfer ETH (~17.55) to gatehub

     timestamp:              08-01-2017 01:00:00 (1501567200)
     transaction type:       transfer
     source currency:        ETH
     destination currency:   ETH
     source wallet:          gatehub
     destination wallet:     gdax
     source value:           1.16000000
     destination value:      1.16000000
     notes:                  transfer ETH (~226) to gatehub

     timestamp:              09-01-2017 01:00:00 (1504245600)
     transaction type:       sell
     source currency:        ETH
     destination currency:   USD
     source wallet:          gdax
     destination wallet:     fiat
     source value:           0.58000000
     destination value:      227.00000000
     notes:                  sell half ETH (~391) on gdax

  Balance: 0.58000000


  Wallet Info:
  Wallet Name ... gatehub
  Currency Name ... ETH
  Related Transactions:
     timestamp:              03-01-2017 01:00:00 (1488351600)
     transaction type:       transfer
     source currency:        ETH
     destination currency:   ETH
     source wallet:          gdax
     destination wallet:     gatehub
     source value:           1.00000000
     destination value:      1.00000000
     notes:                  transfer ETH (~17.55) to gatehub

     timestamp:              04-01-2017 01:00:00 (1491026400)
     transaction type:       buy
     source currency:        ETH
     destination currency:   XRP
     source wallet:          gatehub
     destination wallet:     gatehub
     source value:           1.00000000
     destination value:      2530.00000000
     notes:                  convert ETH (~50.6) to XRP (~.02)

     timestamp:              07-01-2017 01:00:00 (1498888800)
     transaction type:       sell
     source currency:        XRP
     destination currency:   ETH
     source wallet:          gatehub
     destination wallet:     gatehub
     source value:           1265.00000000
     destination value:      1.16000000
     notes:                  convert half XRP (~.24) back to ETH (~261)

     timestamp:              08-01-2017 01:00:00 (1501567200)
     transaction type:       transfer
     source currency:        ETH
     destination currency:   ETH
     source wallet:          gatehub
     destination wallet:     gdax
     source value:           1.16000000
     destination value:      1.16000000
     notes:                  transfer ETH (~226) to gatehub

  Balance: 0.00000000

  Currency Name ... XRP
  Related Transactions:
     timestamp:              04-01-2017 01:00:00 (1491026400)
     transaction type:       buy
     source currency:        ETH
     destination currency:   XRP
     source wallet:          gatehub
     destination wallet:     gatehub
     source value:           1.00000000
     destination value:      2530.00000000
     notes:                  convert ETH (~50.6) to XRP (~.02)

     timestamp:              07-01-2017 01:00:00 (1498888800)
     transaction type:       sell
     source currency:        XRP
     destination currency:   ETH
     source wallet:          gatehub
     destination wallet:     gatehub
     source value:           1265.00000000
     destination value:      1.16000000
     notes:                  convert half XRP (~.24) back to ETH (~261)

  Balance: 1265.00000000


  Gain Summary for year 2017
  Net Gain: 396.92

  ## Long-term gain records ##
   Timestamp ........... 01-02-2017 01:00:00 (1483340400)
   Original Timestamp .. 01-01-2016 01:00:00 (1451631600)
   Coin Value .......... 1.00000000
   Fiat Value .......... 8.33
   Gain ................ 7.41
   Gain Type ........... long term

  Long-term gains ...... 7.41

  ## Short-term gain records ##
   Timestamp ........... 04-01-2017 01:00:00 (1491026400)
   Original Timestamp .. 02-01-2017 01:00:00 (1485932400)
   Coin Value .......... 1.00000000
   Fiat Value .......... 50.60
   Gain ................ 39.89
   Gain Type ........... short term

   Timestamp ........... 07-01-2017 01:00:00 (1498888800)
   Original Timestamp .. 04-01-2017 01:00:00 (1491026400)
   Coin Value .......... 1265.00000000
   Fiat Value .......... 150.91
   Gain ................ 274.00
   Gain Type ........... short term

   Timestamp ........... 09-01-2017 01:00:00 (1504245600)
   Original Timestamp .. 07-01-2017 01:00:00 (1498888800)
   Coin Value .......... 0.58000000
   Fiat Value .......... 113.50
   Gain ................ 75.62
   Gain Type ........... short term

  Short-term gains ..... 389.51

Errors
------
If you encounter any errors, make sure your data is formatted properly. As the data is in CSV (comma-separated) format, make sure your source/destination values don't have any commas. 

Thanks
~~~~~~

This project uses the CryptoCompare API (`CryptoCompare <https://www.cryptocompare.com>`__) to resolve crypto-crypto fiat value conversion. If you find this tool useful, please consider donating to them!

Donate
~~~~~~

If you have found this script useful and have saved a ton of time figuring out your capital gains/losses, please consider donating. Any amount is appreciated!

  ::

  BTC - 3Q7HcHa1dVa2tDd6FCdhRqJ9sJkxLhCZMw
  
  LTC - LWw3py4dgbxzc615zGa6q3qdL3nE6bFG6P
  
  ETH - 0xCc65952B042B2Cfc41E9b6AdF5AC40230df609EC
  
  XRP - rGq6vkJi4RULUEBU4AXdgA7bxtynQq3xPL
