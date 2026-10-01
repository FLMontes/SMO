# Referencias del laboratorio — índice

Documentos que el laboratorio compartió en su Drive. Están en `laboratorio/`; la carpeta `laboratorio/texto/` tiene el texto extraído de los PDF para leerlos rápido. **`laboratorio/` está excluida de git** porque es documentación interna: no se sube a GitHub.

## Contexto de Franco
- Franco se incorporó al laboratorio de materiales (FCEFyN‑UNC) en abril de 2026.
- Lo invitó Lautaro, responsable del proyecto SMO, y Franco le responde a él. Las autoridades del laboratorio tienen poca presencia, así que hay que interpretar sus documentos y proponer soluciones.
- Su primer trabajo fue la BD de aleaciones de Al (`data/raw/`, `scripts/construir_bd.py`). El segundo fue el PMV de este repositorio.

## Documentos
| Archivo | Qué es | Lo más importante |
|---|---|---|
| `minutaproygemas06oct2025` | Reunión inicial | Arrancar con aleaciones de Al; imaginar las aristas; explicar PageRank; repositorio en Drive |
| `minutaproygemas27nov2025` | Flujo de datos | Crudos → curados → objetos (pandas) → BD (sqlite) → red (networkx); 6 atributos (E, límite elástico, ρ, α, T fusión, precio); explicación de PageRank y de d; "red configurable según el diseño" |
| `minutaproygemas14abr2026` | Ingreso de Franco | Subsidio SeCyT (~300 k$); modelo de juguete con frutas; cubos vs bolas para las vecindades (problema de unidades); PC con 16 GB e i7 |
| `minutaproygemas05jun2026` | Revisión del código de frutas | Tolerancias por nodo; una arista por sobrelape, orientada al valor creciente; red primigenia por composición (aleación → elemento) |
| `minutaproygemas12jun2026` | Decisión de enviar a Argencon | Póster; tareas: red primigenia + red primaria de Al; probar con ejemplos de Ashby |
| `PanelDeTareas.pdf` | Tablero de tareas | Trabajo **aceptado en Argencon el 22/09/2026**: versión final en octubre + póster. Pendiente: alta formal de Franco (SID/SIGEVA) |
| `IEEEconferencelibre.tex/.pdf` | Manuscrito enviado a Argencon | Marco, metodología, modelo de juguete; el prototipo con Al figura como "trabajo en curso"; sin validación |
| `Frutas_PageRank.ipynb` | Código del modelo de juguete (lo hizo Luis con un chatbot) | Tolerancias uniformes, aristas ponderadas 1/5…5/5 |
| `sitiosdatosfrutas.txt/.docx` | Fuentes de datos de frutas | — |
| `RHCD-2025-329...pdf` | Resolución de la Facultad | Declara de interés académico Argencon 2026 (11–13/11/2026, FCEFyN) |

## Equipo (autores del manuscrito)
Ignacio, Carlos, Lautaro, Luis, Horacio, Juan, Franco. Las minutas las redacta el coordinador. Carlos subió las planillas de Al, Ti y acero; Luis, el código y las planillas de frutas.
