"""Interfaz gráfica (tkinter) del rompecabezas deslizante.

Controles: clic sobre una ficha o teclas de dirección. Botones: Nueva partida,
Reiniciar, tamaño 3x3 / 4x4 y Resolver (pista con A* en 3x3, voraz en 4x4).
"""
import time
import tkinter as tk
from tkinter import messagebox

import logica
import solver

TAM_CASILLA = 100
COLORES = {"fondo": "#1f2937", "ficha": "#3b82f6", "texto": "#ffffff", "vacio": "#111827", "ok": "#10b981"}


class Juego:
    def __init__(self, raiz):
        self.raiz = raiz
        raiz.title("Rompecabezas Deslizante")
        raiz.configure(bg=COLORES["fondo"])
        raiz.resizable(False, False)
        self.n = 3
        self.mejor_mov = {3: None, 4: None}
        self.mejor_tiempo = {3: None, 4: None}
        self.var_mov = tk.StringVar()
        self.var_tiempo = tk.StringVar()
        self.var_mejor = tk.StringVar()
        self._armar_widgets()
        self.nueva_partida()
        self._tick()

    def _armar_widgets(self):
        barra = tk.Frame(self.raiz, bg=COLORES["fondo"])
        barra.pack(padx=12, pady=(12, 4), fill="x")
        for var in (self.var_mov, self.var_tiempo):
            tk.Label(barra, textvariable=var, fg=COLORES["texto"], bg=COLORES["fondo"],
                     font=("Arial", 13, "bold")).pack(side="left", padx=8)
        self.canvas = tk.Canvas(self.raiz, bg=COLORES["fondo"], highlightthickness=0)
        self.canvas.pack(padx=12, pady=4)
        self.canvas.bind("<Button-1>", self._clic)
        self.raiz.bind("<Key>", self._tecla)
        tk.Label(self.raiz, textvariable=self.var_mejor, fg="#9ca3af", bg=COLORES["fondo"],
                 font=("Arial", 10)).pack()
        botones = tk.Frame(self.raiz, bg=COLORES["fondo"])
        botones.pack(padx=12, pady=(4, 12))
        for texto, cmd in (("Nueva partida", self.nueva_partida), ("Reiniciar", self.reiniciar),
                           ("3x3", lambda: self.cambiar_tamano(3)), ("4x4", lambda: self.cambiar_tamano(4)),
                           ("Resolver", self.resolver)):
            tk.Button(botones, text=texto, command=cmd, width=11).pack(side="left", padx=3)

    # ---- partida ----
    def nueva_partida(self):
        self.tablero = logica.mezclar(self.n)
        self.inicial = [f[:] for f in self.tablero]
        self._empezar()

    def reiniciar(self):
        self.tablero = [f[:] for f in self.inicial]
        self._empezar()

    def cambiar_tamano(self, n):
        self.n = n
        self.nueva_partida()

    def _empezar(self):
        self.movimientos = 0
        self.inicio = None          # el cronómetro arranca con el primer movimiento
        self.terminado = False
        self.resolviendo = False
        lado = self.n * TAM_CASILLA
        self.canvas.config(width=lado, height=lado)
        self._actualizar()

    # ---- eventos ----
    def _clic(self, evento):
        if self.terminado or self.resolviendo:
            return
        self._intentar(evento.y // TAM_CASILLA, evento.x // TAM_CASILLA)

    def _tecla(self, evento):
        mapa = {"Up": "arriba", "Down": "abajo", "Left": "izquierda", "Right": "derecha"}
        if evento.keysym in mapa and not self.terminado and not self.resolviendo:
            # La flecha mueve la ficha en esa dirección hacia el vacío
            if logica.mover_direccion(self.tablero, mapa[evento.keysym]):
                self._tras_mover()

    def _intentar(self, f, c):
        if logica.mover(self.tablero, f, c):
            self._tras_mover()

    def _tras_mover(self):
        if self.inicio is None:
            self.inicio = time.time()
        self.movimientos += 1
        if logica.esta_resuelto(self.tablero):
            self.terminado = True
            self._registrar_record()
        self._actualizar()
        if self.terminado:
            messagebox.showinfo("¡Victoria!", f"Resuelto en {self.movimientos} movimientos y {self._segundos()} s.")

    def _registrar_record(self):
        n, seg = self.n, self._segundos()
        if self.mejor_mov[n] is None or self.movimientos < self.mejor_mov[n]:
            self.mejor_mov[n] = self.movimientos
        if self.mejor_tiempo[n] is None or seg < self.mejor_tiempo[n]:
            self.mejor_tiempo[n] = seg

    def resolver(self):
        """Resuelve la partida actual animando la solución calculada."""
        if self.terminado or self.resolviendo:
            return
        estado = solver.a_tupla(self.tablero)
        algoritmo = solver.a_estrella if self.n == 3 else solver.voraz
        ruta, _ = algoritmo(estado, self.n)
        if not ruta:
            return
        self.resolviendo = True
        self._animar(ruta, 1)

    def _animar(self, ruta, i):
        if i >= len(ruta):
            self.resolviendo = False
            self.terminado = True
            self._actualizar()
            return
        n = self.n
        self.tablero = [list(ruta[i][r * n:(r + 1) * n]) for r in range(n)]
        if self.inicio is None:
            self.inicio = time.time()
        self.movimientos += 1
        self._actualizar()
        self.raiz.after(150, self._animar, ruta, i + 1)

    # ---- dibujo ----
    def _segundos(self):
        return 0 if self.inicio is None else int(time.time() - self.inicio)

    def _tick(self):
        if not self.terminado:
            self.var_tiempo.set(f"Tiempo: {self._segundos()} s")
        self.raiz.after(500, self._tick)

    def _actualizar(self):
        self.var_mov.set(f"Movimientos: {self.movimientos}")
        self.var_tiempo.set(f"Tiempo: {self._segundos()} s")
        m, t = self.mejor_mov[self.n], self.mejor_tiempo[self.n]
        self.var_mejor.set("Mejor ({0}x{0}): ".format(self.n) + (f"{m} mov. / {t} s" if m else "sin registro"))
        self.canvas.delete("all")
        for i, fila in enumerate(self.tablero):
            for j, v in enumerate(fila):
                x, y = j * TAM_CASILLA, i * TAM_CASILLA
                color = COLORES["vacio"] if v == 0 else (COLORES["ok"] if self.terminado else COLORES["ficha"])
                self.canvas.create_rectangle(x + 3, y + 3, x + TAM_CASILLA - 3, y + TAM_CASILLA - 3,
                                             fill=color, outline="")
                if v:
                    self.canvas.create_text(x + TAM_CASILLA / 2, y + TAM_CASILLA / 2, text=str(v),
                                            fill=COLORES["texto"], font=("Arial", 30, "bold"))


if __name__ == "__main__":
    raiz = tk.Tk()
    Juego(raiz)
    raiz.mainloop()
