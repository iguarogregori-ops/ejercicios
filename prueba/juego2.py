import math
import random
import pygame

pygame.init()
ANCHO, ALTO = 900, 500
MUNDO = 3200  # ancho total del nivel (más largo que la pantalla)
pantalla = pygame.display.set_mode((ANCHO, ALTO))
pygame.display.set_caption("Mi juego de plataformas")
reloj = pygame.time.Clock()
fuente = pygame.font.SysFont("arial", 28, bold=True)
fuente_grande = pygame.font.SysFont("arial", 56, bold=True)

# ---------- FONDO DE NOCHE ----------
# Degradado del cielo (se crea una sola vez)
cielo = pygame.Surface((ANCHO, ALTO))
for y in range(ALTO):
    k = y / ALTO
    color = (int(15 + 75 * k), int(15 + 35 * k), int(50 + 70 * k))
    pygame.draw.line(cielo, color, (0, y), (ANCHO, y))

# Estrellas en posiciones fijas
random.seed(3)
estrellas = [(random.randint(0, ANCHO), random.randint(0, 300)) for _ in range(70)]

# Castillo (silueta oscura con ventanas encendidas)
castillo = pygame.Surface((800, 320), pygame.SRCALPHA)
oscuro = (25, 20, 60)
pygame.draw.rect(castillo, oscuro, (100, 150, 600, 170))
for tx in (60, 330, 600):
    pygame.draw.rect(castillo, oscuro, (tx, 60, 140, 260))
    pygame.draw.polygon(castillo, oscuro, [(tx - 10, 60), (tx + 70, 0), (tx + 150, 60)])
    pygame.draw.rect(castillo, (255, 200, 90), (tx + 60, 110, 14, 24))
    pygame.draw.rect(castillo, (255, 200, 90), (tx + 60, 190, 14, 24))

# ---------- PERSONAJE (sprite dibujado con código) ----------
def crear_personaje(paso):
    s = pygame.Surface((36, 50), pygame.SRCALPHA)
    pygame.draw.rect(s, (70, 45, 30), (6, 0, 24, 10), border_radius=4)       # pelo
    pygame.draw.rect(s, (240, 190, 150), (8, 6, 20, 14), border_radius=4)    # cara
    pygame.draw.rect(s, (255, 255, 255), (20, 10, 4, 4))                     # ojo
    pygame.draw.rect(s, (210, 40, 40), (4, 20, 28, 18), border_radius=5)     # sudadera roja
    pygame.draw.rect(s, (30, 30, 50), (8 + paso, 38, 9, 9))                  # pierna 1
    pygame.draw.rect(s, (30, 30, 50), (19 - paso, 38, 9, 9))                 # pierna 2
    pygame.draw.rect(s, (235, 235, 235), (7 + paso, 46, 11, 4))              # zapato 1
    pygame.draw.rect(s, (235, 235, 235), (18 - paso, 46, 11, 4))             # zapato 2
    return s

frames_personaje = {"quieto": crear_personaje(0), "a": crear_personaje(-3), "b": crear_personaje(3)}

# ---------- MURCIÉLAGO ----------
def dibujar_murcielago(cx, cy, t):
    ala = int(math.sin(t * 0.3) * 10)  # aleteo
    pygame.draw.polygon(pantalla, (110, 50, 150), [(cx - 4, cy), (cx - 28, cy - 8 - ala), (cx - 18, cy + 8)])
    pygame.draw.polygon(pantalla, (110, 50, 150), [(cx + 4, cy), (cx + 28, cy - 8 - ala), (cx + 18, cy + 8)])
    pygame.draw.circle(pantalla, (80, 30, 110), (cx, cy), 10)                # cuerpo
    pygame.draw.circle(pantalla, (255, 230, 0), (cx - 4, cy - 2), 2)         # ojos
    pygame.draw.circle(pantalla, (255, 230, 0), (cx + 4, cy - 2), 2)

