# DashBoard IPTU de São Paulo

Repositório para criação e desenvolvimento da prova de conceito do uso do Dash com Vaex para criação de DashBoards / Infográficos com a base de dados de IPTU de São Paulo

## Motivação

A base de dados de IPTU disponibilizada pela Prefeitura de São Paulo, apesar de possuir enorme potencial para leituras das dinâmicas da cidade pode apresentar desafios para a maioria das pessoas por sua quantidade de registros e atributos. Para a série histórica são mais de 83 milhões de registros com 17 dimensões/atributos. Havendo uma maneira de sintetizar, filtrar e agregar dados de maneira mais simples e rápida, muito provavelmente o acesso à essa informação seria disseminada de forma mais democrática e ampla e com muito menos restrições.

## Objetivo

Portanto o objetivo desse repositório é estudar as possibilidade e desenvolver um 'DashBoard' ou Infográfico interativo para facilitar e ampliar o uso dos dados do IPTU da cidade de São Paulo e assim contribuir para uma cultura de transparência ativa e disseminação de uso dos dados abertos como ferramenta essencial para o exerício da cidadania.

## Materiais e Métodos

Os dados de IPTU estão disponíveis para acesso público pelo portal GeoSampa. Para torná-los mais eficiente computacionalmente eles foram convertidos para formato HDF5 e disponibilizados no [Kaggle](https://www.kaggle.com/datasets/andasampa/iptu-sao-paulo) para todos os exercícios desde 1995. Desssa maneira então é possivel estabelecer uma dimensão cronológica desses dados cadastrais, atualizados anualmente. Além dos atributos disponibilizados, é possível espacializar os dados, seja através do lote, da quadra fiscal ou mesmo do endereço (que não foi realizado nesse desenvolvimento). A espacialização do dado cadastral do IPTU possibilita  a agregação da informação por diversas divisões territoriais ou geográficas.

A premissa é que os dados do IPTU possam ser organizados, visualizados e analisados em 3 dimensões ou perspectivas: A cronológica anual, a dimensão espacial com diversas agregações até a escala do lote, e as dimensões de atributos cadastrais a partir das dimensões espaciais e cronológicas. 

Para a dimensão cronológica existe a possibilidade de filtragem e agrupamento por faixas de anos para análises como variações e dinâmicas temporais. Para as dimensões espaciais é possível filtrar e agrupar por diversos arranjos, sejam eles: políticos administrativos, como distritos e sub-prefeituras, sejam cadastrais, fiscais e legais como setor fiscal, Leis de Zoneamento, macro-áreas, ZEIS, ou mesmo logradouro e ainda agragações com arranjos para finalidades analíticas específicas, como Zona de Origem-destino.

Para as dimensões cadastrais, são calculados os índices urbanísticos de Taxa de Ocupação (TO) e Coeficiente de Aproveitamento (CA), assim como os devidos agrupamentos nos campos de categoriais, como uso e tipo de imóvel. 

Os processamentos ficarão à disposição em Notebooks escritos em Python utilizando as bibliotecas: Numpy, Pandas, GeoPandas, Vaex e o DashBoard será gerado utilizando a bilioteca Dash/Plotly

## Procedimento de atualização anual

Anualmente os dados de IPTU são atualizados pela Secretaria da Fazenda e deve-se atualizar os dados desse repositório pelo seguinte procedimento

- Download do IPTU para a pasta apropriada `data\IPTU_{ano}\`
- Reprocessamento dos dados 
- Download dos lotes fiscais
- Agre

## Docker

Para subir uma versão do Dash utilize o Docker:

```
docker build -t dash-iptu .
docker run -p 8050:8050 -v /home/ubuntu/dash-iptu:/opt/app -d dash-iptu
```

## Resultados

Ambiente de testes disponível em [https://dashiptu.centrodametropole.fflch.usp.br]
