"""Genera una escena ilustrada (SVG) del pasajero según sus datos y la predicción.

El personaje se dibuja en coordenadas locales: los pies en y=0 y la cabeza
centrada en (0, -124). Cada función devuelve un fragmento SVG como texto.
"""

PIEL = "#F6CBA5"
CONTORNO = "#3A2E2A"
MEJILLAS = "#F4A6A0"

# Colores de ropa por clase y sexo
ROPA = {
    (1, "male"): {"saco": "#22252E", "pantalon": "#22252E"},
    (2, "male"): {"saco": "#8D6E63", "pantalon": "#5D4037"},
    (3, "male"): {"saco": "#B9A88A", "pantalon": "#6D6A5E"},
    (1, "female"): {"vestido": "#7B3FA0"},
    (2, "female"): {"vestido": "#2A9D8F"},
    (3, "female"): {"vestido": "#7C8C6E"},
}
COLORES_FAMILIA = ["#90A4AE", "#B0BEC5", "#A1887F", "#9FA8DA"]
PUERTOS = {"S": "Southampton", "C": "Cherbourg", "Q": "Queenstown"}

ESTILOS = """
<style>
  .tt-ola { animation: tt-ola 4s ease-in-out infinite alternate; }
  .tt-bote { animation: tt-balanceo 3.5s ease-in-out infinite alternate;
             transform-box: fill-box; transform-origin: center bottom; }
  .tt-saludo { animation: tt-saludo 0.9s ease-in-out infinite alternate;
               transform-box: view-box; }
  .tt-flota { animation: tt-flota 2.4s ease-in-out infinite alternate; }
  .tt-sol { animation: tt-giro 30s linear infinite;
            transform-box: fill-box; transform-origin: center; }
  @keyframes tt-ola { from { transform: translateX(-14px); } to { transform: translateX(14px); } }
  @keyframes tt-balanceo { from { transform: rotate(-2.5deg); } to { transform: rotate(2.5deg); } }
  @keyframes tt-saludo { from { transform: rotate(-12deg); } to { transform: rotate(14deg); } }
  @keyframes tt-flota { from { transform: translateY(-3px); } to { transform: translateY(3px); } }
  @keyframes tt-giro { to { transform: rotate(360deg); } }
</style>
"""


def grupo_edad(edad):
    if edad <= 12:
        return "nino"
    if edad >= 60:
        return "mayor"
    return "adulto"


# ---------------------------------------------------------------- Partes del personaje
def _pelo_trasero(sexo, grupo, color):
    """Cabello largo detrás de la cabeza (mujeres)."""
    if sexo != "female" or grupo == "mayor":
        return ""
    return (f'<path d="M-25,-124 Q-28,-153 0,-151 Q28,-153 25,-124 L27,-92 '
            f'Q0,-86 -27,-92 Z" fill="{color}"/>')


def _pelo_frontal(sexo, grupo, color):
    if sexo == "female":
        if grupo == "mayor":  # moño canoso
            return (f'<circle cx="0" cy="-150" r="11" fill="{color}"/>'
                    f'<path d="M-23,-124 Q-22,-150 0,-148 Q22,-150 23,-124 Q12,-138 0,-136 '
                    f'Q-12,-138 -23,-124 Z" fill="{color}"/>')
        lazo = ('<path d="M14,-146 l10,-6 l0,12 Z M14,-146 l-8,-8 l-2,12 Z" fill="#E57373"/>'
                if grupo == "nino" else "")
        return (f'<path d="M-23,-126 Q-19,-151 0,-149 Q19,-151 23,-126 Q11,-139 0,-135 '
                f'Q-11,-141 -23,-126 Z" fill="{color}"/>{lazo}')
    if grupo == "mayor":  # entradas y bigote canoso
        return (f'<ellipse cx="-21" cy="-128" rx="5" ry="9" fill="{color}"/>'
                f'<ellipse cx="21" cy="-128" rx="5" ry="9" fill="{color}"/>'
                f'<path d="M-9,-114 Q0,-120 9,-114 Q0,-111 -9,-114 Z" fill="{color}"/>')
    return (f'<path d="M-22,-127 Q-23,-151 0,-150 Q23,-151 22,-127 Q15,-140 0,-139 '
            f'Q-15,-140 -22,-127 Z" fill="{color}"/>')


