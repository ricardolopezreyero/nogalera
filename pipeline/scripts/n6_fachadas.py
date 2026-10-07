"""N6 · los 9 tipos de fachada del Modelo Nogal y la regla para repartirlos entre los lotes.
Lo usan n6_direcciones.py (fachada de cada lote en el mapa) y n6_casa.py (dibujos)."""
import unicodedata

NOMBRES = ["Cantera", "Celosía", "Marco", "Duela", "Ladrillo", "Hacienda", "Horizonte", "Lamas", "Concreto"]
SEQ = [0, 4, 7, 2, 5, 8, 1, 3, 6]          # orden a lo largo de la calle: tipos vecinos lo más distintos posible

def slug(n): return unicodedata.normalize("NFD", n).encode("ascii", "ignore").decode().lower()

def fachada_de(k, lado_norte, calle_i):
    """k: lugar del lote en su acera (0 = el más al poniente). Nunca se repite con el vecino de al lado
    ni con el de enfrente (la acera de enfrente va 4 lugares corrida), y cada calle empieza en otro punto."""
    return NOMBRES[SEQ[(k + (4 if lado_norte else 0) + 2 * calle_i) % 9]]
