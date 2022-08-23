## TO médio em lotes não condominiais

Os lotes não condominiais são aqueles que tem apenas um contribuinte e consequentemente a `FRACAO IDEAL` igual a 1 (um). O critério de `NUMERO DO CONDOMINIO` igual a `00-0` foi utilizado para diferenciar daqueles lotes ou lançamentos que são condominiais.

A Taxa de Ocupação (TO) é um índice urbanístico que representa a proporção do Terreno que é ocupada por edificações. Esse atributo não está presente originalmente no cadastro do IPTU e foi obtido pelo seguinte cálculo:

TO = `AREA OCUPADA` / `AREA DO TERRENO`

Foi considerada a média para agregar espacialmente o TO. Apesar de entendermos que a mediana expressaria melhor tais agregações, por uma limitação técnica e de performance da biblioteca escolhida, foi utilizada a média.