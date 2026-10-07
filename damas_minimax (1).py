import random

# Representación de los jugadores:
# Blancas = 1, Negras = -1
BLANCAS, NEGRAS = 1, -1

# Valores utilizados por la función de evaluación:
# Un peón vale 1 y una dama vale 2.5
VALOR_PEON, VALOR_DAMA = 1.0, 2.5

# Si pasan 40 movimientos sin captura ni coronación,
# se considera que la partida termina en tablas.
LIMITE_SIN_PROGRESO = 40

# Profundidad utilizada por Minimax.
# 1 = la IA solo analiza su movimiento y luego evalúa el tablero.
PROFUNDIDAD = 2

# Símbolos utilizados para mostrar el tablero.
# o = peón blanco, O = dama blanca
# x = peón negro, X = dama negra
SIMBOLOS = {0: "·", 1: "o", 2: "O", -1: "x", -2: "X"}


# ============================================================
# REGLAS DEL JUEGO
# ============================================================

def tablero_inicial():
    """
    Crea la posición inicial de una partida de damas.

    El tablero se representa como una matriz 8x8:
      0  = casilla vacía
      1  = peón blanco
      2  = dama blanca
     -1  = peón negro
     -2  = dama negra
    """
    T = [[0] * 8 for _ in range(8)]

    # Se recorren todas las casillas del tablero.
    for f in range(8):
        for c in range(8):

            # Solo se utilizan las casillas oscuras.
            if (f + c) % 2 == 1:

                # Las tres primeras filas contienen las negras.
                if f < 3:
                    T[f][c] = -1

                # Las tres últimas filas contienen las blancas.
                elif f > 4:
                    T[f][c] = 1

    return T


def color(p):
    """
    Determina el color de una pieza.

    Devuelve:
      0  -> casilla vacía
      1  -> pieza blanca
     -1  -> pieza negra
    """
    return 0 if p == 0 else (1 if p > 0 else -1)


def direcciones(p):
    """
    Devuelve las direcciones en las que una pieza puede moverse.

    Los peones solamente avanzan hacia adelante.
    Las damas pueden moverse en las cuatro diagonales.
    """

    # Una pieza con valor absoluto 2 es una dama.
    if abs(p) == 2:

        # La dama puede moverse en las cuatro diagonales.
        return [(-1, -1), (-1, 1), (1, -1), (1, 1)]

    # Los peones blancos avanzan hacia arriba.
    if p > 0:
        return [(-1, -1), (-1, 1)]

    # Los peones negros avanzan hacia abajo.
    return [(1, -1), (1, 1)]


def dentro(f, c):
    """Comprueba si una posición pertenece al tablero 8x8."""
    return 0 <= f < 8 and 0 <= c < 8


def corona(p, f):
    """
    Comprueba si un peón llegó a la última fila
    y debe convertirse en dama.
    """

    # Peón blanco llega a la fila 1.
    # Peón negro llega a la fila 8.
    return (p == 1 and f == 0) or (p == -1 and f == 7)


def _seguir(T, f, c, p, camino, caps, salida):
    """
    Busca capturas encadenadas.

    Se utiliza recursivamente para encontrar si una pieza
    puede realizar varias capturas durante el mismo turno.

    T       = tablero actual
    f, c    = posición actual de la pieza
    p       = pieza que se está moviendo
    camino  = posiciones por las que pasa la pieza
    caps    = piezas capturadas
    salida  = lista donde se guardan las capturas posibles
    """

    hubo = False

    # Se revisan todas las direcciones posibles.
    for df, dc in direcciones(p):

        # Posición de la pieza que podría ser capturada.
        mf, mc = f + df, c + dc

        # Posición donde aterrizaría la pieza después de capturar.
        tf, tc = f + 2 * df, c + 2 * dc

        # Para capturar:
        # 1. La posición final debe estar dentro del tablero.
        # 2. Debe haber una pieza enemiga.
        # 3. La posición después de saltar debe estar vacía.
        if dentro(tf, tc) and color(T[mf][mc]) == -color(p) and T[tf][tc] == 0:

            hubo = True

            # Se crea una copia del tablero para probar la captura.
            T2 = [fila[:] for fila in T]

            # Se elimina la pieza capturada.
            T2[mf][mc] = 0

            # Se guarda la nueva posición de la pieza.
            nuevo_camino = camino + [(tf, tc)]

            # Se guarda la pieza que fue capturada.
            nuevas_caps = caps + [(mf, mc)]

            # Si la pieza llega a la última fila, se corona.
            # En este programa la coronación termina el turno.
            if corona(p, tf):
                salida.append((nuevo_camino, nuevas_caps))

            else:
                # Se continúa buscando otra captura encadenada.
                _seguir(
                    T2, tf, tc, p,
                    nuevo_camino,
                    nuevas_caps,
                    salida
                )

    # Si no hay más capturas y ya se realizó al menos un movimiento,
    # se guarda esta secuencia como una captura legal.
    if not hubo and len(camino) > 1:
        salida.append((camino, caps))


