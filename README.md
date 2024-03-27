# pyDoppelkopf

An implementation of the famous german card game "Doppelkopf".


## Run Server in Development

Assuming you have Python 3 installed, you first need to create a virtual environment (for example in the root of this project) with `python -m venv env`.
Activate the virtual environment with `source env/bin/activate`, and install the dependencies using `pip install -r requirements.txt`.

From the root of this project, you can start the server using `uvicorn doppelkopf_server.main:app --reload`.
A Swagger-UI will be available at `http://127.0.0.1:8000/docs#/`.