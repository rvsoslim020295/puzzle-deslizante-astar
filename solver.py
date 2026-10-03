"""Solvers del rompecabezas: A* (Manhattan), BFS (fuerza bruta) y Voraz (best-first).

Los estados se representan como tuplas planas para poder usarlas en conjuntos y diccionarios.
Cada solver devuelve (movimientos, nodos_expandidos); movimientos es la lista de estados
desde el inicial hasta la meta, o None si no hay solución.
"""
import heapq
from collections import deque
from itertools import count


def a_tupla(tablero):
    return tuple(v for fila in tablero for v in fila)


def meta(n):
    return tuple(list(range(1, n * n)) + [0])


def vecinos(estado, n):
    i = estado.index(0)
    f, c = divmod(i, n)
    for df, dc in ((-1, 0), (1, 0), (0, -1), (0, 1)):
        nf, nc = f + df, c + dc
        if 0 <= nf < n and 0 <= nc < n:
            j = nf * n + nc
            lista = list(estado)
            lista[i], lista[j] = lista[j], 0
            yield tuple(lista)


def manhattan(estado, n):
    """Heurística admisible: suma de distancias Manhattan de cada ficha a su casilla meta."""
    total = 0
    for pos, v in enumerate(estado):
        if v:
            fm, cm = divmod(v - 1, n)
            f, c = divmod(pos, n)
            total += abs(f - fm) + abs(c - cm)
    return total


def _camino(padres, estado):
    ruta = [estado]
    while padres[estado] is not None:
        estado = padres[estado]
        ruta.append(estado)
    return ruta[::-1]


def a_estrella(inicio, n):
    """f(x) = g(x) + h(x). Garantiza el camino más corto porque h es admisible."""
    objetivo = meta(n)
    desempate = count()
    abierta = [(manhattan(inicio, n), 0, next(desempate), inicio)]
    padres = {inicio: None}
    mejor_g = {inicio: 0}
    expandidos = 0
    while abierta:
        _, g, _, actual = heapq.heappop(abierta)
        if g > mejor_g[actual]:
            continue
        expandidos += 1
        if actual == objetivo:
            return _camino(padres, actual), expandidos
        for sig in vecinos(actual, n):
            ng = g + 1
            if ng < mejor_g.get(sig, float("inf")):
                mejor_g[sig] = ng
                padres[sig] = actual
                heapq.heappush(abierta, (ng + manhattan(sig, n), ng, next(desempate), sig))
    return None, expandidos


def bfs(inicio, n, limite_nodos=None):
    """Búsqueda en anchura: explora todos los estados por niveles (fuerza bruta)."""
    objetivo = meta(n)
    cola = deque([inicio])
    padres = {inicio: None}
    expandidos = 0
    while cola:
        actual = cola.popleft()
        expandidos += 1
        if actual == objetivo:
            return _camino(padres, actual), expandidos
        if limite_nodos and expandidos >= limite_nodos:
            return None, expandidos
        for sig in vecinos(actual, n):
            if sig not in padres:
                padres[sig] = actual
                cola.append(sig)
    return None, expandidos


def voraz(inicio, n, limite_nodos=None):
    """Best-first: solo usa h(x). Rápido, pero no garantiza el camino más corto."""
    objetivo = meta(n)
    desempate = count()
    abierta = [(manhattan(inicio, n), next(desempate), inicio)]
    padres = {inicio: None}
    expandidos = 0
    while abierta:
        _, _, actual = heapq.heappop(abierta)
        expandidos += 1
        if actual == objetivo:
            return _camino(padres, actual), expandidos
        if limite_nodos and expandidos >= limite_nodos:
            return None, expandidos
        for sig in vecinos(actual, n):
            if sig not in padres:
                padres[sig] = actual
                heapq.heappush(abierta, (manhattan(sig, n), next(desempate), sig))
    return None, expandidos