def _cara(sobrevive, grupo):
    ojos = (f'<circle cx="-8" cy="-126" r="2.8" fill="{CONTORNO}"/>'
            f'<circle cx="8" cy="-126" r="2.8" fill="{CONTORNO}"/>')
    mejillas = (f'<ellipse cx="-14" cy="-117" rx="4.5" ry="3" fill="{MEJILLAS}" opacity="0.7"/>'
                f'<ellipse cx="14" cy="-117" rx="4.5" ry="3" fill="{MEJILLAS}" opacity="0.7"/>')
    if sobrevive:
        boca = (f'<path d="M-8,-115 Q0,-106 8,-115" fill="none" stroke="{CONTORNO}" '
                f'stroke-width="2.5" stroke-linecap="round"/>')
        cejas = ""
    else:
        boca = '<ellipse cx="0" cy="-111" rx="3.5" ry="4.5" fill="#8C3B3B"/>'
        cejas = (f'<path d="M-13,-135 L-4,-132 M13,-135 L4,-132" stroke="{CONTORNO}" '
                 f'stroke-width="2" stroke-linecap="round"/>')
    lentes = ""
    if grupo == "mayor":
        lentes = (f'<g fill="none" stroke="{CONTORNO}" stroke-width="1.6">'
                  f'<circle cx="-8" cy="-126" r="6.5"/><circle cx="8" cy="-126" r="6.5"/>'
                  f'<path d="M-1.5,-126 L1.5,-126"/></g>')
    return ojos + mejillas + boca + cejas + lentes


def _sombrero(sexo, clase):
    if sexo == "male":
        if clase == 1:  # sombrero de copa
            return ('<rect x="-15" y="-186" width="30" height="38" rx="3" fill="#1B1B1F"/>'
                    '<rect x="-15" y="-160" width="30" height="6" fill="#A31F2C"/>'
                    '<rect x="-27" y="-152" width="54" height="7" rx="3.5" fill="#1B1B1F"/>')
        if clase == 2:  # bombín
            return ('<path d="M-18,-146 Q-19,-174 0,-174 Q19,-174 18,-146 Z" fill="#4E342E"/>'
                    '<rect x="-26" y="-149" width="52" height="6" rx="3" fill="#4E342E"/>')
        return ('<path d="M-23,-139 Q-21,-161 2,-159 Q23,-157 23,-139 Z" fill="#707070"/>'  # gorra
                '<path d="M6,-141 L36,-139 Q32,-132 8,-135 Z" fill="#5A5A5A"/>')
    if clase == 1:  # sombrero ancho con pluma
        return ('<path d="M12,-160 Q30,-196 42,-174 Q28,-172 16,-156 Z" fill="#F8BBD0"/>'
                '<ellipse cx="0" cy="-147" rx="36" ry="7" fill="#5E2B7E"/>'
                '<path d="M-17,-147 Q-15,-168 0,-168 Q15,-168 17,-147 Z" fill="#5E2B7E"/>'
                '<circle cx="-12" cy="-151" r="4.5" fill="#F48FB1"/>')
    if clase == 2:  # capota
        return ('<path d="M-27,-122 Q-30,-162 0,-162 Q30,-162 27,-122 Q21,-148 0,-148 '
                'Q-21,-148 -27,-122 Z" fill="#E9C46A"/>'
                '<path d="M-24,-122 Q0,-74 24,-122" fill="none" stroke="#E76F51" stroke-width="2.5"/>')
    return ('<path d="M-26,-120 Q-29,-158 0,-158 Q29,-158 26,-120 Q17,-141 0,-141 '  # pañuelo
            'Q-17,-141 -26,-120 Z" fill="#C0504D"/>'
            '<circle cx="-10" cy="-150" r="1.8" fill="#FFF"/><circle cx="6" cy="-153" r="1.8" fill="#FFF"/>'
            '<circle cx="15" cy="-144" r="1.8" fill="#FFF"/>'
            '<path d="M24,-124 l9,6 l-9,4 Z" fill="#C0504D"/>')


