import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_post_funcionario():
    payload = {
        "cpf": "12345678900",
        "nome_funcionario": "Teste Usuario",
        "codigo_cargo": "P999",
        "cargo": "Testador",
        "codigo_unidade": "U999",
        "unidade": "Unidade Teste",
        "codigo_setor": "D999",
        "setor": "Setor Teste",
        "data_admissao": "2025-01-01"
    }
    response = client.post("/funcionarios", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["nome_funcionario"] == "Teste Usuario"

def test_get_funcionarios_lista():
    response = client.get("/funcionarios")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_get_funcionario_por_id():
    payload = {
        "cpf": "99988877766",
        "nome_funcionario": "Para Buscar",
        "codigo_cargo": "P998",
        "cargo": "Cargo Busca",
        "codigo_unidade": "U998",
        "unidade": "Unidade Busca",
        "codigo_setor": "D998",
        "setor": "Setor Busca",
        "data_admissao": "2025-02-01"
    }
    post_resp = client.post("/funcionarios", json=payload)
    func_id = post_resp.json()["id"]

    response = client.get(f"/funcionarios/{func_id}")
    assert response.status_code == 200
    assert response.json()["nome_funcionario"] == "Para Buscar"

def test_put_funcionario():
    payload = {
        "cpf": "11122233344",
        "nome_funcionario": "Para Atualizar",
        "codigo_cargo": "P997",
        "cargo": "Cargo Inicial",
        "codigo_unidade": "U997",
        "unidade": "Unidade Inicial",
        "codigo_setor": "D997",
        "setor": "Setor Inicial",
        "data_admissao": "2025-03-01"
    }
    post_resp = client.post("/funcionarios", json=payload)
    func_id = post_resp.json()["id"]

    update_payload = {"cargo": "Cargo Atualizado"}
    response = client.put(f"/funcionarios/{func_id}", json=update_payload)
    assert response.status_code == 200
    assert response.json()["cargo"] == "Cargo Atualizado"

def test_delete_funcionario():
    payload = {
        "cpf": "55566677788",
        "nome_funcionario": "Para Deletar",
        "codigo_cargo": "P996",
        "cargo": "Cargo Delete",
        "codigo_unidade": "U996",
        "unidade": "Unidade Delete",
        "codigo_setor": "D996",
        "setor": "Setor Delete",
        "data_admissao": "2025-04-01"
    }
    post_resp = client.post("/funcionarios", json=payload)
    func_id = post_resp.json()["id"]

    response = client.delete(f"/funcionarios/{func_id}")
    assert response.status_code == 200
    assert response.json()["message"] == "Funcionário removido com sucesso"
