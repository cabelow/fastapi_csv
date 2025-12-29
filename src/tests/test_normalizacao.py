from utils.normalizacao import normalizar_cpf

def test_normalizar_cpf():
    assert normalizar_cpf("123.456.789-00") == "12345678900"
    assert normalizar_cpf("00011122233") == "00011122233"
    assert normalizar_cpf(None) is None

from utils.normalizacao import normalizar_texto

def test_normalizar_texto():
    assert normalizar_texto("  João Silva  ") == "Joao Silva"
    assert normalizar_texto("áéíóú") == "aeiou"
    assert normalizar_texto(None) is None
