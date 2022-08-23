## CA médio em lotes não condominiais

Os lotes não condominiais são aqueles que tem apenas um contribuinte e consequentemente a `FRACAO IDEAL` igual a 1 (um). O critério de `NUMERO DO CONDOMINIO` igual a `00-0` foi utilizado para diferenciar daqueles lotes ou lançamentos que são condominiais.

O Coeficiente de Aproveitamento (CA) é um índice urbanístico que representa o densidade construtiva em planta (2D), que pode ser entendida como a proporção entre a Área construída em relação a Área do Terreno. Esse atributo não está presente originalmente no cadastro do IPTU e foi obtido pelo seguinte cálculo:

CA = `AREA CONSTRUIDA` / `FRACAO IDEAL` / `AREA DO TERRENO`

Foi considerada a média para agregar espacialmente o CA. Apesar de entendermos que a mediana expressaria melhor tais agregações, por uma limitação técnica e de performance da biblioteca escolhida, foi utilizada a média.