OCPP PoC Package (PriceSignal Anomaly)
Files:
 - ocpp_central.py
 - charger_ocpp_client.py
 - ids_correlation.py
Requirements:
 pip install ocpp websockets asyncio
Run:
 1) Start IDS: python ids_correlation.py
 2) Start central: python ocpp_central.py
 3) Start clients: python charger_ocpp_client.py --id CP1 --central ws://localhost:9000/CP1
Notes:
 - These are educational stubs. Adapt to your ocpp library version and environment.
