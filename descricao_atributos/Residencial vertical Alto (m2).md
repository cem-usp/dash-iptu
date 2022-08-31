## Residencial vertical Alto (m2)

Filtra apenas os registros de Lançamentos de Imóveis Residenciais verticais de Alto Padrão, retornando a soma do total de metros quadrados construídos.

Este atributo está presente no cadastro do IPTU para cada lançamento no campo originalmente chamado de `TIPO DE PADRAO DA CONSTRUCAO`, que para o exercício de 2022, apresentava 29 variações com descrições unicas. Tais descrições pode ser agrupadas conforme o uso em: _Comercial_, _Residencial_, _Terreno_ e _Outros Usos_. Para os usos _Residencial_ e _Comercial_ ainda há  a classificação original quanto a sua tipo-morfologia, sendo: _horizontal_ e _vertical_ e ainda  atribuídos padrãoes, conforme legislação vigente variando os valores de `A` a `F`, que, para fins de análise, foram rearranjados conforme abaixo:

| Original  | Agrupamento |
|-----------|-------------|
| `A` e `B` | Baixo |
| `C`       | Médio |
| `D`, `E` e `F` | Alto |

Para maiores detalhes, o `TIPO DE PADRAO DA CONSTRUCAO` é estabelecido pelo [Tabela V, anexa à Lei 10.235, de 16 de dezembro de 1986](https://legislacao.prefeitura.sp.gov.br/leis/lei-10235-de-16-de-dezembro-de-1986), atualizada pela [LEI Nº 15.044, DE 3 DE DEZEMBRO DE 2009](https://www.prefeitura.sp.gov.br/cidade/secretarias/upload/arquivos/secretarias/financas/legislacao/Lei-15044-2009.pdf)