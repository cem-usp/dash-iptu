## CA médio em lotes condominiais

Os lotes condominiais são aqueles que tem mais do que um contribuinte e consequentemente a `FRACAO IDEAL` diferente de 1 (um). Eles ainda possuem dois dígitos, além de um verificador, que conferem uma identificação do Condomínio na Quadra Fiscal. Esse dado está presente no cadastro origional do IPTU no campo `NUMERO DO CONDOMINIO` e foi utilizado para diferenciar daqueles lotes ou lançamentos que não são condominiais.

O Coeficiente de Aproveitamento (CA) é um índice urbanístico que representa o densidade construtiva em planta (2D), que pode ser entendida como a proporção entre a Área construída em relação a Área do Terreno. Esse atributo não está presente originalmente no cadastro do IPTU e foi obtido pelo seguinte cálculo:

CA = `AREA CONSTRUIDA` / `FRACAO IDEAL` / `AREA DO TERRENO`

Foi considerada a média para agregar espacialmente o CA. Apesar de entendermos que a mediana expressaria melhor tais agregações, por uma limitação técnica e de performance da biblioteca escolhida, foi utilizada a média.