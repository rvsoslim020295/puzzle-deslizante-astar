# Rompecabezas Deslizante (8-Puzzle / 15-Puzzle)

Proyecto final – Análisis de Algoritmos y Estrategias de Programación.

## Requisitos
- Python 3.8 o superior (se probó con 3.10 en macOS).
- tkinter (viene con Python; en Linux: `sudo apt install python3-tk`).
- No necesita instalar librerías externas.

## Cómo ejecutar el juego
```
python3 gui.py
```
(En Windows, si `python3` no funciona, use `python gui.py`.)

### Controles
- **Clic** sobre una ficha vecina al espacio vacío, o **teclas de dirección**.
- **Nueva partida**: mezcla otro tablero (siempre con solución).
- **Reiniciar**: vuelve al tablero inicial de la partida.
- **3x3 / 4x4**: cambia el tamaño del tablero.
- **Resolver**: resuelve el tablero (A* en 3x3, búsqueda voraz en 4x4) animando los movimientos.
- El cronómetro empieza con el primer movimiento; se muestra el mejor puntaje por tamaño.

## Pruebas y análisis empírico
```
python3 pruebas.py
```
Ejecuta las 12 pruebas funcionales y compara A*, BFS y voraz (en 4x4 tarda unos segundos).
Los tiempos varían según el equipo; los nodos y movimientos son siempre los mismos (semilla fija).

## Archivos
- `logica.py`: tablero, movimientos, solubilidad por paridad y mezclado.
- `solver.py`: algoritmos A* (Manhattan), BFS y voraz.
- `gui.py`: interfaz gráfica con tkinter.
- `pruebas.py`: pruebas funcionales y análisis empírico.
- `capturas/`: capturas de pantalla usadas en el informe.
