# CC219-TP-TF-2025-1-
# Mouse Facial
# Integrantes:
- Joaquín Eduardo Velarde Leyva
- Daniel Ivan Carbajal Robles
- Salvador Diaz Aguirre


# Objetivo del trabajo
Este trabajo tiene objetivo, hacer un mouse facial utilizando computer vision. Busca que personas con discpacidad motriz puedan utilizar sin problemas una computadora.

# Descripción del dataset
El dataset utilizado es de Kaggle, se trata de diferentes gestos de la cara, hechos por diferentes razas de personas. 

# Conclusiones
- El presente trabajo ha demostrado que es posible diseñar un sistema de control por expresiones faciales aplicando técnicas de visión computacional y aprendizaje profundo. A partir de un conjunto de datos balanceado y representativo, se implementaron y compararon distintos modelos de clasificación, entre ellos CNN simple, CNN con atención y ResNet, evaluando su rendimiento mediante métricas estándar como accuracy, precisión, recall y F1-score. La arquitectura ResNet se destacó como la más eficiente, alcanzando una precisión de validación entre el 70% y 85% y mostrando un mejor balance entre generalización y exactitud en comparación con los otros modelos. Por su parte, el modelo con atención, pese a su enfoque más avanzado, no logró superar al modelo CNN básico, lo que sugiere que la complejidad adicional no siempre garantiza mejores resultados, especialmente con conjuntos de datos pequeños.
- Además, se identificaron desafíos clave en la clasificación de ciertas expresiones como “wink_right” y “brows_lifted”, las cuales tienden a confundirse con gestos similares. Esto resalta la necesidad de seguir refinando la recolección de datos y explorar técnicas de aumento específicas para mejorar la discriminación entre clases visualmente similares. En conjunto, los hallazgos permiten concluir que el enfoque propuesto es prometedor para el desarrollo de interfaces accesibles sin contacto físico, aunque aún se requiere optimización en aspectos como la latencia en tiempo real y la personalización del sistema para adaptarse a diferentes morfologías faciales. Este proyecto constituye un paso significativo hacia la inclusión tecnológica y la mejora de la interacción humano-computadora.


# Licencia 
https://www.mit.edu/~amini/LICENSE.md



