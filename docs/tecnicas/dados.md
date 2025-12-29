## Codificação de caracteres ##

* Foi realizada inspeção técnica dos arquivos fornecidos pelos sistemas AYZ e BTP utilizando o comando file -i. Em ambos os casos foi identificado o uso da codificação ISO-8859-1.
Como padrão de integração e persistência, definiu-se o uso de UTF-8 no sistema de destino e na API. Dessa forma, todo arquivo recebido deve ser convertido previamente de ISO-8859-1 para UTF-8, garantindo consistência de acentuação e evitando corrupção de dados textuais.

* Apesar de os arquivos de origem utilizarem ISO-8859-1, defini UTF-8 como padrão do sistema de destino por ser o encoding nativo da API, do ecossistema Python e mais seguro para integrações futuras, garantindo compatibilidade e consistência dos dados.Documento de Integração