def _cuerpo(sexo, clase):
    if sexo == "male":
        colores = ROPA[(clase, "male")]
        piernas = (f'<rect x="-14" y="-52" width="11" height="48" rx="4" fill="{colores["pantalon"]}"/>'
                   f'<rect x="3" y="-52" width="11" height="48" rx="4" fill="{colores["pantalon"]}"/>'
                   '<ellipse cx="-9" cy="-3" rx="9" ry="5" fill="#3B2A20"/>'
                   '<ellipse cx="9" cy="-3" rx="9" ry="5" fill="#3B2A20"/>')
        torso = f'<rect x="-24" y="-103" width="48" height="58" rx="12" fill="{colores["saco"]}"/>'
        if clase == 1:  # camisa y moño
            detalle = ('<path d="M-8,-103 L8,-103 L0,-78 Z" fill="#FFFFFF"/>'
                       '<path d="M-8,-99 L0,-95 L-8,-91 Z M8,-99 L0,-95 L8,-91 Z" fill="#C62828"/>'
                       '<circle cx="0" cy="-70" r="1.8" fill="#FFF"/><circle cx="0" cy="-60" r="1.8" fill="#FFF"/>')
        elif clase == 2:  # camisa y corbata
            detalle = ('<path d="M-7,-103 L7,-103 L0,-88 Z" fill="#F5F5F5"/>'
                       '<path d="M-3,-100 L3,-100 L4,-78 L0,-72 L-4,-78 Z" fill="#1E5F8C"/>')
        else:  # tirantes y parche
            detalle = ('<path d="M-12,-103 L-10,-46 M12,-103 L10,-46" stroke="#5D4037" stroke-width="3.5"/>'
                       '<rect x="-20" y="-74" width="10" height="10" fill="#8D9B6A"/>'
                       '<path d="M-20,-74 h10 v10 h-10 Z" fill="none" stroke="#4E4E4E" '
                       'stroke-width="1" stroke-dasharray="2 2"/>')
        return piernas + torso + detalle

    vestido = ROPA[(clase, "female")]["vestido"]
    piernas = (f'<rect x="-11" y="-30" width="7" height="27" rx="3" fill="{PIEL}"/>'
               f'<rect x="4" y="-30" width="7" height="27" rx="3" fill="{PIEL}"/>'
               '<ellipse cx="-8" cy="-3" rx="8" ry="4.5" fill="#5D3A2E"/>'
               '<ellipse cx="8" cy="-3" rx="8" ry="4.5" fill="#5D3A2E"/>')
    falda = f'<path d="M-20,-103 Q0,-109 20,-103 L37,-24 Q0,-15 -37,-24 Z" fill="{vestido}"/>'
    if clase == 1:  # collar y cinturón
        detalle = ('<path d="M-12,-100 Q0,-90 12,-100" fill="none" stroke="#FFF8E1" '
                   'stroke-width="2.5" stroke-dasharray="0.1 4.5" stroke-linecap="round"/>'
                   '<rect x="-22" y="-74" width="44" height="5" fill="#F2C94C"/>')
    elif clase == 2:  # cuello blanco
        detalle = '<path d="M-12,-104 L0,-94 L12,-104 Z" fill="#FFFFFF"/>'
    else:  # delantal y parche
        detalle = ('<path d="M-14,-80 L14,-80 L19,-30 L-19,-30 Z" fill="#F3EFE4"/>'
                   '<rect x="16" y="-56" width="9" height="9" fill="#B5838D" transform="rotate(12 20 -52)"/>')
    return piernas + falda + detalle


