"""Lógica del rompecabezas deslizante (sin interfaz gráfica).

El tablero es una lista de listas N x N. El valor 0 representa el espacio vacío.
"""
import random

DIRECCIONES = {"arriba": (-1, 0), "abajo": (1, 0), "izquierda": (0, -1), "derecha": (0, 1)}


def crear_tablero(n):
    """RF-01: tablero ordenado 1..n*n-1 con el vacío (0) al final."""
    valores = list(range(1, n * n)) + [0]
    return [valores[i * n:(i + 1) * n] for i in range(n)]


def posicion_vacio(tablero):
    for i, fila in enumerate(tablero):
        for j, v in enumerate(fila):
            if v == 0:
                return i, j


def esta_resuelto(tablero):
    """RF-05: el tablero está ordenado y el vacío está al final."""
    return tablero == crear_tablero(len(tablero))


def contar_inversiones(tablero):
    plano = [v for fila in tablero for v in fila if v != 0]
    return sum(1 for i in range(len(plano)) for j in range(i + 1, len(plano)) if plano[i] > plano[j])


def es_resoluble(tablero):
    """Criterio de paridad de Johnson y Story (1879).

    N impar: resoluble si las inversiones son pares.
    N par: resoluble si (inversiones + fila del vacío contada desde abajo) es impar.
    """
    n = len(tablero)
    inv = contar_inversiones(tablero)
    if n % 2 == 1:
        return inv % 2 == 0
    fila_desde_abajo = n - posicion_vacio(tablero)[0]
    return (inv + fila_desde_abajo) % 2 == 1


def mover(tablero, fila, col):
    """RF-03/RF-04: mueve la ficha (fila, col) si es adyacente al vacío.

    Devuelve True si movió; si no es válido no modifica el tablero.
    """
    n = len(tablero)
    if not (0 <= fila < n and 0 <= col < n):
        return False
    vf, vc = posicion_vacio(tablero)
    if abs(fila - vf) + abs(col - vc) != 1:
        return False
    tablero[vf][vc], tablero[fila][col] = tablero[fila][col], 0
    return True


def mover_direccion(tablero, direccion):
    """Mueve la ficha hacia la dirección dada (la ficha se desliza hacia el vacío)."""
    df, dc = DIRECCIONES[direccion]
    vf, vc = posicion_vacio(tablero)
    return mover(tablero, vf - df, vc - dc)


def mezclar(n, pasos=None):
    """RF-02: mezcla con movimientos válidos aleatorios, así el estado siempre es resoluble."""
    tablero = crear_tablero(n)
    pasos = pasos or 200 * n
    anterior = None
    for _ in range(pasos):
        vf, vc = posicion_vacio(tablero)
        vecinos = [(vf + df, vc + dc) for df, dc in DIRECCIONES.values()
                   if 0 <= vf + df < n and 0 <= vc + dc < n and (vf + df, vc + dc) != anterior]
        elegido = random.choice(vecinos)
        anterior = (vf, vc)
        mover(tablero, *elegido)
    if esta_resuelto(tablero):
        return mezclar(n, pasos)
    return tablero


def mezclar_aleatorio(n):
    """Mezcla ingenua (permutación al azar). Solo para comparar: ~50 % sin solución."""
    valores = list(range(n * n))
    random.shuffle(valores)
    return [valores[i * n:(i + 1) * n] for i in range(n)]
