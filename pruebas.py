"""Pruebas funcionales (OE-8) y análisis empírico de los algoritmos."""
import random
import statistics
import time

import logica
import solver


def pruebas_funcionales():
    resultados = []

    def caso(nombre, condicion):
        resultados.append((nombre, bool(condicion)))

    # RF-01
    t = logica.crear_tablero(3)
    caso("RF-01 Tablero 3x3 con 8 fichas y vacío", t == [[1, 2, 3], [4, 5, 6], [7, 8, 0]])
    caso("RF-01 Tablero 4x4 con 15 fichas y vacío", logica.crear_tablero(4)[3] == [13, 14, 15, 0])
    # RF-02
    ok3 = all(logica.es_resoluble(logica.mezclar(3)) for _ in range(500))
    ok4 = all(logica.es_resoluble(logica.mezclar(4)) for _ in range(500))
    caso("RF-02 500 mezclas 3x3 resolubles", ok3)
    caso("RF-02 500 mezclas 4x4 resolubles", ok4)
    caso("Paridad detecta tablero imposible (2 fichas intercambiadas)",
         not logica.es_resoluble([[2, 1, 3], [4, 5, 6], [7, 8, 0]]))
    # RF-03 / RF-04
    t = logica.crear_tablero(3)
    caso("RF-03 Mover ficha adyacente (8) al vacío", logica.mover(t, 2, 1) and t[2][2] == 8)
    t = logica.crear_tablero(3)
    copia = [f[:] for f in t]
    caso("RF-04 Ficha no adyacente rechazada y tablero intacto", not logica.mover(t, 0, 0) and t == copia)
    caso("RF-04 Coordenadas fuera del tablero rechazadas", not logica.mover(t, 5, 5) and t == copia)
    # RF-05
    caso("RF-05 Detecta tablero resuelto", logica.esta_resuelto(logica.crear_tablero(3)))
    caso("RF-05 No marca victoria en tablero mezclado", not logica.esta_resuelto(logica.mezclar(3)))
    t = logica.crear_tablero(3)
    logica.mover(t, 2, 1)
    caso("RF-05 Victoria tras deshacer el último movimiento", not logica.esta_resuelto(t) and logica.mover(t, 2, 2) and logica.esta_resuelto(t))
    # Solver
    t = logica.mezclar(3)
    ruta, _ = solver.a_estrella(solver.a_tupla(t), 3)
    caso("Solver A* llega a la meta en tablero 3x3", ruta and ruta[-1] == solver.meta(3))
    return resultados


def tablero_a_distancia(n, pasos):
    """Genera un tablero resoluble con un número controlado de pasos aleatorios."""
    t = logica.crear_tablero(n)
    anterior = None
    for _ in range(pasos):
        vf, vc = logica.posicion_vacio(t)
        opciones = [(vf + a, vc + b) for a, b in ((-1, 0), (1, 0), (0, -1), (0, 1))
                    if 0 <= vf + a < n and 0 <= vc + b < n and (vf + a, vc + b) != anterior]
        elegido = random.choice(opciones)
        anterior = (vf, vc)
        logica.mover(t, *elegido)
    return t


def medir(algoritmo, estado, n, **kw):
    ini = time.perf_counter()
    ruta, nodos = algoritmo(estado, n, **kw)
    ms = (time.perf_counter() - ini) * 1000
    return (len(ruta) - 1 if ruta else None), nodos, ms


def analisis_empirico(cantidad=50, semilla=2026):
    random.seed(semilla)
    # 1) 3x3 aleatorios completos: A*, BFS, Voraz
    tableros = [solver.a_tupla(logica.mezclar(3, 300)) for _ in range(cantidad)]
    resumen = {}
    for nombre, f in (("A*", solver.a_estrella), ("BFS", solver.bfs), ("Voraz", solver.voraz)):
        datos = [medir(f, t, 3) for t in tableros]
        resumen[nombre] = {
            "pasos": statistics.mean(d[0] for d in datos),
            "nodos": statistics.mean(d[1] for d in datos),
            "ms": statistics.mean(d[2] for d in datos),
            "optimas": sum(1 for d, a in zip(datos, [medir(solver.a_estrella, t, 3) for t in tableros]) if d[0] == a[0]),
        }
    # 2) 4x4 a distancia moderada: A* y Voraz (BFS inviable)
    t4 = [solver.a_tupla(tablero_a_distancia(4, 60)) for _ in range(20)]
    r4 = {}
    for nombre, f, kw in (("A*", solver.a_estrella, {}), ("Voraz", solver.voraz, {}),
                          ("BFS", solver.bfs, {"limite_nodos": 200000})):
        datos = [medir(f, t, 4, **kw) for t in t4]
        resueltos = [d for d in datos if d[0] is not None]
        r4[nombre] = {
            "resueltos": len(resueltos), "total": len(datos),
            "pasos": statistics.mean(d[0] for d in resueltos) if resueltos else None,
            "nodos": statistics.mean(d[1] for d in datos),
            "ms": statistics.mean(d[2] for d in datos),
        }
    # 3) Mezcla ingenua vs. con paridad
    ingenuos = [logica.mezclar_aleatorio(3) for _ in range(1000)]
    sin_sol = sum(1 for t in ingenuos if not logica.es_resoluble(t))
    return resumen, r4, sin_sol


def tiempo_respuesta_movimiento():
    t = logica.mezclar(4)
    ini = time.perf_counter()
    for _ in range(1000):
        logica.mover(t, 0, 0)
        logica.esta_resuelto(t)
    return (time.perf_counter() - ini) * 1000 / 1000


if __name__ == "__main__":
    print("=== PRUEBAS FUNCIONALES ===")
    res = pruebas_funcionales()
    for nombre, ok in res:
        print(("OK   " if ok else "FALLA"), nombre)
    print(f"Total: {sum(ok for _, ok in res)}/{len(res)} aprobadas\n")

    print("=== ANÁLISIS EMPÍRICO ===")
    r3, r4, sin_sol = analisis_empirico()
    print("3x3 (50 tableros aleatorios):")
    for k, v in r3.items():
        print(f"  {k:6} pasos={v['pasos']:.2f} nodos={v['nodos']:.1f} ms={v['ms']:.3f} soluciones óptimas={v['optimas']}/50")
    print("4x4 (20 tableros a 60 pasos de la meta):")
    for k, v in r4.items():
        p = f"{v['pasos']:.2f}" if v['pasos'] is not None else "-"
        print(f"  {k:6} resueltos={v['resueltos']}/{v['total']} pasos={p} nodos={v['nodos']:.1f} ms={v['ms']:.2f}")
    print(f"Mezcla ingenua 3x3: {sin_sol}/1000 sin solución ({sin_sol/10:.1f} %)")
    print(f"Tiempo de respuesta por movimiento (lógica): {tiempo_respuesta_movimiento():.5f} ms")