def movimientos(estado):
    """
    Genera todos los movimientos legales del jugador actual.

    Regla importante:
    Si existe alguna captura, la captura es obligatoria.
    Si no existe ninguna captura, se permiten movimientos simples.
    """

    T, turno, _ = estado

    # Se separan capturas y movimientos simples.
    capturas = []
    simples = []

    # Se revisa cada casilla del tablero.
    for f in range(8):
        for c in range(8):

            p = T[f][c]

            # Si la pieza no pertenece al jugador que tiene el turno,
            # se ignora.
            if color(p) != turno:
                continue

            # Se crea una copia para buscar capturas.
            T2 = [fila[:] for fila in T]
            T2[f][c] = 0

            # Busca capturas simples y encadenadas.
            _seguir(
                T2, f, c, p,
                [(f, c)],
                [],
                capturas
            )

            # También se buscan movimientos normales.
            for df, dc in direcciones(p):

                nf, nc = f + df, c + dc

                # El movimiento es válido si la casilla está
                # dentro del tablero y está vacía.
                if dentro(nf, nc) and T[nf][nc] == 0:
                    simples.append(
                        ([(f, c), (nf, nc)], [])
                    )

    # Si existe al menos una captura, solamente se devuelven capturas.
    # Esto implementa la regla de captura obligatoria.
    return capturas if capturas else simples


def aplicar(estado, mov):
    """
    Aplica un movimiento y genera un nuevo estado.

    Importante para Minimax:
    NO modifica el tablero original.
    Crea una copia y realiza el movimiento sobre esa copia.

    Esto permite que la IA pueda probar movimientos
    sin alterar el tablero real de la partida.
    """

    T, turno, k = estado
    camino, caps = mov

    # Copia del tablero.
    T2 = [fila[:] for fila in T]

    # Posición inicial y final del movimiento.
    (f0, c0), (f1, c1) = camino[0], camino[-1]

    # Se obtiene la pieza que se va a mover.
    p = T2[f0][c0]

    # Se elimina de su posición original.
    T2[f0][c0] = 0

    # Se eliminan las piezas capturadas.
    for (f, c) in caps:
        T2[f][c] = 0

    # Se comprueba si la pieza llegó a la última fila.
    coronado = corona(p, f1)

    if coronado:
        # El peón se convierte en dama.
        p = 2 * color(p)

    # Se coloca la pieza en su nueva posición.
    T2[f1][c1] = p

    # Si hubo captura o coronación, se reinicia el contador.
    # Si fue un movimiento normal, aumenta en uno.
    k2 = 0 if (caps or coronado) else k + 1

    # Cambia el turno al jugador contrario.
    return (T2, -turno, k2)


# ============================================================
# MINIMAX
# ============================================================

def evaluar(T, agente):
    """
    Función de evaluación.

    Calcula qué tan buena es una posición para la IA.

    Fórmula:

        valor = material de la IA - material del rival

    Peón = 1.0
    Dama = 2.5

    Un valor positivo favorece a la IA.
    Un valor negativo favorece al rival.
    """

    total = 0.0

    # Se revisan todas las piezas del tablero.
    for fila in T:
        for p in fila:

            if p:

                # Se asigna el valor correspondiente a la pieza.
                v = VALOR_DAMA if abs(p) == 2 else VALOR_PEON

                # Si pertenece a la IA, se suma.
                # Si pertenece al rival, se resta.
                total += v if color(p) == agente else -v

    return total


def minimax(estado, prof, agente):
    """
    Algoritmo Minimax sin poda alfa-beta.

    MAX = IA:
        intenta obtener el valor más alto.

    MIN = rival:
        intenta obtener el valor más bajo para la IA.

    prof = profundidad restante del árbol.
    """

    T, turno, k = estado

    # Genera todas las jugadas posibles desde esta posición.
    movs = movimientos(estado)

    # Si no existen movimientos, el jugador que tiene el turno pierde.
    if not movs:
        return (-1000 - prof) if turno == agente else (1000 + prof)

    # Si se alcanzan 40 movimientos sin captura ni coronación,
    # se considera empate.
    if k >= LIMITE_SIN_PROGRESO:
        return 0

    # Si se llegó al límite de profundidad,
    # ya no se siguen generando movimientos.
    # Se evalúa directamente la posición actual.
    if prof == 0:
        return evaluar(T, agente)

    # Para cada movimiento:
    # 1. Se aplica sobre una copia del tablero.
    # 2. Se llama nuevamente a Minimax.
    # 3. Se reduce la profundidad en 1.
    valores = (
        minimax(
            aplicar(estado, m),
            prof - 1,
            agente
        )
        for m in movs
    )

    # Si es el turno de la IA, selecciona el valor máximo.
    # Si es el turno del rival, selecciona el valor mínimo.
    return max(valores) if turno == agente else min(valores)