def _brazos(sexo, clase, sobrevive):
    manga = ROPA[(clase, "male")]["saco"] if sexo == "male" else ROPA[(clase, "female")]["vestido"]
    izquierdo = (f'<path d="M-21,-96 L-31,-58" stroke="{manga}" stroke-width="10" stroke-linecap="round"/>'
                 f'<circle cx="-31" cy="-56" r="5.5" fill="{PIEL}"/>')
    if sobrevive:  # saluda con la mano derecha
        derecho = (f'<g class="tt-saludo" style="transform-origin: 21px -96px">'
                   f'<path d="M21,-96 L40,-136" stroke="{manga}" stroke-width="10" stroke-linecap="round"/>'
                   f'<circle cx="41" cy="-139" r="6" fill="{PIEL}"/></g>')
        return izquierdo + derecho
    # brazos arriba pidiendo ayuda
    return (f'<path d="M-21,-96 L-40,-134" stroke="{manga}" stroke-width="10" stroke-linecap="round"/>'
            f'<circle cx="-41" cy="-137" r="5.5" fill="{PIEL}"/>'
            f'<path d="M21,-96 L40,-134" stroke="{manga}" stroke-width="10" stroke-linecap="round"/>'
            f'<circle cx="41" cy="-137" r="5.5" fill="{PIEL}"/>')


def personaje(pasajero, sobrevive, x, y, escala=1.0):
    """Personaje principal ubicado con los pies en (x, y)."""
    sexo, clase = pasajero["Sex"], int(pasajero["Pclass"])
    grupo = grupo_edad(pasajero["Age"])
    escala *= 0.66 if grupo == "nino" else 1.0
    color_pelo = "#D9D9D9" if grupo == "mayor" else ("#6B3E26" if sexo == "female" else "#3E2723")

    baston = ""
    if grupo == "mayor" and sobrevive:
        baston = ('<path d="M-31,-56 L-35,-2 M-31,-56 Q-31,-66 -22,-64" fill="none" '
                  'stroke="#6D4C41" stroke-width="4" stroke-linecap="round"/>')

    partes = [
        _pelo_trasero(sexo, grupo, color_pelo),
        _cuerpo(sexo, clase),
        _brazos(sexo, clase, sobrevive),
        baston,
        f'<rect x="-5" y="-108" width="10" height="9" fill="{PIEL}"/>',
        f'<circle cx="0" cy="-124" r="22" fill="{PIEL}"/>',
        _cara(sobrevive, grupo),
        _pelo_frontal(sexo, grupo, color_pelo),
        _sombrero(sexo, clase),
    ]
    return f'<g transform="translate({x} {y}) scale({escala})">{"".join(partes)}</g>'


def acompanante(x, y, escala, color):
    """Figura simple (silueta) para hermanos, cónyuges, padres o hijos."""
    return (f'<g transform="translate({x} {y}) scale({escala})">'
            f'<rect x="-20" y="-100" width="40" height="96" rx="18" fill="{color}"/>'
            f'<circle cx="0" cy="-122" r="19" fill="{PIEL}"/>'
            f'<circle cx="-6" cy="-124" r="2.4" fill="{CONTORNO}"/><circle cx="6" cy="-124" r="2.4" fill="{CONTORNO}"/>'
            f'<path d="M-6,-114 Q0,-109 6,-114" fill="none" stroke="{CONTORNO}" stroke-width="2"/></g>')


def _familia(pasajero, x_centro, y, escala_base):
    """Acompañantes alrededor del personaje (máximo 4 visibles)."""
    tipos = ["adulto"] * int(pasajero["SibSp"]) + ["nino"] * int(pasajero["Parch"])
    visibles, extra = tipos[:4], len(tipos) - 4
    desplazamientos = [-72, 72, -112, 112]
    figuras = "".join(
        acompanante(x_centro + desplazamientos[i], y,
                    escala_base * (0.72 if tipo == "adulto" else 0.5),
                    COLORES_FAMILIA[i % len(COLORES_FAMILIA)])
        for i, tipo in enumerate(visibles)
    )
    if extra > 0:
        figuras += (f'<text x="{x_centro + 150}" y="{y - 40}" font-size="18" font-weight="700" '
                    f'fill="#FFFFFF" stroke="#1F3A5F" stroke-width="4" paint-order="stroke" '
                    f'text-anchor="middle" font-family="sans-serif">+{extra}</text>')
    return figuras


# ---------------------------------------------------------------- Elementos de la escena
def _banderin(puerto):
    nombre = PUERTOS.get(puerto, puerto)
    return ('<g transform="translate(18 18)">'
            '<rect x="0" y="0" width="3" height="46" fill="#5D4037"/>'
            '<path d="M3,2 L120,2 L108,16 L120,30 L3,30 Z" fill="#FFFFFF" opacity="0.92"/>'
            f'<text x="10" y="21" font-size="12" font-weight="700" fill="#1F3A5F" '
            f'font-family="sans-serif">⚓ {nombre}</text></g>')


