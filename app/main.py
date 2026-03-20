# Lenguaje de programación Eval-Número 4 
# Allan González V- 28.660.376
# Andrés Reyes V- 30.520.333
# Fernando Reyes V-30.159.566
# Mitchael Ruíz V- 31.416.127

import pygame
import random
import sys

pygame.mixer.pre_init(44100, -16, 2, 512) 
pygame.init()
pygame.mixer.init()

ANCHO_VENTANA = 800
ALTO_VENTANA = 700
TAMANO_BLOQUE = 30

COLUMNAS, FILAS = 10, 20
X_GRID, Y_GRID = 50, 50
ANCHO_GRID, ALTO_GRID = COLUMNAS * TAMANO_BLOQUE, FILAS * TAMANO_BLOQUE

# Colores
NEGRO = (5, 5, 10); GRIS_BORDE = (40, 40, 50); BLANCO = (255, 255, 255)
AZUL_NEON = (0, 255, 255); VERDE_NEON = (50, 255, 50); ROJO_NEON = (255, 50, 50); AMARILLO = (255, 255, 0)

COLORES_PIEZAS = [(0, 255, 255), (255, 255, 0), (160, 32, 240), (0, 255, 0), (255, 0, 0), (0, 0, 255), (255, 140, 0)]
FORMAS = [[[1, 1, 1, 1]], [[1, 1], [1, 1]], [[0, 1, 0], [1, 1, 1]], [[0, 1, 1], [1, 1, 0]], [[1, 1, 0], [0, 1, 1]], [[1, 0, 0], [1, 1, 1]], [[0, 0, 1], [1, 1, 1]]]

PANTALLA = pygame.display.set_mode((ANCHO_VENTANA, ALTO_VENTANA))
pygame.display.set_caption("TETRIS ULTIMATE - WAV EDITION")

# =================================================================
# 2. CLASES Y LÓGICA
# =================================================================
class Pieza:
    def __init__(self, x, y):
        self.x, self.y = x, y
        self.tipo = random.randint(0, len(FORMAS) - 1)
        self.forma = FORMAS[self.tipo]
        self.color = COLORES_PIEZAS[self.tipo]
    def rotar(self):
        self.forma = [list(row) for row in zip(*self.forma[::-1])]

