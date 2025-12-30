## ver codificação da planilha ##

file -i nome_do_arquivo.csv

exemplo:
file -i btp.csv
file -i ayz.csv

exemplo de saida:
btp.csv: text/plain; charset=utf-8
btp.csv: text/plain; charset=iso-8859-1
ayz.csv: text/csv; charset=iso-8859-1

## Executar aplicalão ##

uvicorn main:app --reload --app-dir src

## Executar com docker: ##

docker compose build --no-cache
docker build --no-cache -t my-image-name:latest .

docker-compose up


## Atualizar libs ##

pip freeze > requirements.txt


## Git para arquivos grandes ##

git lfs install
git lfs track "src/utils/transformer_model/*"

git add .gitattributes
git add -f src/utils/transformer_model/

git remote set-url origin git@github.com:cabelow/fastapi_csv.git
