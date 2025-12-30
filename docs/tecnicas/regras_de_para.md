# Regras de Normalização e DE-PARA

Este documento descreve as regras de normalização de dados e os mapas DE-PARA utilizados na integração de sistemas. Ele serve como referência para entender como cada campo é comparado entre as bases BTP e AYZ.

## 1. Normalização de Dados

Antes de qualquer comparação, os valores passam por normalização:

- **Textos:** convertidos para minúsculas, sem espaços extras no início/fim.
- **CPFs:** removidos caracteres não numéricos, garantindo 11 dígitos.
- **Salários:** convertidos para float, negativos são considerados inválidos.
- **Datas:** padronizadas em formato YYYY-MM-DD.

## 2. Comparação de Campos

Cada campo é comparado usando uma das seguintes abordagens:

| Tipo de Comparação | Descrição |
|------------------|-----------|
| **Regra DE-PARA** | Quando há um mapeamento explícito entre os valores da base BTP e a base AYZ. Ex.: códigos de departamento, cargos ou unidades. |
| **DE-PARA com IA** | Para campos que possuem múltiplas formas de escrever o mesmo valor. Usa DE-PARA + similaridade semântica para validar. Ex.: nomes de cargos ou setores. |
| **Semântica (IA)** | Para campos livres como nomes completos. Compara usando similaridade semântica e um threshold de aceitação. |

### 2.1 Thresholds

- **Threshold Semântico:** 0.85 (ajustável)
- **Threshold Fullname:** 0.5 (ajustável)

---

## 3. Campos e Tabelas DE-PARA

### Campos de Código (Regra DE-PARA)

| Campo | Descrição | Exemplo DE-PARA |
|-------|-----------|----------------|
| `unit_code` | Código da unidade | `{"u001": "U10", "u002": "U11"}` |
| `department_code` | Código do setor | `{"d010": "ST10", "d020": "ST20"}` |
| `position_code` | Código do cargo | `{"c001": "CG10", "c002": "CG11"}` |

### Campos de Nome (DE-PARA + IA)

| Campo | Descrição | Exemplo DE-PARA |
|-------|-----------|----------------|
| `unit_name` | Nome da unidade | `{"financeiro": ["fin", "contabilidade"]}` |
| `department_name` | Nome do setor | `{"contabilidade": ["contab", "finanças"]}` |
| `position_name` | Nome do cargo | `{"analista": ["analista jr", "analista pleno"]}` |
| `employment_status` | Status do contrato | `{"ativo": ["ativo", "em andamento"], "inativo": ["demitido", "rescindido"]}` |

### Campos Comparados Semânticamente (IA)

- `full_name` (nome completo do funcionário)
- Outros campos livres ou textos que não possuem DE-PARA explícito

---

## 4. Lógica de Comparação

A decisão de como comparar cada campo segue o fluxo:

1. Se o campo tem **DE-PARA explícito**, aplica **Regra DE-PARA**.
2. Se o campo tem **DE-PARA com múltiplos valores possíveis**, aplica **DE-PARA + IA**.
3. Para campos livres sem DE-PARA, aplica **IA (similaridade semântica)**.
4. Se um campo estiver vazio ou inválido, marca como **campo vazio** ou **dados inválidos**.
5. Salário negativo é considerado inválido.
6. CPFs mal formados ou duplicados geram alertas críticos.

---

## 5. Exemplo de Resultado

```json
{
  "matches_exatos": [{"cpf": "12345678901", "btp_id": 1, "ayz_id": 101}],
  "matches_semanticos": [{"cpf": "23456789012", "btp_id": 2, "ayz_id": 102, "divergencias": {...}}],
  "divergencias_reais": [{"cpf": "34567890123", "btp_id": 3, "ayz_id": 103, "divergencias": {...}}],
  "nao_encontrados": [{"cpf": "45678901234", "btp_id": 4}],
  "alertas_criticos": [{"cpf": "56789012345", "btp_id": 5, "motivo": "CPF Mal Formado", "origem": "BTP"}]
}
```



## 6. Fluxo de Integração ##

```mermaid
flowchart TD
    A[Início da Comparação] --> B{Campo tem DE-PARA explícito?}
    B -- Sim --> C[Regra DE-PARA]
    B -- Não --> D{Campo tem DE-PARA com múltiplos valores?}
    D -- Sim --> E[DE-PARA + IA]
    D -- Não --> F[IA (similaridade semântica)]
    C --> G{Valor aceito?}
    E --> G
    F --> G
    G -- Sim --> H[Campo aprovado]
    G -- Não --> I[Campo divergente]
    I --> J{Salário negativo ou campo vazio?}
    J -- Sim --> K[Erro de validação]
    J -- Não --> L[Alertas críticos se CPF mal formado ou duplicado]
    H --> M[Fim da comparação]
    K --> M
    L --> M

```