# Documento de Integração

## Sistema AYZ → Sistema BTP

---

## 1. Introdução

### 1.1 Objetivo

Este documento descreve a análise técnica, o mapeamento de campos (dê-para), as divergências identificadas e as regras de normalização adotadas para a integração de dados entre os sistemas AYZ (origem) e BTP (destino).

### 1.2 Contexto

Os sistemas AYZ e BTP representam funcionários, unidades, setores e cargos, porém utilizam nomenclaturas, códigos, formatos e níveis de granularidade diferentes, exigindo um processo de saneamento e padronização antes da integração.

---

## 2. Visão Geral dos Sistemas

### 2.1 Sistema AYZ (Origem)

* Sistema legado exportado pelo cliente
* Codificação do arquivo: ISO-8859-1
* Datas no formato DD/MM/YYYY
* CPF com máscara
* Uso de abreviações e variações semânticas
* Possui dados inconsistentes e campos ausentes

### 2.2 Sistema BTP (Destino)

* Estrutura padrão da plataforma integrada
* Arquivos recebidos em ISO-8859-1
* Padrão interno e persistência: UTF-8
* Datas no formato ISO 8601 (YYYY-MM-DD)
* Modelo canônico utilizado pela API e banco de dados

---

## 3. Comparação Estrutural (Dê-Para de Campos)

### 3.1 Funcionários

| AYZ              | BTP               | Observação                |
| ---------------- | ----------------- | ------------------------- |
| cod_func         | employee_id       | Identificador interno     |
| nome_funcionario | full_name         | Normalização de texto     |
| cpf              | document_number   | Remover máscara e validar |
| data_admissao    | hire_date         | Conversão de formato      |
| salario          | monthly_salary    | Campo complementar        |
| status           | employment_status | Padronização de valores   |

### 3.2 Unidades

| AYZ      | BTP       |
| -------- | --------- |
| cod_unid | unit_code |
| unidade  | unit_name |

### 3.3 Setores

| AYZ       | BTP             |
| --------- | --------------- |
| cod_setor | department_code |
| setor     | department_name |

### 3.4 Cargos

| AYZ       | BTP           |
| --------- | ------------- |
| cod_cargo | position_code |
| cargo     | position_name |

---

## 4. Divergências Identificadas

### 4.1 Codificação de Caracteres

* Ambos os arquivos utilizam ISO-8859-1
* Ocorrência de caracteres corrompidos quando interpretados como UTF-8

**Decisão:** Conversão obrigatória para UTF-8 no pipeline de integração.

### 4.2 Formato de Dados

* Datas: AYZ (DD/MM/YYYY) → BTP (YYYY-MM-DD)
* CPF: AYZ com máscara → BTP somente números

### 4.3 Divergências Semânticas

* Setores: TI, Tecnologia, Infraestrutura TI
* RH, Recursos Humanos, Gestão de Pessoas
* Cargos: Analista Sistemas, Dev Backend, Desenvolvedor

### 4.4 Divergências de Granularidade

* AYZ possui maior variedade de setores e cargos
* BTP trabalha com conjunto consolidado

### 4.5 Inconsistências de Dados

* CPF ausente
* Código de unidade ausente
* Valores inexistentes no destino

---

## 5. Regras de Normalização

### 5.1 Codificação

* Entrada: ISO-8859-1
* Padrão interno: UTF-8

### 5.2 Texto

* Remover espaços duplicados
* Normalizar acentuação
* Padronizar capitalização

### 5.3 CPF

* Remover pontuação
* Validar dígitos verificadores
* CPF obrigatório e único

### 5.4 Datas

* Converter para ISO 8601
* Bloquear datas futuras

### 5.5 Códigos

* Códigos AYZ não são reutilizados diretamente
* Todos os valores devem ser mapeados via tabelas de dê-para

### 5.6 Tratamento de Registros Inválidos

* Rejeição quando CPF ou código de unidade estiver ausente
* Encaminhamento para fila de exceção quando aplicável

---

## 6. Tabelas de Dê-Para

### 6.1 Unidades

Tabela de equivalência entre códigos e nomes de unidades do AYZ e BTP.

### 6.2 Setores

Tabela de consolidação semântica dos setores.

### 6.3 Cargos

Tabela de equivalência e consolidação dos cargos.

Essas tabelas são tratadas como dimensões de referência.

---

## 7. Considerações Finais

* O BTP define o modelo canônico da integração
* O processo de normalização reduz riscos operacionais
* O dê-para garante rastreabilidade e consistência dos dados

---