def mejor_jugada(estado, prof):
    """
    Busca la mejor jugada para la IA.

    Prueba todos los movimientos legales y utiliza Minimax
    para obtener un valor para cada uno.
    """

    turno = estado[1]

    # Inicialmente se considera que el mejor valor es infinito negativo.
    mejor_val = float("-inf")
    mejores = []

    # Se prueban todos los movimientos posibles.
    for m in movimientos(estado):

        # Se aplica el movimiento y se analiza el resultado
        # utilizando Minimax.
        v = minimax(
            aplicar(estado, m),
            prof - 1,
            turno
        )

        # Si encontramos un valor mejor, se guarda.
        if v > mejor_val:
            mejor_val, mejores = v, [m]

        # Si hay varias jugadas con el mismo valor,
        # se guardan todas.
        elif v == mejor_val:
            mejores.append(m)

    # Si existen varias jugadas iguales,
    # se selecciona una aleatoriamente.
    return random.choice(mejores), mejor_val


# ============================================================
# INTERFAZ DEL JUEGO
# ============================================================

def mostrar(T):
    """
    Muestra el tablero en la consola.
    """

    print("\n    " + " ".join(str(c + 1) for c in range(8)))

    for f in range(8):

        # Las casillas claras se muestran vacías.
        fila = [
            " " if (f + c) % 2 == 0 else SIMBOLOS[T[f][c]]
            for c in range(8)
        ]

        print(f" {f + 1} | " + " ".join(fila))

    print("(o/O = blancas, x/X = negras; mayúscula = dama)")


def texto_mov(mov):
    """
    Convierte un movimiento a texto para mostrarlo
    en la consola.
    """

    camino, caps = mov

    s = "->".join(
        f"({f + 1},{c + 1})"
        for f, c in camino
    )

    # Si hubo capturas, se indica cuántas.
    return s + (
        f"  [captura {len(caps)}]"
        if caps else ""
    )


def main():
    """
    Función principal del juego.

    Controla:
      - inicio de la partida
      - turnos
      - movimientos del jugador
      - movimientos de la IA
      - detección de tablas
      - finalización de la partida
    """

    print("=== Damas con Minimax (sin poda) ===")

    # El usuario debe elegir jugar con blancas o negras.
    op = ""

    while op not in ("b", "n"):
        op = input(
            "Tu color (b = blancas, n = negras): "
        ).strip().lower()

    # Se convierte la opción del usuario al valor correspondiente.
    humano = BLANCAS if op == "b" else NEGRAS

    # Se utiliza la profundidad definida al principio.
    prof = PROFUNDIDAD

    # Estado inicial:
    # tablero inicial + turno de blancas + contador k = 0
    estado = (
        tablero_inicial(),
        BLANCAS,
        0
    )

    # Diccionario para controlar la repetición de posiciones.
    vistos = {}

    while True:

        T, turno, k = estado

        # Muestra el tablero actual.
        mostrar(T)

        nombre = "Blancas" if turno == BLANCAS else "Negras"

        # Se crea una clave con:
        # tablero + jugador que tiene el turno.
        clave = (
            tuple(map(tuple, T)),
            turno
        )

        # Cuenta cuántas veces apareció esta posición.
        vistos[clave] = vistos.get(clave, 0) + 1

        # Obtiene los movimientos legales.
        movs = movimientos(estado)

        # Si no hay movimientos, el jugador pierde.
        if not movs:
            ganan = "Negras" if turno == BLANCAS else "Blancas"
            print(
                f"\n{nombre} no tienen movimientos. "
                f"¡Ganan {ganan}!"
            )
            break

        # Tablas por 40 movimientos sin progreso.
        if k >= LIMITE_SIN_PROGRESO:
            print(
                "\nTablas: 40 jugadas sin captura "
                "ni coronación."
            )
            break

        # Tablas si la misma posición aparece tres veces.
        if vistos[clave] >= 3:
            print(
                "\nTablas: la posición se repitió 3 veces."
            )
            break

        # ----------------------------------------------------
        # TURNO DEL JUGADOR HUMANO
        # ----------------------------------------------------
        if turno == humano:

            print(
                f"\nTurno de {nombre}. "
                "Movimientos legales:"
            )

            # Muestra todos los movimientos disponibles.
            for i, m in enumerate(movs, 1):
                print(
                    f"  {i}. {texto_mov(m)}"
                )

            # El usuario selecciona uno de los movimientos.
            while True:
                try:
                    mov = movs[
                        int(input("Elige el número: ")) - 1
                    ]
                    break

                except (ValueError, IndexError):
                    print("Opción inválida.")

        # ----------------------------------------------------
        # TURNO DE LA IA
        # ----------------------------------------------------
        else:

            # Minimax analiza las jugadas posibles
            # y selecciona la que tenga el mejor valor.
            mov, val = mejor_jugada(
                estado,
                prof
            )

            print(
                f"\nIA ({nombre}) juega: "
                f"{texto_mov(mov)}   "
                f"(valor minimax = {val})"
            )

        # Se aplica el movimiento elegido y cambia el turno.
        estado = aplicar(estado, mov)


# Punto de entrada del programa.
# Ejecuta main() solamente cuando se ejecuta este archivo directamente.
if __name__ == "__main__":
    main()