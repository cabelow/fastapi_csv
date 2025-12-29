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