class JuegoTetris:
    def __init__(self):
        self.cuadricula = [[(0,0,0) for _ in range(COLUMNAS)] for _ in range(FILAS)]
        self.puntuacion = 0
        self.nivel = 1
        self.estado = "MENU" 
        self.ms_acumulados = 0 
        self.pieza_actual = Pieza(3, 0)
        self.siguiente_pieza = Pieza(3, 0)
        self.pausa_mensaje_nivel = 0
        self.musica_actual = ""
        
        # Carga de efectos (WAV es lo mejor aquí)
        try:
            self.snd_punto = pygame.mixer.Sound("punto.wav")
            self.snd_perder = pygame.mixer.Sound("perder.wav")
            self.snd_ganar = pygame.mixer.Sound("ganar.wav")
            self.audio_ok = True
        except Exception as e:
            print(f"Error cargando sonidos: {e}")
            self.audio_ok = False

    def cargar_musica_nivel(self):
        if not self.audio_ok: return
        
        # Aunque sean WAV, usamos music.load para que no pesen tanto en RAM
        archivo = f"nivel{self.nivel}.wav"
        
        if self.musica_actual != archivo:
            try:
                pygame.mixer.music.stop()
                pygame.mixer.music.load(archivo)
                pygame.mixer.music.set_volume(0.5)
                pygame.mixer.music.play(-1)
                self.musica_actual = archivo
                print(f"Reproduciendo música: {archivo}")
            except Exception as e:
                print(f"No se pudo cargar {archivo}: {e}")

    def reset_partida(self):
        self.cuadricula = [[(0,0,0) for _ in range(COLUMNAS)] for _ in range(FILAS)]
        self.puntuacion = 0; self.nivel = 1; self.ms_acumulados = 0
        self.estado = "JUGANDO"
        self.musica_actual = ""
        self.cargar_musica_nivel()

    def validar_movimiento(self, pieza, ox=0, oy=0):
        for y, fila in enumerate(pieza.forma):
            for x, valor in enumerate(fila):
                if valor:
                    nx, ny = pieza.x + x + ox, pieza.y + y + oy
                    if nx < 0 or nx >= COLUMNAS or ny >= FILAS: return False
                    if ny >= 0 and self.cuadricula[ny][nx] != (0,0,0): return False
        return True

    def fijar_pieza(self):
        for y, fila in enumerate(self.pieza_actual.forma):
            for x, valor in enumerate(fila):
                if valor: self.cuadricula[self.pieza_actual.y + y][self.pieza_actual.x + x] = self.pieza_actual.color
        self.eliminar_lineas()
        self.pieza_actual = self.siguiente_pieza
        self.siguiente_pieza = Pieza(3, 0)
        if not self.validar_movimiento(self.pieza_actual):
            self.estado = "GAME_OVER"
            pygame.mixer.music.stop()
            if self.audio_ok: self.snd_perder.play()

    def eliminar_lineas(self):
        lineas = 0
        for r in range(FILAS):
            if all(col != (0,0,0) for col in self.cuadricula[r]):
                del self.cuadricula[r]
                self.cuadricula.insert(0, [(0,0,0) for _ in range(COLUMNAS)])
                lineas += 1
        if lineas > 0:
            self.puntuacion += 100 * lineas
            if self.audio_ok: self.snd_punto.play()

    def subir_nivel(self):
        self.nivel += 1
        self.ms_acumulados = 0
        self.cuadricula = [[(0,0,0) for _ in range(COLUMNAS)] for _ in range(FILAS)]
        self.pausa_mensaje_nivel = 90
        self.cargar_musica_nivel()

    def renderizar(self):
        PANTALLA.fill(NEGRO)
        if self.estado == "MENU":
            pygame.draw.rect(PANTALLA, AZUL_NEON, (50, 50, 700, 600), 2)
            self.dibujar_texto_centro("TETRIS ULTIMATE", 85, 150, AZUL_NEON)
            pygame.draw.rect(PANTALLA, (20, 20, 30), (220, 250, 360, 200))
            self.dibujar_texto_centro("CONTROLES", 30, 270, AMARILLO)
            for i, t in enumerate(["FLECHAS: MOVER", "ARRIBA: ROTAR", "ESPACIO: CAER", "ESC: PAUSA"]):
                self.dibujar_texto_centro(t, 22, 310 + (i*35), BLANCO)
            self.dibujar_texto_centro("PRESIONA [ENTER] PARA JUGAR", 35, 550, VERDE_NEON)
        else:
            fondos = {1: (10, 10, 30), 2: (40, 10, 10), 3: (10, 40, 10)}
            PANTALLA.fill(fondos.get(self.nivel, NEGRO))
            pygame.draw.rect(PANTALLA, (0,0,0), (X_GRID, Y_GRID, ANCHO_GRID, ALTO_GRID))
            for y in range(FILAS):
                for x in range(COLUMNAS):
                    color = self.cuadricula[y][x]
                    if color != (0,0,0):
                        pygame.draw.rect(PANTALLA, color, (X_GRID+x*TAMANO_BLOQUE, Y_GRID+y*TAMANO_BLOQUE, TAMANO_BLOQUE, TAMANO_BLOQUE))
                        pygame.draw.rect(PANTALLA, BLANCO, (X_GRID+x*TAMANO_BLOQUE, Y_GRID+y*TAMANO_BLOQUE, TAMANO_BLOQUE, TAMANO_BLOQUE), 1)
                    pygame.draw.rect(PANTALLA, GRIS_BORDE, (X_GRID+x*TAMANO_BLOQUE, Y_GRID+y*TAMANO_BLOQUE, TAMANO_BLOQUE, TAMANO_BLOQUE), 1)

            if self.estado == "JUGANDO":
                for y, fila in enumerate(self.pieza_actual.forma):
                    for x, valor in enumerate(fila):
                        if valor:
                            pygame.draw.rect(PANTALLA, self.pieza_actual.color, (X_GRID+(self.pieza_actual.x+x)*TAMANO_BLOQUE, Y_GRID+(self.pieza_actual.y+y)*TAMANO_BLOQUE, TAMANO_BLOQUE, TAMANO_BLOQUE))
                            pygame.draw.rect(PANTALLA, BLANCO, (X_GRID+(self.pieza_actual.x+x)*TAMANO_BLOQUE, Y_GRID+(self.pieza_actual.y+y)*TAMANO_BLOQUE, TAMANO_BLOQUE, TAMANO_BLOQUE), 1)

            # Sidebar
            x_s = X_GRID + ANCHO_GRID + 60
            f = pygame.font.SysFont("Agency FB", 35, bold=True)
            PANTALLA.blit(f.render(f"PUNTOS: {self.puntuacion}", True, BLANCO), (x_s, 100))
            PANTALLA.blit(f.render(f"NIVEL: {self.nivel}", True, VERDE_NEON), (x_s, 160))
            PANTALLA.blit(f.render(f"TIEMPO: {max(0, 120-(self.ms_acumulados//1000))}s", True, ROJO_NEON), (x_s, 220))

            if self.nivel < 3:
                PANTALLA.blit(f.render("SIGUIENTE:", True, BLANCO), (x_s, 320))
                for y, fila in enumerate(self.siguiente_pieza.forma):
                    for x, valor in enumerate(fila):
                        if valor:
                            pygame.draw.rect(PANTALLA, self.siguiente_pieza.color, (x_s + x*TAMANO_BLOQUE, 380 + y*TAMANO_BLOQUE, TAMANO_BLOQUE, TAMANO_BLOQUE))
                            pygame.draw.rect(PANTALLA, BLANCO, (x_s + x*TAMANO_BLOQUE, 380 + y*TAMANO_BLOQUE, TAMANO_BLOQUE, TAMANO_BLOQUE), 1)

            if self.pausa_mensaje_nivel > 0:
                self.dibujar_texto_centro("¡SIGUIENTE NIVEL!", 60, 350, AMARILLO)
                self.pausa_mensaje_nivel -= 1
            if self.estado == "PAUSA": self.dibujar_capa_oscura("PAUSA", ["1. SEGUIR", "2. REINICIAR", "3. MENÚ", "4. RENDIRSE"])
            elif self.estado == "GAME_OVER": self.dibujar_capa_oscura("GAME OVER", ["Tetris-teza", f"NIVEL: {self.nivel}", f"TIEMPO: {self.ms_acumulados//1000}s", "ENTER PARA VOLVER"])
            elif self.estado == "VICTORIA": self.dibujar_capa_oscura("¡VICTORIA!", ["ERES UN MAESTRO", "ENTER PARA VOLVER"])
        pygame.display.flip()

    def dibujar_texto_centro(self, texto, tamano, y, color):
        fuente = pygame.font.SysFont("Agency FB", tamano, bold=True)
        render = fuente.render(texto, True, color)
        PANTALLA.blit(render, render.get_rect(center=(ANCHO_VENTANA//2, y)))

    def dibujar_capa_oscura(self, tit, lins):
        s = pygame.Surface((ANCHO_VENTANA, ALTO_VENTANA)); s.set_alpha(230); s.fill(NEGRO); PANTALLA.blit(s, (0,0))
        self.dibujar_texto_centro(tit, 90, 150, ROJO_NEON if tit == "GAME OVER" else AZUL_NEON)
        for i, l in enumerate(lins): self.dibujar_texto_centro(l, 32, 300+i*55, BLANCO)

# =================================================================
# 4. BUCLE PRINCIPAL
# =================================================================
j = JuegoTetris(); reloj = pygame.time.Clock(); caida = 0
while True:
    dt = reloj.tick(60)
    for e in pygame.event.get():
        if e.type == pygame.QUIT: pygame.quit(); sys.exit()
        if e.type == pygame.KEYDOWN:
            if j.estado == "MENU" and e.key == pygame.K_RETURN: j.reset_partida()
            elif j.estado == "JUGANDO" and j.pausa_mensaje_nivel <= 0:
                if e.key == pygame.K_LEFT and j.validar_movimiento(j.pieza_actual, ox=-1): j.pieza_actual.x -= 1
                if e.key == pygame.K_RIGHT and j.validar_movimiento(j.pieza_actual, ox=1): j.pieza_actual.x += 1
                if e.key == pygame.K_DOWN and j.validar_movimiento(j.pieza_actual, oy=1): j.pieza_actual.y += 1
                if e.key == pygame.K_UP:
                    prev = j.pieza_actual.forma; j.pieza_actual.rotar()
                    if not j.validar_movimiento(j.pieza_actual): j.pieza_actual.forma = prev
                if e.key == pygame.K_SPACE:
                    while j.validar_movimiento(j.pieza_actual, oy=1): j.pieza_actual.y += 1
                    j.fijar_pieza()
                if e.key in [pygame.K_ESCAPE, pygame.K_p]: j.estado = "PAUSA"
            elif j.estado == "PAUSA":
                if e.key == pygame.K_1: j.estado = "JUGANDO"
                if e.key == pygame.K_2: j.reset_partida()
                if e.key == pygame.K_3: j.estado = "MENU"
                if e.key == pygame.K_4: j.estado = "GAME_OVER"
            elif j.estado in ["GAME_OVER", "VICTORIA"] and e.key == pygame.K_RETURN: j.estado = "MENU"

    if j.estado == "JUGANDO" and j.pausa_mensaje_nivel <= 0:
        j.ms_acumulados += dt
        caida += dt
        v = {1: 800, 2: 500, 3: 300}.get(j.nivel, 800)
        if caida > v:
            if j.validar_movimiento(j.pieza_actual, oy=1): j.pieza_actual.y += 1
            else: j.fijar_pieza()
            caida = 0
        if j.ms_acumulados >= 120000:
            if j.nivel < 3: j.subir_nivel()
            else:
                j.estado = "VICTORIA"
                pygame.mixer.music.stop()
                if j.audio_ok: j.snd_ganar.play()
    j.renderizar()
