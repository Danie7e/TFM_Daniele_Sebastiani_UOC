# Parte 2 – Estudio de ligandos y sitios de unión

Obtenidas las instancias ligando-proteína sobre las que queremos trabajar, se han investigados los elementos que las componen.

Primero, como había muchos casos en que un mismo ligando se encontraba repetido, cada uno con sus coordenadas especificas, en una misma proteína, se decidió "expandir" el dataframe de forma que, cada línea, correspondiera a un complejo ligando proteína especifica.

Sucesivamente, se separaron, mediante un script desarrollado empleando la librería de Biopython, los ligandos y los sitios de unión. Se consideró como sitio de unión, todos los residuos aminoacídicos situados a una distancia menor o igual a **4 Ångströms (Å)** del ligando. Estos elementos fueron guardados en formato PDB en distintas carpetas. Para obtener un resultado homogéneo, se decidió guardar sólo los elementos (ligandos y sitios) en formato PDB, evitando descargar entradas en formato mmCIF con el fin de disponer de un conjunto de datos armonizado. Por este motivo, han descartaron las pocas instancias para las que la descarga en formato PDB resultaba imposible. 

El proceso está descrito en el notebook "**Separar_Ligandos_Sitios_Union_nuevo.ipynb**".

Luego, se utilizó un script interno, proporcionado por el laboratorio de mi tutor, para "arreglar" los ligandos descargados en formato PDB. Este script añade información sobre los enlaces químicos mediante los cuales los ligandos se unen, basándose en su código InChI, además de corregir propiedades de los átomos y de los enlaces. *Este script no se ha subito por motivos de privacidad.*

Se realizó una investigación sobre la conformación de ligandos y de los sitios de unión empleando la técnica de *Ultrafast Shape Recognition* (USR) (https://pubmed.ncbi.nlm.nih.gov/17342716/), una metodología rápida y eficaz para representar la forma tridimensional de las moléculas. Esta técnica se basa en la caracterización de una conformación considerando su geometría en un espacio tridimensional. Cada conformación se describe mediante un vector de doce componentes, que representan determinadas distancias entre el átomo central y sus extremidades. De esta forma, fue posible identificar y comparar las diferentes conformaciones de los ligandos que se unen a distintas familias de proteínas y de los sitios activos que pertenecen a la misma proteína. 

Los análisis están descriptas en los notebooks "**USR_script_ligandos.ipynb**" y "**USR_script_sitios.ipynb**".

Se realizó una comparación de las varias conformaciones de los ligandos agrupados por ligando, evitando las autocomparaciones y, a la vez, la comparación de los sitios de unión que acogían los ligandos. De esta forma se pudo realizar un dataframe con los datos sobre la similitud de las varias conformaciones de un mismo ligando y uno sobre la similitud de las conformaciones de los sitios de unión. Se ha considerado que dos ligandos tengan la misma conformación si su similitud resulta ser > 0,6 mientras que se consideran conformaciones distintas todas las que tienen similitudes ≤ 0,6.

Los análisis están descriptas en los notebooks "**Analisis_USR_grupos_ligandos.ipynb**" y "**Analisis_USR_grupos_sitios.ipynb**".

Para completar la información que se desea almacenar sobre los ligandos, se utilizó el software *ClassyFire* para obtener la taxonomía de los compuestos químicos del dataframe, es decir, de los ligandos. Este programa proporciona una clasificación basada en una agrupación jerárquica cada vez más específica ("Kingdom", "Superclass", "Class", "Subclass"). Se decidió conservar la categoría de "Superclass", excepto en el caso de los lípidos, para los cuales se utilizó la categoría de "Class". 

El análisis se describe en el notebook "**Use_Classyfire.ipynb**".

Sucesivamente, se han convertidos los archivos de ligandos y de proteínas en formato **PDBQT** utilizando los scripts “*prepare_receptor4.py*” y “*prepare_ligand4.py*” de la suite *ADFR*. Durante esta preparación, también se añadieron los átomos de hidrógeno que no estaban presentes en los archivos originales. 

Los procesos están descriptas en el notebook "**Use_prepare_receptor_y_ligand.ipynb**".

Una vez preparados los ligandos y los sitios de unión, fue posible ejecutar el script de **BINANA 2** para obtener un dataframe con la cantidad de interacciones que cada instancia ligando-proteína establece. Descartando las entradas para las cuales no fue posible realizar el análisis debido a errores, se obtuvo el dataframe final, compuesto por 70,378 instancias y 2,871 ligandos únicos. En este dataframe se encuentra almacenada toda la información necesaria desde el punto de vista de los ligandos, de las proteínas y de las interacciones que establecen. 

El proceso se explica en el notebook "**Use_BINANA_2.ipynb**".

Finalmente se realiza un análisis pormenorizado de las conformaciones de ligandos y proteínas y de las interecciones entre ligandos y proteína en los complejos, identificando patrones estadísticamente significativos para cada clase química.

Estos análisis se explican en los notebooks "**Analisis_conformacion.ipynb**" y "**Analisis_Descriptivo.ipynb**".


