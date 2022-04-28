# DashBoard IPTU de São Paulo

Repositório para criação da prova de conceito do uso do Dash com Vaex para criação de DashBoards / Infográficos com a base de dados de IPTU de São Paulo

## Motivação

A base de dados de IPTU disponibilizada pela Prefeitura de São Paulo, apesar de possuir enorme potencial para leituras das dinâmicas da cidade apresenta dificuldade para a maioria das pessoas por seu tamanho extenso. Para a série histõrica são mais de 80 milhões de registros com 17 dimensões/atributos. Havendo uma maneira de sintetizar, filtrar e agregar dados mais simples e rápida, muito provavelmente o acesso à essa informação seria disseminada de forma mais democrática e ampla e com muito menos restritivas.

## Objetivo

Portanto o objetivo desse repositõrio é estudar a possibilidade da criação de um 'DashBoard' ou Infográfico interativo para facilitar e ampliar o uso dos dados do IPTU da cidade de São Paulo e assim contribuir para uma cultura de transparência ativa e disseminação de uso dos dados abertos como ferramenta essencial para o exerício da cidadania.

## Materiais e Métodos

Os dados de IPTU estão disponíveis para acesso público pelo GeoSampa. Para torná-los mais eficiente computacionalmente eles foram convertidos para formato HDF5 e disponibilizados em no [Kaggle](https://www.kaggle.com/datasets/andasampa/iptu-sao-paulo) para todos os exercícios desde 1995. Desssa maneira então é possivel estabelecer uma dimensão cronológica desses dados cadastrais, atualizados anualmente. Além dos atributos disponibilizados, é possível espacializar os dados, seja através do lote, da quadra fiscal ou mesmo do endereço. Esse processamento espacial da informação cadastral será disponibilizado em um NoteBook específico a ser atualizado aqui e quando for disponibilizado possibilitará a agregação da informação do IPTU por diversas divisões territoriais ou geográficas.
Portanto, o dados do IPTU pode ser organizado, visualizado e tematizado em 3 grupos de dimensões: A cronológica anual, as dimensões espaciais até a escala do lote, e as dimensões de atributos cadastrais. Para a dimensão cronológica existe a possibilidade de filtragem e agrupamento por faixas de anos para análises como variações e dinâmicas temporais. Para as dimensões espaciais é possível filtrara e agrupar por diversos arranjos, sejam eles: políticos administrativos, como distritos e sub-prefeituras, sejam cadastrais, fiscais e legais como setor fiscal, Leis de Zoneamento, macro-áreas, ZEIS, ou mesmo logradouro e ainda agragações com arranjos para finalidades analíticas específicas, como Zona de Origem-destino. Para as dimensões cadastrais, serão calculados os índices urbanísticos de Taxa de Ocupação (TO) e Coeficiente de Aproveitamento (CA), assim como os devidos agrupamentos nos campos de categoriais, como uso e tipo de imóvel. Ambos os processamentos serão compartilhados e seus links atualizados aqui nesse texto.
Para os processamentos ficarão à disposição em Notebooks escritos em Python utilizando as bibliotecas: Numpy, Pandas, GeoPandas, Vaex e o DashBoard será gerado utilizando a bilioteca Dash/Plotly

## Docker

Para suber uma versão do Dash utilize o Docker:

```
docker build -t dash-iptu .
docker run -p 8050:8050 -d dash-iptu
```

## Resultados

Ambiente de testes disponível em [https://cem-dash-iptu.herokuapp.com/]