def _boleto(clase, tarifa):
    return ('<g transform="translate(296 248) rotate(-6)">'
            '<rect x="0" y="0" width="92" height="40" rx="6" fill="#FFF3D6" stroke="#C9A227" stroke-width="2"/>'
            '<path d="M66,4 L66,36" stroke="#C9A227" stroke-dasharray="3 3"/>'
            f'<text x="8" y="17" font-size="11" font-weight="700" fill="#7A5C00" font-family="sans-serif">{clase}.ª CLASE</text>'
            f'<text x="8" y="32" font-size="12" fill="#7A5C00" font-family="sans-serif">£{tarifa:.0f}</text>'
            '<text x="79" y="25" font-size="13" text-anchor="middle" font-family="sans-serif">🎫</text></g>')


def _insignia(probabilidad, sobrevive):
    color = "#2E7D32" if sobrevive else "#C62828"
    return ('<g transform="translate(298 14)">'
            f'<rect x="0" y="0" width="88" height="50" rx="12" fill="#FFFFFF" opacity="0.95" stroke="{color}" stroke-width="2.5"/>'
            f'<text x="44" y="27" font-size="21" font-weight="800" fill="{color}" text-anchor="middle" '
            f'font-family="sans-serif">{probabilidad:.0%}</text>'
            '<text x="44" y="42" font-size="9.5" fill="#555" text-anchor="middle" '
            'font-family="sans-serif">de sobrevivir</text></g>')


def _olas(y, color, opacidad):
    crestas = " ".join(f"q 12,-8 24,0 q 12,8 24,0" for _ in range(11))
    return (f'<g class="tt-ola"><path d="M-30,{y} {crestas} L540,330 L-30,330 Z" '
            f'fill="{color}" opacity="{opacidad}"/></g>')


def _escena_sobrevive(pasajero, probabilidad):
    cielo = ('<defs><linearGradient id="tt-cielo-dia" x1="0" y1="0" x2="0" y2="1">'
             '<stop offset="0" stop-color="#7EC8F2"/><stop offset="1" stop-color="#DDF3FF"/></linearGradient></defs>'
             '<rect width="400" height="300" fill="url(#tt-cielo-dia)"/>')
    sol = ('<g class="tt-sol"><circle cx="322" cy="118" r="20" fill="#FFD54F"/>'
           + "".join(f'<rect x="320" y="85" width="4" height="9" rx="2" fill="#FFD54F" '
                     f'transform="rotate({a} 322 118)"/>' for a in range(0, 360, 45))
           + '</g>')
    nubes = ('<g fill="#FFFFFF" opacity="0.9"><ellipse cx="80" cy="96" rx="26" ry="10"/>'
             '<ellipse cx="98" cy="90" rx="18" ry="10"/><ellipse cx="268" cy="84" rx="20" ry="7"/></g>')
    barco_lejano = ('<g opacity="0.45" transform="translate(40 196) rotate(-8)">'
                    '<path d="M0,0 L70,0 L62,10 L6,10 Z" fill="#37474F"/>'
                    '<rect x="20" y="-12" width="7" height="12" fill="#37474F"/>'
                    '<rect x="36" y="-12" width="7" height="12" fill="#37474F"/></g>')
    mar = _olas(208, "#4FA3E0", 1) + _olas(222, "#2F80C8", 0.9)
    bote_casco = ('<path d="M72,214 L328,214 L304,252 Q200,266 96,252 Z" fill="#E8590C"/>'
                  '<path d="M80,224 L320,224" stroke="#FFFFFF" stroke-width="5"/>'
                  '<path d="M72,214 L328,214" stroke="#9C3D08" stroke-width="5" stroke-linecap="round"/>')
    bote = (f'<g class="tt-bote">{_familia(pasajero, 200, 236, 1.0)}'
            f'{personaje(pasajero, True, 200, 236)}{bote_casco}</g>')
    return cielo + sol + nubes + barco_lejano + mar + bote + _olas(262, "#1C6BB0", 0.95)


