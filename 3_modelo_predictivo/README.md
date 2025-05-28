# Parte 3 – Modelo predictivo

Finalmente, los datos conseguido a través de los anteriores estudios se pudieron utilizar para la realización y el entrenamiento de un modelo predictivo de tipo clasificatorio capaz de predecir la unión entre una molécula y una proteína. 
La idea fue la de considerar

• un posible ligando, considerando sus características químicas y geométricas

• una proteína, considerando su secuencia y la geometría del sitio de unión

para predecir la posible unión entre los dos elementos. 

El database generado a lo largo del trabajo almacena datos de complejos reales por los que, por eso, la unión está garantizada de forma empírica. Estos datos se utilizarán como entradas positivas y se etiquetarán como instancias por las que la unión se realiza (en este caso, “1”).

Para entrenar la Red Neuronal Artificial, se precisa también de elementos por los que la unión no se realiza. Se decidió, por ello, identificar decoys negativos, ejemplos artificiales seleccionados a propósito según determinados criterios en los que se supone que la unión no pueda ocurrir. 

Se decidió elegir como negativos, moléculas diferentes de los ligandos positivos del punto de vista químico y geométrico. Por eso los decoys negativos tenían que tener:

• un **coeficiente de Tanimoto** < 0,6 con el correspondiente positivo    

• una **similitud** entre el análisis con *Ultrafast Shape Recognition* < 0,6 con el correspondiente positivo

Al diferir del ligando que sí provoca la unión, se considera razonable suponer que estos compuestos seleccionados como negativos no deberían presentar interacción. 
Para cada ligando único, se generó un decoy negativo, de manera que el número de entradas negativas fuese equivalente al número de entradas positivas presentes en el dataframe. 

Se decidió realizar la búsqueda de los decoys negativos a partir de moléculas en la base de datos Zinc, un repositorio público que contiene compuestos disponibles comercialmente preparados para simulaciones de docking. 

Se utilizaron subconjuntos filtrados según criterios de “drug-likeness”, seleccionando todas las moléculas con peso molecular comprendido entre 250 y 500 Da y valores de logP entre 0 y 5. 

Se descargaron, así, los códigos SMILES de las *16,000,000* moléculas que tenían estas características en formato *.smi*. 

Sucesivamente, se obtuvo una muestra de 100,000 moléculas extraídas al azar para realizar la búsqueda de los decoys según los criterios establecidos.   
El dataframe estará compuesto por instancias ligando-proteína por las que la unión ocurre (etiquetadas como “1”) e instancias calculada con complejos entre ligandos negativos y proteinas por los que la unión no ocurre (etiquetadas como “0”).

El código utilizado es el "**generar_decoys_negativos.py**".

Para armar y entrenar la Red Neuronal Artificial se consideran las siguientes características de los complejos:

• características químicas de los ligandos

• características geométricas de los ligandos

• características de las secuencias de las proteínas

• características geométricas del sitio de unión

Para considerar las características químicas de los ligandos, se decidió generar un embedding basado en *Graph Neural Networks* a partir de representaciones SMILES.

En primer lugar, cada ligando fue transformado a partir de su representación SMILES en un grafo, donde los nodos corresponden a átomos con sus propiedades químicas, y las aristas a enlaces con sus respectivos atributos.

De esta forma, se convierte cada SMILES en un grafo molecular, donde:

• Nodos = átomos, con sus características:
    ◦ Número atómico
        
    ◦ Grado (número de enlaces)
        
    ◦ Carga formal
        
    ◦ Número total de hidrógenos
        
    ◦ Aromaticidad
        
    ◦ Si está en un anillo
        
    ◦ Hibridación (SP, SP2, SP3, etc.)
        
    ◦ Quiralidad (CW, CCW, no especificada)
    
• Aristas = enlaces, con atributos:
    
    ◦ Tipo de enlace (simple, doble, etc.)
    
    ◦ Conjugación
    
    ◦ Si forma parte de un anillo

Con el fin de dotar a la red de una base química significativa, se diseñó una etapa de preentrenamiento en la que la GNN aprendió a predecir el **fingerprint de Morgan** de cada ligando.

Se decidió realizar el preentrenamiento sobre los *~5,700* ligandos únicos del dataframe (entre posivios y negativos), más una muestra de *100,000* moléculas drug-like escogida al azar del las moléculas previamente descargada de la base de datos Zinc.

Una vez entrenado, se descartó el decodificador de salida y se conservaron únicamente las capas de extracción de características, que se utilizaron para generar un vector (embedding) por molécula.
Estos vectores resumen la información química esencial de cada ligando en un formato numérico compacto, lo que permite su uso posterior en modelos supervisados. 
La información del embedding se almacena en 128 columnas.

El proceso se describe en el notebook "**Generar_embedding_ligandos.ipynb**".

Para obtener una representación numérica de las proteínas asociadas al sitio activo, se empleó un modelo de lenguaje preentrenado específicamente diseñado para secuencias biológicas. En concreto, se utilizó **ESM2 (Evolutionary Scale Modeling v2)**, una arquitectura tipo Transformer desarrollada por Meta AI para capturar patrones evolutivos y estructurales en secuencias de aminoácidos.
En este trabajo se consideraron las cadenas relacionadas directamente con el sitio activo, con el objetivo de centrar la atención del modelo en las regiones funcionalmente más relevantes.

Para gestionar eficientemente el cálculo en GPU y evitar cuellos de memoria, se procesaron las secuencias por lotes y se guardaron en archivos temporales. Finalmente, todos los vectores fueron unificados en un único archivo que sirvió como entrada para modelos posteriores de aprendizaje automático. La información del embedding se almacena en 320 columnas.

El proceso se describe en el notebook "**Generar_embedding_sitios_de_union.ipynb**".


Con toda la información obtenida, se puso realizar el dataframe final con todas las instancias (positivas y negativas) y las características.

Se decidió unir para sucesivamente utilizar, la siguiente información:
• Nombre de la instancia (1 columna)

• Embedding de las caracteríasticas químicas del ligando (128 columnas)

• Vector de doce componentes del análisis USR del ligando que corresponde a su geometría (12 columnas)

• Embedding de las características de la secuencia de la cadena proteica del sitio de unión (320 columnas)

• Vector de doce componentes del análisis USR del sitio de unión que corresponde a su geometría (12 columnas)

• Label o etiqueta con “0” para las instancias que no presentan unión y “1” para las que sí la presentan.

Se obtuvo un dataframe con:

- 140,348 instancias (entre positivas y negativas)

- 474 columnas (o *features*)

El proceso se describe en el notebook "**unir_dataframes.ipynb**".