# ---------- NIVEL (coordenadas del mundo) ----------
plataformas = [
    pygame.Rect(0, 450, 700, 50), pygame.Rect(850, 450, 600, 50),
    pygame.Rect(1600, 450, 500, 50), pygame.Rect(2250, 450, 950, 50),
    pygame.Rect(300, 340, 120, 20), pygame.Rect(950, 340, 140, 20),
    pygame.Rect(1150, 260, 140, 20), pygame.Rect(1700, 330, 140, 20),
    pygame.Rect(1900, 250, 120, 20), pygame.Rect(2400, 340, 140, 20),
    pygame.Rect(2650, 260, 140, 20),
]
pinchos = [pygame.Rect(500, 430, 60, 20), pygame.Rect(1000, 430, 60, 20),
           pygame.Rect(1250, 430, 60, 20), pygame.Rect(1800, 430, 60, 20),
           pygame.Rect(2500, 430, 60, 20), pygame.Rect(2800, 430, 60, 20)]
bandera = pygame.Rect(3100, 360, 10, 90)  # meta al final del nivel

def nuevo_nivel():
    """Devuelve monedas y murciélagos (se vuelve a llamar al reiniciar)."""
    monedas = [pygame.Rect(x, y, 20, 20) for x, y in
               [(350, 300), (700, 400), (990, 300), (1200, 220), (1500, 400),
                (1750, 290), (1940, 210), (2440, 300), (2700, 220), (2950, 400)]]
    # cada murciélago: [x centro, y base, rango horizontal, fase]
    murcielagos = [[800, 300, 120, 0.0], [1400, 250, 150, 1.5],
                   [2100, 280, 140, 3.0], [2600, 200, 120, 4.5]]
    return monedas, murcielagos

# ---------- ESTADO DEL JUEGO ----------
INICIO = (60, 300)
jugador = pygame.Rect(INICIO[0], INICIO[1], 36, 50)
vel_y = 0
en_suelo = False
mirando_derecha = True
vidas, puntos = 3, 0
inmune = 0       # frames de invulnerabilidad tras un golpe
ganado = False
t = 0            # contador de frames (para animaciones)
monedas, murcielagos = nuevo_nivel()