def _escena_no_sobrevive(pasajero, probabilidad):
    cielo = ('<defs><linearGradient id="tt-cielo-noche" x1="0" y1="0" x2="0" y2="1">'
             '<stop offset="0" stop-color="#141B33"/><stop offset="1" stop-color="#3E4C7A"/></linearGradient></defs>'
             '<rect width="400" height="300" fill="url(#tt-cielo-noche)"/>')
    estrellas = "".join(f'<circle cx="{x}" cy="{y}" r="1.4" fill="#FFFFFF" opacity="0.8"/>'
                        for x, y in [(30, 80), (70, 40), (150, 30), (190, 70), (250, 40), (120, 95), (230, 105)])
    luna = '<circle cx="168" cy="52" r="16" fill="#F5F3CE"/><circle cx="176" cy="46" r="15" fill="#1B2440"/>'
    iceberg = ('<path d="M8,214 L34,150 L52,172 L70,132 L102,214 Z" fill="#E3F2FD"/>'
               '<path d="M70,132 L102,214 L80,214 L66,160 Z" fill="#B3D4F0"/>')
    barco = ('<g transform="translate(250 186) rotate(-16)">'
             '<rect x="18" y="-58" width="16" height="34" fill="#E0A100"/><rect x="18" y="-58" width="16" height="7" fill="#212121"/>'
             '<rect x="52" y="-58" width="16" height="34" fill="#E0A100"/><rect x="52" y="-58" width="16" height="7" fill="#212121"/>'
             '<rect x="6" y="-26" width="118" height="12" fill="#F5F5F5"/>'
             '<path d="M-14,-14 L160,-14 L148,26 L0,26 Z" fill="#1E1E24"/>'
             '<path d="M-14,-14 L160,-14 L158,-8 L-12,-8 Z" fill="#B71C1C"/>'
             + "".join(f'<circle cx="{x}" cy="2" r="2.6" fill="#FFE082"/>' for x in range(14, 150, 16))
             + '</g>')
    # A menor probabilidad, el agua sube: del cuello (0 %) a la cintura (≥ 50 %), según la altura del personaje
    escala = 0.66 if grupo_edad(pasajero["Age"]) == "nino" else 1.0
    nivel_agua = 292 + (-104 + min(probabilidad, 0.5) / 0.5 * 49) * escala
    agua_fondo = _olas(214, "#22406E", 1)
    figuras = f'{_familia(pasajero, 200, 292, 1.0)}{personaje(pasajero, False, 200, 292)}'
    salvavidas = (f'<g class="tt-flota"><ellipse cx="200" cy="{nivel_agua + 4}" rx="38" ry="10" fill="none" '
                  f'stroke="#FFFFFF" stroke-width="9"/>'
                  f'<ellipse cx="200" cy="{nivel_agua + 4}" rx="38" ry="10" fill="none" stroke="#E53935" '
                  f'stroke-width="9" stroke-dasharray="15 15"/></g>')
    agua_frente = _olas(nivel_agua, "#2B5797", 0.95)
    return cielo + estrellas + luna + iceberg + barco + agua_fondo + figuras + agua_frente + salvavidas


def escena(pasajero, prediccion, probabilidad):
    """Devuelve el SVG completo de la escena para el pasajero y su predicción."""
    sobrevive = prediccion == 1
    contenido = (_escena_sobrevive(pasajero, probabilidad) if sobrevive
                 else _escena_no_sobrevive(pasajero, probabilidad))
    return (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 300" '
        'width="100%" preserveAspectRatio="xMidYMid meet" role="img" '
        'aria-label="Ilustración del pasajero y del resultado de la predicción">'
        f'{ESTILOS}<rect width="400" height="300" rx="18" fill="#FFFFFF"/>'
        '<clipPath id="tt-marco"><rect width="400" height="300" rx="18"/></clipPath>'
        f'<g clip-path="url(#tt-marco)">{contenido}'
        f'{_banderin(pasajero["Embarked"])}{_boleto(int(pasajero["Pclass"]), pasajero["Fare"])}'
        f'{_insignia(probabilidad, sobrevive)}</g></svg>'
    )
