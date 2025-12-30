## Ambiente virtual ##

* venv
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install --upgrade pip
pip install -r requirements.txt


* Atualizar requirements.txt pelo ambiente virtual
pip freeze > requirements.txt



## Install fastapi ##

* install fastapi (se necessário)
pip install fastapi uvicorn sqlalchemy pyodbc


## Testar aplicação ##

uvicorn main:app --reload --app-dir src