corriendo = True
while corriendo:
    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            corriendo = False

    teclas = pygame.key.get_pressed()
    t += 1
    herido = False

    if not ganado:
        # --- Movimiento ---
        mov = 0
        if teclas[pygame.K_LEFT] or teclas[pygame.K_a]:
            mov = -5
            mirando_derecha = False
        if teclas[pygame.K_RIGHT] or teclas[pygame.K_d]:
            mov = 5
            mirando_derecha = True
        jugador.x += mov
        jugador.x = max(0, min(MUNDO - jugador.width, jugador.x))

        # --- Salto ---
        if (teclas[pygame.K_SPACE] or teclas[pygame.K_UP] or teclas[pygame.K_w]) and en_suelo:
            vel_y = -14
            en_suelo = False

        # --- Gravedad y colisión con plataformas ---
        vel_y += 0.7
        jugador.y += vel_y
        en_suelo = False
        for p in plataformas:
            if jugador.colliderect(p) and vel_y >= 0 and jugador.bottom - vel_y <= p.top + 10:
                jugador.bottom = p.top
                vel_y = 0
                en_suelo = True

        # --- Monedas ---
        for m in monedas[:]:
            if jugador.colliderect(m):
                monedas.remove(m)
                puntos += 100

        # --- Murciélagos: se mueven en onda; si les caes encima, mueren ---
        for b in murcielagos[:]:
            bx = b[0] + math.sin(t * 0.02 + b[3]) * b[2]
            by = b[1] + math.sin(t * 0.05 + b[3]) * 30
            caja = pygame.Rect(bx - 20, by - 12, 40, 24)
            if jugador.colliderect(caja):
                if vel_y > 0 and jugador.bottom - vel_y <= caja.top + 12:
                    murcielagos.remove(b)   # pisotón
                    vel_y = -10
                    puntos += 200
                elif inmune == 0:
                    herido = True

        # --- Pinchos y vacío ---
        if inmune == 0 and any(jugador.colliderect(s) for s in pinchos):
            herido = True
        if jugador.top > ALTO + 100:
            herido = True
            inmune = 0  # caer al vacío siempre cuesta una vida

        if herido:
            vidas -= 1
            inmune = 90
            if jugador.top > ALTO or True:
                jugador.topleft = INICIO if jugador.top > ALTO else jugador.topleft
            vel_y = -8 if jugador.top <= ALTO else 0
        if inmune > 0:
            inmune -= 1

        # --- Game over y meta ---
        if vidas <= 0:
            vidas, puntos = 3, 0
            monedas, murcielagos = nuevo_nivel()
            jugador.topleft = INICIO
            vel_y = 0
        if jugador.colliderect(bandera):
            ganado = True
    else:
        if teclas[pygame.K_r]:  # reiniciar tras ganar
            ganado = False
            vidas, puntos = 3, 0
            monedas, murcielagos = nuevo_nivel()
            jugador.topleft = INICIO
            vel_y = 0

    # --- Cámara: sigue al jugador sin salirse del nivel ---
    camara = max(0, min(MUNDO - ANCHO, jugador.centerx - ANCHO // 2))

    # ---------- DIBUJAR ----------
    pantalla.blit(cielo, (0, 0))
    for ex, ey in estrellas:
        pygame.draw.circle(pantalla, (255, 255, 230), (ex, ey), 1)
    pygame.draw.circle(pantalla, (240, 235, 200), (720, 110), 50)   # luna
    pygame.draw.circle(pantalla, (220, 215, 180), (705, 100), 12)   # cráter
    for cx in (300, 1100, 1900):                                    # castillos (parallax lento)
        pantalla.blit(castillo, (cx - camara * 0.3, 130))

    for p in plataformas:
        r = p.move(-camara, 0)
        pygame.draw.rect(pantalla, (70, 50, 60), r)                              # tierra
        pygame.draw.rect(pantalla, (80, 180, 70), (r.x, r.y, r.width, 10))       # pasto
    for s in pinchos:
        r = s.move(-camara, 0)
        for i in range(0, r.width, 15):                                          # triángulos
            pygame.draw.polygon(pantalla, (210, 210, 220),
                                [(r.x + i, r.bottom), (r.x + i + 7, r.top), (r.x + i + 15, r.bottom)])
    for m in monedas:
        pygame.draw.circle(pantalla, (255, 210, 0), m.move(-camara, 0).center, 10)
        pygame.draw.circle(pantalla, (200, 150, 0), m.move(-camara, 0).center, 10, 2)
    for b in murcielagos:
        bx = b[0] + math.sin(t * 0.02 + b[3]) * b[2]
        by = b[1] + math.sin(t * 0.05 + b[3]) * 30
        dibujar_murcielago(int(bx - camara), int(by), t)

    # Bandera de meta
    br = bandera.move(-camara, 0)
    pygame.draw.rect(pantalla, (230, 230, 230), br)
    pygame.draw.polygon(pantalla, (255, 90, 90), [(br.right, br.top), (br.right + 45, br.top + 15), (br.right, br.top + 30)])

    # Personaje (parpadea cuando está inmune)
    if not (inmune > 0 and (t // 4) % 2 == 0):
        if not en_suelo or not (teclas[pygame.K_LEFT] or teclas[pygame.K_RIGHT] or teclas[pygame.K_a] or teclas[pygame.K_d]):
            sprite = frames_personaje["quieto"]
        else:
            sprite = frames_personaje["a" if (t // 8) % 2 == 0 else "b"]
        if not mirando_derecha:
            sprite = pygame.transform.flip(sprite, True, False)
        pantalla.blit(sprite, (jugador.x - camara, jugador.y))

    # Marcador
    pantalla.blit(fuente.render("♥️ " * vidas, True, (255, 90, 110)), (15, 10))
    pantalla.blit(fuente.render(f"Puntos: {puntos}", True, (255, 255, 255)), (ANCHO - 200, 12))

    if ganado:
        txt = fuente_grande.render("¡GANASTE!", True, (255, 220, 60))
        pantalla.blit(txt, (ANCHO // 2 - txt.get_width() // 2, 180))
        sub = fuente.render("Presiona R para jugar de nuevo", True, (255, 255, 255))
        pantalla.blit(sub, (ANCHO // 2 - sub.get_width() // 2, 260))

    pygame.display.flip()
    reloj.tick(60)

pygame.quit()