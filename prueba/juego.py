import pygame

pygame.init()
ANCHO, ALTO = 900, 500
pantalla = pygame.display.set_mode((ANCHO, ALTO))
pygame.display.set_caption("Mi juego de plataformas")
reloj = pygame.time.Clock()
fuente = pygame.font.SysFont("arial", 28, bold=True)

# Jugador: un rectángulo (luego lo cambias por una imagen)
jugador = pygame.Rect(60, 300, 36, 50)
vel_y = 0
en_suelo = False
vidas = 3
puntos = 0
INICIO = (60, 300)  # donde reaparece al perder una vida

# Plataformas (x, y, ancho, alto)
plataformas = [
    pygame.Rect(0, 450, 350, 50),
    pygame.Rect(450, 450, 450, 50),
    pygame.Rect(300, 340, 120, 20),
    pygame.Rect(600, 330, 140, 20),
]

# Monedas y pinchos
monedas = [pygame.Rect(340, 300, 20, 20), pygame.Rect(650, 290, 20, 20),
           pygame.Rect(780, 410, 20, 20)]
pinchos = [pygame.Rect(250, 430, 60, 20), pygame.Rect(520, 430, 60, 20)]

corriendo = True
while corriendo:
    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            corriendo = False

    # Movimiento horizontal con flechas o A/D
    teclas = pygame.key.get_pressed()
    if teclas[pygame.K_LEFT] or teclas[pygame.K_a]:
        jugador.x -= 5
    if teclas[pygame.K_RIGHT] or teclas[pygame.K_d]:
        jugador.x += 5
    jugador.x = max(0, min(ANCHO - jugador.width, jugador.x))  # no salir de pantalla

    # Salto con ESPACIO o flecha arriba
    if (teclas[pygame.K_SPACE] or teclas[pygame.K_UP]) and en_suelo:
        vel_y = -14
        en_suelo = False

    # Gravedad
    vel_y += 0.7
    jugador.y += vel_y

    # Colisión con plataformas (solo cuando cae encima de una)
    en_suelo = False
    for p in plataformas:
        if jugador.colliderect(p) and vel_y >= 0 and jugador.bottom - vel_y <= p.top + 10:
            jugador.bottom = p.top
            vel_y = 0
            en_suelo = True

    # Recoger monedas
    for m in monedas[:]:
        if jugador.colliderect(m):
            monedas.remove(m)
            puntos += 100

    # Pinchos o caída al vacío = perder una vida y reaparecer
    if any(jugador.colliderect(s) for s in pinchos) or jugador.top > ALTO:
        vidas -= 1
        jugador.topleft = INICIO
        vel_y = 0
        if vidas <= 0:  # reiniciar el juego
            vidas, puntos = 3, 0
            monedas = [pygame.Rect(340, 300, 20, 20), pygame.Rect(650, 290, 20, 20),
                       pygame.Rect(780, 410, 20, 20)]

    # Dibujar todo
    pantalla.fill((40, 30, 90))  # cielo morado
    for p in plataformas:
        pygame.draw.rect(pantalla, (60, 160, 70), p)
    for s in pinchos:
        pygame.draw.rect(pantalla, (200, 200, 200), s)
    for m in monedas:
        pygame.draw.circle(pantalla, (255, 210, 0), m.center, 10)
    pygame.draw.rect(pantalla, (220, 50, 50), jugador)
    pantalla.blit(fuente.render(f"Vidas: {vidas}   Puntos: {puntos}", True, (255, 255, 255)), (15, 12))

    pygame.display.flip()
    reloj.tick(60)  # 60 cuadros por segundo

pygame.quit()