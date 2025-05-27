# TFM_Daniele_Sebastiani_UOC
En este repositorio de GitHub se almacenarán los códigos utilizados a lo largo del desarrollo de mi Trabajo de Fin de Máster (TFM) del Máster en Bioinformática y Bioestadística de la Universidad UOC

Este estudio está enfocado en crear un modelo predictivo para la búsqueda de potenciales sitios de unión alternativos de un ligando en diferentes familias de proteínas. Para esto, se aplicará una aproximación basada en redes neuronales artificiales (ANN) y redes neuronales en grafos (GNN), que utilizan información obtenida a raíz de una búsqueda sobre un set de complejos ligandos proteínas. acerca de los grupos funcionales de la molécula, su estructura tridimensional y el tipo químico y geométrico del complejo con la proteína.

Se inició el proyecto con el estudio exhaustivo de más de 200 mil estructuras del Protein Data Bank (PDB). Se sometió a este grandes volúmenes de datos a un filtrado gradual y cuidadoso hasta llegar a una colección más pequeña y bien definida. Esta se destaca por la precisión en la descripción geométrica y química del ligando, sus sitios de unión correspondientes en las proteínas y sus interacciones particulares involucradas en cada complejo.

Por último, el conocimiento conseguido se usará como fundamento para el entrenamiento de una modelo predictivo de clasificación compuesta por ANN y GNN. El modelo así formado podrá calcular con precisión potenciales lugares alternativos de unión para un mismo ligando en diferentes proteínas, teniendo en cuenta tanto propiedades químicas como características geométricas del espacio del sistema ligando-proteína.

---------------------------------------------------------------

El trabajo se divide en tres partes:

1. Identificación de instancias de ligandos con proteínas en el PDB (Protein Data Bank)
Se realiza la selección y clasificación de complejos proteína-ligando presentes en el PDB, asegurando la representación de diversas familias proteicas. Para ello, se seleccionan únicamente los ligandos relevantes, descartando compuestos como solventes, agua, contraiones o aquellos unidos covalentemente. Este proceso garantiza la representatividad de ligandos que se unen a proteínas de diferentes familias, lo que permitirá disponer de una base de datos robusta sobre la cual trabajar.

2. Descarga y análisis de archivos PDB
Se descarga y filtran los archivos PDB o mmCIF seleccionados para estudiar y caracterizar los grupos funcionales de los ligandos, las características del sitio de unión y los tipos de interacción establecidos entre moléculas y proteínas.
 
3. Desarrollo del modelo predictivo
Finalmente, se programará y entrenará una Red Neuronal Artificial (ANN) que, utilizando la información derivada de los análisis previos, identifique de manera precisa los posibles sitios de unión en diferentes familias de proteínas según los grupos funcionales presentes en la molécula.

La primera parte se explica en la carpeta "**1_identificacion_ligandos_proteinas**" de este repositorio.

En esta primera fase, se llevaron a cabo las siguientes tares:

**a. Identificar instancias de ligandos con proteínas de diferentes familias en PDB** 

1. Descarga de la lista de IDs de complejos proteína-ligando
   
2. Creación de la tabla con información sobre las entradas PDB
 
3. Armonización de la columna “Classification” en la tabla de complejos proteína-ligando
 
4. Filtrado por método experimental (descarte de entradas NMR)
 
5. Filtrado por resolución (Descarte entrada con baja resolución)
    
6. Filtrado por clasificación (Descarte entradas no proteicas)
    
7. Adición de la columna de afinidad ligando-proteína
    
8. Descarga de archivos mmCIF de los complejos
    
9. Descarte de ligandos unidos covalentemente a la proteína
    
10. Descarte de azúcares simples
    
11. Descarte de entradas sin identificador Uniprot
    
12. Descarte de entradas con ligandos sin código InCh

13. Descarte de oligosacáridos ramificados

14. Corrección de errores en descargas

15. Descarte de entradas por tamaño (archivos más grandes de 3MB)

16. Descarte de ligandos enterrados

17. Identificación instancias ligandos-proteínas

---------------------------------------------------------------------------

La segunda parte se explica en la carpeta "**2_estudio_ligandos_sitios_union**" de este repositorio.

En esta fase, se llevaron a cabo las siguientes tares:

**b. Descargar PDBs y analizar interacciones**

1. Separar ligando y sitio de unión

2. Preparar los ligandos

3. Investigación de conformación de los ligandos y de los sitios de unión

4. Identificación los grupos funcionales de los ligandos.

5. Clasificación taxonómica de los ligandos

6. Preparación los ligandos y los sitios de unión en formato pdbqt para los análisis sucesivos

7. Uso de BINANA para las interacciones

8. Análisis estadístico de las interacciones y de la conformación de ligandos y sitios de unión

------------------------------------------------------------------------------------------------

La última parte del proyecto se explica en la carpeta "**3_modelo_predictivo**" de este repositorio.

En esta fase se llaveron a cabo las siguientes tares:

**c. Modelo predictivo que codifique sitio de unión y ligando**

1. Generar Embedding basado em GNN de los ligandos

2. Generar Embedding de las secuencias de las proteínas

3. Generar los Decoys negativos

4. Dividir el dataframe en train y test set

5. Armar un modelo predictivo basado en Red Neuronal Artificial (ANN)

6. Validar el modelo y analizar los resultados

