import streamlit as st
import time
import random
import json
import os
from collections import Counter
from datetime import datetime, timedelta

# --- 1. CONFIGURACIÓN ---
st.set_page_config(page_title="Simulacro ICFES Pro", page_icon="🇨🇴", layout="wide")

# ==========================================
# 💾 SISTEMA DE PERSISTENCIA (CORREGIDO)
# ==========================================
DB_FILE = "db_usuarios.json"

def cargar_datos_usuario(uid):
    datos_por_defecto = {"intentos": 0, "premium": False, "fecha_inicio": None}
    
    if not os.path.exists(DB_FILE):
        return datos_por_defecto
    
    try:
        # CORRECCIÓN AQUÍ: Separamos las líneas
        with open(DB_FILE, "r") as f:
            db = json.load(f)
        
        datos = db.get(uid, datos_por_defecto)
        
        # Migración y validación
        if "fecha_inicio" not in datos: datos["fecha_inicio"] = None
        if "premium" not in datos: datos["premium"] = False
        if "intentos" not in datos: datos["intentos"] = 0
            
        if datos["premium"] and datos["fecha_inicio"]:
            try:
                ini = datetime.fromisoformat(datos["fecha_inicio"])
                if (datetime.now() - ini).days >= 30:
                    datos["premium"] = False
                    datos["fecha_inicio"] = None
                    guardar_datos_usuario(uid, datos["intentos"], False, None)
                    st.toast("⚠️ Tu suscripción ha vencido.", icon="📅")
            except:
                datos["fecha_inicio"] = None
        return datos
    except:
        return datos_por_defecto

def guardar_datos_usuario(uid, intentos, es_premium, fecha_inicio=None):
    db = {}
    # Cargar DB existente
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, "r") as f:
                db = json.load(f)
        except:
            pass
    
    fecha_g = fecha_inicio
    if es_premium and not fecha_inicio:
        fecha_g = db.get(uid, {}).get("fecha_inicio", datetime.now().isoformat())
    elif not es_premium:
        fecha_g = None

    db[uid] = {"intentos": intentos, "premium": es_premium, "fecha_inicio": fecha_g}
    
    # Guardar cambios
    with open(DB_FILE, "w") as f:
        json.dump(db, f)

if "uid" not in st.query_params:
    st.query_params["uid"] = str(random.randint(100000, 999999))

st.session_state.user_id = st.query_params["uid"]
datos_guardados = cargar_datos_usuario(st.session_state.user_id)

# --- 2. VARIABLES DE SESIÓN ---
defaults = {
    'examen_iniciado': False, 'preguntas_examen': [], 'indice': 0, 'puntaje': 0,
    'temas_fallados': [], 'respondida': False, 'historial_respuestas': [],
    'intentos_usados': datos_guardados["intentos"], 
    'es_premium': datos_guardados["premium"],
    'modo_actual': "Estándar", 'cantidad_preguntas': 10
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

CODIGO_SECRETO = "ICFES2025"
LIMITE_INTENTOS_GRATIS = 3
LINK_DE_PAGO = "https://mpago.li/1goqyK6"
banco_estandar = [
    # ---------------- MATEMÁTICAS (NIVEL EXPERTO) ----------------
    {
        "materia": "Matemáticas",
        "tema": "Probabilidad Condicional",
        "pregunta": "Se tienen dos urnas: La Urna A contiene 4 bolas rojas y 2 azules. La Urna B contiene 3 bolas rojas y 5 azules. Se lanza una moneda: si cae cara, se extrae una bola de la Urna A; si cae sello, se extrae de la Urna B. ¿Cuál es la probabilidad total de sacar una bola roja?",
        "opciones": ["A. 7/14", "B. 17/24", "C. 17/48", "D. 25/48"],
        "respuesta": "D. 25/48",
        "explicacion_ia": "Teorema de Probabilidad Total. P(Roja) = P(Cara)*P(Roja|A) + P(Sello)*P(Roja|B). (1/2 * 4/6) + (1/2 * 3/8) = 25/48."
    },
    {
        "materia": "Matemáticas",
        "tema": "Funciones y Cálculo",
        "pregunta": "La vida media de un isótopo radiactivo es de 10 años. Si inicialmente hay 100 gramos, ¿cuántos gramos quedarán después de 40 años?",
        "opciones": ["A. 0 gramos.", "B. 6.25 gramos.", "C. 12.5 gramos.", "D. 25 gramos."],
        "respuesta": "B. 6.25 gramos.",
        "explicacion_ia": "En cada vida media, la cantidad se reduce a la mitad. 10 años(50g) -> 20 años(25g) -> 30 años(12.5g) -> 40 años(6.25g)."
    },
    {
        "materia": "Matemáticas",
        "tema": "Geometría Vectorial",
        "pregunta": "Dos corredores parten del mismo punto. El corredor A va hacia el norte a 6 km/h y el corredor B va hacia el este a 8 km/h. Al cabo de 2 horas, ¿qué distancia los separa en línea recta?",
        "opciones": ["A. 14 km", "B. 28 km", "C. 20 km", "D. 10 km"],
        "respuesta": "C. 20 km",
        "explicacion_ia": "Forman un triángulo rectángulo (Pitágoras). Distancias: 12km y 16km. Hipotenusa = raíz(12² + 16²) = raíz(144+256) = raíz(400) = 20."
    },
    {
        "materia": "Matemáticas",
        "tema": "Cálculo - Teoremas",
        "pregunta": "Una función f(x) es continua en [a, b] con f(a) < 0 y f(b) > 0. Según el Teorema de Bolzano, esto garantiza que:",
        "opciones": ["A. La función es creciente.", "B. Existe al menos un punto c en (a, b) tal que f(c) = 0.", "C. La función es positiva.", "D. No tiene raíces."],
        "respuesta": "B. Existe al menos un punto c en (a, b) tal que f(c) = 0.",
        "explicacion_ia": "Si una función continua cambia de signo en un intervalo, obligatoriamente cruza el eje X (tiene una raíz)."
    },
    {
        "materia": "Matemáticas",
        "tema": "Trigonometría",
        "pregunta": "En un triángulo rectángulo, sen(α) = 3/5. ¿Cuánto vale tan(α)?",
        "opciones": ["A. 4/5", "B. 3/4", "C. 5/3", "D. 5/4"],
        "respuesta": "B. 3/4",
        "explicacion_ia": "Es un triángulo notable 3-4-5. Opuesto=3, Hipotenusa=5, Adyacente=4. Tan = Opuesto/Adyacente = 3/4."
    },
    {
        "materia": "Matemáticas",
        "tema": "Cálculo - Límites",
        "pregunta": "El límite de (sin(x) / x) cuando x tiende a 0 es:",
        "opciones": ["A. 0", "B. 1", "C. Infinito.", "D. Indeterminado."],
        "respuesta": "B. 1",
        "explicacion_ia": "Es un límite notable fundamental, demostrable por la regla de L'Hôpital o geometría."
    },
    {
        "materia": "Matemáticas",
        "tema": "Álgebra de Funciones",
        "pregunta": "Si f(x) = x². ¿Cómo cambia la gráfica si hacemos f(x - 2)?",
        "opciones": ["A. Se desplaza 2 unidades hacia arriba.", "B. Se desplaza 2 unidades hacia la izquierda.", "C. Se desplaza 2 unidades hacia la derecha.", "D. Se desplaza 2 unidades hacia abajo."],
        "respuesta": "C. Se desplaza 2 unidades hacia la derecha.",
        "explicacion_ia": "En transformaciones f(x-c) desplaza horizontalmente a la derecha."
    },
    {
        "materia": "Matemáticas",
        "tema": "Optimización",
        "pregunta": "Un agricultor quiere cercar un terreno rectangular junto a un río (sin cerca en el río) con 120m de alambre. La función de área A(x) en función del lado perpendicular x es:",
        "opciones": ["A. A(x) = 120x - x²", "B. A(x) = 120x - 2x²", "C. A(x) = 60x - x²", "D. A(x) = x(120 - x)"],
        "respuesta": "B. A(x) = 120x - 2x²",
        "explicacion_ia": "Perímetro = 2x + y = 120 -> y = 120-2x. Área = x*y = x(120-2x) = 120x - 2x²."
    },

    # ---------------- CIENCIAS NATURALES (NIVEL EXPERTO) ----------------
    {
        "materia": "Ciencias Naturales",
        "tema": "Física de Gases",
        "pregunta": "Si un buzo asciende demasiado rápido, sufre 'mal de descompresión' por burbujas de nitrógeno. ¿Qué ley explica esto?",
        "opciones": ["A. Ley de Boyle.", "B. Ley de Henry.", "C. Ley de Charles.", "D. Arquímedes."],
        "respuesta": "B. Ley de Henry.",
        "explicacion_ia": "La solubilidad de un gas en líquido es proporcional a la presión. Al bajar la presión rápido, el gas sale de la solución formando burbujas."
    },
    {
        "materia": "Ciencias Naturales",
        "tema": "Química - Equilibrio",
        "pregunta": "En la reacción N2 + 3H2 ↔ 2NH3, si aumentamos la presión, el sistema se desplaza hacia:",
        "opciones": ["A. Izquierda (más moles).", "B. Derecha (menos moles).", "C. No hace nada.", "D. Aumenta temperatura."],
        "respuesta": "B. Derecha (menos moles).",
        "explicacion_ia": "Principio de Le Chatelier: A mayor presión, el sistema va hacia donde hay menos volumen (menos moles de gas). Derecha tiene 2 moles, Izquierda 4."
    },
    {
        "materia": "Ciencias Naturales",
        "tema": "Genética Mendeliana",
        "pregunta": "En un cruce AaBb x AaBb, ¿probabilidad de obtener fenotipo doble recesivo (aabb)?",
        "opciones": ["A. 1/4", "B. 9/16", "C. 1/16", "D. 3/16"],
        "respuesta": "C. 1/16",
        "explicacion_ia": "Cruce dihíbrido clásico: proporción 9:3:3:1. Solo 1 de 16 es recesivo puro."
    },
    {
        "materia": "Ciencias Naturales",
        "tema": "Evolución",
        "pregunta": "La resistencia a pesticidas en insectos es ejemplo de:",
        "opciones": ["A. Mutación dirigida.", "B. Selección natural direccional.", "C. Deriva genética.", "D. Selección disruptiva."],
        "respuesta": "B. Selección natural direccional.",
        "explicacion_ia": "El pesticida mata a los débiles, seleccionando a los resistentes y moviendo la población en esa dirección."
    },
    {
        "materia": "Ciencias Naturales",
        "tema": "Termodinámica",
        "pregunta": "La mezcla de HCl y NaOH calienta el vaso. La reacción es:",
        "opciones": ["A. Endotérmica.", "B. Exotérmica.", "C. Isotérmica.", "D. Reversible."],
        "respuesta": "B. Exotérmica.",
        "explicacion_ia": "Liberan calor al entorno (ΔH < 0)."
    },
    {
        "materia": "Ciencias Naturales",
        "tema": "Física - Mecánica",
        "pregunta": "Si un objeto se mueve a velocidad constante en el espacio, la fuerza neta es:",
        "opciones": ["A. Positiva.", "B. Cero.", "C. Igual a gravedad.", "D. Creciente."],
        "respuesta": "B. Cero.",
        "explicacion_ia": "Primera Ley de Newton: Sin aceleración, la suma de fuerzas es cero."
    },
    {
        "materia": "Ciencias Naturales",
        "tema": "Bioquímica",
        "pregunta": "Los catalizadores (enzimas) aceleran reacciones porque:",
        "opciones": ["A. Aumentan temperatura.", "B. Disminuyen la energía de activación.", "C. Aumentan producto.", "D. Eliminan reactivos."],
        "respuesta": "B. Disminuyen la energía de activación.",
        "explicacion_ia": "Reducen la barrera energética necesaria para que inicie la reacción."
    },
    {
        "materia": "Ciencias Naturales",
        "tema": "Biología Celular",
        "pregunta": "Si colocas un glóbulo rojo en agua destilada (hipotónica):",
        "opciones": ["A. Se arruga (crenación).", "B. Se hincha y explota (hemólisis).", "C. Nada.", "D. Se divide."],
        "respuesta": "B. Se hincha y explota (hemólisis).",
        "explicacion_ia": "El agua entra a la célula por ósmosis buscando equilibrar la concentración, hinchándola."
    },

    # ---------------- SOCIALES Y CIUDADANAS (NIVEL EXPERTO) ----------------
    {
        "materia": "Sociales y Ciudadanas",
        "tema": "Economía",
        "pregunta": "El Banco de la República sube tasas de interés para:",
        "opciones": ["A. Subir consumo.", "B. Reducir la inflación.", "C. Subir dólar.", "D. Generar empleo."],
        "respuesta": "B. Reducir la inflación.",
        "explicacion_ia": "Política contractiva: crédito caro = menos gasto = bajan precios."
    },
    {
        "materia": "Sociales y Ciudadanas",
        "tema": "Derechos Fundamentales",
        "pregunta": "La Objeción de Conciencia en Colombia NO aplica para:",
        "opciones": ["A. Servicio militar.", "B. Aborto (médicos).", "C. Pagar impuestos.", "D. Eutanasia."],
        "respuesta": "C. Pagar impuestos.",
        "explicacion_ia": "El deber de solidaridad y financiamiento del Estado prevalece sobre la conciencia individual en temas tributarios."
    },
    {
        "materia": "Sociales y Ciudadanas",
        "tema": "Teoría Política",
        "pregunta": "El 'Realismo' en relaciones internacionales sostiene que:",
        "opciones": ["A. Importa la cooperación.", "B. Los Estados actúan por interés y poder en un sistema anárquico.", "C. Las leyes importan más.", "D. Todos somos amigos."],
        "respuesta": "B. Los Estados actúan por interés y poder en un sistema anárquico.",
        "explicacion_ia": "Visión pragmática donde la seguridad nacional y el poder militar son lo central."
    },
    {
        "materia": "Sociales y Ciudadanas",
        "pregunta": "El 'Control de Conventionalidad' obliga a los jueces a:",
        "tema": "Derecho Internacional",
        "opciones": ["A. Aplicar solo ley nacional.", "B. Interpretar leyes según la Convención Americana de DDHH.", "C. Consultar al Presidente.", "D. Usar leyes de EE.UU."],
        "respuesta": "B. Interpretar leyes según la Convención Americana de DDHH.",
        "explicacion_ia": "Las normas internas no pueden violar tratados internacionales de DDHH ratificados."
    },
    {
        "materia": "Sociales y Ciudadanas",
        "tema": "Mecanismos de Protección",
        "pregunta": "La 'Pérdida de Investidura' para un congresista implica:",
        "opciones": ["A. Perder elecciones.", "B. Muerte política: no poder ser elegido nunca más.", "C. Multa.", "D. Regaño."],
        "respuesta": "B. Muerte política: no poder ser elegido nunca más.",
        "explicacion_ia": "Es la sanción disciplinaria más grave por violar el régimen de inhabilidades o conflicto de intereses."
    },
    {
        "materia": "Sociales y Ciudadanas",
        "tema": "Historia Universal",
        "pregunta": "El 'Consenso de Washington' promovió:",
        "opciones": ["A. Nacionalización.", "B. Privatización, apertura y reducción del Estado (neoliberalismo).", "C. Comunismo.", "D. Cerrar fronteras."],
        "respuesta": "B. Privatización, apertura y reducción del Estado (neoliberalismo).",
        "explicacion_ia": "Receta económica aplicada en Latam en los 90s."
    },
    {
        "materia": "Sociales y Ciudadanas",
        "tema": "Fenómenos Urbanos",
        "pregunta": "La 'Gentrificación' implica:",
        "opciones": ["A. Mejorar parques.", "B. Desplazamiento de pobres por ricos en barrios renovados.", "C. Gente amable.", "D. Construir hospitales."],
        "respuesta": "B. Desplazamiento de pobres por ricos en barrios renovados.",
        "explicacion_ia": "Elitización de zonas populares que expulsa a los residentes originales por el costo de vida."
    },
    {
        "materia": "Sociales y Ciudadanas",
        "tema": "Derecho Internacional",
        "pregunta": "La Corte Penal Internacional (CPI) interviene cuando:",
        "opciones": ["A. Alguien roba un banco.", "B. El Estado nacional no puede o no quiere juzgar crímenes de lesa humanidad.", "C. Hay disputa limítrofe.", "D. Sube el IVA."],
        "respuesta": "B. El Estado nacional no puede o no quiere juzgar crímenes de lesa humanidad.",
        "explicacion_ia": "Principio de Complementariedad: solo actúa si la justicia local falla."
    },

    # ---------------- LECTURA CRÍTICA (NIVEL EXPERTO) ----------------
    {
        "materia": "Lectura Crítica",
        "tema": "Filosofía de la Ciencia",
        "pregunta": "Para Popper, la ciencia no busca verificar verdades, sino:",
        "opciones": ["A. Verificar todo.", "B. Falsar (refutar) teorías.", "C. Inducción.", "D. Dogmas."],
        "respuesta": "B. Falsar (refutar) teorías.",
        "explicacion_ia": "El falsacionismo es el criterio de demarcación: si no se puede probar falso, no es ciencia."
    },
    {
        "materia": "Lectura Crítica",
        "tema": "Figuras Literarias",
        "pregunta": "'Es un cadáver viviente'. Figura retórica:",
        "opciones": ["A. Sinestesia.", "B. Oxímoron.", "C. Metonimia.", "D. Elipsis."],
        "respuesta": "B. Oxímoron.",
        "explicacion_ia": "Unión de dos términos opuestos."
    },
    {
        "materia": "Lectura Crítica",
        "tema": "Filosofía Política",
        "pregunta": "'La democracia es la tiranía de la mayoría'. Esta frase advierte sobre:",
        "opciones": ["A. Voto electrónico.", "B. Riesgo de vulnerar minorías con el voto popular.", "C. Monarquía.", "D. Corrupción."],
        "respuesta": "B. Riesgo de vulnerar minorías con el voto popular.",
        "explicacion_ia": "Alexis de Tocqueville: la mayoría puede ser tan opresora como un dictador si no hay contrapesos."
    },
    {
        "materia": "Lectura Crítica",
        "tema": "Lógica",
        "pregunta": "'Fumar daña. Pedro fuma. Pedro se dañará'. Razonamiento:",
        "opciones": ["A. Inductivo.", "B. Deductivo.", "C. Abductivo.", "D. Analógico."],
        "respuesta": "B. Deductivo.",
        "explicacion_ia": "Va de lo general a lo particular. La conclusión es necesaria."
    },
    {
        "materia": "Lectura Crítica",
        "pregunta": "La 'intertextualidad' es:",
        "tema": "Teoría Literaria",
        "opciones": ["A. Texto largo.", "B. Diálogo o cita de un texto con otro anterior.", "C. Texto en internet.", "D. Texto anónimo."],
        "respuesta": "B. Diálogo o cita de un texto con otro anterior.",
        "explicacion_ia": "Relación entre textos (ej: Los Simpson parodiando películas)."
    },
    {
        "materia": "Lectura Crítica",
        "tema": "Falacias",
        "pregunta": "Falacia 'Hombre de Paja':",
        "opciones": ["A. Agrícola.", "B. Distorsionar el argumento del oponente para atacarlo fácil.", "C. Insultar.", "D. Escribir mal."],
        "respuesta": "B. Distorsionar el argumento del oponente para atacarlo fácil.",
        "explicacion_ia": "Atacar una versión caricaturizada del argumento rival."
    },
    {
        "materia": "Lectura Crítica",
        "tema": "Lingüística",
        "pregunta": "El prefijo 'epi' en epigenética significa:",
        "opciones": ["A. Debajo.", "B. Sobre o por encima.", "C. Dentro.", "D. Contra."],
        "respuesta": "B. Sobre o por encima.",
        "explicacion_ia": "Epidermis (sobre la dermis), Epigenética (sobre los genes)."
    },
    {
        "materia": "Lectura Crítica",
        "tema": "Filosofía",
        "pregunta": "El 'Nihilismo' (Nietzsche) se asocia con:",
        "opciones": ["A. Fe absoluta.", "B. Negación de sentido o valores supremos.", "C. Comunismo.", "D. Construcción."],
        "respuesta": "B. Negación de sentido o valores supremos.",
        "explicacion_ia": "Del latín nihil (nada). La vida carece de propósito intrínseco u objetivo."
    },
    {
        "materia": "Matemáticas",
        "pregunta": "Un tanque de agua tiene forma cilíndrica. Si se duplica el radio de la base manteniendo la misma altura, ¿qué sucede con el volumen del tanque?",
        "opciones": ["A. Se duplica.", "B. Se cuadruplica.", "C. Se reduce a la mitad.", "D. Permanece igual."],
        "respuesta": "B. Se cuadruplica.",
        "explicacion_ia": "El volumen de un cilindro es V = π·r²·h. Si duplicamos el radio (2r), la fórmula cambia a V = π·(2r)²·h = π·4r²·h. Al sacar el 4, vemos que el volumen es 4 veces el original."
    },
    {
        "materia": "Lectura Crítica",
        "pregunta": "En el enunciado: 'Aunque el día estaba soleado, Juan llevó paraguas', el conector 'Aunque' introduce una relación de:",
        "opciones": ["A. Causa y efecto.", "B. Adición.", "C. Oposición o concesión.", "D. Tiempo."],
        "respuesta": "C. Oposición o concesión.",
        "explicacion_ia": "'Aunque' es un conector adversativo o concesivo. Indica que, a pesar de una condición (sol), ocurre algo que parece contrario a la lógica esperada (llevar paraguas)."
    },
    {
        "materia": "Sociales y Ciudadanas",
        "pregunta": "El mecanismo de participación ciudadana que permite a los ciudadanos someter a votación la terminación del mandato de un gobernador o alcalde antes de que culmine su periodo se llama:",
        "opciones": ["A. Plebiscito.", "B. Referendo derogatorio.", "C. Revocatoria del mandato.", "D. Cabildo abierto."],
        "respuesta": "C. Revocatoria del mandato.",
        "explicacion_ia": "La revocatoria del mandato es un derecho político por medio del cual los ciudadanos pueden dar por terminado el mandato que le han conferido a un gobernador o un alcalde."
    },
    {
        "materia": "Ciencias Naturales",
        "pregunta": "¿Qué función principal cumplen los ribosomas dentro de una célula?",
        "opciones": ["A. Almacenar agua y nutrientes.", "B. Sintetizar proteínas.", "C. Producir energía (ATP).", "D. Controlar el paso de sustancias."],
        "respuesta": "B. Sintetizar proteínas.",
        "explicacion_ia": "Los ribosomas son los organelos encargados de la traducción del ARN mensajero para ensamblar aminoácidos y formar proteínas, fundamentales para la estructura y función celular."
    },
    {
        "materia": "Matemáticas",
        "pregunta": "En una bolsa hay 3 bolas rojas, 2 azules y 5 verdes. Si se saca una bola al azar, ¿cuál es la probabilidad de que NO sea verde?",
        "opciones": ["A. 50%", "B. 30%", "C. 20%", "D. 70%"],
        "respuesta": "A. 50%",
        "explicacion_ia": "Hay un total de 10 bolas (3+2+5). Las bolas que NO son verdes son las rojas y azules, que suman 5 (3+2). La probabilidad es 5/10, que equivale a 0.5 o 50%."
    },
    {
        "materia": "Sociales y Ciudadanas",
        "pregunta": "Durante la segunda mitad del siglo XX, América Latina vivió una serie de dictaduras militares. ¿Qué doctrina geopolítica promovida por Estados Unidos influyó en estos regímenes para combatir el comunismo?",
        "opciones": ["A. La Doctrina Monroe.", "B. La Doctrina de Seguridad Nacional.", "C. El Plan Marshall.", "D. La Alianza para el Progreso."],
        "respuesta": "B. La Doctrina de Seguridad Nacional.",
        "explicacion_ia": "Esta doctrina definía al comunismo como un 'enemigo interno'. Bajo esta lógica, las fuerzas armadas latinoamericanas tomaron el poder para 'proteger' a la nación, justificando la represión política."
    },
    {
        "materia": "Ciencias Naturales",
        "pregunta": "Si un átomo neutro pierde dos electrones, se convierte en:",
        "opciones": ["A. Un anión con carga -2.", "B. Un isótopo.", "C. Un catión con carga +2.", "D. Un átomo inestable."],
        "respuesta": "C. Un catión con carga +2.",
        "explicacion_ia": "Los electrones tienen carga negativa. Al perder electrones, el átomo queda con un exceso de carga positiva (protones), convirtiéndose en un ion positivo o catión."
    },
    {
        "materia": "Lectura Crítica",
        "pregunta": "¿Cuál es la tesis central en un texto que argumenta: 'La educación virtual democratiza el conocimiento, pero requiere una autodisciplina que no todos poseen'?",
        "opciones": ["A. La educación virtual es mejor que la presencial.", "B. La autodisciplina es imposible de aprender.", "C. La educación virtual tiene ventajas de acceso, pero desafíos de hábito personal.", "D. El conocimiento no debería ser democrático."],
        "respuesta": "C. La educación virtual tiene ventajas de acceso, pero desafíos de hábito personal.",
        "explicacion_ia": "La tesis balancea dos puntos: el beneficio (acceso/democratización) y la condición limitante (disciplina), reflejando exactamente la opción C."
    },
    {
        "materia": "Matemáticas",
        "pregunta": "Un artículo cuesta $100.000. Primero sube un 10% y luego, sobre el nuevo precio, baja un 10%. ¿Cuál es el precio final?",
        "opciones": ["A. $100.000", "B. $99.000", "C. $101.000", "D. $90.000"],
        "respuesta": "B. $99.000",
        "explicacion_ia": "Precio inicial: 100.000. Sube 10% (10.000) -> Nuevo precio: 110.000. Ahora baja el 10% de 110.000 (que es 11.000). 110.000 - 11.000 = 99.000. No vuelve al precio original."
    },
    {
        "materia": "Sociales y Ciudadanas",
        "pregunta": "Un juez de la República decide no casar a una pareja del mismo sexo argumentando que sus creencias religiosas se lo prohíben. ¿Es válida su actuación según la Constitución?",
        "opciones": ["A. Sí, porque la libertad de conciencia es un derecho fundamental.", "B. No, porque como funcionario público debe acatar la ley y la Constitución sobre sus creencias personales.", "C. Sí, porque el matrimonio igualitario no es legal en Colombia.", "D. No, a menos que pida permiso al Vaticano."],
        "respuesta": "B. No, porque como funcionario público debe acatar la ley y la Constitución sobre sus creencias personales.",
        "explicacion_ia": "Aunque existe la objeción de conciencia, la Corte Constitucional ha establecido que los jueces, al administrar justicia en nombre del Estado, no pueden anteponer sus creencias para negar derechos civiles reconocidos legalmente."
    },
    {
        "materia": "Ciencias Naturales",
        "pregunta": "En una cadena trófica, ¿qué sucede con la energía a medida que pasa de un nivel a otro (ej: de productor a consumidor primario)?",
        "opciones": ["A. Se conserva el 100% de la energía.", "B. Se pierde aproximadamente el 90% en forma de calor y metabolismo.", "C. Aumenta para sustentar a los depredadores.", "D. Se recicla infinitamente sin pérdidas."],
        "respuesta": "B. Se pierde aproximadamente el 90% en forma de calor y metabolismo.",
        "explicacion_ia": "Es la regla del 10%. Solo alrededor del 10% de la energía de un nivel trófico es asimilada por el siguiente nivel; el resto se disipa como calor o se usa en procesos vitales."
    },
    {
        "materia": "Lectura Crítica",
        "pregunta": "Identifique la figura literaria en: 'Sus cabellos son de oro y sus ojos dos luceros'.",
        "opciones": ["A. Símil.", "B. Hipérbole.", "C. Metáfora.", "D. Personificación."],
        "respuesta": "C. Metáfora.",
        "explicacion_ia": "Es una metáfora pura. Sustituye el término real (rubio / brillantes) por uno imaginario (oro / luceros) basándose en una semejanza, sin usar la palabra 'como'."
    },
    {
        "materia": "Matemáticas",
        "pregunta": "La suma de tres números consecutivos es 60. ¿Cuál es el número mayor?",
        "opciones": ["A. 19", "B. 20", "C. 21", "D. 22"],
        "respuesta": "C. 21",
        "explicacion_ia": "Si los números son x, x+1, x+2. La ecuación es: 3x + 3 = 60 -> 3x = 57 -> x = 19. Los números son 19, 20 y 21. El mayor es 21."
    },
    {
        "materia": "Sociales y Ciudadanas",
        "pregunta": "¿Qué fenómeno económico se define como el aumento generalizado y sostenido de los precios de bienes y servicios en un país?",
        "opciones": ["A. Deflación.", "B. Inflación.", "C. Devaluación.", "D. Recesión."],
        "respuesta": "B. Inflación.",
        "explicacion_ia": "La inflación es el indicador que mide el encarecimiento del costo de vida. Implica que con el mismo dinero se pueden comprar menos cosas que antes."
    },
    {
        "materia": "Ciencias Naturales",
        "pregunta": "Si lanzas una pelota hacia arriba, en el punto más alto de su trayectoria, su velocidad es:",
        "opciones": ["A. Máxima.", "B. Cero.", "C. Igual a la gravedad.", "D. Constante."],
        "respuesta": "B. Cero.",
        "explicacion_ia": "En el punto más alto, la pelota se detiene momentáneamente antes de empezar a caer. En ese instante exacto, la velocidad vertical es 0 m/s (aunque la aceleración sigue siendo la gravedad)."
    },
    {
        "materia": "Matemáticas",
        "pregunta": "En un triángulo rectángulo, los catetos miden 3 cm y 4 cm. ¿Cuánto mide la hipotenusa?",
        "opciones": ["A. 5 cm", "B. 7 cm", "C. 6 cm", "D. 12 cm"],
        "respuesta": "A. 5 cm",
        "explicacion_ia": "Usando el Teorema de Pitágoras: h² = a² + b². h² = 3² + 4² = 9 + 16 = 25. La raíz cuadrada de 25 es 5."
    },
    {
        "materia": "Lectura Crítica",
        "pregunta": "Si un texto comienza con 'Había una vez...' y narra hechos fantásticos, lo clasificamos principalmente como:",
        "opciones": ["A. Texto expositivo.", "B. Texto argumentativo.", "C. Texto narrativo.", "D. Texto instructivo."],
        "respuesta": "C. Texto narrativo.",
        "explicacion_ia": "La estructura de relatar sucesos en una secuencia temporal con personajes y tramas es propia del género narrativo (cuentos, novelas, fábulas)."
    },
    {
        "materia": "Sociales y Ciudadanas",
        "pregunta": "La 'Revolución de los Comuneros' en 1781 fue un antecedente de la independencia. ¿Cuál fue su principal causa?",
        "opciones": ["A. El deseo de imponer una religión protestante.", "B. El alza desmedida de impuestos por la Corona Española.", "C. La invasión de Napoleón a España.", "D. La lucha por el voto femenino."],
        "respuesta": "B. El alza desmedida de impuestos por la Corona Española.",
        "explicacion_ia": "El movimiento comunero surgió en el Socorro (Santander) como protesta contra las reformas borbónicas que subían impuestos al tabaco, aguardiente y otros productos."
    },
    {
        "materia": "Ciencias Naturales",
        "pregunta": "¿Cuál es la unidad básica de la herencia que se transmite de padres a hijos?",
        "opciones": ["A. El cromosoma.", "B. El gen.", "C. La proteína.", "D. El núcleo."],
        "respuesta": "B. El gen.",
        "explicacion_ia": "El gen es un segmento de ADN que contiene la información necesaria para producir una característica específica. Es la unidad funcional de la herencia."
    },
    {
        "materia": "Matemáticas",
        "pregunta": "¿Cuántos grados suma la totalidad de los ángulos internos de cualquier triángulo?",
        "opciones": ["A. 90 grados.", "B. 360 grados.", "C. 180 grados.", "D. 270 grados."],
        "respuesta": "C. 180 grados.",
        "explicacion_ia": "Es una propiedad fundamental de la geometría euclidiana: la suma de los tres ángulos internos de un triángulo siempre es 180°."
    },
    {
        "materia": "Sociales y Ciudadanas",
        "pregunta": "En Colombia, las tres ramas del poder público son:",
        "opciones": ["A. Ejecutiva, Legislativa y Judicial.", "B. Presidencial, Congresional y Militar.", "C. Pública, Privada y Mixta.", "D. Nacional, Departamental y Municipal."],
        "respuesta": "A. Ejecutiva, Legislativa y Judicial.",
        "explicacion_ia": "La Constitución establece la división de poderes: Ejecutiva (administra), Legislativa (hace leyes) y Judicial (juzga y resuelve conflictos)."
    },
    {
        "materia": "Lectura Crítica",
        "pregunta": "Sinónimo contextual de la palabra 'efímero' en la frase: 'La fama en redes sociales suele ser efímera'.",
        "opciones": ["A. Duradera.", "B. Pasajera.", "C. Costosa.", "D. Brillante."],
        "respuesta": "B. Pasajera.",
        "explicacion_ia": "Efímero significa que dura muy poco tiempo. En el contexto, se refiere a que la fama pasa rápido, es breve o fugaz."
    },
    {
        "materia": "Ciencias Naturales",
        "pregunta": "El método de separación de mezclas que utiliza la diferencia en los puntos de ebullición se llama:",
        "opciones": ["A. Filtración.", "B. Decantación.", "C. Destilación.", "D. Tamizado."],
        "respuesta": "C. Destilación.",
        "explicacion_ia": "La destilación consiste en calentar una mezcla líquida para que el componente con menor punto de ebullición se evapore primero y luego se condense en otro recipiente."
    },
    {
        "materia": "Matemáticas",
        "pregunta": "Si x/4 = 5, ¿cuál es el valor de x?",
        "opciones": ["A. 9", "B. 1.25", "C. 20", "D. 25"],
        "respuesta": "C. 20",
        "explicacion_ia": "Para despejar x, el 4 que está dividiendo pasa al otro lado a multiplicar. x = 5 * 4, por lo tanto, x = 20."
    },
    {
        "materia": "Sociales y Ciudadanas",
        "pregunta": "¿Qué organismo internacional fue creado después de la Segunda Guerra Mundial para mantener la paz y seguridad internacionales?",
        "opciones": ["A. La OTAN.", "B. La ONU.", "C. La OEA.", "D. El FMI."],
        "respuesta": "B. La ONU.",
        "explicacion_ia": "La Organización de las Naciones Unidas (ONU) se fundó en 1945 con el objetivo principal de evitar futuros conflictos bélicos globales y promover los derechos humanos."
    },
    {
        "materia": "Ciencias Naturales",
        "pregunta": "¿Qué gas es el principal responsable del efecto invernadero causado por la actividad humana?",
        "opciones": ["A. Oxígeno (O2).", "B. Dióxido de carbono (CO2).", "C. Nitrógeno (N2).", "D. Hidrógeno (H2)."],
        "respuesta": "B. Dióxido de carbono (CO2).",
        "explicacion_ia": "Aunque hay otros gases, el CO2 proveniente de la quema de combustibles fósiles es el que más contribuye al calentamiento global antropogénico actual."
    },
    {
        "materia": "Lectura Crítica",
        "pregunta": "Lea: 'Juan no estudió, por consiguiente, reprobó el examen'. La expresión 'por consiguiente' cumple la función de:",
        "opciones": ["A. Introducir una causa.", "B. Introducir una consecuencia.", "C. Introducir una condición.", "D. Introducir una comparación."],
        "respuesta": "B. Introducir una consecuencia.",
        "explicacion_ia": "Es un conector consecutivo. Indica que lo que sigue (reprobar) es el resultado lógico de lo anterior (no estudiar)."
    },
    {
        "materia": "Matemáticas",
        "pregunta": "¿Cuál es la mediana del siguiente conjunto de datos: 2, 5, 8, 1, 4?",
        "opciones": ["A. 5", "B. 4", "C. 8", "D. 20"],
        "respuesta": "B. 4",
        "explicacion_ia": "Para hallar la mediana, primero se ordenan los datos de menor a mayor: 1, 2, 4, 5, 8. El dato que queda exactamente en el centro es el 4."
    },
    {
        "materia": "Sociales y Ciudadanas",
        "pregunta": "La tutela es un mecanismo para proteger:",
        "opciones": ["A. Derechos colectivos.", "B. Derechos fundamentales.", "C. Normas de tránsito.", "D. Deudas económicas."],
        "respuesta": "B. Derechos fundamentales.",
        "explicacion_ia": "El artículo 86 de la Constitución define la Tutela como el mecanismo preferente y sumario para la protección inmediata de los Derechos Fundamentales constitucionales."
    },
    {
        "materia": "Ciencias Naturales",
        "pregunta": "La Ley de Inercia (Primera Ley de Newton) establece que:",
        "opciones": ["A. F = m * a.", "B. A toda acción corresponde una reacción.", "C. Un cuerpo mantiene su estado de reposo o movimiento a menos que una fuerza externa actúe sobre él.", "D. La energía no se crea ni se destruye."],
        "respuesta": "C. Un cuerpo mantiene su estado de reposo o movimiento a menos que una fuerza externa actúe sobre él.",
        "explicacion_ia": "La inercia es la resistencia de los cuerpos a cambiar su estado de movimiento. Si no hay fuerza neta, el objeto sigue quieto o moviéndose en línea recta a velocidad constante."
    },
    {
        "materia": "Matemáticas",
        "pregunta": "En una rifa se imprimieron 100 boletas numeradas del 01 al 100. Si se venden todas las boletas, ¿cuál es la probabilidad de que el número ganador sea un múltiplo de 20?",
        "opciones": ["A. 1/20", "B. 1/25", "C. 5/100", "D. 1/5"],
        "respuesta": "C. 5/100",
        "explicacion_ia": "Los múltiplos de 20 entre 1 y 100 son: 20, 40, 60, 80 y 100. Hay 5 casos favorables de un total de 100 casos posibles. Por lo tanto, la probabilidad es 5/100."
    },
    {
        "materia": "Ciencias Naturales",
        "pregunta": "Un estudiante observa que al poner una planta en un cuarto oscuro, sus hojas se tornan amarillas y se caen. ¿Cuál de los siguientes procesos celulares se ve afectado directamente por la falta de luz?",
        "opciones": ["A. La respiración celular.", "B. La fotosíntesis.", "C. La mitosis.", "D. La síntesis de proteínas."],
        "respuesta": "B. La fotosíntesis.",
        "explicacion_ia": "La fotosíntesis es el proceso mediante el cual las plantas utilizan la energía lumínica para producir glucosa. Sin luz, este proceso se detiene y la planta pierde su coloración (clorosis)."
    },
    {
        "materia": "Sociales y Ciudadanas",
        "pregunta": "Durante el siglo XIX en Colombia, el federalismo fue una característica central de varias constituciones. ¿Cuál fue una consecuencia directa de la implementación del modelo federal en esa época?",
        "opciones": ["A. La centralización absoluta del recaudo de impuestos.", "B. El fortalecimiento del ejército nacional sobre los ejércitos regionales.", "C. La autonomía de los estados para dictar sus propias leyes y tener ejércitos propios.", "D. La unificación inmediata de la educación religiosa en todo el país."],
        "respuesta": "C. La autonomía de los estados para dictar sus propias leyes y tener ejércitos propios.",
        "explicacion_ia": "El federalismo (Constitución de 1863) otorgó gran soberanía a los estados, permitiéndoles legislar internamente y mantener fuerzas armadas regionales."
    },
    {
        "materia": "Lectura Crítica",
        "pregunta": "Lea la frase: 'No hay medicina que cure lo que no cura la felicidad' (Gabriel García Márquez). ¿Qué intención comunicativa predomina en el enunciado?",
        "opciones": ["A. Describir un procedimiento médico alternativo.", "B. Exaltar el valor emocional como superior al remedio físico.", "C. Informar sobre los avances farmacéuticos.", "D. Cuestionar la eficacia de los médicos modernos."],
        "respuesta": "B. Exaltar el valor emocional como superior al remedio físico.",
        "explicacion_ia": "La frase es una metáfora que resalta que el bienestar emocional (la felicidad) tiene un poder sanador que trasciende a la medicina convencional."
    },
    {
        "materia": "Matemáticas",
        "pregunta": "Una función lineal representa el costo de producción de zapatos. Si producir 10 pares cuesta 200.000 y producir 20 pares cuesta 350.000, ¿qué representa la pendiente de la recta en este contexto?",
        "opciones": ["A. El costo fijo de la fábrica.", "B. El costo variable por cada par de zapatos adicional.", "C. El precio de venta al público.", "D. La ganancia total."],
        "respuesta": "B. El costo variable por cada par de zapatos adicional.",
        "explicacion_ia": "La pendiente indica la razón de cambio. En costos, es cuánto aumenta el costo total por cada unidad extra producida (costo marginal)."
    },
    {
        "materia": "Sociales y Ciudadanas",
        "pregunta": "Un alcalde decide prohibir el consumo de dosis mínima en parques para proteger a los niños. Un grupo de ciudadanos demanda la medida alegando el libre desarrollo de la personalidad. ¿Qué tensión de derechos se presenta aquí?",
        "opciones": ["A. Derecho al trabajo vs. Derecho a la salud.", "B. Derechos de los niños vs. Libre desarrollo de la personalidad.", "C. Derecho a la educación vs. Libertad de expresión.", "D. Seguridad alimentaria vs. Espacio público."],
        "respuesta": "B. Derechos de los niños vs. Libre desarrollo de la personalidad.",
        "explicacion_ia": "El conflicto es entre la protección prevalente de los derechos de los menores y el derecho individual de los adultos al libre desarrollo de la personalidad."
    },
    {
        "materia": "Ciencias Naturales",
        "pregunta": "Si se deja caer una bola de boliche y una pluma al mismo tiempo en una cámara de vacío (sin aire), ¿qué ocurrirá?",
        "opciones": ["A. La bola cae primero porque es más pesada.", "B. La pluma flota y no cae.", "C. Ambas caen al mismo tiempo y con la misma velocidad.", "D. La bola cae más rápido, pero la pluma la alcanza al final."],
        "respuesta": "C. Ambas caen al mismo tiempo y con la misma velocidad.",
        "explicacion_ia": "En el vacío (sin aire), la única fuerza es la gravedad. Según Galileo, todos los objetos caen con la misma aceleración independientemente de su masa."
    },
    {
        "materia": "Lectura Crítica",
        "pregunta": "En un texto argumentativo, el autor afirma: 'El uso excesivo de redes sociales está erosionando la capacidad de concentración de los jóvenes'. Esta oración funciona en el texto como:",
        "opciones": ["A. Una evidencia científica.", "B. Una tesis o postura central.", "C. Un contraargumento.", "D. Una cita de autoridad."],
        "respuesta": "B. Una tesis o postura central.",
        "explicacion_ia": "Es una afirmación debatible que expresa la opinión del autor, la cual deberá ser defendida con argumentos. Es la idea núcleo."
    },
    {
        "materia": "Matemáticas",
        "pregunta": "El área de un cuadrado es 36 cm². Si se duplica la longitud de sus lados, ¿cuál será la nueva área?",
        "opciones": ["A. 72 cm²", "B. 144 cm²", "C. 108 cm²", "D. 48 cm²"],
        "respuesta": "B. 144 cm²",
        "explicacion_ia": "Si el área es 36, el lado mide 6. Al duplicar, el lado es 12. La nueva área es 12x12 = 144. (Regla: si duplicas el lado, el área se cuadruplica)."
    },
    {
        "materia": "Ciencias Naturales",
        "pregunta": "En una reacción química, la ley de conservación de la materia establece que:",
        "opciones": ["A. La masa de los reactivos es mayor que la de los productos.", "B. La materia se destruye para liberar energía.", "C. La masa total de los reactivos es igual a la masa total de los productos.", "D. Los átomos cambian de identidad durante la reacción."],
        "respuesta": "C. La masa total de los reactivos es igual a la masa total de los productos.",
        "explicacion_ia": "La ley de Lavoisier indica que la materia no se crea ni se destruye, solo se transforma. La masa se conserva constante."
    },
    {
        "materia": "Matemáticas",
        "pregunta": "Juan tiene el doble de la edad de Pedro. Si sus edades suman 36 años, ¿cuántos años tiene Pedro?",
        "opciones": ["A. 12 años.", "B. 24 años.", "C. 18 años.", "D. 9 años."],
        "respuesta": "A. 12 años.",
        "explicacion_ia": "Si la edad de Pedro es x, la de Juan es 2x. La ecuación es: x + 2x = 36. Esto suma 3x = 36. Al dividir, x = 12. Pedro tiene 12 y Juan 24."
    },
    {
        "materia": "Ciencias Naturales",
        "pregunta": "El pH es una medida de acidez o alcalinidad. Una solución con un pH de 2 se considera:",
        "opciones": ["A. Neutra.", "B. Fuertemente ácida.", "C. Ligeramente básica.", "D. Fuertemente alcalina."],
        "respuesta": "B. Fuertemente ácida.",
        "explicacion_ia": "La escala de pH va de 0 a 14. 7 es neutro. Menor a 7 es ácido y mayor a 7 es básico. Un pH de 2 es muy bajo, indicando alta acidez (como el jugo de limón o gástrico)."
    },
    {
        "materia": "Sociales y Ciudadanas",
        "pregunta": "¿Cuál fue el evento histórico ocurrido el 9 de abril de 1948 que desató una ola de violencia en Bogotá y el resto del país?",
        "opciones": ["A. La Masacre de las Bananeras.", "B. El Bogotazo.", "C. La toma del Palacio de Justicia.", "D. La Guerra de los Mil Días."],
        "respuesta": "B. El Bogotazo.",
        "explicacion_ia": "El asesinato del líder liberal Jorge Eliécer Gaitán el 9 de abril de 1948 provocó revueltas populares conocidas como 'El Bogotazo', marcando el inicio de la época conocida como 'La Violencia'."
    },
    {
        "materia": "Lectura Crítica",
        "pregunta": "En la frase 'El candidato brilló por su ausencia en el debate', se utiliza una figura retórica llamada:",
        "opciones": ["A. Pleonasmo.", "B. Paradoja u Oxímoron.", "C. Aliteración.", "D. Onomatopeya."],
        "respuesta": "B. Paradoja u Oxímoron.",
        "explicacion_ia": "Es una ironía construida sobre una contradicción aparente (paradoja): no se puede 'brillar' (destacar visualmente) si se está 'ausente' (no se está). Resalta lo notoria que fue su falta de asistencia."
    },
    {
        "materia": "Matemáticas",
        "pregunta": "Un mapa tiene una escala de 1:100.000. Esto significa que 1 cm en el mapa equivale en la realidad a:",
        "opciones": ["A. 100 metros.", "B. 1 kilómetro.", "C. 10 kilómetros.", "D. 10.000 metros."],
        "respuesta": "B. 1 kilómetro.",
        "explicacion_ia": "1 cm en el mapa son 100.000 cm reales. Como 100 cm = 1 m, entonces son 1.000 metros. Y 1.000 metros equivalen a 1 kilómetro."
    },
    {
        "materia": "Ciencias Naturales",
        "pregunta": "¿Cuál es la diferencia principal entre una célula procariota y una eucariota?",
        "opciones": ["A. Las procariotas no tienen membrana celular.", "B. Las eucariotas no tienen ADN.", "C. Las procariotas carecen de núcleo definido.", "D. Las eucariotas son siempre unicelulares."],
        "respuesta": "C. Las procariotas carecen de núcleo definido.",
        "explicacion_ia": "La distinción fundamental es que las células eucariotas tienen su material genético encerrado en un núcleo, mientras que en las procariotas (como las bacterias) el ADN está disperso en el citoplasma."
    },
    {
        "materia": "Sociales y Ciudadanas",
        "pregunta": "Si un ciudadano no está de acuerdo con una ley aprobada por el Congreso porque considera que va en contra de la Constitución, puede presentar:",
        "opciones": ["A. Una demanda de inconstitucionalidad.", "B. Una acción de tutela.", "C. Un derecho de petición.", "D. Una moción de censura."],
        "respuesta": "A. Una demanda de inconstitucionalidad.",
        "explicacion_ia": "La Acción Pública de Inconstitucionalidad es el mecanismo mediante el cual cualquier ciudadano puede solicitar a la Corte Constitucional que retire una ley del ordenamiento jurídico por contradecir la Carta Magna."
    },
    {
        "materia": "Lectura Crítica",
        "pregunta": "Si en un texto se lee: 'La deforestación avanza a pasos agigantados, devorando la esperanza verde del planeta', el tono del autor es:",
        "opciones": ["A. Objetivo y neutral.", "B. Alarmista y crítico.", "C. Sarcástico y humorístico.", "D. Indiferente."],
        "respuesta": "B. Alarmista y crítico.",
        "explicacion_ia": "El uso de palabras cargadas emocionalmente como 'devorando' y 'esperanza verde' indica una postura subjetiva de preocupación y denuncia, no una simple descripción técnica."
    },
    {
        "materia": "Matemáticas",
        "pregunta": "En una clase de 30 estudiantes, el 40% son mujeres. ¿Cuántos hombres hay en la clase?",
        "opciones": ["A. 12", "B. 15", "C. 18", "D. 20"],
        "respuesta": "C. 18",
        "explicacion_ia": "Si el 40% son mujeres, el 60% son hombres. El 60% de 30 se calcula: 0.6 * 30 = 18. O: 10% es 3, 60% es 3*6=18."
    },
    {
        "materia": "Ciencias Naturales",
        "pregunta": "Cuando el agua hierve y pasa de estado líquido a gaseoso, este cambio físico se denomina:",
        "opciones": ["A. Fusión.", "B. Sublimación.", "C. Evaporación o Ebullición.", "D. Solidificación."],
        "respuesta": "C. Evaporación o Ebullición.",
        "explicacion_ia": "La ebullición es el cambio de fase de líquido a gas cuando se alcanza la temperatura de ebullición. La fusión es de sólido a líquido, solidificación de líquido a sólido."
    },
    {
        "materia": "Sociales y Ciudadanas",
        "pregunta": "¿Qué significa que Colombia es un 'Estado Social de Derecho'?",
        "opciones": ["A. Que las leyes se aplican solo a la sociedad civil.", "B. Que el Estado debe garantizar derechos fundamentales y el bienestar social, no solo el orden legal.", "C. Que es un Estado socialista.", "D. Que los jueces tienen más poder que el presidente."],
        "respuesta": "B. Que el Estado debe garantizar derechos fundamentales y el bienestar social, no solo el orden legal.",
        "explicacion_ia": "Implica que el Estado no solo vigila el cumplimiento de la ley (Estado de Derecho), sino que interviene activamente para asegurar la dignidad humana, la equidad y los derechos económicos, sociales y culturales."
    },
    {
        "materia": "Lectura Crítica",
        "pregunta": "¿Qué función cumple el título en un texto periodístico o noticia?",
        "opciones": ["A. Resumir todo el contenido detalladamente.", "B. Captar la atención del lector y anticipar el tema central.", "C. Ocultar la información principal para el final.", "D. Firmar el nombre del autor."],
        "respuesta": "B. Captar la atención del lector y anticipar el tema central.",
        "explicacion_ia": "El titular debe ser conciso y atractivo (función apelativa) y a la vez informativo (función referencial) para indicar de qué trata la noticia."
    },
    {
        "materia": "Matemáticas",
        "pregunta": "¿Cuál es el perímetro de un rectángulo de base 5 cm y altura 3 cm?",
        "opciones": ["A. 15 cm", "B. 8 cm", "C. 16 cm", "D. 12 cm"],
        "respuesta": "C. 16 cm",
        "explicacion_ia": "El perímetro es la suma de todos los lados. P = 2*base + 2*altura. P = 2(5) + 2(3) = 10 + 6 = 16 cm."
    },
    {
        "materia": "Ciencias Naturales",
        "pregunta": "La teoría de la evolución por selección natural fue propuesta principalmente por:",
        "opciones": ["A. Isaac Newton.", "B. Charles Darwin.", "C. Albert Einstein.", "D. Louis Pasteur."],
        "respuesta": "B. Charles Darwin.",
        "explicacion_ia": "Charles Darwin, en su libro 'El origen de las especies' (1859), propuso que las especies evolucionan a lo largo del tiempo mediante la selección natural de las variaciones más favorables."
    },
    {
        "materia": "Sociales y Ciudadanas",
        "pregunta": "El voto en blanco en Colombia tiene un efecto político real. Si gana el voto en blanco por mayoría absoluta en una elección:",
        "opciones": ["A. Se debe repetir la elección con los mismos candidatos.", "B. Gana el candidato que quedó en segundo lugar.", "C. Se debe repetir la elección con candidatos nuevos.", "D. El actual gobernante se queda en el poder."],
        "respuesta": "C. Se debe repetir la elección con candidatos nuevos.",
        "explicacion_ia": "Es una herramienta de disenso. Si gana el voto en blanco (más del 50% de los votos válidos), la elección se anula y debe repetirse por una sola vez con aspirantes distintos a los anteriores."
    },
    {
        "materia": "Lectura Crítica",
        "pregunta": "Identifique la premisa en el silogismo: 'Todos los hombres son mortales. Sócrates es hombre. Por lo tanto, Sócrates es mortal'.",
        "opciones": ["A. 'Por lo tanto, Sócrates es mortal'.", "B. 'Todos los hombres son mortales'.", "C. 'Sócrates'.", "D. Ninguna de las anteriores."],
        "respuesta": "B. 'Todos los hombres son mortales'.",
        "explicacion_ia": "Un silogismo tiene premisa mayor, premisa menor y conclusión. La frase citada en B es la premisa mayor (general). La opción A es la conclusión."
    },
    {
        "materia": "Matemáticas",
        "pregunta": "Un dado tiene 6 caras numeradas del 1 al 6. ¿Cuál es la probabilidad de sacar un número par?",
        "opciones": ["A. 1/6", "B. 1/2", "C. 1/3", "D. 2/3"],
        "respuesta": "B. 1/2",
        "explicacion_ia": "Los números pares son 2, 4, 6 (3 casos favorables). El total de casos es 6. La probabilidad es 3/6, que simplificado es 1/2 o 50%."
    },
    {
        "materia": "Ciencias Naturales",
        "pregunta": "¿Qué tipo de energía tiene un objeto debido a su altura o posición?",
        "opciones": ["A. Energía cinética.", "B. Energía potencial gravitatoria.", "C. Energía térmica.", "D. Energía elástica."],
        "respuesta": "B. Energía potencial gravitatoria.",
        "explicacion_ia": "La energía potencial depende de la posición. Si un objeto se eleva, gana energía potencial (Ep = m*g*h). Si se mueve, tiene energía cinética."
    },
    {
        "materia": "Sociales y Ciudadanas",
        "pregunta": "La globalización económica se caracteriza principalmente por:",
        "opciones": ["A. El cierre de fronteras para proteger el comercio local.", "B. La libre circulación de capitales, bienes y servicios entre países.", "C. La prohibición de internet.", "D. El fortalecimiento exclusivo de las culturas locales."],
        "respuesta": "B. La libre circulación de capitales, bienes y servicios entre países.",
        "explicacion_ia": "La globalización busca la integración de las economías mundiales, reduciendo aranceles y barreras para permitir el flujo internacional de mercados."
    },
    {
        "materia": "Lectura Crítica",
        "pregunta": "Si un autor cita estadísticas, estudios y expertos para defender su idea, está utilizando un argumento de:",
        "opciones": ["A. Autoridad.", "B. Ad hominem.", "C. Emotividad.", "D. Tradición."],
        "respuesta": "A. Autoridad.",
        "explicacion_ia": "El argumento de autoridad valida una premisa basándose en el prestigio o conocimiento técnico de una fuente externa experta en la materia."
    },
    {
        "materia": "Matemáticas",
        "pregunta": "¿Cuál es el valor de 3 elevado a la 4 (3⁴)?",
        "opciones": ["A. 12", "B. 27", "C. 81", "D. 64"],
        "respuesta": "C. 81",
        "explicacion_ia": "3 elevado a la 4 significa multiplicar 3 por sí mismo 4 veces: 3 x 3 x 3 x 3. (3x3=9, 9x3=27, 27x3=81)."
    },
    {
        "materia": "Ciencias Naturales",
        "pregunta": "Los antibióticos son medicamentos diseñados específicamente para combatir:",
        "opciones": ["A. Virus (como la gripe).", "B. Bacterias.", "C. Hongos.", "D. Parásitos."],
        "respuesta": "B. Bacterias.",
        "explicacion_ia": "Los antibióticos atacan estructuras o procesos bacterianos. No son efectivos contra virus (para los cuales se usan antivirales) ni hongos (antifúngicos)."
    },
    {
        "materia": "Sociales y Ciudadanas",
        "pregunta": "¿Cuál es la función principal de la Contraloría General de la República?",
        "opciones": ["A. Investigar delitos penales de los ciudadanos.", "B. Vigilar la gestión fiscal y el buen uso de los recursos públicos.", "C. Juzgar a los congresistas.", "D. Elegir al Presidente."],
        "respuesta": "B. Vigilar la gestión fiscal y el buen uso de los recursos públicos.",
        "explicacion_ia": "La Contraloría es un órgano de control fiscal. Su misión es asegurar que el dinero del Estado se gaste correctamente y no se pierda por corrupción o mala gestión."
    },
    {
        "materia": "Lectura Crítica",
        "pregunta": "Antónimo contextual de 'prolífico' en: 'Gabriel García Márquez fue un escritor prolífico'.",
        "opciones": ["A. Famoso.", "B. Estéril o improductivo.", "C. Creativo.", "D. Costeño."],
        "respuesta": "B. Estéril o improductivo.",
        "explicacion_ia": "Prolífico significa que produce mucho (muchas obras, mucha descendencia). Su antónimo sería alguien que no produce nada o muy poco (estéril/improductivo)."
    },
    {
        "materia": "Matemáticas",
        "pregunta": "Resuelve para x: 2x - 5 = 15",
        "opciones": ["A. 5", "B. 10", "C. 20", "D. 7.5"],
        "respuesta": "B. 10",
        "explicacion_ia": "Sumamos 5 a ambos lados: 2x = 20. Dividimos por 2: x = 10."
    },
    {
        "materia": "Matemáticas",
        "pregunta": "Un vehículo recorre 120 km en 2 horas manteniendo una velocidad constante. ¿Cuánto tiempo tardará en recorrer 300 km a la misma velocidad?",
        "opciones": ["A. 4 horas.", "B. 5 horas.", "C. 6 horas.", "D. 3.5 horas."],
        "respuesta": "B. 5 horas.",
        "explicacion_ia": "Primero hallamos la velocidad: 120 km / 2 h = 60 km/h. Luego usamos la fórmula t = d / v. Tiempo = 300 km / 60 km/h = 5 horas."
    },
    {
        "materia": "Ciencias Naturales",
        "pregunta": "¿Qué nombre recibe el proceso mediante el cual una célula se divide para formar dos células hijas genéticamente idénticas?",
        "opciones": ["A. Meiosis.", "B. Fecundación.", "C. Mitosis.", "D. Transcripción."],
        "respuesta": "C. Mitosis.",
        "explicacion_ia": "La mitosis es el proceso de división celular somática que garantiza que las células hijas tengan el mismo número de cromosomas que la madre. La meiosis reduce la carga genética a la mitad (para gametos)."
    },
    {
        "materia": "Sociales y Ciudadanas",
        "pregunta": "La Constitución Política de 1991 reconoce a Colombia como un país pluriétnico y multicultural. Esto implica que:",
        "opciones": ["A. Todos los ciudadanos deben hablar la misma lengua.", "B. El Estado debe proteger y promover la diversidad cultural y los derechos de las minorías étnicas.", "C. Las leyes indígenas están por encima de la Constitución.", "D. La religión católica es la única oficial."],
        "respuesta": "B. El Estado debe proteger y promover la diversidad cultural y los derechos de las minorías étnicas.",
        "explicacion_ia": "El reconocimiento de la diversidad implica obligaciones estatales para preservar las culturas, lenguas y tradiciones de los grupos étnicos, garantizando su igualdad y dignidad."
    },
    {
        "materia": "Lectura Crítica",
        "pregunta": "Lea la frase: 'Es mejor ser cabeza de ratón que cola de león'. Este refrán sugiere que:",
        "opciones": ["A. Los ratones son más inteligentes que los leones.", "B. Es preferible ser el primero en una comunidad pequeña que el último en una grande.", "C. La biología animal determina el liderazgo.", "D. Siempre se debe aspirar a ser un león."],
        "respuesta": "B. Es preferible ser el primero en una comunidad pequeña que el último en una grande.",
        "explicacion_ia": "Es un dicho popular que valora la importancia, el liderazgo o la autonomía en un entorno modesto sobre la insignificancia o subordinación en un entorno poderoso."
    },
    {
        "materia": "Matemáticas",
        "pregunta": "Si el radio de un círculo es 10 cm, ¿cuál es su área aproximada? (Tome π ≈ 3.14)",
        "opciones": ["A. 31.4 cm²", "B. 314 cm²", "C. 100 cm²", "D. 62.8 cm²"],
        "respuesta": "B. 314 cm²",
        "explicacion_ia": "La fórmula del área es A = π * r². A = 3.14 * (10)². A = 3.14 * 100 = 314 cm²."
    },
    {
        "materia": "Ciencias Naturales",
        "pregunta": "El hierro se oxida al dejarlo a la intemperie. Este es un ejemplo de:",
        "opciones": ["A. Cambio físico.", "B. Cambio químico.", "C. Evaporación.", "D. Mezcla heterogénea."],
        "respuesta": "B. Cambio químico.",
        "explicacion_ia": "La oxidación implica una reacción química donde el hierro reacciona con el oxígeno formando una nueva sustancia (óxido de hierro), cambiando su composición molecular irreversiblemente."
    },
    {
        "materia": "Sociales y Ciudadanas",
        "pregunta": "¿Qué rama del poder público se encarga de hacer control político al gobierno y aprobar el presupuesto nacional?",
        "opciones": ["A. La Rama Ejecutiva.", "B. La Rama Judicial.", "C. La Rama Legislativa (Congreso).", "D. La Procuraduría."],
        "respuesta": "C. La Rama Legislativa (Congreso).",
        "explicacion_ia": "El Congreso de la República (Senado y Cámara) tiene como funciones principales reformar la constitución, hacer las leyes y ejercer control político sobre el gobierno y la administración."
    },
    {
        "materia": "Lectura Crítica",
        "pregunta": "En un texto narrativo, el 'narrador omnisciente' se caracteriza por:",
        "opciones": ["A. Ser un personaje más dentro de la historia que cuenta lo que ve.", "B. Saber todo lo que piensan y sienten los personajes, así como el pasado y el futuro.", "C. Narrar solo lo que se puede ver desde fuera, como una cámara.", "D. Dirigirse al lector en segunda persona ('tú')."],
        "respuesta": "B. Saber todo lo que piensan y sienten los personajes, así como el pasado y el futuro.",
        "explicacion_ia": "El término 'omnisciente' significa 'que todo lo sabe'. Es un narrador externo que conoce la interioridad de los personajes y la totalidad de la trama."
    },
    {
        "materia": "Matemáticas",
        "pregunta": "En una tienda ofrecen un descuento del 20% sobre una camisa que cuesta $50.000. ¿Cuánto paga el cliente finalmente?",
        "opciones": ["A. $10.000", "B. $40.000", "C. $30.000", "D. $45.000"],
        "respuesta": "B. $40.000",
        "explicacion_ia": "El 20% de 50.000 es 10.000 (50.000 * 0.20). Se resta el descuento al precio original: 50.000 - 10.000 = 40.000."
    },
    {
        "materia": "Ciencias Naturales",
        "pregunta": "¿Cuál es la función principal de los glóbulos rojos en la sangre?",
        "opciones": ["A. Combatir infecciones.", "B. Coagular la sangre.", "C. Transportar oxígeno.", "D. Regular la temperatura."],
        "respuesta": "C. Transportar oxígeno.",
        "explicacion_ia": "Los glóbulos rojos (eritrocitos) contienen hemoglobina, una proteína que se une al oxígeno en los pulmones y lo transporta a todos los tejidos del cuerpo."
    },
    {
        "materia": "Sociales y Ciudadanas",
        "pregunta": "El 'Frente Nacional' (1958-1974) fue un pacto político entre liberales y conservadores con el objetivo de:",
        "opciones": ["A. Crear una dictadura militar permanente.", "B. Poner fin a la violencia bipartidista mediante la alternancia en el poder.", "C. Integrar a las guerrillas al gobierno.", "D. Declarar la guerra a Estados Unidos."],
        "respuesta": "B. Poner fin a la violencia bipartidista mediante la alternancia en el poder.",
        "explicacion_ia": "Fue un acuerdo para detener la guerra civil no declarada (La Violencia). Acordaron turnarse la presidencia cada 4 años y repartir los cargos públicos equitativamente durante 16 años."
    },
    {
        "materia": "Lectura Crítica",
        "pregunta": "Identifique el tipo de argumento: 'Según la Organización Mundial de la Salud (OMS), el consumo de tabaco es la principal causa de muerte prevenible'.",
        "opciones": ["A. Argumento de ejemplificación.", "B. Argumento de autoridad.", "C. Argumento por analogía.", "D. Argumento ad hominem."],
        "respuesta": "B. Argumento de autoridad.",
        "explicacion_ia": "Se cita a una entidad experta y reconocida (la OMS) para validar la afirmación, lo cual es la definición de argumento de autoridad."
    },
    {
        "materia": "Matemáticas",
        "pregunta": "¿Cuál es el resultado de la operación: 5 + 3 x 2?",
        "opciones": ["A. 16", "B. 11", "C. 10", "D. 13"],
        "respuesta": "B. 11",
        "explicacion_ia": "Según la jerarquía de las operaciones (PEMDAS), primero se hacen las multiplicaciones y luego las sumas. 3 x 2 = 6. Luego 5 + 6 = 11."
    },
    {
        "materia": "Ciencias Naturales",
        "pregunta": "En el sistema solar, ¿cuál es el planeta más grande?",
        "opciones": ["A. Tierra.", "B. Marte.", "C. Júpiter.", "D. Saturno."],
        "respuesta": "C. Júpiter.",
        "explicacion_ia": "Júpiter es un gigante gaseoso y es el planeta con mayor masa y volumen del sistema solar, superando por mucho a la Tierra."
    },
    {
        "materia": "Sociales y Ciudadanas",
        "pregunta": "Un ciudadano vende su voto a cambio de un mercado o dinero. Esta práctica se conoce como:",
        "opciones": ["A. Democracia participativa.", "B. Clientelismo o corrupción al sufragante.", "C. Voto programático.", "D. Voto censitario."],
        "respuesta": "B. Clientelismo o corrupción al sufragante.",
        "explicacion_ia": "Es una práctica corrupta donde el voto deja de ser una decisión libre de conciencia y se convierte en una transacción comercial, debilitando la democracia."
    },
    {
        "materia": "Lectura Crítica",
        "pregunta": "En la oración 'La casa *cuya* fachada es azul se vendió ayer', la palabra 'cuya' funciona como:",
        "opciones": ["A. Un verbo.", "B. Un adjetivo calificativo.", "C. Un pronombre relativo posesivo.", "D. Una preposición."],
        "respuesta": "C. Un pronombre relativo posesivo.",
        "explicacion_ia": "'Cuyo/a' es un relativo que indica posesión (la fachada DE la casa) y al mismo tiempo introduce una oración subordinada."
    },
    {
        "materia": "Matemáticas",
        "pregunta": "La media aritmética (promedio) de las notas 3.0, 4.0 y 5.0 es:",
        "opciones": ["A. 3.5", "B. 4.0", "C. 4.5", "D. 12.0"],
        "respuesta": "B. 4.0",
        "explicacion_ia": "Se suman los datos (3+4+5=12) y se divide entre la cantidad de datos (3). 12 / 3 = 4.0."
    },
    {
        "materia": "Ciencias Naturales",
        "pregunta": "¿Qué ley de la física explica por qué al remar un bote hacia atrás, este avanza hacia adelante?",
        "opciones": ["A. Ley de la Gravedad.", "B. Primera Ley de la Termodinámica.", "C. Tercera Ley de Newton (Acción y Reacción).", "D. Ley de Ohm."],
        "respuesta": "C. Tercera Ley de Newton (Acción y Reacción).",
        "explicacion_ia": "La acción es empujar el agua hacia atrás con el remo; la reacción es que el agua empuja el bote hacia adelante con la misma fuerza."
    },
    {
        "materia": "Sociales y Ciudadanas",
        "pregunta": "El sector primario de la economía agrupa actividades como:",
        "opciones": ["A. La industria manufacturera.", "B. El transporte y turismo.", "C. La agricultura, ganadería y minería.", "D. La educación y salud."],
        "respuesta": "C. La agricultura, ganadería y minería.",
        "explicacion_ia": "El sector primario se encarga de la extracción de materias primas directamente de la naturaleza. El secundario transforma (industria) y el terciario ofrece servicios."
    },
    {
        "materia": "Lectura Crítica",
        "pregunta": "¿Qué vicio del lenguaje se comete en la frase: 'Sube para arriba y tráeme el libro'?",
        "opciones": ["A. Cacofonía.", "B. Pleonasmo o redundancia.", "C. Barbarismo.", "D. Anfibología."],
        "respuesta": "B. Pleonasmo o redundancia.",
        "explicacion_ia": "Es el uso de palabras innecesarias para el sentido de la frase, ya que 'subir' implica necesariamente ir hacia 'arriba'."
    },
    {
        "materia": "Matemáticas",
        "pregunta": "¿Cuál de las siguientes fracciones es equivalente a 0.75?",
        "opciones": ["A. 1/2", "B. 3/4", "C. 2/5", "D. 4/5"],
        "respuesta": "B. 3/4",
        "explicacion_ia": "Al dividir 3 entre 4 obtienes 0.75. También puedes verlo como 75/100, que simplificado (dividiendo por 25 arriba y abajo) es 3/4."
    },
    {
        "materia": "Ciencias Naturales",
        "pregunta": "La molécula responsable de almacenar la información genética en la mayoría de los seres vivos es:",
        "opciones": ["A. ARN.", "B. Proteína.", "C. ADN.", "D. Glucosa."],
        "respuesta": "C. ADN.",
        "explicacion_ia": "El Ácido Desoxirribonucleico (ADN) contiene las instrucciones genéticas usadas en el desarrollo y funcionamiento de todos los organismos vivos conocidos."
    },
    {
        "materia": "Sociales y Ciudadanas",
        "pregunta": "El derecho al 'Habeas Corpus' sirve para:",
        "opciones": ["A. Solicitar información pública.", "B. Proteger la libertad personal ante capturas ilegales o arbitrarias.", "C. Proteger el derecho a la salud.", "D. Demandar alimentos a los padres."],
        "respuesta": "B. Proteger la libertad personal ante capturas ilegales o arbitrarias.",
        "explicacion_ia": "Es una garantía fundamental que permite a cualquier persona detenida solicitar a un juez que revise la legalidad de su captura. Si es ilegal, debe ser liberada en máximo 36 horas."
    },
    {
        "materia": "Lectura Crítica",
        "pregunta": "En el texto: 'El agua es vida, cuídala', la función del lenguaje predominante es:",
        "opciones": ["A. Referencial (informa).", "B. Apelativa o Conativa (busca influir en el receptor).", "C. Poética (belleza del mensaje).", "D. Fática (verifica el canal)."],
        "respuesta": "B. Apelativa o Conativa (busca influir en el receptor).",
        "explicacion_ia": "La frase es un imperativo ('cuídala') que busca generar una reacción o cambio de comportamiento en quien lee el mensaje."
    },
    {
        "materia": "Matemáticas",
        "pregunta": "Un ángulo recto mide:",
        "opciones": ["A. Menos de 90 grados.", "B. Exactamente 90 grados.", "C. Más de 90 grados.", "D. 180 grados."],
        "respuesta": "B. Exactamente 90 grados.",
        "explicacion_ia": "Por definición geométrica, un ángulo recto es aquel que mide exactamente 90°, como la esquina de un cuadrado."
    },
    {
        "materia": "Ciencias Naturales",
        "pregunta": "¿Qué partícula subatómica tiene carga negativa y orbita alrededor del núcleo?",
        "opciones": ["A. Protón.", "B. Neutrón.", "C. Electrón.", "D. Fotón."],
        "respuesta": "C. Electrón.",
        "explicacion_ia": "Los electrones son las partículas de carga negativa que forman la corteza del átomo. Protones (+) y neutrones (neutros) están en el núcleo."
    },
    {
        "materia": "Sociales y Ciudadanas",
        "pregunta": "¿Qué consecuencia tuvo la caída del Muro de Berlín en 1989?",
        "opciones": ["A. El inicio de la Segunda Guerra Mundial.", "B. El fin de la Guerra Fría y la reunificación de Alemania.", "C. La creación de la Unión Soviética.", "D. La separación de Panamá."],
        "respuesta": "B. El fin de la Guerra Fría y la reunificación de Alemania.",
        "explicacion_ia": "La caída del muro simbolizó el colapso del bloque comunista en Europa del Este y marcó el final de la bipolaridad mundial (Guerra Fría) y la unión de las dos Alemanias."
    },
    {
        "materia": "Lectura Crítica",
        "pregunta": "Si un texto explica detalladamente cómo armar un mueble paso a paso, es un texto:",
        "opciones": ["A. Narrativo.", "B. Instructivo.", "C. Argumentativo.", "D. Lírico."],
        "respuesta": "B. Instructivo.",
        "explicacion_ia": "Los textos instructivos tienen como propósito dirigir las acciones del lector mediante pasos secuenciales para lograr un objetivo (recetas, manuales)."
    },
    {
        "materia": "Matemáticas",
        "pregunta": "Si lanzas dos monedas al aire, ¿cuál es la probabilidad de que ambas caigan en 'cara'?",
        "opciones": ["A. 1/2", "B. 1/4", "C. 1/3", "D. 1/8"],
        "respuesta": "B. 1/4",
        "explicacion_ia": "Hay 4 resultados posibles: Cara-Cara, Cara-Sello, Sello-Cara, Sello-Sello. Solo uno es favorable (Cara-Cara). Probabilidad = 1/4 (25%)."
    },
    {
        "materia": "Ciencias Naturales",
        "pregunta": "El proceso mediante el cual las plantas liberan vapor de agua a través de sus hojas se llama:",
        "opciones": ["A. Absorción.", "B. Transpiración.", "C. Condensación.", "D. Precipitación."],
        "respuesta": "B. Transpiración.",
        "explicacion_ia": "La transpiración vegetal es la pérdida de agua en forma de vapor, principalmente a través de los estomas de las hojas, fundamental para el ciclo del agua."
    },
    {
        "materia": "Matemáticas",
        "pregunta": "En un plano cartesiano, el punto A tiene coordenadas (2, 3) y el punto B tiene coordenadas (2, -2). ¿Cuál es la distancia entre estos dos puntos?",
        "opciones": ["A. 1 unidad.", "B. 5 unidades.", "C. 4 unidades.", "D. 6 unidades."],
        "respuesta": "B. 5 unidades.",
        "explicacion_ia": "Como la coordenada x es la misma (2), la distancia es la diferencia vertical entre y=3 y y=-2. La operación es: 3 - (-2) = 3 + 2 = 5."
    },
    {
        "materia": "Ciencias Naturales",
        "pregunta": "¿Cuál es la principal diferencia entre la respiración aerobia y la anaerobia?",
        "opciones": ["A. La aerobia produce alcohol.", "B. La anaerobia requiere oxígeno.", "C. La aerobia requiere oxígeno, mientras que la anaerobia no.", "D. La anaerobia produce mucha más energía que la aerobia."],
        "respuesta": "C. La aerobia requiere oxígeno, mientras que la anaerobia no.",
        "explicacion_ia": "El término 'aerobio' significa 'con aire' (oxígeno). La respiración celular aerobia usa oxígeno para romper la glucosa; la anaerobia (como la fermentación) ocurre en ausencia de este."
    },
    {
        "materia": "Sociales y Ciudadanas",
        "pregunta": "La 'Séptima Papeleta' fue un movimiento estudiantil que dio origen a:",
        "opciones": ["A. La independencia de Panamá.", "B. El Frente Nacional.", "C. La Constitución Política de 1991.", "D. Los Acuerdos de Paz de 2016."],
        "respuesta": "C. La Constitución Política de 1991.",
        "explicacion_ia": "En 1990, estudiantes impulsaron una papeleta adicional en las elecciones para convocar una Asamblea Nacional Constituyente, proceso que culminó con la Constitución del 91."
    },
    {
        "materia": "Lectura Crítica",
        "pregunta": "En la frase: 'El rascacielos arañaba las nubes con sus dedos de acero', se presenta una:",
        "opciones": ["A. Hipérbole.", "B. Personificación o Prosopopeya.", "C. Comparación.", "D. Antítesis."],
        "respuesta": "B. Personificación o Prosopopeya.",
        "explicacion_ia": "Se atribuyen cualidades humanas (tener dedos, acción de arañar) a un objeto inanimado (el rascacielos)."
    },
    {
        "materia": "Matemáticas",
        "pregunta": "Si un litro de leche cuesta $2.500 y compro 3.5 litros, ¿cuánto debo pagar?",
        "opciones": ["A. $7.500", "B. $8.750", "C. $9.000", "D. $8.500"],
        "respuesta": "B. $8.750",
        "explicacion_ia": "Multiplicamos el precio unitario por la cantidad: 2.500 * 3.5. (2.500 * 3 = 7.500) + (la mitad de 2.500 es 1.250). 7.500 + 1.250 = 8.750."
    },
    {
        "materia": "Ciencias Naturales",
        "pregunta": "En la tabla periódica, los elementos se ordenan principalmente según su:",
        "opciones": ["A. Número atómico (cantidad de protones).", "B. Estado de agregación.", "C. Abundancia en la Tierra.", "D. Fecha de descubrimiento."],
        "respuesta": "A. Número atómico (cantidad de protones).",
        "explicacion_ia": "La ley periódica moderna establece que las propiedades de los elementos son función periódica de sus números atómicos (Z), que es el número de protones en el núcleo."
    },
    {
        "materia": "Sociales y Ciudadanas",
        "pregunta": "El Personero Estudiantil es un estudiante encargado de:",
        "opciones": ["A. Vigilar la asistencia de los profesores.", "B. Promover y defender los derechos y deberes de los estudiantes.", "C. Organizar las fiestas del colegio.", "D. Asignar las notas de disciplina."],
        "respuesta": "B. Promover y defender los derechos y deberes de los estudiantes.",
        "explicacion_ia": "Según la Ley 115, el Personero es un alumno de último grado encargado de velar por el cumplimiento de los derechos y deberes estudiantiles establecidos en el Manual de Convivencia."
    },
    {
        "materia": "Lectura Crítica",
        "pregunta": "¿Cuál es la intención principal de una caricatura política?",
        "opciones": ["A. Enseñar a dibujar.", "B. Narrar una historia de superhéroes.", "C. Opinar o criticar un hecho de actualidad mediante el humor y la sátira.", "D. Decorar el periódico."],
        "respuesta": "C. Opinar o criticar un hecho de actualidad mediante el humor y la sátira.",
        "explicacion_ia": "La caricatura es un género periodístico de opinión que usa la exageración gráfica y el humor para cuestionar el poder o situaciones sociales."
    },
    {
        "materia": "Matemáticas",
        "pregunta": "¿Cuánto es el 15% de 200?",
        "opciones": ["A. 15", "B. 20", "C. 30", "D. 45"],
        "respuesta": "C. 30",
        "explicacion_ia": "El 10% de 200 es 20. El 5% es la mitad, o sea 10. Entonces 15% (10%+5%) es 20 + 10 = 30. O simplemente: 200 * 0.15 = 30."
    },
    {
        "materia": "Ciencias Naturales",
        "pregunta": "La fuerza que ejerce la Tierra sobre los objetos atrayéndolos hacia su centro se llama:",
        "opciones": ["A. Magnetismo.", "B. Fricción.", "C. Peso.", "D. Masa."],
        "respuesta": "C. Peso.",
        "explicacion_ia": "Ojo con la diferencia: Masa es la cantidad de materia (kg), Peso es la fuerza (Newtons) con la que la gravedad atrae esa masa (P = m*g)."
    },
    {
        "materia": "Sociales y Ciudadanas",
        "pregunta": "¿Qué es el 'voto preferente' en las elecciones al Congreso?",
        "opciones": ["A. Votar solo por el logo del partido.", "B. La posibilidad de marcar el logo del partido y el número específico de un candidato.", "C. Votar por el candidato más joven.", "D. El voto que vale doble."],
        "respuesta": "B. La posibilidad de marcar el logo del partido y el número específico de un candidato.",
        "explicacion_ia": "En listas con voto preferente (listas abiertas), el ciudadano puede elegir a un candidato específico dentro del partido para que ese individuo tenga más opción de ganar curul."
    },
    {
        "materia": "Lectura Crítica",
        "pregunta": "Lea: 'Más vale pájaro en mano que cien volando'. ¿Qué tipo de texto es?",
        "opciones": ["A. Un aforismo o refrán.", "B. Una noticia.", "C. Un poema épico.", "D. Un ensayo académico."],
        "respuesta": "A. Un aforismo o refrán.",
        "explicacion_ia": "Es una sentencia breve de uso popular que expresa una enseñanza o consejo moral (sabiduría popular)."
    },
    {
        "materia": "Matemáticas",
        "pregunta": "La suma de los ángulos interiores de un cuadrilátero (como un cuadrado o rectángulo) es:",
        "opciones": ["A. 180 grados.", "B. 360 grados.", "C. 270 grados.", "D. 90 grados."],
        "respuesta": "B. 360 grados.",
        "explicacion_ia": "Cualquier cuadrilátero se puede dividir en dos triángulos. Como cada triángulo suma 180°, dos triángulos suman 360° (180+180)."
    },
    {
        "materia": "Ciencias Naturales",
        "pregunta": "¿Qué sistema del cuerpo humano se encarga de procesar información y coordinar las respuestas mediante impulsos eléctricos?",
        "opciones": ["A. Sistema Digestivo.", "B. Sistema Endocrino.", "C. Sistema Nervioso.", "D. Sistema Respiratorio."],
        "respuesta": "C. Sistema Nervioso.",
        "explicacion_ia": "El sistema nervioso (cerebro, médula espinal, nervios) utiliza neuronas para transmitir señales eléctricas rápidas que controlan acciones voluntarias e involuntarias."
    },
    {
        "materia": "Sociales y Ciudadanas",
        "pregunta": "La Constitución colombiana protege la 'propiedad privada', pero advierte que esta tiene una 'función social'. ¿Qué significa esto?",
        "opciones": ["A. Que nadie puede tener casa propia.", "B. Que el interés particular debe ceder ante el interés público o social cuando sea necesario (ej: expropiación para una vía).", "C. Que todas las casas deben estar abiertas al público.", "D. Que el Estado es dueño de todo."],
        "respuesta": "B. Que el interés particular debe ceder ante el interés público o social cuando sea necesario (ej: expropiación para una vía).",
        "explicacion_ia": "Implica que el derecho a la propiedad no es absoluto; si se necesita un terreno para construir un hospital o carretera que beneficie a todos, el interés general prevalece (con indemnización)."
    },
    {
        "materia": "Lectura Crítica",
        "pregunta": "Si un texto tiene introducción, desarrollo de argumentos y conclusión, su tipología es:",
        "opciones": ["A. Texto Argumentativo.", "B. Texto Narrativo.", "C. Texto Descriptivo.", "D. Texto Poético."],
        "respuesta": "A. Texto Argumentativo.",
        "explicacion_ia": "Esta es la superestructura clásica del ensayo o texto argumentativo, diseñado para defender una tesis o punto de vista."
    },
    {
        "materia": "Matemáticas",
        "pregunta": "¿Qué número es solución de la ecuación: 3x - 2 = 10?",
        "opciones": ["A. 3", "B. 5", "C. 4", "D. 6"],
        "respuesta": "C. 4",
        "explicacion_ia": "3x = 10 + 2 -> 3x = 12 -> x = 12 / 3 -> x = 4."
    },
    {
        "materia": "Ciencias Naturales",
        "pregunta": "La energía que se obtiene del viento se denomina:",
        "opciones": ["A. Energía Solar.", "B. Energía Hidráulica.", "C. Energía Eólica.", "D. Energía Geotérmica."],
        "respuesta": "C. Energía Eólica.",
        "explicacion_ia": "Eólica viene de 'Eolo' (dios del viento). Se captura mediante aerogeneradores que transforman la energía cinética del viento en electricidad."
    },
    {
        "materia": "Sociales y Ciudadanas",
        "pregunta": "¿Cuál de los siguientes NO es un mecanismo de protección de Derechos Humanos en Colombia?",
        "opciones": ["A. Acción de Tutela.", "B. Habeas Data.", "C. Acción de Grupo.", "D. Estado de Conmoción Interior."],
        "respuesta": "D. Estado de Conmoción Interior.",
        "explicacion_ia": "El Estado de Conmoción Interior es un estado de excepción que declara el Presidente para conjurar graves perturbaciones del orden público, no es una herramienta ciudadana de protección."
    },
    {
        "materia": "Lectura Crítica",
        "pregunta": "En la frase: 'Compré pan, leche, huevos y café', la coma se usa para:",
        "opciones": ["A. Separar oraciones independientes.", "B. Introducir una cita.", "C. Enumerar elementos de una serie.", "D. Separar el sujeto del predicado."],
        "respuesta": "C. Enumerar elementos de una serie.",
        "explicacion_ia": "Es una 'coma enumerativa'. Sirve para separar elementos análogos dentro de una misma lista."
    },
    {
        "materia": "Matemáticas",
        "pregunta": "Un triángulo equilátero tiene:",
        "opciones": ["A. Dos lados iguales y uno diferente.", "B. Tres lados de diferente medida.", "C. Tres lados de igual medida.", "D. Un ángulo recto."],
        "respuesta": "C. Tres lados de igual medida.",
        "explicacion_ia": "Equi (igual) látero (lado). Por definición, sus tres lados miden lo mismo y sus tres ángulos internos miden 60° cada uno."
    },
    {
        "materia": "Ciencias Naturales",
        "pregunta": "¿Qué tipo de carga eléctrica tiene un protón?",
        "opciones": ["A. Negativa.", "B. Positiva.", "C. Neutra.", "D. Variable."],
        "respuesta": "B. Positiva.",
        "explicacion_ia": "Los protones se encuentran en el núcleo del átomo y tienen carga positiva (+), contrarrestando la carga negativa de los electrones."
    },
    {
        "materia": "Sociales y Ciudadanas",
        "pregunta": "La división política administrativa de Colombia agrupa al territorio en:",
        "opciones": ["A. Estados federales.", "B. Departamentos y Municipios.", "C. Provincias autónomas.", "D. Reinos."],
        "respuesta": "B. Departamentos y Municipios.",
        "explicacion_ia": "Colombia es una república unitaria descentralizada administrativamente, dividida en 32 departamentos, que a su vez se dividen en municipios."
    },
    {
        "materia": "Lectura Crítica",
        "pregunta": "La palabra 'Inverosímil' significa:",
        "opciones": ["A. Que es muy verdadero.", "B. Que es difícil de creer o tiene apariencia de mentira.", "C. Que es similar al invierno.", "D. Que está probado científicamente."],
        "respuesta": "B. Que es difícil de creer o tiene apariencia de mentira.",
        "explicacion_ia": "El prefijo 'in' es negación. Verosímil es 'que parece verdad'. Inverosímil es algo que no parece verdadero o creíble."
    },
    {
        "materia": "Matemáticas",
        "pregunta": "¿Cuál es el mínimo común múltiplo (MCM) de 4 y 6?",
        "opciones": ["A. 24", "B. 12", "C. 10", "D. 2"],
        "respuesta": "B. 12",
        "explicacion_ia": "Múltiplos de 4: 4, 8, 12, 16... Múltiplos de 6: 6, 12, 18... El primer número común en ambas listas es el 12."
    },
    {
        "materia": "Ciencias Naturales",
        "pregunta": "El proceso de fotosíntesis en las plantas libera al ambiente:",
        "opciones": ["A. Dióxido de carbono (CO2).", "B. Oxígeno (O2).", "C. Nitrógeno.", "D. Metano."],
        "respuesta": "B. Oxígeno (O2).",
        "explicacion_ia": "Las plantas absorben CO2 y luz solar para producir glucosa (su alimento) y, como subproducto o desecho, liberan oxígeno vital para nosotros."
    },
    {
        "materia": "Sociales y Ciudadanas",
        "pregunta": "El conflicto armado en Colombia ha tenido múltiples actores. ¿Cuál de los siguientes NO es un actor armado ilegal?",
        "opciones": ["A. Guerrillas (FARC, ELN).", "B. Paramilitares (AUC).", "C. Fuerzas Militares de Colombia (Ejército).", "D. Bandas Criminales (BACRIM)."],
        "respuesta": "C. Fuerzas Militares de Colombia (Ejército).",
        "explicacion_ia": "El Ejército es un actor armado LEGAL e institucional, cuya función constitucional es defender la soberanía y proteger a la población civil, a diferencia de los otros grupos que operan al margen de la ley."
    },
    {
        "materia": "Lectura Crítica",
        "pregunta": "¿Qué recurso literario se usa en: 'Sus ojos eran dos luceros que iluminaban mi camino'?",
        "opciones": ["A. Metáfora.", "B. Símil.", "C. Hipérbaton.", "D. Onomatopeya."],
        "respuesta": "A. Metáfora.",
        "explicacion_ia": "Se sustituye el término real (ojos brillantes) por uno imaginario (luceros) estableciendo una identidad directa sin usar comparativos como 'cual' o 'como'."
    },
    {
        "materia": "Matemáticas",
        "pregunta": "Si un dado tiene probabilidad 1/6 de sacar un 5. ¿Qué probabilidad hay de sacar un 5 si lanzo el dado dos veces seguidas (eventos independientes)?",
        "opciones": ["A. 2/6", "B. 1/36", "C. 1/12", "D. 1/3"],
        "respuesta": "B. 1/36",
        "explicacion_ia": "Al ser eventos independientes, las probabilidades se multiplican. 1/6 * 1/6 = 1/36."
    },
    {
        "materia": "Ciencias Naturales",
        "pregunta": "La unidad básica de medida de la masa en el Sistema Internacional es:",
        "opciones": ["A. El gramo.", "B. El kilogramo.", "C. La libra.", "D. La tonelada."],
        "respuesta": "B. El kilogramo.",
        "explicacion_ia": "Aunque usamos mucho el gramo, el estándar científico internacional (SI) define al Kilogramo (kg) como la unidad base de masa."
    },
    {
        "materia": "Sociales y Ciudadanas",
        "pregunta": "¿Qué busca proteger el mecanismo del 'Habeas Data'?",
        "opciones": ["A. La libertad física.", "B. El derecho a conocer, actualizar y rectificar la información recogida sobre uno en bases de datos.", "C. El derecho a la vivienda.", "D. El derecho a la educación."],
        "respuesta": "B. El derecho a conocer, actualizar y rectificar la información recogida sobre uno en bases de datos.",
        "explicacion_ia": "Es el derecho a la autodeterminación informática. Permite, por ejemplo, corregir un reporte negativo injusto en Datacrédito."
    },
    {
        "materia": "Lectura Crítica",
        "pregunta": "En un texto, la conclusión tiene la función de:",
        "opciones": ["A. Presentar a los personajes.", "B. Exponer los argumentos.", "C. Cerrar el tema sintetizando lo expuesto o reafirmando la tesis.", "D. Introducir el tema."],
        "respuesta": "C. Cerrar el tema sintetizando lo expuesto o reafirmando la tesis.",
        "explicacion_ia": "La conclusión es el cierre lógico donde se retoman los puntos clave para dejar un mensaje final claro al lector."
    },
    {
        "materia": "Matemáticas",
        "pregunta": "Un ángulo agudo mide:",
        "opciones": ["A. Más de 90 grados.", "B. Menos de 90 grados.", "C. 90 grados exactos.", "D. 180 grados."],
        "respuesta": "B. Menos de 90 grados.",
        "explicacion_ia": "Los ángulos se clasifican en: Agudo (<90°), Recto (=90°), Obtuso (>90° y <180°) y Llano (180°)."
    },
    {
        "materia": "Ciencias Naturales",
        "pregunta": "¿Cuál es el estado de la materia donde las partículas tienen mayor energía cinética y ocupan todo el volumen del recipiente?",
        "opciones": ["A. Sólido.", "B. Líquido.", "C. Gaseoso.", "D. Condensado de Bose-Einstein."],
        "respuesta": "C. Gaseoso.",
        "explicacion_ia": "En el estado gaseoso, las moléculas se mueven libremente a altas velocidades, chocando entre sí y expandiéndose para llenar cualquier contenedor."
    },
    {
        "materia": "Sociales y Ciudadanas",
        "pregunta": "Simón Bolívar es conocido como 'El Libertador' porque:",
        "opciones": ["A. Descubrió América.", "B. Lideró las campañas de independencia de varios países sudamericanos frente a España.", "C. Escribió la Constitución de Estados Unidos.", "D. Fue el primer rey de Colombia."],
        "respuesta": "B. Lideró las campañas de independencia de varios países sudamericanos frente a España.",
        "explicacion_ia": "Bolívar fue la figura central de la independencia de Colombia, Venezuela, Ecuador, Perú y Bolivia."
    },
    {
        "materia": "Lectura Crítica",
        "pregunta": "Sinónimo de 'Paradigma':",
        "opciones": ["A. Mentira.", "B. Modelo o patrón a seguir.", "C. Paradoja.", "D. Problema."],
        "respuesta": "B. Modelo o patrón a seguir.",
        "explicacion_ia": "Un paradigma es un ejemplo, modelo o conjunto de creencias aceptadas que sirven de norma en una disciplina."
    },
    {
        "materia": "Matemáticas",
        "pregunta": "Si un cuadrado tiene un área de 100 m², ¿cuánto mide su lado?",
        "opciones": ["A. 50 m", "B. 25 m", "C. 10 m", "D. 20 m"],
        "respuesta": "C. 10 m",
        "explicacion_ia": "El área del cuadrado es Lado x Lado (L²). Qué número multiplicado por sí mismo da 100? Es 10. (10 x 10 = 100)."
    },
    {
        "materia": "Ciencias Naturales",
        "pregunta": "El órgano encargado de filtrar la sangre y producir orina es:",
        "opciones": ["A. El hígado.", "B. El páncreas.", "C. El riñón.", "D. La vejiga."],
        "respuesta": "C. El riñón.",
        "explicacion_ia": "Los riñones son los filtros del cuerpo, eliminan desechos y exceso de agua de la sangre para formar la orina."
    },
    {
        "materia": "Sociales y Ciudadanas",
        "pregunta": "¿Qué es la 'Consulta Popular'?",
        "opciones": ["A. Una encuesta en internet.", "B. Un mecanismo donde el pueblo decide 'Sí' o 'No' sobre un asunto trascendental (ej: minería en su municipio).", "C. Una reunión de amigos.", "D. La elección del alcalde."],
        "respuesta": "B. Un mecanismo donde el pueblo decide 'Sí' o 'No' sobre un asunto trascendental (ej: minería en su municipio).",
        "explicacion_ia": "Es un mecanismo de participación donde se somete una pregunta de carácter general a consideración del pueblo para que este se pronuncie formalmente."
    },
    {
        "materia": "Lectura Crítica",
        "pregunta": "¿Qué significa la expresión 'Círculo Vicioso'?",
        "opciones": ["A. Una figura geométrica perfecta.", "B. Una situación repetitiva de la cual es difícil salir porque la causa genera el efecto y viceversa.", "C. Un grupo de amigos muy unidos.", "D. Un error de dibujo."],
        "respuesta": "B. Una situación repetitiva de la cual es difícil salir porque la causa genera el efecto y viceversa.",
        "explicacion_ia": "Se refiere a una cadena de acontecimientos que se repiten indefinidamente en bucle, generalmente empeorando la situación."
    },
    {
        "materia": "Matemáticas",
        "pregunta": "¿Cuál es el resultado de restar -5 - (-3)?",
        "opciones": ["A. -8", "B. -2", "C. 2", "D. 8"],
        "respuesta": "B. -2",
        "explicacion_ia": "Restar un negativo equivale a sumar. -5 + 3 = -2."
    },
    {
        "materia": "Ciencias Naturales",
        "pregunta": "La mitocondria es un organelo celular encargado de:",
        "opciones": ["A. La fotosíntesis.", "B. La producción de energía (respiración celular).", "C. La digestión.", "D. El control genético."],
        "respuesta": "B. La producción de energía (respiración celular).",
        "explicacion_ia": "Es conocida como la 'central eléctrica' de la célula porque genera ATP."
    },
    {
        "materia": "Sociales y Ciudadanas",
        "pregunta": "¿Cuál es la máxima autoridad de la Rama Judicial encargada de proteger la Constitución?",
        "opciones": ["A. La Fiscalía.", "B. La Corte Suprema de Justicia.", "C. La Corte Constitucional.", "D. El Consejo de Estado."],
        "respuesta": "C. La Corte Constitucional.",
        "explicacion_ia": "Su función principal es la guarda de la integridad y supremacía de la Constitución."
    },
    {
        "materia": "Lectura Crítica",
        "pregunta": "Un texto que narra la vida de una persona escrita por ella misma es:",
        "opciones": ["A. Una biografía.", "B. Una autobiografía.", "C. Una crónica.", "D. Un cuento."],
        "respuesta": "B. Una autobiografía.",
        "explicacion_ia": "El prefijo 'auto' indica que el autor y el protagonista son la misma persona."
    },
    {
        "materia": "Matemáticas",
        "pregunta": "En estadística, la 'moda' es:",
        "opciones": ["A. El promedio de los datos.", "B. El dato que más se repite.", "C. El dato central.", "D. La diferencia entre el mayor y el menor."],
        "respuesta": "B. El dato que más se repite.",
        "explicacion_ia": "La moda es el valor con mayor frecuencia absoluta en un conjunto de datos."
    },
    {
        "materia": "Ciencias Naturales",
        "pregunta": "¿Cuál es el símbolo químico del agua?",
        "opciones": ["A. Ho2", "B. H2O", "C. Oh2", "D. HO"],
        "respuesta": "B. H2O",
        "explicacion_ia": "Dos átomos de hidrógeno y uno de oxígeno."
    },
    {
        "materia": "Sociales y Ciudadanas",
        "pregunta": "El Derecho Internacional Humanitario (DIH) se aplica:",
        "opciones": ["A. En tiempos de paz.", "B. Solo en conflictos armados internacionales o internos.", "C. En desastres naturales.", "D. En protestas sociales."],
        "respuesta": "B. Solo en conflictos armados internacionales o internos.",
        "explicacion_ia": "El DIH son las 'reglas de la guerra' para proteger a quienes no participan en las hostilidades."
    },
    {
        "materia": "Lectura Crítica",
        "pregunta": "¿Qué conector usaría para agregar información a una idea?",
        "opciones": ["A. Pero.", "B. Además.", "C. Por lo tanto.", "D. Sin embargo."],
        "respuesta": "B. Además.",
        "explicacion_ia": "'Además' es un conector de adición."
    },
    {
        "materia": "Matemáticas",
        "pregunta": "Si un tren viaja a 80 km/h, ¿qué distancia recorre en 30 minutos?",
        "opciones": ["A. 80 km", "B. 40 km", "C. 160 km", "D. 20 km"],
        "respuesta": "B. 40 km",
        "explicacion_ia": "30 minutos es media hora (0.5 h). 80 * 0.5 = 40 km."
    },
    {
        "materia": "Ciencias Naturales",
        "pregunta": "Los animales vertebrados se caracterizan por:",
        "opciones": ["A. No tener huesos.", "B. Tener exoesqueleto.", "C. Tener columna vertebral y cráneo.", "D. Ser todos acuáticos."],
        "respuesta": "C. Tener columna vertebral y cráneo.",
        "explicacion_ia": "La presencia de endoesqueleto óseo o cartilaginoso es su rasgo distintivo."
    },
    {
        "materia": "Sociales y Ciudadanas",
        "pregunta": "¿Qué región natural de Colombia es conocida por su biodiversidad selvática y el río más largo del mundo?",
        "opciones": ["A. Andina.", "B. Caribe.", "C. Orinoquía.", "D. Amazonía."],
        "respuesta": "D. Amazonía.",
        "explicacion_ia": "La región Amazónica alberga gran parte de la selva tropical y la cuenca del río Amazonas."
    },
    {
        "materia": "Lectura Crítica",
        "pregunta": "En la frase 'El tiempo es oro', se emplea:",
        "opciones": ["A. Símil.", "B. Metáfora.", "C. Anáfora.", "D. Hipérbaton."],
        "respuesta": "B. Metáfora.",
        "explicacion_ia": "Identifica el tiempo con el oro por su valor, sin usar 'como'."
    },
    {
        "materia": "Matemáticas",
        "pregunta": "¿Cuál es la raíz cuadrada de 144?",
        "opciones": ["A. 10", "B. 11", "C. 12", "D. 14"],
        "respuesta": "C. 12",
        "explicacion_ia": "12 x 12 = 144."
    },
    {
        "materia": "Ciencias Naturales",
        "pregunta": "La Primera Ley de la Termodinámica afirma que la energía:",
        "opciones": ["A. Se destruye con el uso.", "B. Se crea de la nada.", "C. No se crea ni se destruye, solo se transforma.", "D. Es infinita."],
        "respuesta": "C. No se crea ni se destruye, solo se transforma.",
        "explicacion_ia": "Es el principio de conservación de la energía."
    },
    {
        "materia": "Sociales y Ciudadanas",
        "pregunta": "El Cabildo Abierto es un mecanismo donde:",
        "opciones": ["A. Los ciudadanos se reúnen con los concejales para discutir asuntos de interés local.", "B. Se elige al presidente.", "C. Se destituye a un alcalde.", "D. Se aprueban impuestos."],
        "respuesta": "A. Los ciudadanos se reúnen con los concejales para discutir asuntos de interés local.",
        "explicacion_ia": "Permite la participación directa de la comunidad en las sesiones del Concejo Municipal."
    },
    {
        "materia": "Lectura Crítica",
        "pregunta": "Un texto editorial en un periódico refleja:",
        "opciones": ["A. Una noticia objetiva.", "B. La opinión institucional del medio sobre un tema.", "C. Un anuncio publicitario.", "D. Una entrevista."],
        "respuesta": "B. La opinión institucional del medio sobre un tema.",
        "explicacion_ia": "El editorial es un género de opinión que no suele ir firmado porque representa la voz del periódico."
    },
    {
        "materia": "Matemáticas",
        "pregunta": "Si a = 3 y b = 2, ¿cuánto es 2a + 3b?",
        "opciones": ["A. 10", "B. 12", "C. 13", "D. 5"],
        "respuesta": "B. 12",
        "explicacion_ia": "2(3) + 3(2) = 6 + 6 = 12."
    },
    {
        "materia": "Ciencias Naturales",
        "pregunta": "¿Qué es un ecosistema?",
        "opciones": ["A. Solo los animales de una zona.", "B. El conjunto de seres vivos (bióticos) y el medio físico (abiótico) interactuando.", "C. Un zoológico.", "D. El clima de una región."],
        "respuesta": "B. El conjunto de seres vivos (bióticos) y el medio físico (abiótico) interactuando.",
        "explicacion_ia": "Implica la interacción dinámica entre los organismos y su entorno."
    },
    {
        "materia": "Sociales y Ciudadanas",
        "pregunta": "La discriminación racial en Colombia está prohibida por:",
        "opciones": ["A. Sugerencia cultural.", "B. La Constitución y la ley penal.", "C. Las normas de etiqueta.", "D. La iglesia."],
        "respuesta": "B. La Constitución y la ley penal.",
        "explicacion_ia": "El artículo 13 de la Constitución y leyes antidiscriminación penalizan el racismo."
    },
    {
        "materia": "Lectura Crítica",
        "pregunta": "Sinónimo de 'Eficas':",
        "opciones": ["A. Inútil.", "B. Rápido.", "C. Que logra el efecto deseado.", "D. Costoso."],
        "respuesta": "C. Que logra el efecto deseado.",
        "explicacion_ia": "La eficacia es la capacidad de alcanzar el objetivo propuesto."
    },
    {
        "materia": "Matemáticas",
        "pregunta": "¿Cuántos mililitros hay en 1.5 litros?",
        "opciones": ["A. 150 ml", "B. 1500 ml", "C. 1000 ml", "D. 1050 ml"],
        "respuesta": "B. 1500 ml",
        "explicacion_ia": "1 litro son 1000 ml. 1.5 litros son 1.5 * 1000 = 1500 ml."
    },
    {
        "materia": "Ciencias Naturales",
        "pregunta": "El instrumento para medir la temperatura es:",
        "opciones": ["A. Barómetro.", "B. Termómetro.", "C. Cronómetro.", "D. Anemómetro."],
        "respuesta": "B. Termómetro.",
        "explicacion_ia": "Mide la temperatura en grados Celsius, Fahrenheit o Kelvin."
    },
    {
        "materia": "Sociales y Ciudadanas",
        "pregunta": "¿Qué significa que el voto en Colombia es 'secreto'?",
        "opciones": ["A. Que nadie vota.", "B. Que el elector no debe revelar por quién votó y el Estado debe garantizar su privacidad.", "C. Que se vota de noche.", "D. Que el conteo es privado."],
        "respuesta": "B. Que el elector no debe revelar por quién votó y el Estado debe garantizar su privacidad.",
        "explicacion_ia": "Garantiza la libertad del elector frente a presiones externas."
    },
    {
        "materia": "Lectura Crítica",
        "pregunta": "¿Cuál es el propósito de un texto publicitario?",
        "opciones": ["A. Informar imparcialmente.", "B. Persuadir al receptor para que adquiera un producto o servicio.", "C. Educar moralmente.", "D. Narrar un cuento."],
        "respuesta": "B. Persuadir al receptor para que adquiera un producto o servicio.",
        "explicacion_ia": "Su función principal es la persuasión comercial."
    },
    {
        "materia": "Matemáticas",
        "pregunta": "En un triángulo rectángulo, el lado más largo se llama:",
        "opciones": ["A. Cateto adyacente.", "B. Cateto opuesto.", "C. Hipotenusa.", "D. Altura."],
        "respuesta": "C. Hipotenusa.",
        "explicacion_ia": "La hipotenusa siempre es el lado opuesto al ángulo de 90 grados y el de mayor longitud."
    },
    {
        "materia": "Ciencias Naturales",
        "pregunta": "¿Qué planeta es conocido como el 'Planeta Rojo'?",
        "opciones": ["A. Venus.", "B. Júpiter.", "C. Marte.", "D. Saturno."],
        "respuesta": "C. Marte.",
        "explicacion_ia": "Debido al óxido de hierro en su superficie que le da ese color."
    },
    {
        "materia": "Sociales y Ciudadanas",
        "pregunta": "La independencia de Colombia se selló definitivamente en la Batalla de:",
        "opciones": ["A. Boyacá (1819).", "B. Cartagena.", "C. Cúcuta.", "D. Palonegro."],
        "respuesta": "A. Boyacá (1819).",
        "explicacion_ia": "Ocurrió el 7 de agosto de 1819, consolidando la campaña libertadora."
    },
    {
        "materia": "Lectura Crítica",
        "pregunta": "La moraleja es característica principal de:",
        "opciones": ["A. La novela.", "B. La fábula.", "C. El ensayo.", "D. La noticia."],
        "respuesta": "B. La fábula.",
        "explicacion_ia": "Las fábulas son narraciones breves, usualmente con animales, que dejan una enseñanza final."
    },
    {
        "materia": "Matemáticas",
        "pregunta": "El 50% de un número es 40. ¿Cuál es el número?",
        "opciones": ["A. 20", "B. 60", "C. 80", "D. 100"],
        "respuesta": "C. 80",
        "explicacion_ia": "Si la mitad (50%) es 40, el total (100%) es el doble: 80."
    },
    {
        "materia": "Ciencias Naturales",
        "pregunta": "La unión de dos o más átomos forma:",
        "opciones": ["A. Un electrón.", "B. Una molécula.", "C. Un núcleo.", "D. Una célula."],
        "respuesta": "B. Una molécula.",
        "explicacion_ia": "La molécula es la partícula más pequeña de una sustancia que conserva sus propiedades químicas."
    },
    {
        "materia": "Sociales y Ciudadanas",
        "pregunta": "¿Qué función cumple la Defensoría del Pueblo?",
        "opciones": ["A. Juzgar criminales.", "B. Velar por la promoción, el ejercicio y la divulgación de los derechos humanos.", "C. Recaudar impuestos.", "D. Dirigir el ejército."],
        "respuesta": "B. Velar por la promoción, el ejercicio y la divulgación de los derechos humanos.",
        "explicacion_ia": "Es la institución encargada de defender los derechos de los habitantes ante abusos."
    },
    {
        "materia": "Lectura Crítica",
        "pregunta": "Si alguien 'se ahoga en un vaso de agua', significa que:",
        "opciones": ["A. No sabe nadar.", "B. Se complica demasiado ante un problema pequeño.", "C. Tiene mucha sed.", "D. Es muy dramático en el teatro."],
        "respuesta": "B. Se complica demasiado ante un problema pequeño.",
        "explicacion_ia": "Es una expresión idiomática sobre la falta de resiliencia ante dificultades menores."
    },
    {
        "materia": "Matemáticas",
        "pregunta": "¿Qué figura geométrica tiene todos sus puntos a la misma distancia del centro?",
        "opciones": ["A. Cuadrado.", "B. Triángulo.", "C. Círculo (Circunferencia).", "D. Rectángulo."],
        "respuesta": "C. Círculo (Circunferencia).",
        "explicacion_ia": "Es la definición geométrica de circunferencia."
    },
    {
        "materia": "Ciencias Naturales",
        "pregunta": "El cambio de estado de sólido a líquido se llama:",
        "opciones": ["A. Solidificación.", "B. Fusión.", "C. Condensación.", "D. Sublimación."],
        "respuesta": "B. Fusión.",
        "explicacion_ia": "Ocurre cuando se aplica calor al sólido hasta su punto de fusión (ej: hielo a agua)."
    },
    {
        "materia": "Sociales y Ciudadanas",
        "pregunta": "La 'Minga' es una forma de trabajo y protesta asociada principalmente a:",
        "opciones": ["A. Los sindicatos obreros.", "B. Los pueblos indígenas.", "C. Los estudiantes universitarios.", "D. Los empresarios."],
        "respuesta": "B. Los pueblos indígenas.",
        "explicacion_ia": "Es una tradición ancestral de trabajo colectivo y actualmente de movilización social indígena."
    },
    {
        "materia": "Lectura Crítica",
        "pregunta": "En 'Lloran las piedras al verlo pasar', la figura es:",
        "opciones": ["A. Hipérbole (exageración) y Personificación.", "B. Símil.", "C. Descripción técnica.", "D. Ironía."],
        "respuesta": "A. Hipérbole (exageración) y Personificación.",
        "explicacion_ia": "Exagera el dolor y atribuye llanto a objetos inanimados."
    },
    {
        "materia": "Matemáticas",
        "pregunta": "¿Cuánto es 7 al cuadrado (7²)?",
        "opciones": ["A. 14", "B. 49", "C. 21", "D. 70"],
        "respuesta": "B. 49",
        "explicacion_ia": "7 x 7 = 49."
    },
    {
        "materia": "Ciencias Naturales",
        "pregunta": "¿Qué gas respiramos principalmente del aire para vivir?",
        "opciones": ["A. Nitrógeno.", "B. Oxígeno.", "C. Helio.", "D. Carbono."],
        "respuesta": "B. Oxígeno.",
        "explicacion_ia": "Aunque el aire tiene más nitrógeno, el oxígeno es el que metabolizamos."
    },
    {
        "materia": "Sociales y Ciudadanas",
        "pregunta": "¿Cuál es la moneda oficial de Colombia?",
        "opciones": ["A. El Dólar.", "B. El Peso Colombiano.", "C. El Real.", "D. El Bolívar."],
        "respuesta": "B. El Peso Colombiano.",
        "explicacion_ia": "Es la unidad monetaria de curso legal en el país."
    },
    {
        "materia": "Lectura Crítica",
        "pregunta": "Un texto que da instrucciones para usar un electrodoméstico es:",
        "opciones": ["A. Narrativo.", "B. Argumentativo.", "C. Instructivo.", "D. Poético."],
        "respuesta": "C. Instructivo.",
        "explicacion_ia": "Guía paso a paso al usuario."
    },
    {
        "materia": "Matemáticas",
        "pregunta": "Un número primo es aquel que:",
        "opciones": ["A. Es impar.", "B. Solo es divisible por 1 y por sí mismo.", "C. Termina en 0.", "D. Es par."],
        "respuesta": "B. Solo es divisible por 1 y por sí mismo.",
        "explicacion_ia": "Ejemplos: 2, 3, 5, 7, 11."
    },
    {
        "materia": "Ciencias Naturales",
        "pregunta": "La velocidad es una magnitud que relaciona:",
        "opciones": ["A. Masa y volumen.", "B. Distancia y tiempo.", "C. Fuerza y aceleración.", "D. Temperatura y presión."],
        "respuesta": "B. Distancia y tiempo.",
        "explicacion_ia": "v = d / t."
    },
    {
        "materia": "Sociales y Ciudadanas",
        "pregunta": "La capital de Colombia es:",
        "opciones": ["A. Medellín.", "B. Cali.", "C. Bogotá.", "D. Barranquilla."],
        "respuesta": "C. Bogotá.",
        "explicacion_ia": "Bogotá D.C. es la capital y sede de los poderes públicos."
    },
    {
        "materia": "Lectura Crítica",
        "pregunta": "¿Qué es un 'eufemismo'?",
        "opciones": ["A. Una mentira.", "B. Una palabra suave para sustituir una ofensiva o dura.", "C. Un insulto.", "D. Un poema."],
        "respuesta": "B. Una palabra suave para sustituir una ofensiva o dura.",
        "explicacion_ia": "Ej: 'Pasar a mejor vida' en lugar de 'morir'."
    },
    {
        "materia": "Matemáticas",
        "pregunta": "Si x + 5 = 12, entonces x vale:",
        "opciones": ["A. 5", "B. 6", "C. 7", "D. 8"],
        "respuesta": "C. 7",
        "explicacion_ia": "12 - 5 = 7."
    },
    {
        "materia": "Ciencias Naturales",
        "pregunta": "El centro del sistema solar es:",
        "opciones": ["A. La Tierra.", "B. La Luna.", "C. El Sol.", "D. Marte."],
        "respuesta": "C. El Sol.",
        "explicacion_ia": "Es la estrella sobre la cual orbitan los planetas."
    },
    {
        "materia": "Sociales y Ciudadanas",
        "pregunta": "¿Qué es el PIB (Producto Interno Bruto)?",
        "opciones": ["A. Un banco.", "B. El valor total de bienes y servicios producidos por un país en un periodo.", "C. La deuda externa.", "D. El salario mínimo."],
        "respuesta": "B. El valor total de bienes y servicios producidos por un país en un periodo.",
        "explicacion_ia": "Es el principal indicador del tamaño de la economía."
    },
    {
        "materia": "Lectura Crítica",
        "pregunta": "La palabra 'bilingüe' tiene el prefijo 'bi' que significa:",
        "opciones": ["A. Uno.", "B. Dos.", "C. Tres.", "D. Nuevo."],
        "respuesta": "B. Dos.",
        "explicacion_ia": "Bilingüe = que habla dos lenguas."
    },
    {
        "materia": "Matemáticas",
        "pregunta": "¿Qué es 3.5 expresado en fracción?",
        "opciones": ["A. 3/5", "B. 7/2", "C. 5/3", "D. 1/2"],
        "respuesta": "B. 7/2",
        "explicacion_ia": "7 dividido entre 2 es 3.5."
    },
    {
        "materia": "Ciencias Naturales",
        "pregunta": "La parte de la planta que absorbe agua y nutrientes del suelo es:",
        "opciones": ["A. La hoja.", "B. El tallo.", "C. La raíz.", "D. La flor."],
        "respuesta": "C. La raíz.",
        "explicacion_ia": "Fija la planta y absorbe la savia bruta."
    },
    {
        "materia": "Matemáticas",
        "pregunta": "Un tanque de agua se llena mediante un grifo que vierte 20 litros por minuto. Al mismo tiempo, por una fisura, se pierden 5 litros por minuto. Si el tanque tiene una capacidad de 600 litros y está vacío, ¿en cuánto tiempo se llenará completamente?",
        "opciones": ["A. 30 minutos.", "B. 40 minutos.", "C. 60 minutos.", "D. 120 minutos."],
        "respuesta": "B. 40 minutos.",
        "explicacion_ia": "La tasa neta de llenado es lo que entra menos lo que sale: 20 - 5 = 15 litros por minuto. Para llenar 600 litros: 600 / 15 = 40 minutos."
    },
    {
        "materia": "Lectura Crítica",
        "pregunta": "En el enunciado: 'El ministro afirmó que la economía va bien, sin embargo, el desempleo aumentó', ¿qué función cumple el conector 'sin embargo'?",
        "opciones": ["A. Ratificar lo dicho anteriormente.", "B. Introducir una causa del problema económico.", "C. Introducir una objeción o contraste que debilita la afirmación inicial.", "D. Concluir la idea principal."],
        "respuesta": "C. Introducir una objeción o contraste que debilita la afirmación inicial.",
        "explicacion_ia": "'Sin embargo' es un conector adversativo. Su función es contraponer dos ideas: la percepción positiva del ministro frente al dato negativo de la realidad (desempleo)."
    },
    {
        "materia": "Sociales y Ciudadanas",
        "pregunta": "Un colegio prohíbe a un estudiante asistir a clases por llevar el cabello largo, argumentando que el Manual de Convivencia exige corte militar. La Corte Constitucional ha fallado reiteradamente que esto vulnera el derecho al:",
        "opciones": ["A. Debido proceso.", "B. Libre desarrollo de la personalidad.", "C. Libertad de cultos.", "D. Derecho al trabajo."],
        "respuesta": "B. Libre desarrollo de la personalidad.",
        "explicacion_ia": "El Manual de Convivencia no puede estar por encima de la Constitución. La apariencia personal es una decisión íntima del individuo protegida por el libre desarrollo de la personalidad, siempre que no afecte derechos de terceros."
    },
    {
        "materia": "Ciencias Naturales",
        "pregunta": "Si colocamos una célula animal en un medio muy salado (hipertónico), ¿qué fenómeno se espera que ocurra?",
        "opciones": ["A. La célula se hincha y explota (lisis).", "B. La célula pierde agua y se arruga (crenación).", "C. La célula mantiene su forma intacta.", "D. La célula comienza a dividirse."],
        "respuesta": "B. La célula pierde agua y se arruga (crenación).",
        "explicacion_ia": "Por ósmosis, el agua tiende a salir de la célula hacia donde hay mayor concentración de sal para equilibrar el medio, provocando que la célula se deshidrate y encoja."
    },
    {
        "materia": "Matemáticas",
        "pregunta": "En una rifa de 100 boletas (00 a 99), Juan compra todas las boletas que terminan en 5. ¿Cuál es la probabilidad de que Juan gane?",
        "opciones": ["A. 1/100", "B. 1/10", "C. 5/100", "D. 1/5"],
        "respuesta": "B. 1/10",
        "explicacion_ia": "Las boletas terminadas en 5 son: 05, 15, 25, 35, 45, 55, 65, 75, 85, 95. Son 10 boletas en total. La probabilidad es 10/100, que simplificado es 1/10."
    },
    {
        "materia": "Sociales y Ciudadanas",
        "pregunta": "El concepto de 'Descentralización' administrativa en Colombia implica que:",
        "opciones": ["A. El Presidente toma todas las decisiones de cada municipio.", "B. Se transfieren funciones, recursos y autoridad del nivel central a las entidades territoriales (municipios y departamentos).", "C. Se eliminan los departamentos.", "D. La capital del país se mueve a otra ciudad."],
        "respuesta": "B. Se transfieren funciones, recursos y autoridad del nivel central a las entidades territoriales (municipios y departamentos).",
        "explicacion_ia": "Busca que las regiones tengan autonomía para gestionar sus propios asuntos (salud, educación, vías) con recursos transferidos por la Nación o propios."
    },
    {
        "materia": "Lectura Crítica",
        "pregunta": "Identifique la premisa implícita en: 'Juan es político, por lo tanto, es corrupto'.",
        "opciones": ["A. Juan ha robado dinero público.", "B. Todos los políticos son corruptos.", "C. La corrupción es un delito.", "D. Juan no debería ser político."],
        "respuesta": "B. Todos los políticos son corruptos.",
        "explicacion_ia": "Para que la conclusión ('Juan es corrupto') se derive lógicamente de la premisa ('Juan es político'), es necesario asumir la generalización no dicha de que 'Todos los políticos son corruptos'."
    },
    {
        "materia": "Ciencias Naturales",
        "pregunta": "Dos objetos de diferente masa se dejan caer desde la misma altura en el vacío (sin aire). Según la física clásica:",
        "opciones": ["A. El más pesado cae más rápido.", "B. El más liviano cae más rápido.", "C. Ambos llegan al suelo al mismo tiempo.", "D. El más pesado llega primero, pero con menos velocidad."],
        "respuesta": "C. Ambos llegan al suelo al mismo tiempo.",
        "explicacion_ia": "Galileo demostró que la aceleración debida a la gravedad es constante para todos los objetos independientemente de su masa, si se ignora la resistencia del aire."
    },
    {
        "materia": "Matemáticas",
        "pregunta": "Un artículo tiene un precio base de $100. Se le aplica un IVA del 19% y luego un descuento del 10% sobre el valor total. ¿Cuál es el precio final aproximado?",
        "opciones": ["A. $109.000", "B. $107.100", "C. $119.000", "D. $100.000"],
        "respuesta": "B. $107.100",
        "explicacion_ia": "Precio con IVA: 100 + 19 = 119. Ahora descontamos el 10% de 119 (que es 11.9). 119 - 11.9 = 107.1. (Asumiendo que los valores están en miles o unidades simples, la lógica es la misma)."
    },
    {
        "materia": "Sociales y Ciudadanas",
        "pregunta": "¿Qué diferencia principal existe entre la Acción de Tutela y la Acción Popular?",
        "opciones": ["A. La Tutela protege derechos fundamentales individuales y la Popular derechos colectivos.", "B. La Popular es más rápida que la Tutela.", "C. La Tutela requiere abogado y la Popular no.", "D. No hay diferencia, son lo mismo."],
        "respuesta": "A. La Tutela protege derechos fundamentales individuales y la Popular derechos colectivos.",
        "explicacion_ia": "La Tutela es para proteger a una persona específica (ej: salud, vida). La Acción Popular protege intereses de la comunidad (ej: espacio público, medio ambiente, moralidad administrativa)."
    },
    {
        "materia": "Ciencias Naturales",
        "pregunta": "La lluvia ácida es una consecuencia de la contaminación atmosférica, principalmente por la emisión de:",
        "opciones": ["A. Oxígeno y Nitrógeno.", "B. Óxidos de azufre y nitrógeno que reaccionan con el agua.", "C. Polvo y arena.", "D. Clorofluorocarbonos (CFC)."],
        "respuesta": "B. Óxidos de azufre y nitrógeno que reaccionan con el agua.",
        "explicacion_ia": "Estos gases (SO2 y NOx) provienen de industrias y vehículos. Al mezclarse con el vapor de agua en las nubes, forman ácido sulfúrico y nítrico, que caen con la lluvia."
    },
    {
        "materia": "Lectura Crítica",
        "pregunta": "En un texto argumentativo, ¿qué es un contraargumento?",
        "opciones": ["A. Una mentira dicha por el autor.", "B. Una idea que se opone a la tesis del autor, usada para ser refutada y fortalecer la postura propia.", "C. La conclusión del texto.", "D. Un insulto al lector."],
        "respuesta": "B. Una idea que se opone a la tesis del autor, usada para ser refutada y fortalecer la postura propia.",
        "explicacion_ia": "El autor anticipa posibles objeciones ('Algunos dirán que...') para luego desmentirlas, demostrando que su tesis resiste críticas."
    },
    {
        "materia": "Matemáticas",
        "pregunta": "En un triángulo rectángulo, si un cateto mide 6 y la hipotenusa mide 10, ¿cuánto mide el otro cateto?",
        "opciones": ["A. 4", "B. 8", "C. 16", "D. 12"],
        "respuesta": "B. 8",
        "explicacion_ia": "Teorema de Pitágoras: a² + b² = c². Entonces: 6² + b² = 10². 36 + b² = 100. b² = 64. La raíz de 64 es 8."
    },
    {
        "materia": "Sociales y Ciudadanas",
        "pregunta": "La inflación afecta negativamente sobre todo a las personas de ingresos fijos porque:",
        "opciones": ["A. Aumenta sus ahorros en el banco.", "B. Disminuye su poder adquisitivo (compran menos con el mismo dinero).", "C. El gobierno les baja el sueldo.", "D. Los bancos les prestan más dinero."],
        "respuesta": "B. Disminuye su poder adquisitivo (compran menos con el mismo dinero).",
        "explicacion_ia": "Si los precios suben y el salario se mantiene igual, la cantidad real de bienes que la persona puede llevar a casa se reduce."
    },
    {
        "materia": "Ciencias Naturales",
        "pregunta": "¿Qué ley de Newton explica el 'latigazo cervical' en un accidente de auto (el cuello se va hacia atrás cuando el auto acelera bruscamente)?",
        "opciones": ["A. Segunda Ley (F=ma).", "B. Tercera Ley (Acción-Reacción).", "C. Primera Ley (Inercia).", "D. Ley de la Gravitación."],
        "respuesta": "C. Primera Ley (Inercia).",
        "explicacion_ia": "La cabeza tiende a mantener su estado de reposo (inercia) mientras el cuerpo es empujado hacia adelante por el asiento, creando la sensación de que la cabeza se va hacia atrás."
    },
    {
        "materia": "Lectura Crítica",
        "pregunta": "¿Cuál es la diferencia entre 'hecho' y 'opinión'?",
        "opciones": ["A. El hecho es subjetivo y la opinión objetiva.", "B. El hecho es comprobable y verificable; la opinión es un juicio de valor personal.", "C. No hay diferencia en el periodismo.", "D. La opinión siempre es verdadera."],
        "respuesta": "B. El hecho es comprobable y verificable; la opinión es un juicio de valor personal.",
        "explicacion_ia": "Hecho: 'Está lloviendo' (verificable). Opinión: 'Es un día feo' (juicio personal sobre la lluvia)."
    },
    {
        "materia": "Matemáticas",
        "pregunta": "Si lanzamos dos dados, ¿cuál es la probabilidad de que la suma de los puntos sea 7?",
        "opciones": ["A. 1/6", "B. 1/12", "C. 1/36", "D. 7/36"],
        "respuesta": "A. 1/6",
        "explicacion_ia": "Combinaciones que suman 7: (1,6), (2,5), (3,4), (4,3), (5,2), (6,1). Son 6 casos favorables. Total de casos: 6x6=36. Probabilidad: 6/36 = 1/6."
    },
    {
        "materia": "Sociales y Ciudadanas",
        "pregunta": "El conflicto entre el Gobierno Nacional y los sindicatos sobre el aumento del salario mínimo es un ejemplo de:",
        "opciones": ["A. Conflicto religioso.", "B. Conflicto de intereses económicos y sociales.", "C. Guerra civil.", "D. Violación de derechos humanos."],
        "respuesta": "B. Conflicto de intereses económicos y sociales.",
        "explicacion_ia": "Es una tensión democrática normal donde un grupo busca maximizar beneficios laborales y el otro controlar la inflación y el gasto, requiriendo negociación."
    },
    {
        "materia": "Ciencias Naturales",
        "pregunta": "En una red trófica, si se extinguen los descomponedores (hongos y bacterias), ¿qué consecuencia inmediata ocurriría?",
        "opciones": ["A. Aumentarían los productores.", "B. Se acumularía materia orgánica muerta y no se reciclarían nutrientes.", "C. Los carnívoros se volverían herbívoros.", "D. No pasaría nada grave."],
        "respuesta": "B. Se acumularía materia orgánica muerta y no se reciclarían nutrientes.",
        "explicacion_ia": "Los descomponedores cierran el ciclo de la materia, devolviendo nutrientes al suelo para que las plantas los usen. Sin ellos, el ciclo se rompe."
    },
    {
        "materia": "Lectura Crítica",
        "pregunta": "En la frase 'Es un secreto a voces', la figura literaria es:",
        "opciones": ["A. Metáfora.", "B. Oxímoron.", "C. Símil.", "D. Anáfora."],
        "respuesta": "B. Oxímoron.",
        "explicacion_ia": "Un oxímoron combina dos términos de significado opuesto ('secreto' vs 'a voces') para generar un nuevo sentido (algo que se supone oculto pero todos saben)."
    },
    {
        "materia": "Matemáticas",
        "pregunta": "El área de un círculo es 16π cm². ¿Cuánto mide su perímetro (circunferencia)?",
        "opciones": ["A. 8π cm", "B. 16π cm", "C. 4π cm", "D. 32 cm"],
        "respuesta": "A. 8π cm",
        "explicacion_ia": "Área = πr² = 16π -> r² = 16 -> r = 4. Perímetro = 2πr -> 2π(4) = 8π."
    },
    {
        "materia": "Sociales y Ciudadanas",
        "pregunta": "Si un alcalde decide construir una carretera atravesando un resguardo indígena sin consultarles, viola el derecho fundamental a:",
        "opciones": ["A. La libre locomoción.", "B. La Consulta Previa.", "C. La propiedad privada urbana.", "D. El voto popular."],
        "respuesta": "B. La Consulta Previa.",
        "explicacion_ia": "Las comunidades étnicas tienen derecho a ser consultadas de manera libre e informada sobre proyectos que afecten sus territorios o formas de vida."
    },
    {
        "materia": "Ciencias Naturales",
        "pregunta": "¿Por qué el hielo flota en el agua?",
        "opciones": ["A. Porque el hielo es más denso que el agua líquida.", "B. Porque el hielo es menos denso que el agua líquida.", "C. Porque tiene aire atrapado.", "D. Por la tensión superficial."],
        "respuesta": "B. Porque el hielo es menos denso que el agua líquida.",
        "explicacion_ia": "El agua es una sustancia anómala; al congelarse, sus moléculas forman una estructura cristalina hexagonal que ocupa más volumen, reduciendo su densidad."
    },
    {
        "materia": "Lectura Crítica",
        "pregunta": "El propósito principal de una columna de opinión es:",
        "opciones": ["A. Informar hechos recientes de manera neutral.", "B. Entretener con chistes.", "C. Plantear un punto de vista personal y persuadir al lector.", "D. Resumir un libro."],
        "respuesta": "C. Plantear un punto de vista personal y persuadir al lector.",
        "explicacion_ia": "A diferencia de la noticia, la columna es subjetiva y argumentativa; busca convencer o generar debate sobre una postura específica."
    },
    {
        "materia": "Matemáticas",
        "pregunta": "Si 5 obreros construyen un muro en 10 días, ¿cuántos días tardarán 10 obreros trabajando al mismo ritmo?",
        "opciones": ["A. 20 días.", "B. 5 días.", "C. 10 días.", "D. 2.5 días."],
        "respuesta": "B. 5 días.",
        "explicacion_ia": "Es una regla de tres inversa. Si duplicas la cantidad de trabajadores (fuerza laboral), el tiempo se reduce a la mitad. 5*10 = 50 (días-hombre). 50 / 10 obreros = 5 días."
    },
    {
        "materia": "Sociales y Ciudadanas",
        "pregunta": "La 'Rendición de Cuentas' es un deber de los gobernantes que consiste en:",
        "opciones": ["A. Pagar sus deudas personales.", "B. Informar y explicar a la ciudadanía sobre su gestión y el uso de recursos públicos.", "C. Renunciar al cargo.", "D. Entregar el mando al ejército."],
        "respuesta": "B. Informar y explicar a la ciudadanía sobre su gestión y el uso de recursos públicos.",
        "explicacion_ia": "Es un mecanismo de transparencia y control social para evitar la corrupción y mejorar la gestión pública."
    },
    {
        "materia": "Ciencias Naturales",
        "pregunta": "En química, un enlace covalente se caracteriza por:",
        "opciones": ["A. La transferencia total de electrones.", "B. La atracción electrostática entre iones.", "C. El compartimiento de pares de electrones entre átomos.", "D. Ocurrir solo entre metales."],
        "respuesta": "C. El compartimiento de pares de electrones entre átomos.",
        "explicacion_ia": "A diferencia del iónico (donde uno cede y otro capta), en el covalente los átomos comparten electrones para alcanzar estabilidad."
    },
    {
        "materia": "Lectura Crítica",
        "pregunta": "¿Qué indica el uso de comillas en la palabra 'amigo' en la frase: Ese 'amigo' me traicionó?",
        "opciones": ["A. Que es una cita textual.", "B. Que se usa con ironía o sentido figurado (no es un verdadero amigo).", "C. Que es un título de un libro.", "D. Que es un error ortográfico."],
        "respuesta": "B. Que se usa con ironía o sentido figurado (no es un verdadero amigo).",
        "explicacion_ia": "Las comillas irónicas señalan que la palabra no debe entenderse en su sentido literal, sino opuesto o cuestionable."
    },
    {
        "materia": "Matemáticas",
        "pregunta": "¿Cuál es la pendiente de la recta descrita por la ecuación y = -3x + 2?",
        "opciones": ["A. 2", "B. -3", "C. 3", "D. -2"],
        "respuesta": "B. -3",
        "explicacion_ia": "En la ecuación explícita de la recta (y = mx + b), el coeficiente que acompaña a la x (m) es la pendiente."
    },
    {
        "materia": "Sociales y Ciudadanas",
        "pregunta": "¿Qué implica que Colombia sea un Estado 'laico'?",
        "opciones": ["A. Que todos deben ser ateos.", "B. Que hay separación entre Iglesia y Estado, y se garantiza la libertad de cultos.", "C. Que la Iglesia Católica manda sobre el Estado.", "D. Que está prohibido rezar."],
        "respuesta": "B. Que hay separación entre Iglesia y Estado, y se garantiza la libertad de cultos.",
        "explicacion_ia": "El Estado no tiene religión oficial y debe tratar a todas las confesiones con igualdad, sin favorecer a ninguna."
    },
    {
        "materia": "Ciencias Naturales",
        "pregunta": "La selección natural favorece a los individuos que:",
        "opciones": ["A. Son más fuertes físicamente.", "B. Tienen características que les permiten adaptarse mejor a su entorno y reproducirse.", "C. Son más grandes.", "D. Viven menos tiempo."],
        "respuesta": "B. Tienen características que les permiten adaptarse mejor a su entorno y reproducirse.",
        "explicacion_ia": "No sobrevive el más fuerte, sino el que mejor se adapta al cambio (Darwin). La eficacia biológica se mide en reproducción."
    },
    {
        "materia": "Lectura Crítica",
        "pregunta": "Lea: 'Salió el sol, luego se secó la ropa'. El conector 'luego' tiene un valor:",
        "opciones": ["A. Temporal (secuencia).", "B. Adversativo (oposición).", "C. Causal (consecuencia lógica).", "D. Comparativo."],
        "respuesta": "A. Temporal (secuencia).",
        "explicacion_ia": "Indica que una acción ocurrió después de la otra en el tiempo."
    },
    {
        "materia": "Matemáticas",
        "pregunta": "La suma de dos números es 20 y su diferencia es 4. ¿Cuáles son los números?",
        "opciones": ["A. 10 y 10", "B. 12 y 8", "C. 15 y 5", "D. 14 y 6"],
        "respuesta": "B. 12 y 8",
        "explicacion_ia": "12 + 8 = 20. 12 - 8 = 4. (Sistema de ecuaciones: x+y=20, x-y=4 -> 2x=24 -> x=12)."
    },
    {
        "materia": "Sociales y Ciudadanas",
        "pregunta": "El mecanismo de 'Voto Programático' obliga a alcaldes y gobernadores a:",
        "opciones": ["A. Cumplir su plan de gobierno propuesto en campaña; si no, pueden ser revocados.", "B. Votar siempre por su partido.", "C. Programar las elecciones.", "D. Comprar votos."],
        "respuesta": "A. Cumplir su plan de gobierno propuesto en campaña; si no, pueden ser revocados.",
        "explicacion_ia": "Al inscribirse, presentan un programa. Al ser elegidos, ese programa se vuelve mandato obligatorio. El incumplimiento es causal de revocatoria."
    },
    {
        "materia": "Ciencias Naturales",
        "pregunta": "¿Qué tipo de energía se almacena en los enlaces químicos de los alimentos (como la glucosa)?",
        "opciones": ["A. Energía cinética.", "B. Energía potencial química.", "C. Energía térmica.", "D. Energía nuclear."],
        "respuesta": "B. Energía potencial química.",
        "explicacion_ia": "Es la energía potencial almacenada en la estructura molecular, que se libera al romper los enlaces durante el metabolismo."
    },
    {
        "materia": "Lectura Crítica",
        "pregunta": "La pragmática estudia:",
        "opciones": ["A. La ortografía.", "B. El significado de las palabras en el diccionario.", "C. El uso del lenguaje en contextos comunicativos específicos y la intención del hablante.", "D. La conjugación de verbos."],
        "respuesta": "C. El uso del lenguaje en contextos comunicativos específicos y la intención del hablante.",
        "explicacion_ia": "Analiza cómo el contexto influye en la interpretación (ej: entender una ironía o una orden indirecta)."
    },
    {
        "materia": "Matemáticas",
        "pregunta": "Si un cubo tiene una arista de 3 cm, ¿cuál es su volumen?",
        "opciones": ["A. 9 cm³", "B. 18 cm³", "C. 27 cm³", "D. 12 cm³"],
        "respuesta": "C. 27 cm³",
        "explicacion_ia": "El volumen de un cubo es lado al cubo (L³). 3 x 3 x 3 = 27."
    },
    {
        "materia": "Sociales y Ciudadanas",
        "pregunta": "¿Cuál es la función principal de los partidos políticos en una democracia?",
        "opciones": ["A. Repartir puestos burocráticos.", "B. Canalizar la voluntad popular, representar ideologías y presentar candidatos a elecciones.", "C. Generar violencia.", "D. Reemplazar al Estado."],
        "respuesta": "B. Canalizar la voluntad popular, representar ideologías y presentar candidatos a elecciones.",
        "explicacion_ia": "Son intermediarios entre la sociedad y el Estado, organizando las diversas opiniones políticas para acceder al poder pacíficamente."
    },
    {
        "materia": "Ciencias Naturales",
        "pregunta": "La homeostasis se refiere a:",
        "opciones": ["A. La reproducción sexual.", "B. La capacidad de un organismo para mantener su equilibrio interno estable a pesar de cambios externos.", "C. La evolución de las especies.", "D. La digestión de alimentos."],
        "respuesta": "B. La capacidad de un organismo para mantener su equilibrio interno estable a pesar de cambios externos.",
        "explicacion_ia": "Ejemplos: regular la temperatura corporal (sudar/temblar) o el nivel de azúcar en sangre."
    },
    {
        "materia": "Lectura Crítica",
        "pregunta": "En el texto 'No es que no quiera ir, es que no puedo', la segunda parte funciona como:",
        "opciones": ["A. Una justificación o argumento.", "B. Una burla.", "C. Una pregunta.", "D. Una comparación."],
        "respuesta": "A. Una justificación o argumento.",
        "explicacion_ia": "Explica la causa real (imposibilidad) para validar la negativa inicial (no ir)."
    },
    {
        "materia": "Lectura Crítica",
        "pregunta": "Lea el siguiente fragmento: 'El utilitarismo es una teoría ética que sostiene que la mejor acción es la que produce la máxima utilidad para el mayor número de personas. Sin embargo, esta visión ha sido criticada por ignorar los derechos de las minorías, pues teóricamente justificaría el sacrificio de un inocente si eso conlleva la felicidad de toda una sociedad.'\n\nA partir del texto, ¿cuál de los siguientes enunciados representa la crítica fundamental al utilitarismo mencionada?",
        "opciones": [
            "A. El utilitarismo falla porque es imposible medir cuantitativamente la felicidad de las personas.",
            "B. El utilitarismo es inválido porque prioriza el bienestar colectivo por encima de la dignidad y los derechos inalienables del individuo.",
            "C. La teoría es errónea porque asume que todas las personas buscan la felicidad de la misma manera.",
            "D. El utilitarismo es una teoría política que solo funciona en sociedades democráticas y no en dictaduras."
        ],
        "respuesta": "B. El utilitarismo es inválido porque prioriza el bienestar colectivo por encima de la dignidad y los derechos inalienables del individuo.",
        "explicacion_ia": "El texto explícitamente señala el 'sacrificio de un inocente' como ejemplo de vulneración de derechos minoritarios en favor de la mayoría, lo que corresponde a la tensión entre bienestar colectivo y dignidad individual (derechos)."
    },
    {
        "materia": "Matemáticas",
        "pregunta": "Una empresa de envíos cobra una tarifa base de $5.000 más $200 por cada kilómetro recorrido hasta los 50 km. Para distancias mayores a 50 km, la tarifa por kilómetro adicional se reduce a $150. Si un envío costó $22.500, ¿cuál fue la distancia total recorrida?",
        "opciones": [
            "A. 87.5 km",
            "B. 100 km",
            "C. 95 km",
            "D. 110 km"
        ],
        "respuesta": "B. 100 km",
        "explicacion_ia": "Costo primeros 50 km: 5.000 + (50 * 200) = 15.000. El total pagado fue 22.500, así que el excedente es 7.500 (22.500 - 15.000). Esos 7.500 se pagan a $150/km: 7.500 / 150 = 50 km adicionales. Total: 50 + 50 = 100 km."
    },
    {
        "materia": "Sociales y Ciudadanas",
        "pregunta": "En un municipio, una multinacional minera obtiene legalmente una licencia ambiental para explotar oro en una zona cercana a un resguardo indígena. La comunidad indígena bloquea la entrada de maquinaria argumentando que la explotación afectará sus fuentes de agua sagradas. El gobierno envía al ESMAD para despejar la vía alegando la libertad de empresa y el orden público. En este conflicto, ¿cuál es el derecho fundamental que el Estado está omitiendo garantizar prioritariamente a la comunidad indígena?",
        "opciones": [
            "A. El derecho al trabajo de los mineros locales.",
            "B. El derecho a la Consulta Previa, Libre e Informada.",
            "C. El derecho a la propiedad privada de la tierra.",
            "D. El derecho a la libre asociación y protesta pacífica."
        ],
        "respuesta": "B. El derecho a la Consulta Previa, Libre e Informada.",
        "explicacion_ia": "Según la Constitución y el Convenio 169 de la OIT, cualquier proyecto que afecte directamente territorios o formas de vida de comunidades étnicas requiere obligatoriamente una Consulta Previa antes de otorgar licencias, derecho que prevalece sobre la libertad de empresa en estos contextos."
    },
    {
        "materia": "Ciencias Naturales",
        "pregunta": "La fibrosis quística es una enfermedad hereditaria autosómica recesiva. Si una pareja, en la que ambos padres son portadores sanos (heterocigotos) del gen defectuoso, decide tener un hijo, ¿cuál es la probabilidad de que el niño nazca enfermo (homocigoto recesivo)?",
        "opciones": [
            "A. 100%",
            "B. 50%",
            "C. 25%",
            "D. 75%"
        ],
        "respuesta": "C. 25%",
        "explicacion_ia": "Padres Aa x Aa. Cuadro de Punnett: AA (sano), Aa (portador), Aa (portador), aa (enfermo). Solo 1 de cada 4 combinaciones resulta en el genotipo recesivo 'aa', es decir, un 25%."
    },
    {
        "materia": "Lectura Crítica",
        "pregunta": "Lea: 'La historia no es una ciencia exacta como las matemáticas; es una interpretación narrativa de hechos seleccionados. Por ende, la objetividad histórica absoluta es una quimera, pues el historiador siempre proyecta sus propios sesgos y el espíritu de su época en el pasado que describe'.\n\n¿Cuál es la tesis central del autor?",
        "opciones": [
            "A. La historia debería adoptar métodos matemáticos para ser considerada una ciencia real.",
            "B. Es imposible conocer el pasado porque no existen hechos, solo interpretaciones.",
            "C. La subjetividad del historiador es inevitable, lo que impide una neutralidad total en el relato histórico.",
            "D. Los historiadores mienten deliberadamente para manipular la opinión pública."
        ],
        "respuesta": "C. La subjetividad del historiador es inevitable, lo que impide una neutralidad total en el relato histórico.",
        "explicacion_ia": "El autor no niega la existencia de hechos (descarta B) ni acusa de mentira (descarta D), sino que argumenta que la naturaleza interpretativa de la historia hace que la 'objetividad absoluta' sea inalcanzable (una quimera)."
    },
    {
        "materia": "Matemáticas",
        "pregunta": "En un estudio epidemiológico, la probabilidad de que una persona tenga una enfermedad rara es del 1%. La prueba diagnóstica tiene una efectividad del 90% (si tienes la enfermedad, da positivo el 90% de las veces; si no la tienes, da negativo el 90% de las veces). Si una persona al azar da positivo en el test, ¿es seguro afirmar que tiene la enfermedad?",
        "opciones": [
            "A. Sí, porque la prueba tiene una alta efectividad del 90%.",
            "B. No, porque es necesario repetir la prueba tres veces para confirmar.",
            "C. No, debido a la alta tasa de falsos positivos en comparación con la baja prevalencia de la enfermedad (Teorema de Bayes).",
            "D. Sí, pero solo si la persona presenta síntomas visibles."
        ],
        "respuesta": "C. No, debido a la alta tasa de falsos positivos en comparación con la baja prevalencia de la enfermedad (Teorema de Bayes).",
        "explicacion_ia": "Al ser la enfermedad tan rara (1%), la gran mayoría de los positivos vendrán del 10% de error de las personas sanas (falsos positivos). Matemáticamente, la probabilidad real de estar enfermo dado un positivo es muy baja (cerca del 8-9%)."
    },
    {
        "materia": "Sociales y Ciudadanas",
        "pregunta": "Durante el siglo XIX, el librecambismo defendido por los liberales radicales chocó con el proteccionismo de los artesanos y conservadores. Si hoy Colombia decidiera imponer aranceles altos a todas las importaciones tecnológicas para desarrollar una industria nacional propia desde cero, ¿cuál sería una consecuencia económica negativa inmediata probable bajo la lógica de la globalización actual?",
        "opciones": [
            "A. El florecimiento inmediato de la industria tecnológica nacional y la generación de empleo masivo.",
            "B. El aislamiento comercial, encarecimiento de bienes tecnológicos y pérdida de competitividad de las empresas locales que dependen de dicha tecnología.",
            "C. La disminución de la deuda externa y el fortalecimiento del peso frente al dólar.",
            "D. El aumento de la inversión extranjera directa interesada en el mercado cerrado."
        ],
        "respuesta": "B. El aislamiento comercial, encarecimiento de bienes tecnológicos y pérdida de competitividad de las empresas locales que dependen de dicha tecnología.",
        "explicacion_ia": "En una economía interconectada, cerrar fronteras (proteccionismo extremo) encarece los insumos que no se producen localmente, haciendo que las empresas nacionales sean menos eficientes y los consumidores paguen más."
    },
    {
        "materia": "Ciencias Naturales",
        "pregunta": "Un buzo se sumerge en el mar. A medida que desciende, siente mayor presión en sus oídos. Si sabemos que la presión hidrostática depende de la densidad del fluido, la gravedad y la profundidad, ¿qué gráfico representaría mejor la relación entre la Presión (eje Y) y la Profundidad (eje X)?",
        "opciones": [
            "A. Una línea recta ascendente que parte desde el origen (0,0).",
            "B. Una línea recta ascendente que parte desde un valor positivo en Y (Presión atmosférica).",
            "C. Una curva exponencial creciente.",
            "D. Una línea horizontal constante."
        ],
        "respuesta": "B. Una línea recta ascendente que parte desde un valor positivo en Y (Presión atmosférica).",
        "explicacion_ia": "La relación es lineal (P = Patm + d*g*h). Sin embargo, en la superficie (profundidad 0) la presión no es cero, sino que existe la presión atmosférica, por lo que la recta no parte del origen."
    },
    {
        "materia": "Lectura Crítica",
        "pregunta": "En la novela '1984' de George Orwell, el gobierno modifica el lenguaje (neolengua) para eliminar palabras que expresen rebelión, argumentando que 'si no existe la palabra para expresar una idea, la idea misma se vuelve impensable'.\n\n¿Qué premisa sobre la relación entre lenguaje y pensamiento subyace en este argumento?",
        "opciones": [
            "A. El pensamiento es independiente del lenguaje y las palabras son solo etiquetas.",
            "B. El lenguaje determina y limita la capacidad de pensamiento conceptual (Determinismo lingüístico).",
            "C. El lenguaje evoluciona naturalmente sin importar la intervención estatal.",
            "D. La política no tiene influencia real sobre la gramática."
        ],
        "respuesta": "B. El lenguaje determina y limita la capacidad de pensamiento conceptual (Determinismo lingüístico).",
        "explicacion_ia": "Se basa en la hipótesis de Sapir-Whorf (versión fuerte), que sugiere que la estructura de una lengua moldea o limita la forma en que sus hablantes perciben y conceptualizan el mundo."
    },
    {
        "materia": "Matemáticas",
        "pregunta": "Se tiene un cuadrado de lado L. Si se inscriben cuatro círculos iguales dentro del cuadrado de tal forma que sean tangentes entre sí y a los lados del cuadrado, ¿qué porcentaje aproximado del área del cuadrado queda sin cubrir (espacio vacío)?",
        "opciones": [
            "A. 0% (cubren todo).",
            "B. Aproximadamente 21.5%.",
            "C. Exactamente 50%.",
            "D. Aproximadamente 10%.",
        ],
        "respuesta": "B. Aproximadamente 21.5%.",
        "explicacion_ia": "Área cuadrado = L². Radio de círculos = L/4. Área de 4 círculos = 4 * π * (L/4)² = πL²/4. El área ocupada es π/4 del cuadrado (aprox 0.785 o 78.5%). El espacio vacío es 100% - 78.5% = 21.5%."
    },
    {
        "materia": "Sociales y Ciudadanas",
        "pregunta": "El artículo 13 de la Constitución establece que 'el Estado promoverá las condiciones para que la igualdad sea real y efectiva y adoptará medidas en favor de grupos discriminados o marginados'. Este principio justifica la implementación de:",
        "opciones": [
            "A. Impuestos iguales para todos sin importar sus ingresos.",
            "B. Acciones Afirmativas (ej: cupos especiales en universidades para minorías).",
            "C. La eliminación de todos los subsidios estatales.",
            "D. La prohibición de la propiedad privada."
        ],
        "respuesta": "B. Acciones Afirmativas (ej: cupos especiales en universidades para minorías).",
        "explicacion_ia": "La 'igualdad material' implica tratar desigual a los desiguales para cerrar brechas históricas. Las acciones afirmativas son herramientas constitucionales para lograr esa equidad."
    },
    {
        "materia": "Ciencias Naturales",
        "pregunta": "En una reacción química en equilibrio A + B ↔ C + Calor, ¿qué sucede si aumentamos la temperatura del sistema según el Principio de Le Chatelier?",
        "opciones": [
            "A. Se favorece la formación de más productos (C).",
            "B. El equilibrio se desplaza hacia la izquierda, favoreciendo los reactivos (A y B).",
            "C. La reacción se detiene completamente.",
            "D. La constante de equilibrio no cambia."
        ],
        "respuesta": "B. El equilibrio se desplaza hacia la izquierda, favoreciendo los reactivos (A y B).",
        "explicacion_ia": "Como la reacción libera calor (exotérmica), el calor actúa como un producto. Si añadimos calor (subimos temperatura), el sistema intentará contrarrestarlo consumiéndolo, desplazando el equilibrio hacia la izquierda (reactivos)."
    },
    {
        "materia": "Lectura Crítica",
        "pregunta": "Lea: 'La democracia es la peor forma de gobierno, a excepción de todas las demás que se han ensayado'. (Winston Churchill).\n\n¿Qué implica esta afirmación paradójica?",
        "opciones": [
            "A. Que la democracia es un sistema perfecto y sin fallas.",
            "B. Que deberíamos probar nuevas formas de dictadura.",
            "C. Que aunque la democracia tiene defectos y problemas, sigue siendo preferible a cualquier alternativa autoritaria conocida.",
            "D. Que Churchill odiaba la política."
        ],
        "respuesta": "C. Que aunque la democracia tiene defectos y problemas, sigue siendo preferible a cualquier alternativa autoritaria conocida.",
        "explicacion_ia": "Es una defensa realista de la democracia: no se idealiza como perfecta, sino como el 'mal menor' o la mejor opción pragmática frente a otras formas de gobierno históricas."
    },
    {
        "materia": "Matemáticas",
        "pregunta": "Un cultivo de bacterias se duplica cada hora. Si inicialmente hay 100 bacterias, ¿cuántas habrá al cabo de 5 horas y qué tipo de crecimiento representa?",
        "opciones": [
            "A. 500 bacterias; Crecimiento Lineal.",
            "B. 3.200 bacterias; Crecimiento Exponencial.",
            "C. 600 bacterias; Crecimiento Aritmético.",
            "D. 1.000 bacterias; Crecimiento Logarítmico."
        ],
        "respuesta": "B. 3.200 bacterias; Crecimiento Exponencial.",
        "explicacion_ia": "Fórmula: Valor final = Inicial * 2^tiempo. 100 * 2^5 = 100 * 32 = 3.200. Al multiplicarse por un factor constante en intervalos iguales, es un crecimiento exponencial."
    },
    {
        "materia": "Sociales y Ciudadanas",
        "pregunta": "En un país ficticio, el Presidente decreta el estado de sitio y cierra el Congreso indefinidamente para 'restablecer el orden'. Además, ordena detener a los líderes de la oposición sin orden judicial. Estas acciones son características típicas de:",
        "opciones": [
            "A. Un Estado Social de Derecho.",
            "B. Una Monarquía Parlamentaria.",
            "C. Un Régimen Totalitario o Dictatorial.",
            "D. Una Democracia Participativa."
        ],
        "respuesta": "C. Un Régimen Totalitario o Dictatorial.",
        "explicacion_ia": "La concentración de poderes (cierre del legislativo), la eliminación de garantías judiciales (detenciones arbitrarias) y la persecución política son rasgos definitorios de una ruptura democrática y el establecimiento de una dictadura."
    },
    {
        "materia": "Ciencias Naturales",
        "pregunta": "Un paracaidista salta de un avión. Antes de abrir el paracaídas, llega un momento en que su velocidad deja de aumentar y se vuelve constante (velocidad terminal). ¿Por qué ocurre esto si la gravedad lo sigue empujando hacia abajo?",
        "opciones": [
            "A. Porque la gravedad deja de actuar a cierta altura.",
            "B. Porque la fuerza de resistencia del aire iguala a la fuerza del peso, anulando la aceleración.",
            "C. Porque el paracaidista se cansa de caer.",
            "D. Porque la masa del paracaidista disminuye al caer."
        ],
        "respuesta": "B. Porque la fuerza de resistencia del aire iguala a la fuerza del peso, anulando la aceleración.",
        "explicacion_ia": "Según la 1ª Ley de Newton, si las fuerzas están equilibradas (Fuerza neta = 0), el objeto no acelera. Aquí, la fricción del aire hacia arriba iguala el peso hacia abajo, logrando velocidad constante."
    },
    {
        "materia": "Lectura Crítica",
        "pregunta": "En un ensayo sobre educación, el autor afirma: 'Evaluar a un pez por su capacidad para trepar árboles es condenarlo a creerse inútil toda su vida'. Esta analogía busca criticar:",
        "opciones": [
            "A. La enseñanza de biología en las escuelas.",
            "B. La falta de deportes acuáticos en el currículo.",
            "C. La estandarización de las pruebas educativas que no consideran las inteligencias múltiples ni los talentos individuales.",
            "D. La crueldad animal en los laboratorios."
        ],
        "respuesta": "C. La estandarización de las pruebas educativas que no consideran las inteligencias múltiples ni los talentos individuales.",
        "explicacion_ia": "La metáfora ilustra el error de usar un único criterio de evaluación estandarizado para medir a individuos con capacidades y naturalezas diversas."
    },
    {
        "materia": "Matemáticas",
        "pregunta": "Se lanzan dos dados honestos de 6 caras. ¿Cuál es la probabilidad de que la suma de los resultados sea un número primo?",
        "opciones": [
            "A. 15/36",
            "B. 1/2",
            "C. 5/12",
            "D. 7/12"
        ],
        "respuesta": "A. 15/36",
        "explicacion_ia": "Primos posibles (min 2, max 12): 2, 3, 5, 7, 11. Casos: (1,1), (1,2), (2,1), (1,4), (4,1), (2,3), (3,2), (1,6), (6,1), (2,5), (5,2), (3,4), (4,3), (5,6), (6,5). Total 15 casos favorables sobre 36 posibles."
    },
    {
        "materia": "Sociales y Ciudadanas",
        "pregunta": "La Corte Penal Internacional (CPI) es un tribunal de última instancia encargado de juzgar crímenes graves internacionales. ¿En qué caso tendría competencia la CPI para intervenir en Colombia?",
        "opciones": [
            "A. Si un ciudadano roba un banco y huye del país.",
            "B. Si el Estado colombiano no quiere o no puede juzgar genuinamente crímenes de lesa humanidad o genocidio ocurridos en su territorio.",
            "C. Si hay una disputa de límites marítimos con Nicaragua.",
            "D. Si el presidente decide subir el IVA sin permiso del Congreso."
        ],
        "respuesta": "B. Si el Estado colombiano no quiere o no puede juzgar genuinamente crímenes de lesa humanidad o genocidio ocurridos en su territorio.",
        "explicacion_ia": "La CPI opera bajo el 'Principio de Complementariedad'. Solo interviene si la justicia nacional falla, es inoperante o simula juicios para garantizar la impunidad en crímenes atroces."
    },
    {
        "materia": "Ciencias Naturales",
        "pregunta": "El principio de conservación de la energía mecánica establece que, en ausencia de rozamiento, la energía mecánica total (cinética + potencial) permanece constante. Si lanzamos una pelota verticalmente hacia arriba, a medida que sube:",
        "opciones": [
            "A. Aumenta su energía cinética y disminuye su energía potencial.",
            "B. Disminuye su energía cinética y aumenta su energía potencial.",
            "C. Ambas energías aumentan simultáneamente.",
            "D. La energía mecánica total disminuye hasta llegar a cero en la altura máxima."
        ],
        "respuesta": "B. Disminuye su energía cinética y aumenta su energía potencial.",
        "explicacion_ia": "Al subir, la velocidad disminuye (menos energía cinética) pero la altura aumenta (más energía potencial gravitatoria). La suma de ambas se mantiene igual."
    },
    {
        "materia": "Matemáticas",
        "pregunta": "Un inversionista deposita $1.000.000 en una cuenta que ofrece un interés compuesto del 10% anual. A diferencia del interés simple, donde el interés se calcula siempre sobre el capital inicial, en el compuesto los intereses se suman al capital para generar nuevos intereses. ¿Cuánto dinero tendrá al final del segundo año?",
        "opciones": [
            "A. $1.200.000",
            "B. $1.210.000",
            "C. $1.100.000",
            "D. $1.020.000"
        ],
        "respuesta": "B. $1.210.000",
        "explicacion_ia": "Año 1: 1.000.000 + 10% = 1.100.000. Año 2: Se calcula el 10% sobre 1.100.000 (que es 110.000). Total final: 1.100.000 + 110.000 = 1.210.000."
    },
    {
        "materia": "Lectura Crítica",
        "pregunta": "Lea: 'La tolerancia ilimitada lleva a la desaparición de la tolerancia. Si extendemos la tolerancia ilimitada aun a aquellos que son intolerantes, si no nos hallamos preparados para defender una sociedad tolerante contra las tropelías de los intolerantes, el resultado será la destrucción de los tolerantes y, junto con ellos, de la tolerancia.' (Karl Popper, La paradoja de la tolerancia).\n\n¿Cuál es la conclusión lógica del autor?",
        "opciones": [
            "A. Que debemos tolerar absolutamente todas las ideas para ser democráticos.",
            "B. Que la intolerancia es necesaria para el progreso social.",
            "C. Que, paradójicamente, para mantener una sociedad tolerante, la sociedad debe reservarse el derecho a no tolerar la intolerancia extrema.",
            "D. Que la tolerancia es una debilidad de las sociedades modernas."
        ],
        "respuesta": "C. Que, paradójicamente, para mantener una sociedad tolerante, la sociedad debe reservarse el derecho a no tolerar la intolerancia extrema.",
        "explicacion_ia": "Popper argumenta que la tolerancia absoluta es autodestructiva; por tanto, el límite de la tolerancia debe ser la intolerancia que amenaza la convivencia misma."
    },
    {
        "materia": "Sociales y Ciudadanas",
        "pregunta": "En el marco de la Constitución de 1991, el Banco de la República es un órgano autónomo e independiente del Gobierno. Su función principal es controlar la inflación (mantener el poder adquisitivo de la moneda). Si el Gobierno le ordenara al Banco imprimir billetes masivamente para pagar sus deudas, el Banco debería:",
        "opciones": [
            "A. Obedecer inmediatamente porque el Presidente es la máxima autoridad.",
            "B. Negarse, pues la emisión descontrolada genera hiperinflación y va en contra de su mandato constitucional.",
            "C. Aceptar, pero solo si el Congreso lo aprueba.",
            "D. Consultar a la Corte Suprema de Justicia."
        ],
        "respuesta": "B. Negarse, pues la emisión descontrolada genera hiperinflación y va en contra de su mandato constitucional.",
        "explicacion_ia": "La autonomía del Banco Central existe precisamente para evitar que los gobiernos de turno manipulen la moneda con fines políticos a corto plazo, lo que destruiría la economía a largo plazo."
    },
    {
        "materia": "Ciencias Naturales",
        "pregunta": "El uso indiscriminado de antibióticos ha generado la aparición de 'superbacterias' resistentes. Desde el punto de vista de la evolución darwiniana, ¿cómo ocurre este fenómeno?",
        "opciones": [
            "A. El antibiótico entrena a las bacterias para que aprendan a defenderse.",
            "B. El antibiótico causa mutaciones en todas las bacterias para salvarlas.",
            "C. En la población bacteriana existen variantes resistentes por azar; al aplicar el antibiótico, mueren las débiles y solo sobreviven y se reproducen las resistentes (selección natural).",
            "D. Las bacterias deciden volverse fuertes al ver el peligro."
        ],
        "respuesta": "C. En la población bacteriana existen variantes resistentes por azar; al aplicar el antibiótico, mueren las débiles y solo sobreviven y se reproducen las resistentes (selección natural).",
        "explicacion_ia": "Es un ejemplo clásico de selección natural. El antibiótico actúa como presión selectiva: no crea la resistencia, sino que selecciona a las que ya la tenían genéticamente, permitiendo que estas proliferen."
    },
    {
        "materia": "Matemáticas",
        "pregunta": "Una urna contiene 3 bolas rojas y 2 bolas azules. Si sacamos dos bolas SIN reposición (sacamos una y no la devolvemos), ¿cuál es la probabilidad de que ambas sean rojas?",
        "opciones": [
            "A. 9/25",
            "B. 3/10",
            "C. 3/5",
            "D. 1/10"
        ],
        "respuesta": "B. 3/10",
        "explicacion_ia": "Probabilidad 1ª roja: 3/5. Al sacar una, quedan 4 bolas en total y 2 rojas. Probabilidad 2ª roja: 2/4 (o 1/2). Probabilidad conjunta: 3/5 * 1/2 = 3/10."
    },
    {
        "materia": "Sociales y Ciudadanas",
        "pregunta": "Un periodista publica una investigación sobre corrupción en la alcaldía. El alcalde lo demanda por 'dañar su buen nombre'. En este caso, al ponderar derechos, la Corte Constitucional generalmente da prelación a:",
        "opciones": [
            "A. El buen nombre del alcalde, porque es una autoridad.",
            "B. La libertad de prensa y el derecho a la información, siempre que lo publicado sea veraz y de interés público.",
            "C. La censura previa para evitar escándalos.",
            "D. El derecho al olvido del funcionario."
        ],
        "respuesta": "B. La libertad de prensa y el derecho a la información, siempre que lo publicado sea veraz y de interés público.",
        "explicacion_ia": "En democracias, los funcionarios públicos están expuestos a un mayor escrutinio. La libertad de prensa prevalece sobre el buen nombre si la información es veraz, imparcial y de relevancia social."
    },
    {
        "materia": "Ciencias Naturales",
        "pregunta": "Si lanzamos una pelota en la Luna, esta llegará más lejos y más alto que si la lanzamos con la misma fuerza en la Tierra. Esto se debe principalmente a que:",
        "opciones": [
            "A. En la Luna no hay gravedad.",
            "B. En la Luna la gravedad es menor (aprox. 1/6 de la terrestre) y no hay resistencia del aire.",
            "C. La pelota pierde masa en el viaje a la Luna.",
            "D. La Tierra gira más rápido que la Luna."
        ],
        "respuesta": "B. En la Luna la gravedad es menor (aprox. 1/6 de la terrestre) y no hay resistencia del aire.",
        "explicacion_ia": "La gravedad lunar es más débil, lo que desacelera menos el objeto hacia abajo, y la ausencia de atmósfera elimina la fricción, permitiendo un movimiento parabólico perfecto y más extenso."
    },
    {
        "materia": "Lectura Crítica",
        "pregunta": "Identifique la falacia en el siguiente argumento: 'No le crean a las propuestas económicas de ese candidato, recuerden que él fue infiel a su esposa y es un mal padre'.",
        "opciones": [
            "A. Falacia de Autoridad.",
            "B. Falacia Ad Hominem (contra el hombre).",
            "C. Falacia de Generalización apresurada.",
            "D. Falacia del Hombre de Paja."
        ],
        "respuesta": "B. Falacia Ad Hominem (contra el hombre).",
        "explicacion_ia": "En lugar de atacar los argumentos económicos del candidato (el tema en cuestión), se ataca su carácter personal o vida privada para desacreditarlo, lo cual es irrelevante para la validez de su plan económico."
    },
    {
        "materia": "Matemáticas",
        "pregunta": "En un mapa a escala, la distancia entre dos ciudades es 5 cm. Si la escala es 1:500.000, ¿cuántos kilómetros separan a las ciudades en la realidad?",
        "opciones": [
            "A. 2.5 km",
            "B. 25 km",
            "C. 250 km",
            "D. 50 km"
        ],
        "respuesta": "B. 25 km",
        "explicacion_ia": "5 cm * 500.000 = 2.500.000 cm. Para pasar a metros, dividimos por 100 (25.000 m). Para pasar a kilómetros, dividimos por 1.000 (25 km)."
    },
    {
        "materia": "Sociales y Ciudadanas",
        "pregunta": "La Jurisdicción Especial para la Paz (JEP) en Colombia tiene como objetivo principal:",
        "opciones": [
            "A. Juzgar delitos comunes como el hurto de celulares.",
            "B. Satisfacer los derechos de las víctimas a la verdad, justicia, reparación y no repetición en el marco del conflicto armado.",
            "C. Perseguir a los opositores políticos del gobierno.",
            "D. Reemplazar a la Corte Suprema de Justicia en todos los casos."
        ],
        "respuesta": "B. Satisfacer los derechos de las víctimas a la verdad, justicia, reparación y no repetición en el marco del conflicto armado.",
        "explicacion_ia": "La JEP es el componente de justicia del Sistema Integral de Verdad, Justicia, Reparación y No Repetición, enfocado en los crímenes más graves cometidos durante el conflicto armado."
    },
    {
        "materia": "Ciencias Naturales",
        "pregunta": "El pH de la sangre humana debe mantenerse estable entre 7.35 y 7.45. Si baja de 7.35 se produce una acidosis. El cuerpo utiliza sistemas 'buffer' o amortiguadores (como el bicarbonato) para:",
        "opciones": [
            "A. Aumentar drásticamente la temperatura.",
            "B. Neutralizar los cambios bruscos de acidez o alcalinidad absorbiendo o liberando iones de hidrógeno.",
            "C. Eliminar toda el agua de la sangre.",
            "D. Detener la circulación."
        ],
        "respuesta": "B. Neutralizar los cambios bruscos de acidez o alcalinidad absorbiendo o liberando iones de hidrógeno.",
        "explicacion_ia": "Los amortiguadores químicos son vitales en la homeostasis, evitando que el pH fluctúe peligrosamente ante la adición de ácidos o bases metabólicos."
    },
    {
        "materia": "Lectura Crítica",
        "pregunta": "Si un texto compara 'la estructura de una novela' con 'los planos de un edificio', el autor está utilizando:",
        "opciones": [
            "A. Una hipérbole.",
            "B. Una analogía.",
            "C. Una contradicción.",
            "D. Una ironía."
        ],
        "respuesta": "B. Una analogía.",
        "explicacion_ia": "La analogía establece una relación de semejanza entre dos cosas distintas (novela y edificio) para explicar una idea (la importancia de la estructura y planificación)."
    },
    {
        "materia": "Matemáticas",
        "pregunta": "El promedio de estatura de 5 jugadores de baloncesto es 1.90 m. Si entra un sexto jugador que mide 2.02 m, ¿cuál es el nuevo promedio del equipo?",
        "opciones": [
            "A. 1.96 m",
            "B. 1.92 m",
            "C. 1.95 m",
            "D. 2.00 m"
        ],
        "respuesta": "B. 1.92 m",
        "explicacion_ia": "Suma de estaturas inicial: 5 * 1.90 = 9.50 m. Nueva suma con el sexto: 9.50 + 2.02 = 11.52 m. Nuevo promedio: 11.52 / 6 = 1.92 m."
    },
    {
        "materia": "Sociales y Ciudadanas",
        "pregunta": "Un grupo de ciudadanos decide dejar de pagar impuestos argumentando que el gobierno es corrupto. Esta acción se clasifica teóricamente como:",
        "opciones": [
            "A. Delincuencia común.",
            "B. Objeción de conciencia o Desobediencia Civil.",
            "C. Participación democrática.",
            "D. Voto en blanco."
        ],
        "respuesta": "B. Objeción de conciencia o Desobediencia Civil.",
        "explicacion_ia": "La desobediencia civil es el acto público, no violento y consciente de incumplir una ley para protestar contra una injusticia, asumiendo las consecuencias legales."
    },
    {
        "materia": "Ciencias Naturales",
        "pregunta": "En un circuito eléctrico en serie, si se funde una de las bombillas:",
        "opciones": [
            "A. Las demás bombillas brillan más fuerte.",
            "B. Se interrumpe el flujo de corriente y todas las demás se apagan.",
            "C. Las demás siguen encendidas sin problemas.",
            "D. Se genera un cortocircuito."
        ],
        "respuesta": "B. Se interrumpe el flujo de corriente y todas las demás se apagan.",
        "explicacion_ia": "En un circuito en serie, hay un solo camino para la corriente. Si un componente falla, el circuito se abre y la electricidad deja de fluir por todo el sistema."
    },
    {
        "materia": "Lectura Crítica",
        "pregunta": "En la frase: 'Vi a la mujer que me cuidó con el telescopio', se presenta un vicio del lenguaje conocido como anfibología o ambigüedad porque:",
        "opciones": [
            "A. La palabra telescopio está mal escrita.",
            "B. No se entiende si él vio a la mujer usando un telescopio, o si la mujer lo cuidó usando un telescopio.",
            "C. Es una oración demasiado larga.",
            "D. Falta una tilde."
        ],
        "respuesta": "B. No se entiende si él vio a la mujer usando un telescopio, o si la mujer lo cuidó usando un telescopio.",
        "explicacion_ia": "La estructura gramatical permite dos interpretaciones distintas, creando confusión sobre quién tenía el telescopio o cómo se realizó la acción."
    },
    {
        "materia": "Matemáticas",
        "pregunta": "Si el lado de un cuadrado aumenta en un 10%, ¿en qué porcentaje aumenta su área?",
        "opciones": [
            "A. 10%",
            "B. 20%",
            "C. 21%",
            "D. 100%"
        ],
        "respuesta": "C. 21%",
        "explicacion_ia": "Supongamos lado = 10 (Área = 100). Nuevo lado = 11 (aumentó 10%). Nueva área = 11*11 = 121. De 100 a 121 hay un aumento del 21%."
    },
    {
        "materia": "Sociales y Ciudadanas",
        "pregunta": "La 'Jurisdicción Especial Indígena' permite que las autoridades de los pueblos indígenas ejerzan funciones judiciales dentro de su territorio. Sin embargo, esta autonomía tiene un límite: no pueden violar:",
        "opciones": [
            "A. Los códigos de policía municipales.",
            "B. La Constitución y las leyes de la República en lo referente a Derechos Humanos fundamentales (ej: no pena de muerte, no tortura).",
            "C. Las normas de tránsito.",
            "D. Las costumbres occidentales."
        ],
        "respuesta": "B. La Constitución y las leyes de la República en lo referente a Derechos Humanos fundamentales (ej: no pena de muerte, no tortura).",
        "explicacion_ia": "La autonomía indígena es amplia pero no absoluta; debe respetar el núcleo esencial de los Derechos Humanos y la Constitución (ej: no se permiten castigos como la lapidación o la pena de muerte)."
    },
    {
        "materia": "Ciencias Naturales",
        "pregunta": "La entalpía es una magnitud termodinámica. Si una reacción química tiene una variación de entalpía negativa (ΔH < 0), significa que:",
        "opciones": [
            "A. La reacción absorbe calor (Endotérmica).",
            "B. La reacción libera calor al entorno (Exotérmica).",
            "C. La reacción no ocurre.",
            "D. La reacción es nuclear."
        ],
        "respuesta": "B. La reacción libera calor al entorno (Exotérmica).",
        "explicacion_ia": "Un cambio de entalpía negativo indica que el sistema perdió energía en forma de calor hacia los alrededores (ej: una combustión)."
    },
    {
        "materia": "Lectura Crítica",
        "pregunta": "Lea: 'El gobierno anunció medidas de austeridad. El pueblo, sin embargo, interpretó el silencio del presidente como una señal de indiferencia'.\n¿Qué concepto de la comunicación falla en esta situación?",
        "opciones": [
            "A. El canal.",
            "B. El código.",
            "C. La decodificación o interpretación del mensaje (y del silencio como mensaje).",
            "D. El ruido físico."
        ],
        "respuesta": "C. La decodificación o interpretación del mensaje (y del silencio como mensaje).",
        "explicacion_ia": "El problema radica en cómo el receptor (pueblo) interpreta (decodifica) la ausencia de comunicación verbal del emisor (presidente), asignándole un significado negativo (indiferencia)."
    },
    {
        "materia": "Ciencias Naturales",
        "pregunta": "¿Cuál es el órgano principal del sistema circulatorio encargado de bombear sangre?",
        "opciones": ["A. Pulmones.", "B. Hígado.", "C. Corazón.", "D. Riñón."],
        "respuesta": "C. Corazón.",
        "explicacion_ia": "El corazón funciona como una bomba muscular doble que impulsa la sangre a través de los vasos sanguíneos hacia todo el cuerpo."
    },
    {
        "materia": "Lectura Crítica",
        "pregunta": "Lea el siguiente texto:\n\n'Nadie es justo por voluntad, sino porque no tiene el poder de ser injusto. Esto lo percibiremos mejor si nos imaginamos las cosas del siguiente modo: demos a dos hombres, uno justo y otro injusto, el poder de hacer lo que quieran; luego, sigámoslos para observar hasta dónde los lleva sus deseos. Sorprenderemos al hombre justo tomando el mismo camino que el injusto, movido por la codicia, que toda naturaleza persigue como un bien, aunque la ley obligue por fuerza a respetar la igualdad. La libertad de la que hablo sería total si tuvieran el poder que, según se cuenta, tuvo Giges. Se dice que era un pastor y que, tras una tormenta, encontró un anillo de oro. Al girar el engaste hacia adentro de su mano, se volvía invisible. Comprobado esto, logró seducir a la reina, matar al rey y apoderarse del trono'. (Platón, La República).\n\nSegún el texto anterior, ¿cuál es la tesis principal sobre la naturaleza humana?",
        "opciones": [
            "A. La justicia es una virtud innata que solo se pierde cuando el hombre obtiene demasiado poder.",
            "B. La invisibilidad física es la única condición necesaria para que un hombre cometa crímenes atroces.",
            "C. La justicia es una construcción social impuesta por la ley, ya que la naturaleza humana tiende instintivamente a la injusticia y la codicia si se le garantiza impunidad.",
            "D. La historia de Giges demuestra que los pastores son más propensos a la corrupción que los reyes."
        ],
        "respuesta": "C. La justicia es una construcción social impuesta por la ley, ya que la naturaleza humana tiende instintivamente a la injusticia y la codicia si se le garantiza impunidad.",
        "explicacion_ia": "El texto argumenta que 'nadie es justo por voluntad', y que si se elimina el miedo al castigo (como con el anillo de invisibilidad), tanto el justo como el injusto actuarían igual de mal, guiados por la codicia natural."
    },
    {
        "materia": "Sociales y Ciudadanas",
        "pregunta": "Contexto: En un municipio de vocación agrícola, una empresa multinacional descubre un yacimiento de petróleo. El Gobierno Nacional, dueño del subsuelo según la Constitución, otorga la licencia de explotación argumentando que las regalías beneficiarán a todo el país. Sin embargo, el Concejo Municipal organiza una consulta popular donde el 98% de la población vota 'NO' a la minería, alegando que contaminará sus fuentes de agua y acabará con la agricultura, su modo de vida tradicional. Se genera un choque entre la decisión local y la nacional.\n\nEn este escenario, ¿cuál es la tensión constitucional principal que debe resolver la Corte?",
        "opciones": [
            "A. La tensión entre el derecho al trabajo de los ingenieros de petróleos y el derecho a la alimentación de los campesinos.",
            "B. La tensión entre el principio de Estado Unitario (propiedad del subsuelo nacional) y el principio de Autonomía Territorial (capacidad de los municipios para decidir sobre el uso de su suelo).",
            "C. La tensión entre la libertad de empresa privada y el derecho a la huelga.",
            "D. La tensión entre la democracia representativa y la dictadura."
        ],
        "respuesta": "B. La tensión entre el principio de Estado Unitario (propiedad del subsuelo nacional) y el principio de Autonomía Territorial (capacidad de los municipios para decidir sobre el uso de su suelo).",
        "explicacion_ia": "Este es un conflicto clásico en la jurisprudencia colombiana. El Estado central es dueño de lo que está bajo tierra (subsuelo), pero el municipio decide qué pasa sobre la tierra (suelo). La Corte debe armonizar ambos poderes."
    },
    {
        "materia": "Ciencias Naturales",
        "pregunta": "Un grupo de científicos estudia el efecto de un fertilizante nitrogenado en un lago cercano a cultivos. Observan la siguiente secuencia de eventos:\n1. Las lluvias arrastran el exceso de fertilizante al lago.\n2. Se produce un crecimiento explosivo de algas en la superficie (bloom algal).\n3. Las algas superficiales bloquean la luz solar, impidiendo la fotosíntesis de las plantas del fondo.\n4. Las plantas del fondo mueren.\n5. Las bacterias descomponen la materia muerta, consumiendo grandes cantidades de oxígeno en el proceso.\n6. Finalmente, los peces mueren masivamente.\n\nSegún esta secuencia, conocida como eutrofización, ¿cuál es la causa directa inmediata de la muerte de los peces?",
        "opciones": [
            "A. La toxicidad directa del fertilizante nitrogenado que envenena sus branquias.",
            "B. El exceso de comida proporcionado por las algas.",
            "C. La hipoxia o falta de oxígeno disuelto en el agua, agotado por la descomposición bacteriana.",
            "D. El aumento de la temperatura del agua debido al bloqueo de la luz solar."
        ],
        "respuesta": "C. La hipoxia o falta de oxígeno disuelto en el agua, agotado por la descomposición bacteriana.",
        "explicacion_ia": "Aunque todo empieza con el fertilizante, la causa directa de la muerte de los peces es la asfixia (anoxia/hipoxia). Las bacterias aeróbicas agotan el oxígeno al descomponer la biomasa muerta."
    },
    {
        "materia": "Matemáticas",
        "pregunta": "Una compañía de telefonía ofrece dos planes mensuales. \n- El Plan A tiene un cargo fijo de $20.000 y cobra $200 por cada minuto de llamada.\n- El Plan B no tiene cargo fijo, pero cobra $300 por cada minuto de llamada.\nUn usuario quiere saber en qué punto ambos planes cuestan exactamente lo mismo para decidir cuál le conviene. Si 'x' es el número de minutos consumidos y 'y' el costo total, ¿cuál es la ecuación que permite hallar el punto de equilibrio?",
        "opciones": [
            "A. 20.000 + 200x = 300x",
            "B. 20.000x + 200 = 300",
            "C. 20.000 - 200x = 300x",
            "D. 200x = 300x + 20.000"
        ],
        "respuesta": "A. 20.000 + 200x = 300x",
        "explicacion_ia": "Se igualan los costos. Costo A = Cargo Fijo (20.000) + Variable (200 * x). Costo B = Variable (300 * x). Al igualarlos (A = B) se obtiene 20.000 + 200x = 300x. (Esto ocurre a los 200 minutos)."
    },
    {
        "materia": "Sociales y Ciudadanas",
        "pregunta": "Lea con atención: 'La gentrificación es un proceso de transformación urbana en el que la población original de un barrio deteriorado o céntrico es progresivamente desplazada por otra de mayor poder adquisitivo, a medida que la zona se renueva, suben los precios de los arriendos y cambian los comercios tradicionales por tiendas de lujo'.\n\nSi una alcaldía decide invertir masivamente en renovar un barrio popular histórico sin implementar controles de precios de vivienda, ¿cuál es la consecuencia social negativa más probable descrita en el concepto anterior?",
        "opciones": [
            "A. El aumento de la delincuencia en el barrio renovado.",
            "B. El desplazamiento y marginación de los habitantes tradicionales que no pueden costear el nuevo nivel de vida.",
            "C. La disminución del turismo en la zona.",
            "D. La caída de los precios de la propiedad raíz."
        ],
        "respuesta": "B. El desplazamiento y marginación de los habitantes tradicionales que no pueden costear el nuevo nivel de vida.",
        "explicacion_ia": "Es la definición misma del efecto negativo de la gentrificación: la expulsión (involuntaria, por presiones económicas) de la comunidad original para dar paso a nuevos residentes más ricos."
    },
    {
        "materia": "Lectura Crítica",
        "pregunta": "Texto: 'A menudo se afirma que la ciencia y la religión son enemigas irreconciliables. Sin embargo, esta visión ignora que muchos de los grandes científicos de la historia, como Newton o Kepler, eran profundamente religiosos y veían en la investigación científica una forma de descifrar el lenguaje de Dios en la naturaleza. El conflicto real no es entre ciencia y fe, sino entre el dogmatismo (ya sea religioso o cientificista) y la libertad de pensamiento'.\n\n¿Qué estrategia argumentativa utiliza el autor para defender su tesis?",
        "opciones": [
            "A. Utiliza datos estadísticos sobre cuántos científicos creen en Dios.",
            "B. Recurre a un argumento de autoridad citando la Biblia.",
            "C. Emplea contraejemplos históricos (Newton y Kepler) para refutar la premisa general de que ciencia y religión son incompatibles.",
            "D. Ataca personalmente a los ateos llamándolos dogmáticos."
        ],
        "respuesta": "C. Emplea contraejemplos históricos (Newton y Kepler) para refutar la premisa general de que ciencia y religión son incompatibles.",
        "explicacion_ia": "El autor derriba la generalización ('son enemigas') mostrando casos concretos que prueban lo contrario (contraejemplos), demostrando que la coexistencia es posible."
    },
    {
        "materia": "Ciencias Naturales",
        "pregunta": "Un estudiante quiere probar si la temperatura afecta la velocidad de una reacción química. Diseña el siguiente experimento:\n- Vaso 1: 100 ml de agua a 10°C + una pastilla efervescente entera.\n- Vaso 2: 100 ml de agua a 40°C + una pastilla efervescente triturada (polvo).\nEl estudiante observa que el Vaso 2 reacciona mucho más rápido y concluye que 'el calor acelera la reacción'.\n\n¿Por qué la conclusión del estudiante NO es científicamente válida basándose en este diseño experimental?",
        "opciones": [
            "A. Porque no midió el tiempo con un cronómetro exacto.",
            "B. Porque introdujo dos variables cambiantes al mismo tiempo (temperatura y superficie de contacto/triturado), por lo que no puede saber cuál causó el efecto.",
            "C. Porque debió usar agua a 100°C para ver mejor la diferencia.",
            "D. Porque las pastillas efervescentes no son reactivos químicos reales."
        ],
        "respuesta": "B. Porque introdujo dos variables cambiantes al mismo tiempo (temperatura y superficie de contacto/triturado), por lo que no puede saber cuál causó el efecto.",
        "explicacion_ia": "Para que un experimento sea válido, se debe aislar la variable a estudiar. Al cambiar la temperatura Y triturar la pastilla (lo cual aumenta la superficie de contacto y acelera la reacción), el experimento está viciado."
    },
    {
        "materia": "Matemáticas",
        "pregunta": "Se realiza una encuesta a 150 personas sobre sus preferencias de transporte. Los resultados muestran que:\n- 80 personas usan Bus.\n- 60 personas usan Bicicleta.\n- 30 personas usan AMBOS medios de transporte.\n- El resto no usa ninguno de los dos.\n\n¿Cuántas personas encuestadas NO usan ni Bus ni Bicicleta?",
        "opciones": [
            "A. 10 personas.",
            "B. 40 personas.",
            "C. 20 personas.",
            "D. 0 personas."
        ],
        "respuesta": "B. 40 personas.",
        "explicacion_ia": "Uso de conjuntos: \nSolo Bus = 80 - 30 (ambos) = 50.\nSolo Bici = 60 - 30 (ambos) = 30.\nAmbos = 30.\nTotal de personas que usan algo = 50 + 30 + 30 = 110.\nTotal encuestados = 150.\nLos que no usan nada = 150 - 110 = 40."
    },
    {
        "materia": "Sociales y Ciudadanas",
        "pregunta": "A mediados del siglo XX, muchos países latinoamericanos adoptaron el modelo de 'Industrialización por Sustitución de Importaciones' (ISI). Este modelo consistía en poner altos impuestos a los productos extranjeros para que fuera más barato producirlos dentro del país y así desarrollar la industria nacional.\n\n¿Cuál fue una consecuencia negativa a largo plazo de la aplicación estricta de este modelo en la región?",
        "opciones": [
            "A. La desaparición total de la agricultura.",
            "B. El fortalecimiento excesivo de la moneda local frente al dólar.",
            "C. La creación de industrias locales poco competitivas y dependientes de subsidios estatales, con productos más caros y de menor calidad para el consumidor.",
            "D. El aumento desmedido de las exportaciones tecnológicas."
        ],
        "respuesta": "C. La creación de industrias locales poco competitivas y dependientes de subsidios estatales, con productos más caros y de menor calidad para el consumidor.",
        "explicacion_ia": "Al no tener competencia extranjera, la industria local no se modernizó ni mejoró su calidad (falta de incentivos), y el proteccionismo terminó encareciendo el costo de vida."
    },
    {
        "materia": "Lectura Crítica",
        "pregunta": "Considere la siguiente paradoja lógica: 'En un pueblo hay un barbero que afeita a todos los hombres que no se afeitan a sí mismos, y solo a ellos'.\n\nLa pregunta es: ¿Se afeita el barbero a sí mismo?\nSi decimos que SÍ se afeita a sí mismo, entonces no debería afeitarse (porque solo afeita a los que NO se afeitan a sí mismos). Si decimos que NO se afeita a sí mismo, entonces debería afeitarse (porque su regla es afeitar a los que no lo hacen).\n\n¿Qué demuestra esta paradoja (Paradoja de Russell) sobre los sistemas lógicos?",
        "opciones": [
            "A. Que los barberos no saben lógica.",
            "B. Que existen contradicciones inherentes cuando un conjunto intenta contenerse a sí mismo o definirse autorreferencialmente.",
            "C. Que es imposible afeitarse correctamente sin un espejo.",
            "D. Que la lógica solo sirve para las matemáticas y no para la vida real."
        ],
        "respuesta": "B. Que existen contradicciones inherentes cuando un conjunto intenta contenerse a sí mismo o definirse autorreferencialmente.",
        "explicacion_ia": "Esta paradoja sacudió las matemáticas a principios del siglo XX, demostrando que la teoría de conjuntos clásica tenía fallos cuando se permitían definiciones circulares o autorreferenciales."
    },
    {
        "materia": "Ciencias Naturales",
        "pregunta": "Contexto: La resistencia eléctrica de un cable depende de su material, su longitud y su grosor (área transversal). La física establece que la resistencia es directamente proporcional a la longitud (más largo = más resistencia) e inversamente proporcional al grosor (más grueso = menos resistencia).\n\nSi tienes un cable de cobre y quieres reemplazarlo por otro que permita pasar MÁS corriente (es decir, que tenga MENOS resistencia), ¿cuál de las siguientes opciones debes elegir?",
        "opciones": [
            "A. Un cable del mismo material, más largo y más delgado.",
            "B. Un cable del mismo material, más corto y más grueso.",
            "C. Un cable del mismo material, de igual longitud pero más delgado.",
            "D. Un cable del mismo material, más largo y de igual grosor."
        ],
        "respuesta": "B. Un cable del mismo material, más corto y más grueso.",
        "explicacion_ia": "Piénsalo como una tubería de agua: si es corta y ancha (gruesa), el agua (electrones) fluye fácil. Si es larga y estrecha (delgada), cuesta más pasar. Para menor resistencia necesitas: menos longitud y más área (grosor)."
    },
    {
        "materia": "Sociales y Ciudadanas",
        "pregunta": "Durante la Guerra Fría, la 'Doctrina de Seguridad Nacional' promovida por Estados Unidos en América Latina justificaba que los ejércitos locales tomaran el poder político para combatir al 'enemigo interno'. En este contexto, ¿a quiénes se catalogaba principalmente como 'enemigo interno'?",
        "opciones": [
            "A. A los ejércitos de países vecinos que amenazaban las fronteras.",
            "B. A los narcotraficantes exclusivamente.",
            "C. A cualquier movimiento social, sindicato, estudiante o partido político sospechoso de tener afinidad con el comunismo o el socialismo.",
            "D. A las multinacionales extranjeras."
        ],
        "respuesta": "C. A cualquier movimiento social, sindicato, estudiante o partido político sospechoso de tener afinidad con el comunismo o el socialismo.",
        "explicacion_ia": "Bajo esta lógica ideológica, la amenaza no venía de afuera (otra nación), sino de adentro (ciudadanos con ideas de izquierda), lo que legitimó la persecución sistemática de opositores políticos."
    },
    {
        "materia": "Matemáticas",
        "pregunta": "Para pintar la fachada de un edificio de 400 m², se contratan 2 pintores que tardan 8 días trabajando 6 horas diarias. Si se quiere pintar otro edificio similar de 800 m², pero se cuenta con 4 pintores trabajando 8 horas diarias, ¿cuántos días tardarán?",
        "opciones": [
            "A. 6 días.",
            "B. 8 días.",
            "C. 4 días.",
            "D. 12 días."
        ],
        "respuesta": "A. 6 días.",
        "explicacion_ia": "Es una regla de tres compuesta. \nSituación 1: 400m², 2 pintores, 8 días, 6h (Total horas-hombre: 2*8*6 = 96h para 400m²). \nSituación 2: 800m² (doble trabajo, requiere 192h hombre). \nTenemos 4 pintores a 8h/día = 32h/día de fuerza laboral. \nDías necesarios = 192 horas totales requeridas / 32 horas diarias = 6 días."
    },
    {
        "materia": "Lectura Crítica",
        "pregunta": "Lea: 'El lenguaje inclusivo (todes, nosotr@s) ha generado un intenso debate. Sus defensores argumentan que lo que no se nombra no existe, y que el masculino genérico invisibiliza a las mujeres y personas no binarias. Sus detractores, como la RAE, sostienen que el masculino gramatical ya es inclusivo por convención y que modificar la morfología del idioma artificialmente dificulta la comunicación y la economía del lenguaje'.\n\n¿Cuál es el punto de choque central entre ambas posturas?",
        "opciones": [
            "A. La estética de las palabras.",
            "B. La tensión entre la función política/social del lenguaje (visibilidad) y su función estructural/gramatical (economía y convención).",
            "C. El odio hacia la Real Academia Española.",
            "D. La dificultad de pronunciar la letra 'e'."
        ],
        "respuesta": "B. La tensión entre la función política/social del lenguaje (visibilidad) y su función estructural/gramatical (economía y convención).",
        "explicacion_ia": "El conflicto radica en dos visiones del idioma: una que lo ve como una herramienta de cambio social y equidad, y otra que lo ve como un sistema de códigos eficiente y regido por reglas históricas."
    },
    {
        "materia": "Ciencias Naturales",
        "pregunta": "La Segunda Ley de la Termodinámica establece que en cualquier proceso natural espontáneo, la entropía (desorden) del universo tiende a aumentar. Sin embargo, los seres vivos somos sistemas altamente ordenados y complejos. ¿Contradice la vida a la Segunda Ley de la Termodinámica?",
        "opciones": [
            "A. Sí, la vida es una excepción a las leyes físicas.",
            "B. No, porque los seres vivos son sistemas abiertos que mantienen su orden interno consumiendo energía del entorno y aumentando el desorden global (liberando calor y desechos).",
            "C. Sí, porque la evolución crea orden a partir del caos sin costo energético.",
            "D. No, porque la termodinámica solo aplica a máquinas de vapor."
        ],
        "respuesta": "B. No, porque los seres vivos son sistemas abiertos que mantienen su orden interno consumiendo energía del entorno y aumentando el desorden global (liberando calor y desechos).",
        "explicacion_ia": "La vida paga el precio de su orden interno exportando desorden al exterior. Al comer y respirar, generamos calor y desordenamos moléculas complejas, cumpliendo así la ley a nivel global."
    },
    {
        "materia": "Sociales y Ciudadanas",
        "pregunta": "En un conflicto escolar, la mediación busca:",
        "opciones": ["A. Que el director imponga un castigo ejemplar.", "B. Que un tercero neutral ayude a las partes a dialogar y encontrar su propia solución.", "C. Que uno de los estudiantes gane y el otro pierda.", "D. Ignorar el problema para que pase el tiempo."],
        "respuesta": "B. Que un tercero neutral ayude a las partes a dialogar y encontrar su propia solución.",
        "explicacion_ia": "La mediación es un mecanismo de resolución pacífica de conflictos donde el mediador no decide (como un juez), sino que facilita la comunicación para lograr un acuerdo mutuo."
    },
    {
        "materia": "Lectura Crítica",
        "pregunta": "Lea el siguiente fragmento: 'El imperativo categórico de Kant establece: «Obra solo según aquella máxima por la cual puedas querer que al mismo tiempo se convierta en ley universal». Supongamos que un comerciante decide no engañar a sus clientes inexpertos en el cambio, no por deber moral, sino porque si se descubre que engaña, perdería su reputación y su negocio quebraría. Según la ética kantiana descrita, ¿es la acción del comerciante moralmente valiosa?'",
        "opciones": [
            "A. Sí, porque el resultado final es bueno: los clientes no fueron engañados.",
            "B. No, porque su acción no está motivada por el deber o la ley moral, sino por un interés egoísta (la reputación).",
            "C. Sí, porque al universalizar su acción, todos los comerciantes serían honestos.",
            "D. No, porque Kant desprecia el comercio como actividad humana."
        ],
        "respuesta": "B. No, porque su acción no está motivada por el deber o la ley moral, sino por un interés egoísta (la reputación).",
        "explicacion_ia": "Para Kant, la moralidad de una acción no radica en sus consecuencias (que no nos engañen), sino en la intención o el motivo. Si se actúa por interés o miedo (conforme al deber, pero no por deber), la acción carece de valor moral genuino."
    },
    {
        "materia": "Sociales y Ciudadanas",
        "pregunta": "Contexto: En Colombia, la Ley de Víctimas y Restitución de Tierras busca devolver los predios a campesinos que fueron despojados violentamente por grupos armados. Sin embargo, surge un conflicto complejo: años después del despojo, muchas de esas tierras fueron compradas por terceros (nuevos dueños) que aseguran haberlas adquirido legalmente y sin saber su origen ilícito ('buena fe').\n\nEn un juicio de restitución, si se demuestra que el campesino original fue despojado, pero el actual dueño compró de buena fe exenta de culpa (hizo todas las averiguaciones y no podía saber del despojo), ¿cuál suele ser la decisión jurídica que equilibra ambos derechos?",
        "opciones": [
            "A. Se deja la tierra al comprador actual y el campesino víctima no recibe nada.",
            "B. Se devuelve la tierra a la víctima (restitución) y el Estado indemniza económicamente al comprador de buena fe.",
            "C. Se divide la tierra en dos partes iguales.",
            "D. Se cárcel al comprador actual por complicidad."
        ],
        "respuesta": "B. Se devuelve la tierra a la víctima (restitución) y el Estado indemniza económicamente al comprador de buena fe.",
        "explicacion_ia": "El derecho de la víctima a la restitución es preferente. Sin embargo, para no vulnerar al tercero que actuó correctamente (buena fe exenta de culpa), el Estado asume la compensación económica para este último."
    },
    {
        "materia": "Matemáticas",
        "pregunta": "Un agricultor quiere cercar un terreno rectangular para ganado junto a un río recto. No necesita poner cerca en el lado del río. Dispone de 120 metros de alambre para los otros tres lados. Si 'x' es la longitud del lado perpendicular al río y 'y' es la longitud del lado paralelo al río, quiere encontrar las dimensiones que maximicen el área.\n\nLa función de área a maximizar en términos de una sola variable 'x' es:",
        "opciones": [
            "A. A(x) = 120x - x²",
            "B. A(x) = 120x - 2x²",
            "C. A(x) = 60x - x²",
            "D. A(x) = x(120 - x)"
        ],
        "respuesta": "B. A(x) = 120x - 2x²",
        "explicacion_ia": "El perímetro usado es 2x + y = 120 (dos lados perpendiculares y uno paralelo). Despejando 'y': y = 120 - 2x. El área es A = x * y. Sustituyendo 'y': A(x) = x * (120 - 2x) = 120x - 2x²."
    },
    {
        "materia": "Lectura Crítica",
        "pregunta": "Lea: 'En la sociedad de consumo, los objetos tienen una obsolescencia programada no solo técnica, sino psicológica. No cambiamos el celular porque deje de funcionar, sino porque el modelo nuevo promete una experiencia de felicidad o estatus que el anterior ya no ofrece. Así, el consumo se convierte en un ritual para calmar la ansiedad de ser irrelevante, una ansiedad que el mismo mercado se encarga de generar constantemente'.\n\n¿Cuál es la premisa subyacente del autor sobre la relación entre mercado y felicidad?",
        "opciones": [
            "A. El mercado satisface necesidades naturales de los seres humanos.",
            "B. La felicidad real solo se alcanza con la tecnología más avanzada.",
            "C. El mercado crea artificialmente una insatisfacción permanente (ansiedad) para mantener el ciclo de consumo.",
            "D. La obsolescencia programada es necesaria para el avance de la ingeniería."
        ],
        "respuesta": "C. El mercado crea artificialmente una insatisfacción permanente (ansiedad) para mantener el ciclo de consumo.",
        "explicacion_ia": "El texto sugiere que la necesidad de cambiar no es funcional ('no porque deje de funcionar'), sino psicológica, inducida por una promesa de felicidad que el mercado manipula para seguir vendiendo."
    },
    {
        "materia": "Ciencias Naturales",
        "pregunta": "Gemelos idénticos (monocigóticos) tienen exactamente el mismo ADN. Sin embargo, si uno fuma y lleva una vida sedentaria mientras el otro es atleta y come sano, el primero puede desarrollar cáncer a los 40 años y el segundo no. Los estudios muestran que, aunque sus secuencias de genes son iguales, la forma en que estos genes se 'encienden' o 'apagan' cambia debido al ambiente (metilación del ADN).\n\n¿Cómo se llama la rama de la biología que estudia estos cambios heredables en la expresión génica que NO implican cambios en la secuencia del ADN?",
        "opciones": [
            "A. Genética Mendeliana.",
            "B. Epigenética.",
            "C. Biología evolutiva.",
            "D. Transgénesis."
        ],
        "respuesta": "B. Epigenética.",
        "explicacion_ia": "La epigenética estudia los mecanismos (como marcas químicas en el ADN) que regulan la expresión de los genes en respuesta al ambiente sin alterar el código genético base."
    },
    {
        "materia": "Sociales y Ciudadanas",
        "pregunta": "El fenómeno económico conocido como 'Enfermedad Holandesa' ocurre cuando un país descubre un recurso natural exportable masivo (ej: petróleo o café), lo que provoca una entrada masiva de divisas (dólares). Esto revalúa la moneda local (el dólar baja de precio). Paradójicamente, esto perjudica gravemente a:",
        "opciones": [
            "A. Los importadores de electrodomésticos.",
            "B. Los turistas nacionales que viajan al exterior.",
            "C. Los otros sectores exportadores (industria y agricultura) que pierden competitividad.",
            "D. El gobierno que recauda impuestos."
        ],
        "respuesta": "C. Los otros sectores exportadores (industria y agricultura) que pierden competitividad.",
        "explicacion_ia": "Si el dólar es muy barato, los productos industriales o agrícolas nacionales se vuelven muy caros para los extranjeros, por lo que dejan de comprarlos. Así, el auge de un recurso (petróleo) 'mata' a las otras industrias."
    },
    {
        "materia": "Matemáticas",
        "pregunta": "Se lanza una pelota hacia arriba. La altura h (en metros) en función del tiempo t (en segundos) está dada por la función cuadrática h(t) = -5t² + 20t + 2.",
        "opciones": [
            "A. A los 4 segundos.",
            "B. A los 2 segundos.",
            "C. A los 5 segundos.",
            "D. A los 10 segundos."
        ],
        "respuesta": "B. A los 2 segundos.",
        "explicacion_ia": "La altura máxima está en el vértice de la parábola. Para una función ax² + bx + c, la coordenada t del vértice es -b / (2a). Aquí a=-5, b=20. t = -20 / (2 * -5) = -20 / -10 = 2 segundos."
    },
    {
        "materia": "Lectura Crítica",
        "pregunta": "En el cuento 'La Biblioteca de Babel', Borges imagina un universo que es una biblioteca infinita que contiene todos los libros posibles (todas las combinaciones posibles de letras). La mayoría de los libros son galimatías sin sentido, pero la biblioteca también contiene necesariamente la verdad absoluta, la historia de tu vida y la refutación de esa historia.\n\n¿Qué sentimiento existencial produce esta 'infinitud' en los bibliotecarios (habitantes) del cuento?",
        "opciones": [
            "A. Una alegría inmensa por tener tanto para leer.",
            "B. Una angustia profunda ante la falta de sentido aparente y la imposibilidad de encontrar, entre tanto caos, el libro que contiene la verdad.",
            "C. Indiferencia, pues no les gusta leer.",
            "D. Esperanza de que el orden alfabético resuelva sus problemas."
        ],
        "respuesta": "B. Una angustia profunda ante la falta de sentido aparente y la imposibilidad de encontrar, entre tanto caos, el libro que contiene la verdad.",
        "explicacion_ia": "La metáfora de Borges apunta a la búsqueda humana de sentido (la verdad) en un universo vasto y caótico donde la información es abrumadora y mayoritariamente inútil."
    },
    {
        "materia": "Sociales y Ciudadanas",
        "pregunta": "Contexto: En un régimen parlamentario (como España o Reino Unido), el Jefe de Gobierno (Primer Ministro) no es elegido directamente por el pueblo, sino por el Parlamento. Si el Parlamento pierde la confianza en el Primer Ministro, puede destituirlo mediante una 'moción de censura' y elegir a otro sin convocar a elecciones generales.\n\n¿Cuál es una diferencia clave de este sistema frente al sistema Presidencialista (como el de Colombia)?",
        "opciones": [
            "A. En el presidencialismo, el Presidente tiene un periodo fijo y es muy difícil destituirlo (juicio político), lo que da estabilidad pero puede generar bloqueos si no tiene apoyo del Congreso.",
            "B. En el parlamentarismo no hay democracia.",
            "C. En el presidencialismo, el Presidente también hace las leyes.",
            "D. En el parlamentarismo, el Rey es quien manda realmente."
        ],
        "respuesta": "A. En el presidencialismo, el Presidente tiene un periodo fijo y es muy difícil destituirlo (juicio político), lo que da estabilidad pero puede generar bloqueos si no tiene apoyo del Congreso.",
        "explicacion_ia": "El sistema parlamentario es más flexible ante crisis políticas (cambian al líder rápido), mientras que el presidencialismo tiene rigidez de periodos (4 años fijos) y separación estricta de poderes."
    },
    {
        "materia": "Ciencias Naturales",
        "pregunta": "El principio de Bernoulli explica por qué vuelan los aviones. Establece que en un fluido en movimiento, donde la velocidad es alta, la presión es baja, y viceversa.",


        "opciones": [
            "A. La presión arriba sea mayor, empujando el avión hacia abajo.",
            "B. La presión arriba sea menor que la presión abajo, generando una fuerza neta hacia arriba (sustentación).",
            "C. La gravedad deje de actuar sobre el avión.",
            "D. El avión se frene por la resistencia."
        ],
        "respuesta": "B. La presión arriba sea menor que la presión abajo, generando una fuerza neta hacia arriba (sustentación).",
        "explicacion_ia": "Al haber mayor velocidad arriba, la presión disminuye (Bernoulli). Como la presión abajo se mantiene mayor, empuja el ala hacia arriba. Esa diferencia de presiones levanta el avión."
    },
    {
        "materia": "Matemáticas",
        "pregunta": "En un país, el 10% de la población más rica posee el 50% de la riqueza total, mientras que el 50% más pobre posee solo el 10% de la riqueza. Un estadístico calcula el 'ingreso promedio' (media) y encuentra que es bastante alto. Sin embargo, la 'mediana' de los ingresos es muy baja.\n\n¿Por qué la mediana es un mejor indicador que el promedio para entender la realidad económica de la mayoría de la gente en este país?",
        "opciones": [
            "A. Porque la mediana siempre es más alta que el promedio.",
            "B. Porque el promedio se deja 'inflar' por los valores extremos de los superricos, dando una falsa sensación de bienestar, mientras que la mediana indica el punto medio real de la población.",
            "C. Porque el promedio es un cálculo muy difícil de hacer.",
            "D. Porque la riqueza no se puede medir."
        ],
        "respuesta": "B. Porque el promedio se deja 'inflar' por los valores extremos de los superricos, dando una falsa sensación de bienestar, mientras que la mediana indica el punto medio real de la población.",
        "explicacion_ia": "La media aritmética es sensible a valores atípicos (outliers). Si Bill Gates entra a un bar, el 'promedio' de riqueza sube millones, pero la 'mediana' (lo que tiene la persona del medio) no cambia, reflejando mejor al ciudadano común."
    },
    {
        "materia": "Sociales y Ciudadanas",
        "pregunta": "Durante la Guerra Fría, Estados Unidos y la Unión Soviética nunca se enfrentaron militarmente de forma directa (guerra caliente), pero sí participaron en guerras 'subsidiarias' o 'proxy' (Vietnam, Corea, Afganistán). ¿Cuál fue la razón estratégica principal para evitar el choque directo?",
        "opciones": [
            "A. Se tenían mucho respeto mutuo.",
            "B. La doctrina de la Destrucción Mutua Asegurada (MAD): un conflicto directo nuclear habría aniquilado a ambos bandos y al planeta.",
            "C. No tenían suficientes soldados.",
            "D. La ONU les prohibió pelear."
        ],
        "respuesta": "B. La doctrina de la Destrucción Mutua Asegurada (MAD): un conflicto directo nuclear habría aniquilado a ambos bandos y al planeta.",
        "explicacion_ia": "El equilibrio del terror nuclear garantizaba que quien disparara primero, moriría segundo. Esto congeló el conflicto directo y lo desvió hacia zonas periféricas."
    },
    {
        "materia": "Lectura Crítica",
        "pregunta": "Texto: 'La inteligencia artificial (IA) generativa puede crear imágenes bellísimas que ganan concursos de arte. Sin embargo, algunos filósofos arguyen que eso no es arte. El arte, dicen, requiere intencionalidad humana, una necesidad de comunicar una experiencia subjetiva de dolor, amor o muerte. La IA no siente, solo procesa probabilidades estadísticas de píxeles'.\n\n¿Qué definición de 'Arte' está defendiendo el texto para excluir a la IA?",
        "opciones": [
            "A. Arte como técnica: lo importante es la calidad visual del resultado final.",
            "B. Arte como expresión: lo esencial es la emoción y la conciencia del creador detrás de la obra.",
            "C. Arte como imitación: lo importante es que se parezca a la realidad.",
            "D. Arte como institución: solo es arte lo que está en los museos."
        ],
        "respuesta": "B. Arte como expresión: lo esencial es la emoción y la conciencia del creador detrás de la obra.",
        "explicacion_ia": "El argumento se centra en la 'intencionalidad' y la 'experiencia subjetiva' (sentir), priorizando el proceso interno del artista sobre el producto estético final."
    },
    {
        "materia": "Ciencias Naturales",
        "pregunta": "Una enzima digestiva humana funciona óptimamente a una temperatura de 37°C y un pH específico. Si una persona tiene una fiebre muy alta (42°C), la digestión se dificulta. ¿Qué le ocurre químicamente a la enzima a esa temperatura?",
        "opciones": [
            "A. La enzima trabaja más rápido por el calor.",
            "B. La enzima se reproduce.",
            "C. La enzima se desnaturaliza: pierde su estructura tridimensional y, por tanto, pierde su función catalítica.",
            "D. La enzima se convierte en grasa."
        ],
        "respuesta": "C. La enzima se desnaturaliza: pierde su estructura tridimensional y, por tanto, pierde su función catalítica.",
        "explicacion_ia": "Las enzimas son proteínas. Al igual que la clara de huevo cambia al cocinarse, el exceso de calor rompe los enlaces que mantienen la forma de la enzima (desnaturalización). Si la forma cambia, ya no puede 'encajar' con el sustrato para digerirlo."
    },
    {
        "materia": "Inglés",
        "pregunta": "Where can you see this sign? 'DO NOT TOUCH THE ART'",
        "opciones": ["A. In a museum.", "B. In a park.", "C. In a gym.", "D. In a kitchen."],
        "respuesta": "A. In a museum.",
        "explicacion_ia": "Contexto: Las obras de arte (Art) se exhiben en museos y la regla principal es no tocarlas."
    },
    {
        "materia": "Inglés",
        "pregunta": "Definition: 'A person who puts out fires.'",
        "opciones": ["A. Teacher.", "B. Firefighter.", "C. Police officer.", "D. Nurse."],
        "respuesta": "B. Firefighter.",
        "explicacion_ia": "Profesiones: Quien apaga incendios (puts out fires) es el Bombero (Firefighter)."
    },
    {
        "materia": "Inglés",
        "pregunta": "Complete: 'She ______ watching TV every night.'",
        "opciones": ["A. watches", "B. watch", "C. watching", "D. watched"],
        "respuesta": "A. watches",
        "explicacion_ia": "Presente Simple: Para la tercera persona (She), al verbo se le agrega 'es' (watch -> watches) cuando es una rutina."
    },
    {
        "materia": "Inglés",
        "pregunta": "Conversation: \n- 'Can I open the window?' \n- '__________'",
        "opciones": ["A. Yes, I do.", "B. No, it is cold.", "C. I am fine.", "D. It is blue."],
        "respuesta": "B. No, it is cold.",
        "explicacion_ia": "Lógica conversacional: Una razón válida para negar abrir la ventana es que hace frío."
    },
    {
        "materia": "Inglés",
        "pregunta": "Where can you see this sign? 'KEEP FROZEN'",
        "opciones": ["A. On a t-shirt.", "B. On a box of ice cream.", "C. On a book.", "D. On a bicycle."],
        "respuesta": "B. On a box of ice cream.",
        "explicacion_ia": "Contexto: 'Mantener congelado' es una instrucción para alimentos como el helado."
    },
    {
        "materia": "Inglés",
        "pregunta": "Definition: 'The room where you cook food.'",
        "opciones": ["A. Bathroom.", "B. Bedroom.", "C. Kitchen.", "D. Living room."],
        "respuesta": "C. Kitchen.",
        "explicacion_ia": "Partes de la casa: Donde se cocina es la Cocina (Kitchen)."
    },
    {
        "materia": "Inglés",
        "pregunta": "Complete: 'They ______ playing soccer now.'",
        "opciones": ["A. is", "B. am", "C. are", "D. be"],
        "respuesta": "C. are",
        "explicacion_ia": "Presente Continuo: Plural 'They' va con 'are'."
    },
    {
        "materia": "Inglés",
        "pregunta": "Vocabulary: The opposite of 'Big' is:",
        "opciones": ["A. Large.", "B. Huge.", "C. Small.", "D. Tall."],
        "respuesta": "C. Small.",
        "explicacion_ia": "Antónimos: Lo opuesto de Grande es Pequeño (Small)."
    },
    {
        "materia": "Inglés",
        "pregunta": "Complete: 'I didn't ______ to school yesterday.'",
        "opciones": ["A. go", "B. went", "C. going", "D. goes"],
        "respuesta": "A. go",
        "explicacion_ia": "Pasado Negativo: El auxiliar 'didn't' ya marca el pasado, así que el verbo principal queda en su forma base 'go'."
    },
    {
        "materia": "Inglés",
        "pregunta": "Conversation: \n- 'I have a headache.' \n- '__________'",
        "opciones": ["A. You should eat candy.", "B. You should take an aspirin.", "C. Congratulations.", "D. See you later."],
        "respuesta": "B. You should take an aspirin.",
        "explicacion_ia": "Consejo (Modales): Si alguien tiene dolor de cabeza, lo lógico es sugerir medicina."
    },
    {
        "materia": "Inglés",
        "pregunta": "Where can you see this sign? 'SLOW DOWN - SCHOOL ZONE'",
        "opciones": ["A. In a kitchen.", "B. On a street.", "C. In a bedroom.", "D. In a plane."],
        "respuesta": "B. On a street.",
        "explicacion_ia": "Contexto: Las señales de tránsito para reducir velocidad están en las calles."
    },
    {
        "materia": "Inglés",
        "pregunta": "Definition: 'You wear this on your head.'",
        "opciones": ["A. Shoe.", "B. Hat.", "C. Glove.", "D. Belt."],
        "respuesta": "B. Hat.",
        "explicacion_ia": "Prendas de vestir: En la cabeza se usa el sombrero/gorra (Hat)."
    },
    {
        "materia": "Inglés",
        "pregunta": "Complete: 'She is the ______ student in the class.'",
        "opciones": ["A. intelligent", "B. more intelligent", "C. most intelligent", "D. intelligenter"],
        "respuesta": "C. most intelligent",
        "explicacion_ia": "Superlativos largos: Para adjetivos largos se usa 'The most'."
    },
    {
        "materia": "Inglés",
        "pregunta": "Vocabulary: 'Sunday' comes after:",
        "opciones": ["A. Monday.", "B. Friday.", "C. Saturday.", "D. Tuesday."],
        "respuesta": "C. Saturday.",
        "explicacion_ia": "Secuencia: El domingo viene después del sábado."
    },
    {
        "materia": "Inglés",
        "pregunta": "Complete: 'If it is sunny, we ______ go to the beach.'",
        "opciones": ["A. will", "B. did", "C. are", "D. have"],
        "respuesta": "A. will",
        "explicacion_ia": "Primer condicional: Futuro posible."
    },
    {
        "materia": "Inglés",
        "pregunta": "Where can you see this sign? 'OUT OF ORDER'",
        "opciones": ["A. On a tree.", "B. On a broken vending machine.", "C. On a dog.", "D. On a cloud."],
        "respuesta": "B. On a broken vending machine.",
        "explicacion_ia": "Significado: 'Fuera de servicio'. Se pone en máquinas dañadas."
    },
    {
        "materia": "Inglés",
        "pregunta": "Definition: 'An animal with a very long neck.'",
        "opciones": ["A. Lion.", "B. Elephant.", "C. Giraffe.", "D. Monkey."],
        "respuesta": "C. Giraffe.",
        "explicacion_ia": "Animales: Cuello largo = Jirafa."
    },
    {
        "materia": "Inglés",
        "pregunta": "Complete: 'Do you ______ chocolate?'",
        "opciones": ["A. likes", "B. like", "C. liking", "D. liked"],
        "respuesta": "B. like",
        "explicacion_ia": "Pregunta Presente Simple: Con 'Do' el verbo va normal."
    },
    {
        "materia": "Inglés",
        "pregunta": "Conversation: \n- 'What time is it?' \n- '__________'",
        "opciones": ["A. It is red.", "B. It is 3 o'clock.", "C. I am fine.", "D. It is raining."],
        "respuesta": "B. It is 3 o'clock.",
        "explicacion_ia": "Hora: La única opción que responde a la hora es la B."
    },
    {
        "materia": "Inglés",
        "pregunta": "Choose the synonym of 'Difficult'.",
        "opciones": ["A. Easy.", "B. Hard.", "C. Soft.", "D. Simple."],
        "respuesta": "B. Hard.",
        "explicacion_ia": "Sinónimos: Difícil es igual a Duro/Complicado (Hard)."
    },
    {
        "materia": "Inglés",
        "pregunta": "Complete: 'The cat is ______ the table.' (Debajo)",
        "opciones": ["A. on", "B. in", "C. under", "D. at"],
        "respuesta": "C. under",
        "explicacion_ia": "Preposiciones: Debajo = Under."
    },
    {
        "materia": "Inglés",
        "pregunta": "Read: 'INSERT COIN'. Where do you see this?",
        "opciones": ["A. In a book.", "B. In a video game machine.", "C. In a flower.", "D. In a mirror."],
        "respuesta": "B. In a video game machine.",
        "explicacion_ia": "Instrucción: Insertar moneda es típico de máquinas (Arcade, Vending)."
    },
    {
        "materia": "Inglés",
        "pregunta": "Definition: 'You use this to cut paper.'",
        "opciones": ["A. Glue.", "B. Scissors.", "C. Pencil.", "D. Ruler."],
        "respuesta": "B. Scissors.",
        "explicacion_ia": "Útiles escolares: Para cortar se usan tijeras."
    },
    {
        "materia": "Inglés",
        "pregunta": "Complete: 'I ______ to music yesterday.'",
        "opciones": ["A. listen", "B. listened", "C. listening", "D. listens"],
        "respuesta": "B. listened",
        "explicacion_ia": "Pasado Regular: Se agrega -ed."
    },
    {
        "materia": "Inglés",
        "pregunta": "Conversation: \n- 'Where are you going?' \n- '__________'",
        "opciones": ["A. To the park.", "B. It is Monday.", "C. Yes, I am.", "D. My name is Ana."],
        "respuesta": "A. To the park.",
        "explicacion_ia": "Pregunta de lugar (Where): Requiere un destino."
    },
    {
        "materia": "Inglés",
        "pregunta": "Vocabulary: Which one is a drink?",
        "opciones": ["A. Bread.", "B. Water.", "C. Cheese.", "D. Apple."],
        "respuesta": "B. Water.",
        "explicacion_ia": "Categoría: Agua es bebida. Los otros son comida sólida."
    },
    {
        "materia": "Inglés",
        "pregunta": "Complete: 'He ______ his homework every afternoon.'",
        "opciones": ["A. do", "B. does", "C. doing", "D. done"],
        "respuesta": "B. does",
        "explicacion_ia": "Presente Simple: Tercera persona de 'Do' es 'Does'."
    },
    {
        "materia": "Inglés",
        "pregunta": "Where can you see this sign? 'TRY ON THESE JEANS'",
        "opciones": ["A. In a pharmacy.", "B. In a clothing store.", "C. In a bakery.", "D. In a bank."],
        "respuesta": "B. In a clothing store.",
        "explicacion_ia": "Contexto: Probarse ropa (Try on) ocurre en tiendas de ropa."
    },
    {
        "materia": "Inglés",
        "pregunta": "Definition: 'The season when leaves fall and it gets windy.'",
        "opciones": ["A. Summer.", "B. Autumn / Fall.", "C. Winter.", "D. Spring."],
        "respuesta": "B. Autumn / Fall.",
        "explicacion_ia": "Estaciones: Otoño es cuando caen las hojas."
    },
    {
        "materia": "Inglés",
        "pregunta": "Complete: '______ you speak French?'",
        "opciones": ["A. Does", "B. Do", "C. Is", "D. Are"],
        "respuesta": "B. Do",
        "explicacion_ia": "Auxiliar de pregunta: Con 'You' se usa 'Do'."
    },
    {
        "materia": "Inglés",
        "pregunta": "Conversation: \n- 'Is this your pen?' \n- '__________'",
        "opciones": ["A. Yes, it is.", "B. Yes, I am.", "C. Yes, he is.", "D. Yes, we are."],
        "respuesta": "A. Yes, it is.",
        "explicacion_ia": "Respuesta corta: El sujeto es un objeto (pen = it), así que la respuesta es 'it is'."
    },
    {
        "materia": "Inglés",
        "pregunta": "Vocabulary: 'Shoes' go on your:",
        "opciones": ["A. Hands.", "B. Feet.", "C. Head.", "D. Ears."],
        "respuesta": "B. Feet.",
        "explicacion_ia": "Cuerpo: Los zapatos van en los pies."
    },
    {
        "materia": "Inglés",
        "pregunta": "Complete: 'This house is ______ big.'",
        "opciones": ["A. very", "B. much", "C. many", "D. a lot"],
        "respuesta": "A. very",
        "explicacion_ia": "Intensificador: Para adjetivos se usa 'Very' (Muy grande)."
    },
    {
        "materia": "Inglés",
        "pregunta": "Read: 'PLEASE CLEAR YOUR TABLE'. Where are you?",
        "opciones": ["A. In a fast food restaurant.", "B. In a car.", "C. In a cinema.", "D. In a store."],
        "respuesta": "A. In a fast food restaurant.",
        "explicacion_ia": "Contexto: Limpiar tu propia mesa es típico de sitios de comida rápida o cafeterías."
    },
    {
        "materia": "Inglés",
        "pregunta": "Definition: 'A vehicle with two wheels.'",
        "opciones": ["A. Car.", "B. Bus.", "C. Bicycle.", "D. Truck."],
        "respuesta": "C. Bicycle.",
        "explicacion_ia": "Transporte: Dos ruedas = Bicicleta."
    },
    {
        "materia": "Inglés",
        "pregunta": "Complete: 'I have ______ seen that movie.'",
        "opciones": ["A. already", "B. yet", "C. ago", "D. since"],
        "respuesta": "A. already",
        "explicacion_ia": "Presente Perfecto: 'Already' (Ya) se usa en afirmativas."
    },
    {
        "materia": "Inglés",
        "pregunta": "Conversation: \n- 'See you later!' \n- '__________'",
        "opciones": ["A. Good morning.", "B. Bye!", "C. Hello.", "D. I am fine."],
        "respuesta": "B. Bye!",
        "explicacion_ia": "Despedida: La respuesta a 'Nos vemos luego' es 'Adiós'."
    },
    {
        "materia": "Inglés",
        "pregunta": "Which word is a number?",
        "opciones": ["A. Ten.", "B. Pen.", "C. Hen.", "D. Men."],
        "respuesta": "A. Ten.",
        "explicacion_ia": "Vocabulario básico: Ten = 10."
    },
    {
        "materia": "Inglés",
        "pregunta": "Complete: 'The birds ______ flying in the sky.'",
        "opciones": ["A. is", "B. am", "C. are", "D. be"],
        "respuesta": "C. are",
        "explicacion_ia": "Plural: Birds (Pájaros) requiere 'are'."
    },
    {
        "materia": "Inglés",
        "pregunta": "Where can you see this sign? 'ADULTS $10 - CHILDREN $5'",
        "opciones": ["A. At a ticket office (Cinema/Zoo).", "B. In a police station.", "C. In a bedroom.", "D. In a school class."],
        "respuesta": "A. At a ticket office (Cinema/Zoo).",
        "explicacion_ia": "Contexto: Lista de precios de entrada."
    },
    {
        "materia": "Matemáticas",
        "pregunta": "Si un pantalón cuesta $50.000 y tiene un descuento del 30%, ¿cuánto paga el cliente?",
        "opciones": ["A. $15.000", "B. $35.000", "C. $40.000", "D. $20.000"],
        "respuesta": "B. $35.000",
        "explicacion_ia": "El 30% de 50.000 es 15.000 (50.000 * 0.30). Restamos el descuento al precio original: 50.000 - 15.000 = 35.000."
    },
    {
        "materia": "Ciencias Naturales",
        "pregunta": "El proceso mediante el cual una oruga se transforma en mariposa se llama:",
        "opciones": ["A. Fotosíntesis.", "B. Metamorfosis.", "C. Osmosis.", "D. Evolución."],
        "respuesta": "B. Metamorfosis.",
        "explicacion_ia": "La metamorfosis es un proceso biológico por el cual un animal se desarrolla desde su nacimiento hasta la madurez por medio de grandes cambios estructurales y fisiológicos."
    },
    {
        "materia": "Sociales y Ciudadanas",
        "pregunta": "¿Cuál es la función principal de la Fiscalía General de la Nación?",
        "opciones": ["A. Hacer leyes.", "B. Investigar y acusar a los presuntos responsables de delitos.", "C. Defender a los pobres.", "D. Contar los votos."],
        "respuesta": "B. Investigar y acusar a los presuntos responsables de delitos.",
        "explicacion_ia": "La Fiscalía es el ente encargado de la acción penal: recolecta pruebas, investiga crímenes y lleva a los acusados ante los jueces."
    },
    {
        "materia": "Lectura Crítica",
        "pregunta": "En la frase 'El tiempo es oro', se utiliza una metáfora para indicar que:",
        "opciones": ["A. El tiempo es de color amarillo.", "B. El tiempo es valioso y no se debe desperdiciar.", "C. Se puede comprar tiempo en el banco.", "D. Los relojes deben ser de oro."],
        "respuesta": "B. El tiempo es valioso y no se debe desperdiciar.",
        "explicacion_ia": "Compara el valor intangible del tiempo con el valor material del oro para resaltar su importancia y escasez."
    },
    {
        "materia": "Inglés",
        "pregunta": "Complete: 'My father ______ a doctor.'",
        "opciones": ["A. are", "B. am", "C. is", "D. be"],
        "respuesta": "C. is",
        "explicacion_ia": "Verbo To Be: Para 'He' (My father), la forma correcta es 'is'."
    },
    {
        "materia": "Matemáticas",
        "pregunta": "¿Cuál es el área de un círculo con radio 4 cm? (Usa π ≈ 3)",
        "opciones": ["A. 12 cm²", "B. 24 cm²", "C. 48 cm²", "D. 16 cm²"],
        "respuesta": "C. 48 cm²",
        "explicacion_ia": "Fórmula aproximada: A = π * r². A = 3 * (4)². A = 3 * 16 = 48."
    },
    {
        "materia": "Ciencias Naturales",
        "pregunta": "¿Qué ley de Newton explica el retroceso de un arma al disparar?",
        "opciones": ["A. Primera Ley (Inercia).", "B. Segunda Ley (Fuerza).", "C. Tercera Ley (Acción y Reacción).", "D. Ley de la Gravedad."],
        "respuesta": "C. Tercera Ley (Acción y Reacción).",
        "explicacion_ia": "A toda acción corresponde una reacción de igual magnitud pero en sentido contrario. La bala sale hacia adelante y el arma empuja hacia atrás."
    },
    {
        "materia": "Sociales y Ciudadanas",
        "pregunta": "El 'Cabildo Abierto' es un mecanismo de participación donde:",
        "opciones": ["A. La gente sale a marchar.", "B. Los ciudadanos se reúnen con el Concejo o Juntas para discutir asuntos de interés común.", "C. Se cierran las puertas de la alcaldía.", "D. Se elige al presidente."],
        "respuesta": "B. Los ciudadanos se reúnen con el Concejo o Juntas para discutir asuntos de interés común.",
        "explicacion_ia": "Es una reunión pública de los concejos distritales, municipales o de las juntas administradoras locales, en la cual los habitantes pueden participar directamente."
    },
    {
        "materia": "Inglés",
        "pregunta": "Vocabulary: 'Chicken', 'Beef' and 'Pork' are types of:",
        "opciones": ["A. Vegetables.", "B. Meat.", "C. Fruit.", "D. Drink."],
        "respuesta": "B. Meat.",
        "explicacion_ia": "Categoría: Pollo, Res y Cerdo son tipos de carne (Meat)."
    },
    {
        "materia": "Matemáticas",
        "pregunta": "Resuelve: 3x - 7 = 14",
        "opciones": ["A. 5", "B. 7", "C. 21", "D. 10"],
        "respuesta": "B. 7",
        "explicacion_ia": "3x = 14 + 7 -> 3x = 21 -> x = 21/3 -> x = 7."
    },
    {
        "materia": "Lectura Crítica",
        "pregunta": "Si un texto narra la vida de una persona escrita por ella misma, es una:",
        "opciones": ["A. Biografía.", "B. Autobiografía.", "C. Crónica.", "D. Fábula."],
        "respuesta": "B. Autobiografía.",
        "explicacion_ia": "El prefijo 'Auto-' significa 'por sí mismo'. Biografía es la vida de otro; Autobiografía es la propia."
    },
    {
        "materia": "Ciencias Naturales",
        "pregunta": "La unidad básica de los seres vivos es:",
        "opciones": ["A. El tejido.", "B. El órgano.", "C. La célula.", "D. El átomo."],
        "respuesta": "C. La célula.",
        "explicacion_ia": "Todos los organismos vivos están formados por células, que son la unidad estructural y funcional más pequeña de la vida."
    },
    {
        "materia": "Inglés",
        "pregunta": "Where can you see this sign? 'SILENCE - LIBRARY'",
        "opciones": ["A. In a disco.", "B. In a place with books.", "C. In a stadium.", "D. In a market."],
        "respuesta": "B. In a place with books.",
        "explicacion_ia": "Contexto: Library significa biblioteca, un lugar lleno de libros donde se exige silencio."
    },
    {
        "materia": "Matemáticas",
        "pregunta": "¿Qué número es divisible por 2 y por 3 al mismo tiempo?",
        "opciones": ["A. 8", "B. 9", "C. 12", "D. 14"],
        "respuesta": "C. 12",
        "explicacion_ia": "Para ser divisible por 2 debe ser par. Para ser divisible por 3, la suma de sus cifras debe ser múltiplo de 3. 12 es par y 1+2=3."
    },
    {
        "materia": "Sociales y Ciudadanas",
        "pregunta": "¿Cuál es la capital de Colombia?",
        "opciones": ["A. Medellín.", "B. Cali.", "C. Bogotá.", "D. Barranquilla."],
        "respuesta": "C. Bogotá.",
        "explicacion_ia": "Bogotá D.C. es la capital de la República de Colombia y del departamento de Cundinamarca."
    },
    {
        "materia": "Lectura Crítica",
        "pregunta": "¿Qué es un 'párrafo'?",
        "opciones": ["A. Una sola palabra.", "B. Un conjunto de oraciones que desarrollan una idea central, separado por un punto y aparte.", "C. Un libro entero.", "D. Un título."],
        "respuesta": "B. Un conjunto de oraciones que desarrollan una idea central, separado por un punto y aparte.",
        "explicacion_ia": "Es la unidad de texto que agrupa oraciones relacionadas temáticamente."
    },
    {
        "materia": "Ciencias Naturales",
        "pregunta": "¿Qué instrumento mide la temperatura?",
        "opciones": ["A. Barómetro.", "B. Termómetro.", "C. Cronómetro.", "D. Metro."],
        "respuesta": "B. Termómetro.",
        "explicacion_ia": "El termómetro es el instrumento utilizado para medir la temperatura de un cuerpo o sustancia."
    },
    {
        "materia": "Inglés",
        "pregunta": "Complete: 'I ______ breakfast at 7:00 AM every day.'",
        "opciones": ["A. has", "B. have", "C. having", "D. had"],
        "respuesta": "B. have",
        "explicacion_ia": "Rutina diaria: 'I have breakfast' significa 'Yo desayuno'. Se usa Presente Simple."
    },
    {
        "materia": "Matemáticas",
        "pregunta": "La suma de los ángulos internos de un triángulo es:",
        "opciones": ["A. 90 grados.", "B. 180 grados.", "C. 360 grados.", "D. 270 grados."],
        "respuesta": "B. 180 grados.",
        "explicacion_ia": "Regla geométrica universal para triángulos planos: A + B + C = 180°."
    },
    {
        "materia": "Sociales y Ciudadanas",
        "pregunta": "¿Qué derecho se vulnera si a un niño no lo dejan entrar al colegio?",
        "opciones": ["A. Derecho al trabajo.", "B. Derecho a la educación.", "C. Derecho a la salud.", "D. Derecho a la vivienda."],
        "respuesta": "B. Derecho a la educación.",
        "explicacion_ia": "La educación es un derecho fundamental de los niños y el Estado debe garantizar su acceso."
    },
    {
        "materia": "Inglés",
        "pregunta": "Conversation: \n- 'Where do you live?' \n- '__________'",
        "opciones": ["A. I live in Bogota.", "B. I am 15 years old.", "C. My name is Juan.", "D. Yes, I do."],
        "respuesta": "A. I live in Bogota.",
        "explicacion_ia": "Pregunta personal: 'Where' pregunta por lugar. La respuesta debe indicar una ciudad o dirección."
    },
    {
        "materia": "Ciencias Naturales",
        "pregunta": "El movimiento de la Tierra alrededor del Sol se llama:",
        "opciones": ["A. Rotación.", "B. Traslación.", "C. Precesión.", "D. Nutación."],
        "respuesta": "B. Traslación.",
        "explicacion_ia": "Traslación es el giro alrededor del sol (dura 1 año). Rotación es el giro sobre su propio eje (dura 1 día)."
    },
    {
        "materia": "Lectura Crítica",
        "pregunta": "El desenlace de un cuento es:",
        "opciones": ["A. El inicio.", "B. El momento de mayor tensión.", "C. El final o resolución del conflicto.", "D. El título."],
        "respuesta": "C. El final o resolución del conflicto.",
        "explicacion_ia": "Es la parte final de la estructura narrativa donde se resuelven los problemas planteados."
    },
    {
        "materia": "Matemáticas",
        "pregunta": "¿Cuánto es 5 al cubo (5³)?",
        "opciones": ["A. 15", "B. 25", "C. 125", "D. 50"],
        "respuesta": "C. 125",
        "explicacion_ia": "5 x 5 x 5 = 125."
    },
    {
        "materia": "Inglés",
        "pregunta": "Definition: 'The color of the sky on a sunny day.'",
        "opciones": ["A. Green.", "B. Red.", "C. Blue.", "D. Yellow."],
        "respuesta": "C. Blue.",
        "explicacion_ia": "Colores: El cielo despejado es azul (Blue)."
    },
    {
        "materia": "Sociales y Ciudadanas",
        "pregunta": "¿Quién es la máxima autoridad en un municipio?",
        "opciones": ["A. El Presidente.", "B. El Gobernador.", "C. El Alcalde.", "D. El Juez."],
        "respuesta": "C. El Alcalde.",
        "explicacion_ia": "El Alcalde es la primera autoridad administrativa y de policía del municipio."
    },
    {
        "materia": "Ciencias Naturales",
        "pregunta": "¿Qué es la materia?",
        "opciones": ["A. Todo lo que tiene masa y ocupa un lugar en el espacio.", "B. Solo lo que se puede ver.", "C. Solo los gases.", "D. La energía pura."],
        "respuesta": "A. Todo lo que tiene masa y ocupa un lugar en el espacio.",
        "explicacion_ia": "Definición clásica de física. Incluye sólidos, líquidos, gases y plasma."
    },
    {
        "materia": "Inglés",
        "pregunta": "Complete: 'They ______ watching a movie now.'",
        "opciones": ["A. is", "B. am", "C. are", "D. be"],
        "respuesta": "C. are",
        "explicacion_ia": "Presente Continuo: Plural 'They' va con 'are'."
    },
    {
        "materia": "Matemáticas",
        "pregunta": "Si un dado tiene 6 caras, ¿cuál es la probabilidad de sacar un 7?",
        "opciones": ["A. 1/6", "B. 0", "C. 1", "D. 1/7"],
        "respuesta": "B. 0",
        "explicacion_ia": "Es un evento imposible. Un dado estándar solo tiene números del 1 al 6."
    },
    {
        "materia": "Lectura Crítica",
        "pregunta": "¿Qué es un 'protagonista'?",
        "opciones": ["A. El personaje principal de la historia.", "B. El enemigo del héroe.", "C. Un personaje secundario.", "D. El narrador."],
        "respuesta": "A. El personaje principal de la historia.",
        "explicacion_ia": "Es quien lleva el peso de la acción principal. El enemigo es el antagonista."
    },
    {
        "materia": "Sociales y Ciudadanas",
        "pregunta": "La democracia participativa permite a los ciudadanos:",
        "opciones": ["A. Solo votar cada 4 años.", "B. Participar activamente en la toma de decisiones y control del poder.", "C. No hacer nada.", "D. Obedecer ciegamente."],
        "respuesta": "B. Participar activamente en la toma de decisiones y control del poder.",
        "explicacion_ia": "A diferencia de la representativa (solo votar), la participativa incluye mecanismos como el referendo, la consulta popular y el cabildo abierto."
    },
    {
        "materia": "Inglés",
        "pregunta": "Choose the correct preposition: 'The apple is ______ the box.' (Dentro)",
        "opciones": ["A. on", "B. in", "C. at", "D. under"],
        "respuesta": "B. in",
        "explicacion_ia": "Preposiciones: 'In' significa dentro."
    },
    {
        "materia": "Ciencias Naturales",
        "pregunta": "¿Cuál es el símbolo químico del Oxígeno?",
        "opciones": ["A. O", "B. Ox", "C. Og", "D. On"],
        "respuesta": "A. O",
        "explicacion_ia": "En la tabla periódica, el Oxígeno se representa con la letra O."
    },
    {
        "materia": "Matemáticas",
        "pregunta": "¿Cuánto es 7 x 8?",
        "opciones": ["A. 54", "B. 56", "C. 48", "D. 64"],
        "respuesta": "B. 56",
        "explicacion_ia": "Tablas de multiplicar básicas."
    },
    {
        "materia": "Inglés",
        "pregunta": "Conversation: \n- 'Goodbye!' \n- '__________'",
        "opciones": ["A. Hello.", "B. See you later.", "C. Good morning.", "D. I am fine."],
        "respuesta": "B. See you later.",
        "explicacion_ia": "Despedida: La respuesta lógica a un adiós es 'Nos vemos luego'."
    },
    {
        "materia": "Lectura Crítica",
        "pregunta": "Una 'moraleja' es típica de:",
        "opciones": ["A. Las noticias.", "B. Las fábulas.", "C. Los ensayos científicos.", "D. Las recetas de cocina."],
        "respuesta": "B. Las fábulas.",
        "explicacion_ia": "Las fábulas son narraciones breves que dejan una enseñanza final o moraleja."
    },
    {
        "materia": "Sociales y Ciudadanas",
        "pregunta": "¿Qué color representa la paz?",
        "opciones": ["A. Rojo.", "B. Negro.", "C. Blanco.", "D. Verde."],
        "respuesta": "C. Blanco.",
        "explicacion_ia": "Simbología universal: La bandera blanca o la paloma blanca son símbolos de paz."
    },
    {
        "materia": "Ciencias Naturales",
        "pregunta": "¿Qué órgano bombea sangre en el cuerpo humano?",
        "opciones": ["A. Cerebro.", "B. Pulmones.", "C. Corazón.", "D. Estómago."],
        "respuesta": "C. Corazón.",
        "explicacion_ia": "El corazón es el músculo vital del sistema circulatorio."
    },
    {
        "materia": "Inglés",
        "pregunta": "Vocabulary: 'Monday' is a day of the:",
        "opciones": ["A. Year.", "B. Month.", "C. Week.", "D. Weekend."],
        "respuesta": "C. Week.",
        "explicacion_ia": "Vocabulario: Lunes es un día de la semana."
    },
    {
        "materia": "Matemáticas",
        "pregunta": "¿Cuál es el doble de 15?",
        "opciones": ["A. 20", "B. 25", "C. 30", "D. 45"],
        "respuesta": "C. 30",
        "explicacion_ia": "15 + 15 = 30."
    },
    {
        "materia": "Matemáticas",
        "pregunta": "Si lanzas dos dados, ¿cuál es la probabilidad de sacar un 'doble' (ej: 1-1, 2-2, etc.)?",
        "opciones": ["A. 1/6", "B. 1/36", "C. 1/12", "D. 1/2"],
        "respuesta": "A. 1/6",
        "explicacion_ia": "Hay 36 combinaciones totales. Los dobles son (1,1), (2,2), (3,3), (4,4), (5,5), (6,6). Son 6 casos favorables. 6/36 se simplifica a 1/6."
    },
    {
        "materia": "Ciencias Naturales",
        "pregunta": "¿Qué ley de la termodinámica dice que el calor fluye naturalmente del cuerpo caliente al frío?",
        "opciones": ["A. Primera Ley.", "B. Segunda Ley.", "C. Ley Cero.", "D. Ley de la Gravedad."],
        "respuesta": "B. Segunda Ley.",
        "explicacion_ia": "La Segunda Ley establece la dirección de los procesos térmicos y el aumento de la entropía. El calor nunca fluye espontáneamente del frío al calor."
    },
    {
        "materia": "Sociales y Ciudadanas",
        "pregunta": "¿Cuál es la función del Banco de la República?",
        "opciones": ["A. Prestar dinero a la gente para comprar casa.", "B. Controlar la inflación y emitir la moneda legal.", "C. Recaudar impuestos.", "D. Pagar el salario del Presidente."],
        "respuesta": "B. Controlar la inflación y emitir la moneda legal.",
        "explicacion_ia": "Es el banco central. Su objetivo principal es mantener el poder adquisitivo de la moneda (controlar que los precios no suban descontroladamente)."
    },
    {
        "materia": "Lectura Crítica",
        "pregunta": "En el enunciado 'Sus ojos eran dos luceros que iluminaban mi camino', la figura literaria es:",
        "opciones": ["A. Símil.", "B. Metáfora.", "C. Anáfora.", "D. Ironía."],
        "respuesta": "B. Metáfora.",
        "explicacion_ia": "Sustituye 'ojos brillantes' por 'luceros' de forma directa, sin usar comparativos como 'como'."
    },
    {
        "materia": "Inglés",
        "pregunta": "Complete: 'My brother ______ football on Saturdays.'",
        "opciones": ["A. play", "B. plays", "C. playing", "D. played"],
        "respuesta": "B. plays",
        "explicacion_ia": "Presente Simple: Tercera persona (My brother/He) añade 's' al verbo."
    },
    {
        "materia": "Matemáticas",
        "pregunta": "El 25% de un número es 20. ¿Cuál es el número?",
        "opciones": ["A. 40", "B. 50", "C. 80", "D. 100"],
        "respuesta": "C. 80",
        "explicacion_ia": "25% es la cuarta parte. Si la cuarta parte es 20, el total es 20 * 4 = 80."
    },
    {
        "materia": "Ciencias Naturales",
        "pregunta": "¿Qué tipo de energía se almacena en una batería?",
        "opciones": ["A. Energía Cinética.", "B. Energía Química.", "C. Energía Nuclear.", "D. Energía Térmica."],
        "respuesta": "B. Energía Química.",
        "explicacion_ia": "Las baterías almacenan energía en enlaces químicos que luego se convierten en energía eléctrica."
    },
    {
        "materia": "Sociales y Ciudadanas",
        "pregunta": "La 'Consulta Popular' es un mecanismo para:",
        "opciones": ["A. Elegir al alcalde.", "B. Que el pueblo decida sobre un asunto de trascendencia nacional, departamental o local mediante una pregunta de SÍ o NO.", "C. Pedir una cita médica.", "D. Protestar en la calle."],
        "respuesta": "B. Que el pueblo decida sobre un asunto de trascendencia nacional, departamental o local mediante una pregunta de SÍ o NO.",
        "explicacion_ia": "Ejemplo: ¿Está usted de acuerdo con que se realice minería en su municipio? SÍ o NO."
    },
    {
        "materia": "Lectura Crítica",
        "pregunta": "Un texto que explica paso a paso cómo armar un mueble es:",
        "opciones": ["A. Narrativo.", "B. Argumentativo.", "C. Instructivo.", "D. Poético."],
        "respuesta": "C. Instructivo.",
        "explicacion_ia": "Su función es guiar al lector para realizar una tarea específica mediante instrucciones secuenciales."
    },
    {
        "materia": "Inglés",
        "pregunta": "Vocabulary: 'Winter' is the season when it is:",
        "opciones": ["A. Hot.", "B. Cold.", "C. Warm.", "D. Dry."],
        "respuesta": "B. Cold.",
        "explicacion_ia": "Estaciones: Winter (Invierno) es la época fría."
    },
    {
        "materia": "Matemáticas",
        "pregunta": "¿Cuánto es la mitad de 1/2?",
        "opciones": ["A. 1", "B. 1/4", "C. 1/3", "D. 2/2"],
        "respuesta": "B. 1/4",
        "explicacion_ia": "Dividir una fracción a la mitad es lo mismo que multiplicarla por 1/2. (1/2) * (1/2) = 1/4."
    },
    {
        "materia": "Ciencias Naturales",
        "pregunta": "¿Cuál es el hueso más largo del cuerpo humano?",
        "opciones": ["A. La tibia.", "B. El fémur.", "C. El húmero.", "D. La costilla."],
        "respuesta": "B. El fémur.",
        "explicacion_ia": "El fémur se encuentra en el muslo y es el hueso más largo y fuerte."
    },
    {
        "materia": "Sociales y Ciudadanas",
        "pregunta": "¿Qué es un 'Estado Laico'?",
        "opciones": ["A. Un estado ateo que prohíbe la religión.", "B. Un estado que es neutral frente a las religiones y garantiza la libertad de cultos.", "C. Un estado gobernado por la iglesia.", "D. Un estado donde solo existe una religión oficial."],
        "respuesta": "B. Un estado que es neutral frente a las religiones y garantiza la libertad de cultos.",
        "explicacion_ia": "Colombia es laico desde 1991. No hay religión oficial, pero se respetan todas."
    },
    {
        "materia": "Lectura Crítica",
        "pregunta": "Si en una noticia el titular dice: 'Voraz incendio devora tres casas', el adjetivo 'voraz' (que come mucho) aplicado al fuego es una:",
        "opciones": ["A. Personificación.", "B. Metáfora.", "C. Comparación.", "D. Hipérbole."],
        "respuesta": "A. Personificación.",
        "explicacion_ia": "Atribuye una cualidad de ser vivo (comer con ansia) a un elemento inanimado (el fuego)."
    },
    {
        "materia": "Inglés",
        "pregunta": "Complete: 'I am ______ tired to run.'",
        "opciones": ["A. to", "B. two", "C. too", "D. toe"],
        "respuesta": "C. too",
        "explicacion_ia": "Intensificador negativo: 'Too tired' significa 'Demasiado cansado' (tanto que no puedo hacerlo)."
    },
    {
        "materia": "Matemáticas",
        "pregunta": "Si 3x = 15, ¿cuánto vale x + 2?",
        "opciones": ["A. 5", "B. 7", "C. 17", "D. 3"],
        "respuesta": "B. 7",
        "explicacion_ia": "Primero hallamos x: 15/3 = 5. Luego sumamos 2: 5 + 2 = 7."
    },
    {
        "materia": "Ciencias Naturales",
        "pregunta": "La 'Inercia' es la propiedad de los cuerpos de:",
        "opciones": ["A. Moverse rápido.", "B. Resistirse a cambiar su estado de reposo o movimiento.", "C. Caer al suelo.", "D. Flotar en el agua."],
        "respuesta": "B. Resistirse a cambiar su estado de reposo o movimiento.",
        "explicacion_ia": "Es la tendencia a seguir haciendo lo que estaban haciendo (quietos o moviéndose) hasta que una fuerza los obligue a cambiar."
    },
    {
        "materia": "Sociales y Ciudadanas",
        "pregunta": "El 'Feminicidio' se diferencia del homicidio común porque:",
        "opciones": ["A. La víctima es mujer y el crimen ocurre por razones de género o discriminación.", "B. La víctima es famosa.", "C. Ocurre de noche.", "D. El asesino es mujer."],
        "respuesta": "A. La víctima es mujer y el crimen ocurre por razones de género o discriminación.",
        "explicacion_ia": "Es un tipo penal específico que castiga la violencia basada en el hecho de ser mujer, como posesión, celos enfermizos o misoginia."
    },
    {
        "materia": "Lectura Crítica",
        "pregunta": "¿Qué es la 'Intención Comunicativa'?",
        "opciones": ["A. Las ganas de hablar.", "B. El objetivo que persigue el autor al escribir (informar, convencer, entretener).", "C. La ortografía del texto.", "D. El nombre del autor."],
        "respuesta": "B. El objetivo que persigue el autor al escribir (informar, convencer, entretener).",
        "explicacion_ia": "Todo texto se escribe para algo. Identificar el 'para qué' es clave en la lectura crítica."
    },
    {
        "materia": "Inglés",
        "pregunta": "Where can you see this sign? 'PLEASE FASTEN YOUR SEATBELT'",
        "opciones": ["A. In a house.", "B. In a park.", "C. In an airplane or car.", "D. In a shower."],
        "respuesta": "C. In an airplane or car.",
        "explicacion_ia": "Instrucción de seguridad: 'Abroche su cinturón de seguridad'."
    },
    {
        "materia": "Matemáticas",
        "pregunta": "¿Cuál es el valor de x en: x/2 + 5 = 10?",
        "opciones": ["A. 5", "B. 10", "C. 15", "D. 20"],
        "respuesta": "B. 10",
        "explicacion_ia": "Despeje: x/2 = 10 - 5 -> x/2 = 5 -> x = 5 * 2 -> x = 10."
    },
    {
        "materia": "Ciencias Naturales",
        "pregunta": "¿Qué parte de la planta se encarga de absorber agua y nutrientes del suelo?",
        "opciones": ["A. Hoja.", "B. Tallo.", "C. Raíz.", "D. Flor."],
        "respuesta": "C. Raíz.",
        "explicacion_ia": "La raíz ancla la planta y absorbe los nutrientes minerales y el agua necesarios para la fotosíntesis."
    },
    {
        "materia": "Sociales y Ciudadanas",
        "pregunta": "¿Qué significa 'Rama Judicial'?",
        "opciones": ["A. Los policías de tránsito.", "B. El conjunto de jueces y magistrados encargados de administrar justicia.", "C. Los abogados privados.", "D. Las cárceles."],
        "respuesta": "B. El conjunto de jueces y magistrados encargados de administrar justicia.",
        "explicacion_ia": "Es una de las tres ramas del poder público. Su función es solucionar conflictos y castigar delitos basándose en la ley."
    },
    {
        "materia": "Lectura Crítica",
        "pregunta": "El antónimo de 'Eficaz' es:",
        "opciones": ["A. Rápido.", "B. Inútil o Ineficaz.", "C. Fuerte.", "D. Valiente."],
        "respuesta": "B. Inútil o Ineficaz.",
        "explicacion_ia": "Eficaz es que logra el efecto deseado. Lo contrario es ineficaz."
    },
    {
        "materia": "Inglés",
        "pregunta": "Choose the correct question: '______ did you go last night?'",
        "opciones": ["A. What", "B. Where", "C. Who", "D. Which"],
        "respuesta": "B. Where",
        "explicacion_ia": "Pregunta por lugar: Si dice 'go' (ir), el pronombre lógico es 'Where' (Dónde)."
    },
    {
        "materia": "Matemáticas",
        "pregunta": "Un cuadrado tiene un área de 36 cm². Si duplicamos la longitud de sus lados, ¿cuál será la nueva área?",
        "opciones": ["A. 72 cm²", "B. 144 cm²", "C. 108 cm²", "D. 360 cm²"],
        "respuesta": "B. 144 cm²",
        "explicacion_ia": "Lado original = 6 (porque 6x6=36). Nuevo lado = 12. Nueva área = 12x12 = 144. (El área se cuadruplica)."
    },
    {
        "materia": "Ciencias Naturales",
        "pregunta": "La molécula de O3 se conoce como:",
        "opciones": ["A. Oxígeno respirable.", "B. Ozono.", "C. Agua.", "D. Dióxido de carbono."],
        "respuesta": "B. Ozono.",
        "explicacion_ia": "O2 es el oxígeno que respiramos. O3 es el Ozono (tóxico abajo, pero protector en la estratósfera)."
    },
    {
        "materia": "Sociales y Ciudadanas",
        "pregunta": "El 'Personero Estudiantil' debe promover:",
        "opciones": ["A. Fiestas cada semana.", "B. La defensa de los derechos y deberes de los estudiantes.", "C. Que no haya clases.", "D. La venta de dulces."],
        "respuesta": "B. La defensa de los derechos y deberes de los estudiantes.",
        "explicacion_ia": "Es la figura democrática escolar encargada de velar porque se cumpla el manual de convivencia y se respeten los derechos de los alumnos."
    },
    {
        "materia": "Lectura Crítica",
        "pregunta": "Si un texto argumentativo termina diciendo: 'En conclusión, es urgente tomar medidas...', esta parte se llama:",
        "opciones": ["A. Introducción.", "B. Tesis.", "C. Conclusión.", "D. Desarrollo."],
        "respuesta": "C. Conclusión.",
        "explicacion_ia": "Es el cierre del texto donde se sintetizan los argumentos y se reafirma la tesis o se hace un llamado a la acción."
    },
    {
        "materia": "Inglés",
        "pregunta": "Complete: 'She ______ speak three languages.'",
        "opciones": ["A. can", "B. cans", "C. can to", "D. canning"],
        "respuesta": "A. can",
        "explicacion_ia": "Modal Can: Nunca lleva 's' en tercera persona ni 'to' después. Siempre es 'She can'."
    },
    {
        "materia": "Matemáticas",
        "pregunta": "En una rifa de 100 números, ¿cuál es la probabilidad de ganar si compras 10 boletas?",
        "opciones": ["A. 1/100", "B. 1/10", "C. 10/1000", "D. 50%"],
        "respuesta": "B. 1/10",
        "explicacion_ia": "Casos favorables: 10. Casos totales: 100. Probabilidad: 10/100. Simplificando (quitando ceros) = 1/10."
    },
    {
        "materia": "Ciencias Naturales",
        "pregunta": "¿Qué ocurre en la 'Fecundación'?",
        "opciones": ["A. Nace el bebé.", "B. Se une el óvulo con el espermatozoide.", "C. La célula se divide.", "D. Se produce leche."],
        "respuesta": "B. Se une el óvulo con el espermatozoide.",
        "explicacion_ia": "Es el momento biológico donde se combinan los gametos masculino y femenino para formar un cigoto."
    },
    {
        "materia": "Sociales y Ciudadanas",
        "pregunta": "¿Qué es la 'Acción de Grupo'?",
        "opciones": ["A. Una reunión de amigos.", "B. Un mecanismo judicial para pedir indemnización cuando un grupo de personas (mínimo 20) sufrió un daño por la misma causa.", "C. Una protesta violenta.", "D. Un partido de fútbol."],
        "respuesta": "B. Un mecanismo judicial para pedir indemnización cuando un grupo de personas (mínimo 20) sufrió un daño por la misma causa.",
        "explicacion_ia": "A diferencia de la Acción Popular (que es preventiva), la de Grupo es reparatoria (busca dinero por daños causados)."
    },
    {
        "materia": "Lectura Crítica",
        "pregunta": "En la oración 'La luna nos miraba tristemente', hay una:",
        "opciones": ["A. Prosopopeya (Personificación).", "B. Símil.", "C. Hipérbole.", "D. Anáfora."],
        "respuesta": "A. Prosopopeya (Personificación).",
        "explicacion_ia": "La luna no tiene ojos ni sentimientos. Se le atribuyen cualidades humanas."
    },
    {
        "materia": "Inglés",
        "pregunta": "Conversation: \n- 'I am thirsty.' \n- '__________'",
        "opciones": ["A. Eat a sandwich.", "B. Have a glass of water.", "C. Go to sleep.", "D. Read a book."],
        "respuesta": "B. Have a glass of water.",
        "explicacion_ia": "Necesidad física: Thirsty = Sediento. Solución = Agua."
    },
    {
        "materia": "Matemáticas",
        "pregunta": "El resultado de multiplicar un número negativo por uno positivo es:",
        "opciones": ["A. Positivo.", "B. Negativo.", "C. Cero.", "D. Depende del número."],
        "respuesta": "B. Negativo.",
        "explicacion_ia": "Ley de los signos: Más por menos da menos (+ * - = -)."
    },
    {
        "materia": "Ciencias Naturales",
        "pregunta": "La gravedad en la Luna es:",
        "opciones": ["A. Mayor que en la Tierra.", "B. Igual que en la Tierra.", "C. Menor que en la Tierra.", "D. No existe gravedad."],
        "respuesta": "C. Menor que en la Tierra.",
        "explicacion_ia": "Como la Luna tiene menos masa que la Tierra, su atracción gravitatoria es menor (aprox. 1/6 de la terrestre)."
    },
    {
        "materia": "Sociales y Ciudadanas",
        "pregunta": "¿Qué es el 'Derecho de Asilo'?",
        "opciones": ["A. El derecho a tener casa.", "B. La protección que un Estado ofrece a personas perseguidas políticamente en su país de origen.", "C. El derecho a ir al ancianato.", "D. El derecho a salir de vacaciones."],
        "respuesta": "B. La protección que un Estado ofrece a personas perseguidas políticamente en su país de origen.",
        "explicacion_ia": "Es un derecho humano fundamental para proteger la vida de quienes son perseguidos por sus ideas, raza o religión."
    },
    {
        "materia": "Inglés",
        "pregunta": "Definition: 'A building where you can see old objects and art.'",
        "opciones": ["A. Bank.", "B. Museum.", "C. Hospital.", "D. Cinema."],
        "respuesta": "B. Museum.",
        "explicacion_ia": "Lugares: Donde se ven objetos antiguos y arte es el Museo."
    },
    {
        "materia": "Lectura Crítica",
        "pregunta": "Si un texto dice: 'Pedro es un lince para los negocios', significa que:",
        "opciones": ["A. Pedro tiene orejas grandes.", "B. Pedro es astuto, rápido y hábil.", "C. Pedro es un animal.", "D. Pedro vive en el bosque."],
        "respuesta": "B. Pedro es astuto, rápido y hábil.",
        "explicacion_ia": "Es una metáfora común. El lince se asocia con agudeza visual y destreza."
    },
    {
        "materia": "Matemáticas",
        "pregunta": "Un padre tiene 45 años y su hijo 15. ¿Dentro de cuántos años la edad del padre será el doble de la del hijo?",
        "opciones": ["A. 10 años", "B. 15 años", "C. 5 años", "D. 20 años"],
        "respuesta": "B. 15 años",
        "explicacion_ia": "Planteamos: (45 + x) = 2 * (15 + x). 45 + x = 30 + 2x. 15 = x. En 15 años, el padre tendrá 60 y el hijo 30."
    },
    {
        "materia": "Lectura Crítica",
        "pregunta": "En el enunciado 'No todo lo que brilla es oro', la intención comunicativa es:",
        "opciones": ["A. Enseñar sobre minería.", "B. Advertir que las apariencias pueden ser engañosas.", "C. Describir las propiedades de los metales.", "D. Promover la joyería."],
        "respuesta": "B. Advertir que las apariencias pueden ser engañosas.",
        "explicacion_ia": "Es un refrán que invita a desconfiar de lo superficialmente atractivo."
    },
    {
        "materia": "Sociales y Ciudadanas",
        "pregunta": "La 'Revolución Industrial' trajo consigo la migración masiva del campo a la ciudad. ¿Qué consecuencia social inmediata generó este fenómeno?",
        "opciones": ["A. La desaparición de la pobreza.", "B. El hacinamiento y malas condiciones laborales en las urbes.", "C. La igualdad total entre clases sociales.", "D. El fin de las monarquías."],
        "respuesta": "B. El hacinamiento y malas condiciones laborales en las urbes.",
        "explicacion_ia": "El rápido crecimiento urbano sin planificación creó cinturones de miseria y explotación laboral (proletariado)."
    },
    {
        "materia": "Ciencias Naturales",
        "pregunta": "¿Qué ocurre si se extirpa la glándula tiroides a una persona?",
        "opciones": ["A. Deja de producir insulina.", "B. Afecta su metabolismo y regulación de temperatura.", "C. No puede digerir grasas.", "D. Pierde la memoria."],
        "respuesta": "B. Afecta su metabolismo y regulación de temperatura.",
        "explicacion_ia": "La tiroides produce tiroxina, hormona clave para regular el ritmo metabólico del cuerpo."
    },
    {
        "materia": "Matemáticas",
        "pregunta": "Si lanzas tres monedas al aire, ¿cuál es la probabilidad de obtener tres caras?",
        "opciones": ["A. 1/3", "B. 1/8", "C. 1/6", "D. 3/8"],
        "respuesta": "B. 1/8",
        "explicacion_ia": "Cada moneda tiene 1/2. Son eventos independientes: 1/2 * 1/2 * 1/2 = 1/8."
    },
    {
        "materia": "Sociales y Ciudadanas",
        "pregunta": "¿Cuál es la función del 'Voto en Blanco' según la legislación colombiana?",
        "opciones": ["A. Regalar el voto al ganador.", "B. Manifestar disconformidad con todos los candidatos.", "C. Anular la tarjeta electoral.", "D. Sumar votos al partido minoritario."],
        "respuesta": "B. Manifestar disconformidad con todos los candidatos.",
        "explicacion_ia": "Es una expresión política válida de disenso. Si gana, obliga a repetir elecciones."
    },
    {
        "materia": "Ciencias Naturales",
        "pregunta": "La fuerza de rozamiento o fricción siempre actúa en dirección:",
        "opciones": ["A. Igual al movimiento.", "B. Perpendicular al movimiento.", "C. Opuesta al movimiento.", "D. Vertical hacia abajo."],
        "respuesta": "C. Opuesta al movimiento.",
        "explicacion_ia": "La fricción es una fuerza resistiva que se opone al deslizamiento entre superficies."
    },
    {
        "materia": "Lectura Crítica",
        "pregunta": "Sinónimo de 'Altruista':",
        "opciones": ["A. Egoísta.", "B. Solidario o filántropo.", "C. Alto.", "D. Indiferente."],
        "respuesta": "B. Solidario o filántropo.",
        "explicacion_ia": "El altruismo es la tendencia a procurar el bien de las personas de manera desinteresada."
    },
    {
        "materia": "Matemáticas",
        "pregunta": "¿Cuál es el área de un triángulo de base 10 cm y altura 5 cm?",
        "opciones": ["A. 50 cm²", "B. 25 cm²", "C. 15 cm²", "D. 100 cm²"],
        "respuesta": "B. 25 cm²",
        "explicacion_ia": "Fórmula: (Base * Altura) / 2. (10 * 5) / 2 = 50 / 2 = 25."
    },
    {
        "materia": "Ciencias Naturales",
        "pregunta": "¿Qué partícula del átomo determina el elemento químico (su identidad)?",
        "opciones": ["A. El neutrón.", "B. El electrón.", "C. El protón.", "D. El fotón."],
        "respuesta": "C. El protón.",
        "explicacion_ia": "El número de protones (Número Atómico Z) define si un átomo es Oro, Oxígeno, etc."
    },
    {
        "materia": "Sociales y Ciudadanas",
        "pregunta": "La tutela NO procede cuando:",
        "opciones": ["A. Se viola un derecho fundamental.", "B. Existen otros mecanismos de defensa judicial eficaces (subsidiariedad).", "C. El afectado es un niño.", "D. La violación la comete un particular encargado de servicio público."],
        "respuesta": "B. Existen otros mecanismos de defensa judicial eficaces (subsidiariedad).",
        "explicacion_ia": "La tutela es un mecanismo residual; si hay otra vía judicial idónea, se debe usar esa primero."
    },
    {
        "materia": "Lectura Crítica",
        "pregunta": "En un texto, la 'idea principal' se diferencia de las 'secundarias' porque:",
        "opciones": ["A. Es la más larga.", "B. Resume la esencia del mensaje y las otras solo la detallan.", "C. Aparece siempre al final.", "D. Está escrita en mayúsculas."],
        "respuesta": "B. Resume la esencia del mensaje y las otras solo la detallan.",
        "explicacion_ia": "La idea principal es la columna vertebral del texto; sin ella, el texto pierde sentido."
    },
    {
        "materia": "Matemáticas",
        "pregunta": "Si un pantalón cuesta $80.000 con el IVA incluido (19%), ¿cuál es el precio aproximado sin IVA?",
        "opciones": ["A. $61.000", "B. $67.226", "C. $75.000", "D. $64.800"],
        "respuesta": "B. $67.226",
        "explicacion_ia": "Precio Base = Precio Final / 1.19. $80.000 / 1.19 ≈ 67.226."
    },
    {
        "materia": "Ciencias Naturales",
        "pregunta": "La 'Selección Artificial' se diferencia de la natural en que:",
        "opciones": ["A. Ocurre más lento.", "B. Es el ser humano quien elige qué rasgos reproducir (ej: razas de perros).", "C. No implica genética.", "D. Solo ocurre en plantas."],
        "respuesta": "B. Es el ser humano quien elige qué rasgos reproducir (ej: razas de perros).",
        "explicacion_ia": "En la artificial, el criterio de selección no es la supervivencia, sino el deseo humano."
    },
    {
        "materia": "Sociales y Ciudadanas",
        "pregunta": "¿Qué bloque económico integran Colombia, Perú, Chile y México?",
        "opciones": ["A. Mercosur.", "B. La Alianza del Pacífico.", "C. La Unión Europea.", "D. La OTAN."],
        "respuesta": "B. La Alianza del Pacífico.",
        "explicacion_ia": "Es una iniciativa de integración regional para fomentar el libre comercio y la cooperación."
    },
    {
        "materia": "Lectura Crítica",
        "pregunta": "¿Qué figura retórica es: 'El viento susurraba tu nombre'?",
        "opciones": ["A. Símil.", "B. Hipérbole.", "C. Prosopopeya (Personificación).", "D. Anáfora."],
        "respuesta": "C. Prosopopeya (Personificación).",
        "explicacion_ia": "Atribuye una cualidad humana (susurrar) a un elemento inanimado (viento)."
    },
    {
        "materia": "Matemáticas",
        "pregunta": "La suma de los ángulos interiores de un pentágono es:",
        "opciones": ["A. 180°", "B. 360°", "C. 540°", "D. 720°"],
        "respuesta": "C. 540°",
        "explicacion_ia": "Fórmula: (n-2) * 180. (5-2)*180 = 3*180 = 540."
    },
    {
        "materia": "Ciencias Naturales",
        "pregunta": "¿Qué ocurre a nivel molecular cuando aumenta la temperatura de un gas en un recipiente cerrado?",
        "opciones": ["A. Las moléculas se detienen.", "B. Aumenta la energía cinética (velocidad) y la presión.", "C. Disminuye el volumen.", "D. Las moléculas se unen."],
        "respuesta": "B. Aumenta la energía cinética (velocidad) y la presión.",
        "explicacion_ia": "El calor agita las moléculas; al moverse más rápido, chocan más fuerte contra las paredes (presión)."
    },
    {
        "materia": "Sociales y Ciudadanas",
        "pregunta": "El 'Bogotazo' dividió la historia de Colombia en dos. ¿Qué consecuencia política inmediata trajo?",
        "opciones": ["A. La paz total.", "B. El recrudecimiento de la violencia bipartidista.", "C. La independencia de España.", "D. La Constitución del 91."],
        "respuesta": "B. El recrudecimiento de la violencia bipartidista.",
        "explicacion_ia": "Tras la muerte de Gaitán, la violencia entre liberales y conservadores se extendió a todo el país."
    },
    {
        "materia": "Lectura Crítica",
        "pregunta": "Un texto que defiende la idea de que 'la tecnología nos aísla' mediante razones y ejemplos es:",
        "opciones": ["A. Expositivo.", "B. Narrativo.", "C. Argumentativo.", "D. Descriptivo."],
        "respuesta": "C. Argumentativo.",
        "explicacion_ia": "Su objetivo es persuadir o sostener una tesis (opinión) con argumentos."
    },
    {
        "materia": "Matemáticas",
        "pregunta": "Si x/2 + 5 = 15, halla x.",
        "opciones": ["A. 10", "B. 20", "C. 5", "D. 25"],
        "respuesta": "B. 20",
        "explicacion_ia": "x/2 = 10 -> x = 10 * 2 -> x = 20."
    },
    {
        "materia": "Ciencias Naturales",
        "pregunta": "Los organismos productores (plantas) ocupan el:",
        "opciones": ["A. Primer nivel trófico.", "B. Segundo nivel trófico.", "C. Último nivel trófico.", "D. Nivel de descomponedores."],
        "respuesta": "A. Primer nivel trófico.",
        "explicacion_ia": "Son la base de la cadena alimenticia porque producen su propia energía (autótrofos)."
    },
    {
        "materia": "Sociales y Ciudadanas",
        "pregunta": "¿Qué es la 'Silla Vacía' en el Congreso colombiano?",
        "opciones": ["A. Un mueble sin uso.", "B. La sanción a un partido que pierde una curul si su congresista es condenado por delitos graves (corrupción, parapolítica).", "C. Un puesto para el público.", "D. La ausencia del presidente."],
        "respuesta": "B. La sanción a un partido que pierde una curul si su congresista es condenado por delitos graves (corrupción, parapolítica).",
        "explicacion_ia": "Busca responsabilizar a los partidos por los avales que otorgan a delincuentes. Nadie reemplaza esa curul."
    },
    {
        "materia": "Lectura Crítica",
        "pregunta": "La palabra 'Procrastinar' significa:",
        "opciones": ["A. Adelantar trabajo.", "B. Diferir o aplazar tareas por pereza o miedo.", "C. Protestar.", "D. Crear algo nuevo."],
        "respuesta": "B. Diferir o aplazar tareas por pereza o miedo.",
        "explicacion_ia": "Es el hábito de retrasar actividades que deben atenderse, sustituyéndolas por otras más irrelevantes."
    },
    {
        "materia": "Matemáticas",
        "pregunta": "¿Cuál es el volumen de una esfera? (Fórmula)",
        "opciones": ["A. 4/3 πr³", "B. πr²", "C. 2πr", "D. Base x Altura"],
        "respuesta": "A. 4/3 πr³",
        "explicacion_ia": "Es la fórmula geométrica estándar para el volumen de una esfera."
    },
    {
        "materia": "Ciencias Naturales",
        "pregunta": "La insulina es producida por:",
        "opciones": ["A. El hígado.", "B. El páncreas.", "C. El riñón.", "D. El estómago."],
        "respuesta": "B. El páncreas.",
        "explicacion_ia": "Las células beta del páncreas secretan insulina para regular la glucosa en sangre."
    },
    {
        "materia": "Sociales y Ciudadanas",
        "pregunta": "La Segunda Guerra Mundial finalizó con:",
        "opciones": ["A. La caída del Muro de Berlín.", "B. El bombardeo atómico a Hiroshima y Nagasaki.", "C. La Revolución Francesa.", "D. La invasión a Polonia."],
        "respuesta": "B. El bombardeo atómico a Hiroshima y Nagasaki.",
        "explicacion_ia": "La rendición de Japón tras las bombas atómicas en 1945 marcó el fin definitivo del conflicto."
    },
    {
        "materia": "Lectura Crítica",
        "pregunta": "¿Qué es una 'falacia ad populum'?",
        "opciones": ["A. Atacar a la persona.", "B. Creer que algo es verdad solo porque la mayoría lo cree.", "C. Apelar a la autoridad.", "D. Una mentira piadosa."],
        "respuesta": "B. Creer que algo es verdad solo porque la mayoría lo cree.",
        "explicacion_ia": "Apela a la popularidad ('todo el mundo lo hace') en lugar de dar razones lógicas."
    },
    {
        "materia": "Matemáticas",
        "pregunta": "Un grifo llena un tanque en 4 horas y otro en 6 horas. Juntos, ¿en cuánto tiempo lo llenan?",
        "opciones": ["A. 5 horas.", "B. 10 horas.", "C. 2.4 horas.", "D. 3 horas."],
        "respuesta": "C. 2.4 horas.",
        "explicacion_ia": "Suma de tasas: 1/4 + 1/6 = 5/12 tanques por hora. Invertimos para hallar el tiempo: 12/5 = 2.4 horas."
    },
    {
        "materia": "Ciencias Naturales",
        "pregunta": "¿Qué ley explica que 'La energía no se crea ni se destruye'?",
        "opciones": ["A. Ley de Ohm.", "B. Primera Ley de la Termodinámica.", "C. Ley de la Gravedad.", "D. Ley de Boyle."],
        "respuesta": "B. Primera Ley de la Termodinámica.",
        "explicacion_ia": "Principio universal de conservación de la energía."
    },
    {
        "materia": "Sociales y Ciudadanas",
        "pregunta": "El apartheid fue un sistema de segregación racial implantado en:",
        "opciones": ["A. Estados Unidos.", "B. Sudáfrica.", "C. Alemania.", "D. Brasil."],
        "respuesta": "B. Sudáfrica.",
        "explicacion_ia": "Fue un régimen legalizado de discriminación contra la población negra, desmantelado en los 90s (Mandela)."
    },
    {
        "materia": "Lectura Crítica",
        "pregunta": "En la oración 'Juan come manzanas', el sujeto es:",
        "opciones": ["A. Manzanas.", "B. Come.", "C. Juan.", "D. Tácito."],
        "respuesta": "C. Juan.",
        "explicacion_ia": "El sujeto es quien realiza la acción del verbo."
    },
    {
        "materia": "Matemáticas",
        "pregunta": "¿Cuál es el siguiente número en la sucesión de Fibonacci: 1, 1, 2, 3, 5, 8...?",
        "opciones": ["A. 10", "B. 11", "C. 13", "D. 12"],
        "respuesta": "C. 13",
        "explicacion_ia": "Cada número es la suma de los dos anteriores: 5 + 8 = 13."
    },
    {
        "materia": "Ciencias Naturales",
        "pregunta": "El ADN se encuentra principalmente en:",
        "opciones": ["A. El citoplasma.", "B. El núcleo celular.", "C. La membrana.", "D. El aparato de Golgi."],
        "respuesta": "B. El núcleo celular.",
        "explicacion_ia": "En las células eucariotas, el material genético está protegido dentro del núcleo."
    },
    {
        "materia": "Sociales y Ciudadanas",
        "pregunta": "Un estado 'Federal' se caracteriza por:",
        "opciones": ["A. Un poder central absoluto.", "B. La autonomía política y legislativa de sus estados o provincias miembros.", "C. No tener presidente.", "D. Ser una monarquía."],
        "respuesta": "B. La autonomía política y legislativa de sus estados o provincias miembros.",
        "explicacion_ia": "Ej: EE.UU. o Brasil. Los estados tienen sus propias constituciones y leyes, unidos bajo una federación."
    },
    {
        "materia": "Lectura Crítica",
        "pregunta": "La 'cohesión' textual se refiere a:",
        "opciones": ["A. Que el texto tenga sentido lógico (coherencia).", "B. La conexión gramatical y léxica entre las palabras y oraciones (uso de conectores, pronombres).", "C. La ortografía.", "D. La longitud del texto."],
        "respuesta": "B. La conexión gramatical y léxica entre las palabras y oraciones (uso de conectores, pronombres).",
        "explicacion_ia": "Es el 'pegamento' lingüístico que une las frases (sintaxis)."
    },
    {
        "materia": "Matemáticas",
        "pregunta": "El 25% de un número es 50. ¿Cuál es el 50% de ese mismo número?",
        "opciones": ["A. 100", "B. 200", "C. 75", "D. 150"],
        "respuesta": "A. 100",
        "explicacion_ia": "Si 25% es 50, el 50% (que es el doble de 25%) será el doble de 50, es decir, 100."
    },
    {
        "materia": "Ciencias Naturales",
        "pregunta": "¿Qué tipo de enlace une a los átomos en la molécula de agua (H2O)?",
        "opciones": ["A. Iónico.", "B. Covalente polar.", "C. Metálico.", "D. Puente de hidrógeno."],
        "respuesta": "B. Covalente polar.",
        "explicacion_ia": "Dentro de la molécula, O y H comparten electrones (covalente), pero desigualmente (polar)."
    },
    {
        "materia": "Sociales y Ciudadanas",
        "pregunta": "El Plan Marshall fue:",
        "opciones": ["A. Una estrategia de guerra.", "B. Un plan de ayuda económica de EE.UU. para reconstruir Europa tras la II Guerra Mundial.", "C. Un plan para invadir Rusia.", "D. Un acuerdo de paz en Colombia."],
        "respuesta": "B. Un plan de ayuda económica de EE.UU. para reconstruir Europa tras la II Guerra Mundial.",
        "explicacion_ia": "Buscaba reactivar la economía europea y frenar el avance del comunismo."
    },
    {
        "materia": "Lectura Crítica",
        "pregunta": "En el género lírico (poesía), predomina la función:",
        "opciones": ["A. Referencial.", "B. Emotiva o Expresiva.", "C. Apelativa.", "D. Metalingüística."],
        "respuesta": "B. Emotiva o Expresiva.",
        "explicacion_ia": "El poeta expresa su subjetividad, sentimientos y mundo interior."
    },
    {
        "materia": "Lectura Crítica",
        "pregunta": "¿Cuál de los siguientes es un medio de comunicación masiva?",
        "opciones": ["A. Un diario personal.", "B. Una carta familiar.", "C. La televisión.", "D. Un memorando de oficina."],
        "respuesta": "C. La televisión.",
        "explicacion_ia": "Los medios masivos (Mass Media) están diseñados para enviar mensajes a grandes audiencias anónimas y heterogéneas simultáneamente (TV, Radio, Internet, Prensa)."
    },
    {
        "materia": "Matemáticas",
        "pregunta": "¿Qué número sigue en la serie: 2, 4, 8, 16, ...?",
        "opciones": ["A. 24", "B. 32", "C. 30", "D. 20"],
        "respuesta": "B. 32",
        "explicacion_ia": "Es una progresión geométrica donde cada término se multiplica por 2 (potencias de 2). 16 x 2 = 32."
    },
    {
        "materia": "Matemáticas",
        "pregunta": "Se tienen dos urnas: La Urna A contiene 4 bolas rojas y 2 azules. La Urna B contiene 3 bolas rojas y 5 azules. Se lanza una moneda: si cae cara, se extrae una bola de la Urna A; si cae sello, se extrae de la Urna B. ¿Cuál es la probabilidad total de sacar una bola roja?",
        "opciones": ["A. 7/14", "B. 17/24", "C. 17/48", "D. 25/48"],
        "respuesta": "D. 25/48",
        "explicacion_ia": "Teorema de Probabilidad Total. P(Roja) = P(Cara)*P(Roja|A) + P(Sello)*P(Roja|B). (1/2 * 4/6) + (1/2 * 3/8) = (1/3) + (3/16) = 16/48 + 9/48 = 25/48."
    },
    {
        "materia": "Lectura Crítica",
        "pregunta": "Lea: 'La ciencia no es un sistema de enunciados seguros y bien asentados... Nuestra ciencia no es conocimiento (episteme): nunca puede pretender que ha alcanzado la verdad. Es un sistema de conjeturas anticipadas que sometemos a las pruebas más rigurosas. No buscamos verificar, sino falsar'. (Karl Popper). ¿Qué criterio de demarcación científica propone el autor?",
        "opciones": ["A. La verificabilidad empírica.", "B. El falsacionismo.", "C. El método inductivo.", "D. El dogmatismo racional."],
        "respuesta": "B. El falsacionismo.",
        "explicacion_ia": "Popper sostiene que una teoría es científica solo si es susceptible de ser probada como falsa (refutada). La ciencia avanza descartando errores, no confirmando verdades absolutas."
    },
    {
        "materia": "Sociales y Ciudadanas",
        "pregunta": "El Banco de la República decide aumentar las tasas de interés de intervención. ¿Cuál es el efecto macroeconómico inmediato que busca esta medida?",
        "opciones": ["A. Aumentar el consumo de los hogares.", "B. Reducir la inflación encareciendo el crédito y desincentivando el gasto.", "C. Aumentar la tasa de cambio del dólar.", "D. Generar más empleo a corto plazo."],
        "respuesta": "B. Reducir la inflación encareciendo el crédito y desincentivando el gasto.",
        "explicacion_ia": "Es una política monetaria contractiva. Al subir tasas, pedir prestado es caro, la gente gasta menos, la demanda baja y, por ende, los precios (inflación) deberían bajar."
    },
    {
        "materia": "Ciencias Naturales",
        "pregunta": "Si un buzo asciende demasiado rápido desde el fondo del mar, puede sufrir el 'mal de descompresión' (burbujas de nitrógeno en la sangre). ¿Qué ley de los gases explica este fenómeno?",
        "opciones": ["A. Ley de Boyle (P1V1 = P2V2).", "B. Ley de Henry (Solubilidad de gases).", "C. Ley de Charles (V1/T1 = V2/T2).", "D. Principio de Arquímedes."],
        "respuesta": "B. Ley de Henry (Solubilidad de gases).",
        "explicacion_ia": "La Ley de Henry establece que la cantidad de gas disuelto en un líquido es proporcional a la presión. Al subir rápido, la presión baja bruscamente y el gas disuelto se vuelve burbuja (como al abrir una gaseosa)."
    },
    {
        "materia": "Matemáticas",
        "pregunta": "La vida media de un isótopo radiactivo es de 10 años. Si inicialmente hay 100 gramos, ¿cuántos gramos quedarán después de 40 años?",
        "opciones": ["A. 0 gramos.", "B. 6.25 gramos.", "C. 12.5 gramos.", "D. 25 gramos."],
        "respuesta": "B. 6.25 gramos.",
        "explicacion_ia": "En cada vida media, la cantidad se reduce a la mitad. 10 años: 50g. 20 años: 25g. 30 años: 12.5g. 40 años: 6.25g."
    },
    {
        "materia": "Sociales y Ciudadanas",
        "pregunta": "La 'Objeción de Conciencia' permite a un ciudadano incumplir una obligación legal si esta va en contra de sus convicciones profundas. En Colombia, ¿en cuál caso NO se ha reconocido este derecho?",
        "opciones": ["A. Prestar servicio militar obligatorio.", "B. Practicar un aborto (para médicos).", "C. Pagar impuestos que financian la guerra.", "D. Practicar la eutanasia (para médicos)."],
        "respuesta": "C. Pagar impuestos que financian la guerra.",
        "explicacion_ia": "La Corte Constitucional ha negado la objeción de conciencia tributaria. El deber de contribuir al financiamiento del Estado prevalece, ya que es imposible segregar el destino de cada peso pagado."
    },
    {
        "materia": "Ciencias Naturales",
        "pregunta": "En genética, si cruzamos dos plantas heterocigotas para dos caracteres diferentes (AaBb x AaBb), ¿cuál es la probabilidad fenotípica de obtener una planta con ambos rasgos recesivos (aabb)?",
        "opciones": ["A. 1/4", "B. 9/16", "C. 1/16", "D. 3/16"],
        "respuesta": "C. 1/16",
        "explicacion_ia": "Según la Tercera Ley de Mendel (distribución independiente), la proporción es 9:3:3:1. Solo 1 de cada 16 combinaciones tendrá ambos rasgos recesivos."
    },
    {
        "materia": "Lectura Crítica",
        "pregunta": "En la frase 'Es un cadáver viviente', la figura retórica empleada es:",
        "opciones": ["A. Sinestesia.", "B. Oxímoron.", "C. Metonimia.", "D. Elipsis."],
        "respuesta": "B. Oxímoron.",
        "explicacion_ia": "El oxímoron consiste en usar dos conceptos de significado opuesto en una sola expresión, generando un nuevo sentido (alguien muerto en vida o sin voluntad)."
    },
    {
        "materia": "Matemáticas",
        "pregunta": "Una función f(x) es continua en el intervalo [a, b] y f(a) < 0 y f(b) > 0. Según el Teorema de Bolzano (Valor Intermedio), esto garantiza que:",
        "opciones": ["A. La función es creciente.", "B. Existe al menos un punto c en (a, b) tal que f(c) = 0.", "C. La función es positiva en todo el intervalo.", "D. La función no tiene raíces."],
        "respuesta": "B. Existe al menos un punto c en (a, b) tal que f(c) = 0.",
        "explicacion_ia": "Si una línea continua pasa de negativo a positivo (o viceversa), obligatoriamente tiene que cortar el eje X en algún punto (la raíz)."
    },
    {
        "materia": "Sociales y Ciudadanas",
        "pregunta": "¿Qué teoría de las Relaciones Internacionales sostiene que los Estados actúan principalmente por interés nacional y poder, en un sistema internacional anárquico?",
        "opciones": ["A. Idealismo.", "B. Constructivismo.", "C. Realismo.", "D. Liberalismo."],
        "respuesta": "C. Realismo.",
        "explicacion_ia": "El Realismo político (Maquiavelo, Hobbes, Morgenthau) ve las relaciones internacionales como una lucha de poder donde la seguridad y el interés propio son lo único que importa."
    },
    {
        "materia": "Ciencias Naturales",
        "pregunta": "Al mezclar 50 ml de HCl 1M con 50 ml de NaOH 1M, la temperatura de la solución aumenta. Esto indica que la reacción de neutralización es:",
        "opciones": ["A. Endotérmica (absorbe calor).", "B. Exotérmica (libera calor).", "C. Isotérmica.", "D. Reversible."],
        "respuesta": "B. Exotérmica (libera calor).",
        "explicacion_ia": "Las reacciones ácido-base fuertes liberan energía en forma de calor al formarse agua y sal."
    },
    {
        "materia": "Lectura Crítica",
        "pregunta": "Si un autor dice: 'La democracia es la tiranía de la mayoría', está expresando una preocupación sobre:",
        "opciones": ["A. La eficiencia del voto electrónico.", "B. El riesgo de que la mayoría vulnere los derechos de las minorías mediante procesos democráticos.", "C. La necesidad de volver a la monarquía.", "D. La corrupción de los senadores."],
        "respuesta": "B. El riesgo de que la mayoría vulnere los derechos de las minorías mediante procesos democráticos.",
        "explicacion_ia": "Es una crítica clásica (Tocqueville/Mill) que advierte que el voto mayoritario no garantiza justicia si aplasta a los grupos minoritarios."
    },
    {
        "materia": "Matemáticas",
        "pregunta": "En un triángulo rectángulo, sen(α) = 3/5. ¿Cuánto vale tan(α)?",
        "opciones": ["A. 4/5", "B. 3/4", "C. 5/3", "D. 5/4"],
        "respuesta": "B. 3/4",
        "explicacion_ia": "Si sen=opuesto/hipotenusa=3/5, el cateto adyacente es 4 (triángulo notable 3-4-5). Tan=opuesto/adyacente=3/4."
    },
    {
        "materia": "Ciencias Naturales",
        "pregunta": "La resistencia a los pesticidas en una población de insectos es un ejemplo de:",
        "opciones": ["A. Mutación dirigida por el pesticida.", "B. Selección natural direccional.", "C. Deriva genética.", "D. Selección disruptiva."],
        "respuesta": "B. Selección natural direccional.",
        "explicacion_ia": "El pesticida elimina a los sensibles, favoreciendo la supervivencia y reproducción de los resistentes (un extremo del fenotipo), desplazando la población hacia la resistencia."
    },
    {
        "materia": "Sociales y Ciudadanas",
        "pregunta": "El 'Control de Conventionalidad' obliga a los jueces colombianos a:",
        "opciones": ["A. Seguir solo las leyes nacionales.", "B. Interpretar las normas nacionales en coherencia con la Convención Americana de Derechos Humanos (Pacto de San José).", "C. Consultar al Presidente antes de fallar.", "D. Aplicar leyes de Estados Unidos."],
        "respuesta": "B. Interpretar las normas nacionales en coherencia con la Convención Americana de Derechos Humanos (Pacto de San José).",
        "explicacion_ia": "Implica que, si una ley interna contradice el tratado internacional de DD.HH., el juez debe aplicar el tratado (Bloque de Constitucionalidad)."
    },
    {
        "materia": "Lectura Crítica",
        "pregunta": "Lea: 'Fumar es perjudicial para la salud'. 'Pedro fuma'. Conclusión: 'Pedro dañará su salud'. Este es un razonamiento:",
        "opciones": ["A. Inductivo.", "B. Deductivo.", "C. Abductivo.", "D. Analógico."],
        "respuesta": "B. Deductivo.",
        "explicacion_ia": "Va de lo general (fumar daña) a lo particular (Pedro fuma -> Pedro se daña). La conclusión se deriva necesariamente de las premisas."
    },
    {
        "materia": "Matemáticas",
        "pregunta": "El límite de (sin(x) / x) cuando x tiende a 0 es:",
        "opciones": ["A. 0", "B. 1", "C. Infinito.", "D. Indeterminado."],
        "respuesta": "B. 1",
        "explicacion_ia": "Es un límite notable fundamental en cálculo, demostrable geométricamente o por regla de L'Hôpital."
    },
    {
        "materia": "Ciencias Naturales",
        "pregunta": "Si un objeto se mueve con velocidad constante en el espacio, la fuerza neta que actúa sobre él es:",
        "opciones": ["A. Constante y positiva.", "B. Cero.", "C. Igual a la gravedad.", "D. Creciente."],
        "respuesta": "B. Cero.",
        "explicacion_ia": "Primera Ley de Newton (Inercia). Si no hay aceleración (velocidad constante), la suma de fuerzas es cero."
    },
    {
        "materia": "Sociales y Ciudadanas",
        "pregunta": "¿Qué implica el principio de 'Pesos y Contrapesos' (Check and Balances)?",
        "opciones": ["A. Que el Presidente pesa más que el Congreso.", "B. Que ninguna rama del poder es absoluta, pues las otras tienen mecanismos para controlarla y limitarla.", "C. Que la economía debe estar equilibrada.", "D. Que los votos valen diferente."],
        "respuesta": "B. Que ninguna rama del poder es absoluta, pues las otras tienen mecanismos para controlarla y limitarla.",
        "explicacion_ia": "Ej: El Congreso hace leyes, pero la Corte puede tumbarlas. El Presidente gobierna, pero el Congreso lo controla políticamente."
    },
    {
        "materia": "Lectura Crítica",
        "pregunta": "La 'intertextualidad' ocurre cuando:",
        "opciones": ["A. Un texto es muy largo.", "B. Un texto cita, alude o dialoga con otro texto anterior.", "C. Un texto está en internet.", "D. Un texto no tiene autor."],
        "respuesta": "B. Un texto cita, alude o dialoga con otro texto anterior.",
        "explicacion_ia": "Es la relación que un texto mantiene con otros textos (ej: Los Simpson parodiando a El Padrino)."
    },
    {
        "materia": "Matemáticas",
        "pregunta": "Dos vectores A y B son perpendiculares (ortogonales) si:",
        "opciones": ["A. Su producto punto (escalar) es 1.", "B. Su producto punto (escalar) es 0.", "C. Su producto cruz es 0.", "D. Son paralelos."],
        "respuesta": "B. Su producto punto (escalar) es 0.",
        "explicacion_ia": "El producto escalar es |A||B|cos(θ). Si son perpendiculares, θ=90°, cos(90°)=0, por tanto el producto es 0."
    },
    {
        "materia": "Ciencias Naturales",
        "pregunta": "El reactivo limitante en una reacción química es aquel que:",
        "opciones": ["A. Tiene menor masa en gramos.", "B. Se consume primero y detiene la reacción.", "C. Sobra al final.", "D. Tiene menor coeficiente estequiométrico."],
        "respuesta": "B. Se consume primero y detiene la reacción.",
        "explicacion_ia": "Determina la cantidad máxima de producto que se puede formar. Una vez se acaba, la reacción para, aunque sobre del otro reactivo."
    },
    {
        "materia": "Sociales y Ciudadanas",
        "pregunta": "La 'Curva de Phillips' en economía sugiere una relación inversa a corto plazo entre:",
        "opciones": ["A. Impuestos y ahorro.", "B. Desempleo e inflación.", "C. Oferta y demanda.", "D. Importaciones y exportaciones."],
        "respuesta": "B. Desempleo e inflación.",
        "explicacion_ia": "Teoría que dice que para reducir el desempleo, a veces se debe tolerar un poco más de inflación (y viceversa)."
    },
    {
        "materia": "Lectura Crítica",
        "pregunta": "En un ensayo filosófico, ¿qué es una 'falacia de hombre de paja'?",
        "opciones": ["A. Un argumento agrícola.", "B. Distorsionar o exagerar el argumento del oponente para atacarlo más fácilmente.", "C. Atacar al hombre en lugar de la idea.", "D. Usar paja para escribir."],
        "respuesta": "B. Distorsionar o exagerar el argumento del oponente para atacarlo más fácilmente.",
        "explicacion_ia": "En lugar de refutar el argumento real, se crea una versión caricaturizada (de paja) y se derriba esa."
    },
    {
        "materia": "Matemáticas",
        "pregunta": "Si lanzamos dos dados, ¿cuál es la probabilidad de sacar un 'doble' (dos números iguales)?",
        "opciones": ["A. 1/6", "B. 1/36", "C. 1/12", "D. 1/2"],
        "respuesta": "A. 1/6",
        "explicacion_ia": "Hay 6 casos favorables: (1,1), (2,2), (3,3), (4,4), (5,5), (6,6). Total casos: 36. Probabilidad: 6/36 = 1/6."
    },
    {
        "materia": "Ciencias Naturales",
        "pregunta": "El dogma central de la biología molecular describe el flujo de información genética como:",
        "opciones": ["A. Proteína -> ARN -> ADN.", "B. ADN -> ARN -> Proteína.", "C. ARN -> ADN -> Proteína.", "D. ADN -> Proteína -> ARN."],
        "respuesta": "B. ADN -> ARN -> Proteína.",
        "explicacion_ia": "Replicación (ADN), Transcripción (a ARN) y Traducción (a Proteína). (Con excepciones como los retrovirus)."
    },
    {
        "materia": "Sociales y Ciudadanas",
        "pregunta": "¿Qué diferencia al Derecho Internacional Humanitario (DIH) de los Derechos Humanos (DDHH)?",
        "opciones": ["A. Son lo mismo.", "B. El DIH aplica solo en conflicto armado; los DDHH aplican siempre.", "C. El DIH protege a los militares y los DDHH a los civiles.", "D. El DIH es nacional y los DDHH internacionales."],
        "respuesta": "B. El DIH aplica solo en conflicto armado; los DDHH aplican siempre.",
        "explicacion_ia": "El DIH es lex specialis para la guerra (Convenios de Ginebra). Los DDHH son universales y permanentes."
    },
    {
        "materia": "Lectura Crítica",
        "pregunta": "El prefijo 'epi-' en 'epigenética' o 'epidermis' significa:",
        "opciones": ["A. Debajo de.", "B. Sobre o por encima de.", "C. Dentro de.", "D. Contrario a."],
        "respuesta": "B. Sobre o por encima de.",
        "explicacion_ia": "Epigenética es lo que está 'sobre' los genes; epidermis es la capa 'sobre' la dermis."
    },
    {
        "materia": "Matemáticas",
        "pregunta": "Una población de bacterias se duplica cada hora. Esta relación es una función:",
        "opciones": ["A. Lineal.", "B. Logarítmica.", "C. Exponencial.", "D. Cuadrática."],
        "respuesta": "C. Exponencial.",
        "explicacion_ia": "El crecimiento es proporcional al tamaño actual (y = a * 2^x)."
    },
    {
        "materia": "Ciencias Naturales",
        "pregunta": "Si colocas un glóbulo rojo en agua destilada (hipotónica), ¿qué le sucede?",
        "opciones": ["A. Se arruga (crenación).", "B. Se hincha y puede explotar (hemólisis/lisis).", "C. No le pasa nada.", "D. Se divide."],
        "respuesta": "B. Se hincha y puede explotar (hemólisis/lisis).",
        "explicacion_ia": "Por ósmosis, el agua entra a la célula (donde hay más solutos) para equilibrar, hinchándola hasta reventar."
    },
    {
        "materia": "Sociales y Ciudadanas",
        "pregunta": "El 'Estado de Bienestar' (Keynesianismo) promueve:",
        "opciones": ["A. La eliminación del Estado.", "B. La intervención estatal en la economía para garantizar servicios básicos y pleno empleo.", "C. El libre mercado absoluto sin regulación.", "D. La dictadura del proletariado."],
        "respuesta": "B. La intervención estatal en la economía para garantizar servicios básicos y pleno empleo.",
        "explicacion_ia": "Busca corregir fallos del mercado y asegurar equidad social mediante gasto público."
    },
    {
        "materia": "Lectura Crítica",
        "pregunta": "Si un texto argumentativo omite deliberadamente información clave para manipular al lector, incurre en:",
        "opciones": ["A. Sesgo de confirmación o manipulación.", "B. Coherencia.", "C. Síntesis.", "D. Objetividad."],
        "respuesta": "A. Sesgo de confirmación o manipulación.",
        "explicacion_ia": "Es una falta ética argumentativa: presentar solo lo que conviene a la tesis."
    },
    {
        "materia": "Matemáticas",
        "pregunta": "¿Qué número sumado con su recíproco da como resultado 2?",
        "opciones": ["A. 2", "B. 0.5", "C. 1", "D. -1"],
        "respuesta": "C. 1",
        "explicacion_ia": "1 + (1/1) = 1 + 1 = 2. Es el único número real con esa propiedad."
    },
    {
        "materia": "Ciencias Naturales",
        "pregunta": "La entropía de un sistema aislado siempre tiende a:",
        "opciones": ["A. Disminuir.", "B. Mantenerse constante.", "C. Aumentar.", "D. Volverse cero."],
        "respuesta": "C. Aumentar.",
        "explicacion_ia": "Segunda Ley de la Termodinámica: el desorden del universo tiende al máximo."
    },
    {
        "materia": "Sociales y Ciudadanas",
        "pregunta": "¿Qué es el 'Habeas Corpus'?",
        "opciones": ["A. Derecho a tener cuerpo.", "B. Acción judicial para recuperar la libertad si la captura fue ilegal.", "C. Derecho a la salud.", "D. Derecho a no ser torturado."],
        "respuesta": "B. Acción judicial para recuperar la libertad si la captura fue ilegal.",
        "explicacion_ia": "Garantía fundamental contra detenciones arbitrarias. Debe resolverse en 36 horas."
    },
    {
        "materia": "Lectura Crítica",
        "pregunta": "El 'nihilismo' (Nietzsche) se asocia con:",
        "opciones": ["A. La fe absoluta en Dios.", "B. La negación de todo sentido, valor o propósito superior en la vida.", "C. El comunismo.", "D. La arquitectura."],
        "respuesta": "B. La negación de todo sentido, valor o propósito superior en la vida.",
        "explicacion_ia": "Del latín 'nihil' (nada). La devaluación de los valores supremos ('Dios ha muerto')."
    },
    {
        "materia": "Matemáticas",
        "pregunta": "La derivada de una función en un punto representa geométricamente:",
        "opciones": ["A. El área bajo la curva.", "B. La pendiente de la recta tangente en ese punto.", "C. El valor de y.", "D. La intersección con el eje x."],
        "respuesta": "B. La pendiente de la recta tangente en ese punto.",
        "explicacion_ia": "Concepto fundamental del cálculo diferencial: la razón de cambio instantánea."
    },
    {
        "materia": "Ciencias Naturales",
        "pregunta": "¿Qué metal es líquido a temperatura ambiente?",
        "opciones": ["A. Hierro.", "B. Oro.", "C. Mercurio.", "D. Plomo."],
        "respuesta": "C. Mercurio.",
        "explicacion_ia": "Es una excepción en la tabla periódica (Hg)."
    },
    {
        "materia": "Sociales y Ciudadanas",
        "pregunta": "La 'Guerra Fría' terminó simbólicamente con:",
        "opciones": ["A. La caída del Muro de Berlín (1989).", "B. La llegada del hombre a la Luna.", "C. La muerte de Hitler.", "D. La guerra de Vietnam."],
        "respuesta": "A. La caída del Muro de Berlín (1989).",
        "explicacion_ia": "Representó el colapso del bloque soviético y el fin de la división bipolar del mundo."
    },
    {
        "materia": "Lectura Crítica",
        "pregunta": "¿Qué es una 'distopía'?",
        "opciones": ["A. Una utopía perfecta.", "B. Una sociedad imaginaria indeseable, opresiva o aterradora.", "C. Un tipo de poema.", "D. Un error visual."],
        "respuesta": "B. Una sociedad imaginaria indeseable, opresiva o aterradora.",
        "explicacion_ia": "Ej: 1984, Un Mundo Feliz. Lo contrario a utopía."
    },
    {
        "materia": "Matemáticas",
        "pregunta": "En un juicio, la probabilidad de que un acusado sea culpable es del 60%. La probabilidad de que un testigo mienta es del 20%. Si el testigo afirma que el acusado es culpable, ¿estamos ante un caso de probabilidad condicional? Para calcular la probabilidad real de culpa dado el testimonio, deberíamos usar:",
        "opciones": ["A. La Ley de los Grandes Números.", "B. El Teorema de Pitágoras.", "C. El Teorema de Bayes.", "D. La desviación estándar."],
        "respuesta": "C. El Teorema de Bayes.",
        "explicacion_ia": "El Teorema de Bayes se utiliza para calcular la probabilidad de un evento (culpabilidad) basándose en una condición previa o nueva información (el testimonio), ajustando la probabilidad inicial."
    },
    {
        "materia": "Lectura Crítica",
        "pregunta": "Lea: 'Decir «te prometo que iré» no es describir un hecho futuro, sino realizar el acto mismo de prometer. Al pronunciar la frase, se crea el compromiso'. Según la teoría de los actos de habla (Austin/Searle), este tipo de enunciado es:",
        "opciones": ["A. Constatativo (describe el mundo).", "B. Performativo o realizativo (hace cosas con palabras).", "C. Metafórico.", "D. Falso."],
        "respuesta": "B. Performativo o realizativo (hace cosas con palabras).",
        "explicacion_ia": "Los enunciados performativos no describen la realidad (no son verdaderos o falsos), sino que *transforman* la realidad social al ser pronunciados (ej: 'los declaro marido y mujer', 'te prometo')."
    },
    {
        "materia": "Sociales y Ciudadanas",
        "pregunta": "Una fábrica emite humo que enferma a los vecinos, pero la fábrica no paga por esos daños médicos, por lo que puede vender sus productos más baratos de lo que realmente cuestan a la sociedad. En economía, este fallo del mercado se conoce como:",
        "opciones": ["A. Monopolio natural.", "B. Externalidad negativa.", "C. Competencia perfecta.", "D. Plusvalía."],
        "respuesta": "B. Externalidad negativa.",
        "explicacion_ia": "Una externalidad negativa ocurre cuando la actividad de producción o consumo afecta a terceros que no participan en ella, sin que el causante pague por ese daño (el costo social es mayor al privado)."
    },
    {
        "materia": "Ciencias Naturales",
        "pregunta": "El Principio de Le Chatelier establece que si se altera un sistema químico en equilibrio, el sistema reaccionará para contrarrestar la perturbación. En la reacción: N2(g) + 3H2(g) ↔ 2NH3(g), si aumentamos drásticamente la presión del recipiente, el sistema buscará:",
        "opciones": ["A. Desplazarse hacia donde hay más moles de gas (izquierda).", "B. Desplazarse hacia donde hay menos moles de gas (derecha) para reducir la presión.", "C. No hacer nada.", "D. Aumentar la temperatura."],
        "respuesta": "B. Desplazarse hacia donde hay menos moles de gas (derecha) para reducir la presión.",
        "explicacion_ia": "A la izquierda hay 4 moles de gas (1+3) y a la derecha solo 2. Si sube la presión, el sistema trata de bajarla yéndose al lado que ocupa menos volumen (menos moles), es decir, hacia el amoníaco (derecha)."
    },
    {
        "materia": "Matemáticas",
        "pregunta": "Una población de bacterias crece siguiendo la función f(t) = 100 * e^(0.5t). ¿Qué representa el número 100 en esta función exponencial?",
        "opciones": ["A. La tasa de crecimiento.", "B. El tiempo transcurrido.", "C. La población inicial (cuando t=0).", "D. El número de Euler."],
        "respuesta": "C. La población inicial (cuando t=0).",
        "explicacion_ia": "Si evaluamos la función en el tiempo t=0, tenemos f(0) = 100 * e^0. Como e^0 = 1, entonces f(0) = 100. Es el valor de arranque."
    },
    {
        "materia": "Sociales y Ciudadanas",
        "pregunta": "La Corte Constitucional ha desarrollado el concepto de 'Estado de Cosas Inconstitucional' (ECI). ¿Cuándo declara la Corte un ECI?",
        "opciones": ["A. Cuando una sola persona es vulnerada.", "B. Cuando existe una violación masiva y generalizada de derechos fundamentales que afecta a una multitud de personas, debida a fallas estructurales del Estado (ej: hacinamiento carcelario).", "C. Cuando el Presidente renuncia.", "D. Cuando se cambia la Constitución."],
        "respuesta": "B. Cuando existe una violación masiva y generalizada de derechos fundamentales que afecta a una multitud de personas, debida a fallas estructurales del Estado (ej: hacinamiento carcelario).",
        "explicacion_ia": "Es una figura jurídica extrema para ordenar a múltiples entidades del Estado que arreglen un problema estructural grave que satura el sistema de tutelas."
    },
    {
        "materia": "Ciencias Naturales",
        "pregunta": "La biomagnificación es un fenómeno ecológico preocupante. Si vertimos mercurio al mar, ¿quién tendrá la mayor concentración de tóxico en su cuerpo?",
        "opciones": ["A. El fitoplancton (productor).", "B. El pez pequeño (consumidor primario).", "C. El tiburón o el humano (depredador tope).", "D. El agua misma."],
        "respuesta": "C. El tiburón o el humano (depredador tope).",
        "explicacion_ia": "El tóxico no se elimina, se acumula. El pez chico come miles de plancton, y el tiburón come miles de peces chicos. Así, el depredador final acumula todo el mercurio de la cadena hacia abajo."
    },
    {
        "materia": "Lectura Crítica",
        "pregunta": "Lea: 'Si permitimos el matrimonio igualitario, pronto permitiremos el matrimonio con animales y luego con objetos'. Este argumento incurre en la falacia de:",
        "opciones": ["A. Ad populum.", "B. Pendiente resbaladiza (Slippery Slope).", "C. Hombre de paja.", "D. Falso dilema."],
        "respuesta": "B. Pendiente resbaladiza (Slippery Slope).",
        "explicacion_ia": "Consiste en sugerir, sin pruebas, que un evento A llevará inevitablemente a una cadena de eventos catastróficos extremos (B, C, D...) para generar miedo."
    },
    {
        "materia": "Matemáticas",
        "pregunta": "Dos corredores parten del mismo punto. El corredor A va hacia el norte a 6 km/h y el corredor B va hacia el este a 8 km/h. Al cabo de 2 horas, ¿qué distancia los separa en línea recta?",
        "opciones": ["A. 14 km", "B. 28 km", "C. 20 km", "D. 10 km"],
        "respuesta": "C. 20 km",
        "explicacion_ia": "Forman un triángulo rectángulo. En 2 horas, A recorrió 12 km (cateto 1) y B recorrió 16 km (cateto 2). Hipotenusa² = 12² + 16² = 144 + 256 = 400. Raíz de 400 = 20 km."
    },
    {
        "materia": "Sociales y Ciudadanas",
        "pregunta": "El 'Consenso de Washington' (década de 1990) fue un paquete de medidas económicas recomendadas para América Latina que incluía:",
        "opciones": ["A. Aumentar el tamaño del Estado y nacionalizar empresas.", "B. Privatización de empresas estatales, reducción del gasto público y apertura comercial (neoliberalismo).", "C. Implementar el comunismo.", "D. Cerrar las fronteras."],
        "respuesta": "B. Privatización de empresas estatales, reducción del gasto público y apertura comercial (neoliberalismo).",
        "explicacion_ia": "Fue la receta económica neoliberal impulsada por el FMI y el Banco Mundial para tratar de estabilizar las economías latinoamericanas, aunque con altos costos sociales."
    },
    {
        "materia": "Ciencias Naturales",
        "pregunta": "Si un astronauta en el espacio exterior empuja una llave inglesa lejos de él, la llave se moverá:",
        "opciones": ["A. Unos metros y se detendrá por falta de motor.", "B. En línea recta y a velocidad constante indefinidamente (o hasta chocar con algo).", "C. En círculos.", "D. Acelerando cada vez más."],
        "respuesta": "B. En línea recta y a velocidad constante indefinidamente (o hasta chocar con algo).",
        "explicacion_ia": "Por la inercia (1ª Ley de Newton) y la falta de fricción en el vacío, no hay fuerza que la detenga. Mantendrá su movimiento perpetuamente."
    },
    {
        "materia": "Lectura Crítica",
        "pregunta": "El 'Boom Latinoamericano' (años 60-70) se caracterizó literariamente por:",
        "opciones": ["A. Copiar el realismo europeo del siglo XIX.", "B. El uso del Realismo Mágico, la experimentación con el tiempo narrativo y la denuncia social.", "C. Escribir solo poesía romántica.", "D. Rechazar la política."],
        "respuesta": "B. El uso del Realismo Mágico, la experimentación con el tiempo narrativo y la denuncia social.",
        "explicacion_ia": "Autores como García Márquez, Cortázar y Vargas Llosa renovaron la narrativa mundial mezclando lo fantástico con lo cotidiano y estructuras no lineales."
    },
    {
        "materia": "Matemáticas",
        "pregunta": "Si la desviación estándar de un grupo de datos es muy alta, esto indica que:",
        "opciones": ["A. Los datos son erróneos.", "B. Los datos están muy dispersos o alejados del promedio.", "C. Todos los datos son iguales.", "D. El promedio es cero."],
        "respuesta": "B. Los datos están muy dispersos o alejados del promedio.",
        "explicacion_ia": "La desviación estándar mide la dispersión. Si es alta, los datos son heterogéneos; si es baja (cercana a 0), los datos son muy parecidos entre sí."
    },
    {
        "materia": "Sociales y Ciudadanas",
        "pregunta": "En Colombia, ¿qué mecanismo permite reformar la Constitución SIN convocar a una Asamblea Constituyente ni a un Referendo?",
        "opciones": ["A. Un decreto del Presidente.", "B. Un Acto Legislativo aprobado por el Congreso en 8 debates.", "C. Una tutela.", "D. Una huelga nacional."],
        "respuesta": "B. Un Acto Legislativo aprobado por el Congreso en 8 debates.",
        "explicacion_ia": "El Congreso tiene función constituyente derivada. Puede cambiar la Constitución mediante Actos Legislativos, pero el proceso es más exigente que para una ley ordinaria (dos vueltas, 8 debates)."
    },
    {
        "materia": "Ciencias Naturales",
        "pregunta": "La paradoja de los gemelos (Relatividad Especial de Einstein) sugiere que si un gemelo viaja al espacio a la velocidad de la luz y vuelve, encontrará que su hermano en la Tierra:",
        "opciones": ["A. Ha envejecido más que él.", "B. Ha rejuvenecido.", "C. Tiene la misma edad.", "D. Ha desaparecido."],
        "respuesta": "A. Ha envejecido más que él.",
        "explicacion_ia": "A velocidades cercanas a la luz, el tiempo se dilata (pasa más lento) para el viajero. Para el que se queda en la Tierra, el tiempo pasa 'normal' (más rápido relativo al viajero), por lo que envejece más."
    },
    {
        "materia": "Lectura Crítica",
        "pregunta": "Identifique la premisa implícita: 'No me gustó la película, es de cine arte europeo'.",
        "opciones": ["A. El cine europeo es muy costoso.", "B. El cine arte europeo suele ser aburrido, lento o difícil de entender para el hablante.", "C. El hablante es un experto crítico de cine.", "D. La película no tenía subtítulos."],
        "respuesta": "B. El cine arte europeo suele ser aburrido, lento o difícil de entender para el hablante.",
        "explicacion_ia": "El argumento asume una generalización negativa sobre el 'cine arte europeo' que justifica, por sí sola, que no le haya gustado."
    },
    {
        "materia": "Matemáticas",
        "pregunta": "En un triángulo, el Teorema del Coseno (c² = a² + b² - 2ab*cosC) es una generalización de Pitágoras. ¿Qué pasa si el ángulo C es de 90 grados?",
        "opciones": ["A. La fórmula no funciona.", "B. Se convierte en el Teorema de Pitágoras, porque cos(90°) es 0.", "C. Se convierte en a² + b² - 2ab.", "D. El triángulo deja de existir."],
        "respuesta": "B. Se convierte en el Teorema de Pitágoras, porque cos(90°) es 0.",
        "explicacion_ia": "Como el coseno de 90° es 0, todo el término '-2ab*cosC' desaparece, quedando solo c² = a² + b²."
    },
    {
        "materia": "Sociales y Ciudadanas",
        "pregunta": "La 'Desobediencia Civil' (como la de Gandhi o Martin Luther King) se distingue de la delincuencia común porque:",
        "opciones": ["A. Es violenta.", "B. Es secreta y busca beneficio personal.", "C. Es pública, pacífica, política y busca cambiar una ley considerada injusta aceptando el castigo.", "D. Es financiada por el Estado."],
        "respuesta": "C. Es pública, pacífica, política y busca cambiar una ley considerada injusta aceptando el castigo.",
        "explicacion_ia": "Su fin es moral y político (mejorar la sociedad), no criminal. Se acepta la cárcel para evidenciar la injusticia de la ley."
    },
    {
        "materia": "Ciencias Naturales",
        "pregunta": "¿Qué papel juega el 'Grupo Control' en un experimento científico?",
        "opciones": ["A. Controlar a los científicos.", "B. Servir de base de comparación al no recibir el tratamiento experimental, para asegurar que los resultados se deben a la variable probada.", "C. Recibir la dosis más alta del medicamento.", "D. Asegurar que nadie se equivoque."],
        "respuesta": "B. Servir de base de comparación al no recibir el tratamiento experimental, para asegurar que los resultados se deben a la variable probada.",
        "explicacion_ia": "Sin grupo control (ej: placebo), no se puede saber si la mejoría se debió al medicamento o al azar/efecto psicológico."
    },
    {
        "materia": "Lectura Crítica",
        "pregunta": "En filosofía, la 'navaja de Ockham' sugiere que:",
        "opciones": ["A. Se deben cortar los argumentos malos.", "B. En igualdad de condiciones, la explicación más sencilla suele ser la correcta (no multiplicar los entes sin necesidad).", "C. La filosofía es peligrosa.", "D. Todo debe ser complejo."],
        "respuesta": "B. En igualdad de condiciones, la explicación más sencilla suele ser la correcta (no multiplicar los entes sin necesidad).",
        "explicacion_ia": "Es un principio metodológico de parsimonia: ante dos teorías que explican lo mismo, elige la que requiere menos suposiciones."
    },
    {
        "materia": "Matemáticas",
        "pregunta": "Si f(x) = x². ¿Cómo cambia la gráfica si hacemos f(x - 2)?",
        "opciones": ["A. Se desplaza 2 unidades hacia arriba.", "B. Se desplaza 2 unidades hacia la izquierda.", "C. Se desplaza 2 unidades hacia la derecha.", "D. Se desplaza 2 unidades hacia abajo."],
        "respuesta": "C. Se desplaza 2 unidades hacia la derecha.",
        "explicacion_ia": "En transformaciones de funciones, f(x - c) desplaza la gráfica horizontalmente a la derecha 'c' unidades. (Es contraintuitivo, el menos mueve a la derecha)."
    },
    {
        "materia": "Sociales y Ciudadanas",
        "pregunta": "El concepto de 'Gentrificación' urbana implica:",
        "opciones": ["A. Mejorar los parques.", "B. El desplazamiento de población pobre de un barrio céntrico debido a la llegada de población rica que encarece el costo de vida.", "C. La llegada de gente amable.", "D. La construcción de hospitales."],
        "respuesta": "B. El desplazamiento de población pobre de un barrio céntrico debido a la llegada de población rica que encarece el costo de vida.",
        "explicacion_ia": "Es un fenómeno de renovación urbana que, aunque embellece la zona, segrega y expulsa a los habitantes tradicionales (elitización)."
    },
    {
        "materia": "Matemáticas",
        "pregunta": "Se lanzan dos dados honestos. ¿Cuál es la probabilidad de que salga un 6 en AL MENOS uno de los dados?",
        "opciones": ["A. 1/3", "B. 11/36", "C. 1/6", "D. 7/36"],
        "respuesta": "B. 11/36",
        "explicacion_ia": "Es más fácil calcular la probabilidad de que NO salga ningún 6 y restársela a 1. P(no 6) = 5/6. P(no 6 y no 6) = 5/6 * 5/6 = 25/36. Por tanto, P(al menos un 6) = 1 - 25/36 = 11/36."
    },
    {
        "materia": "Lectura Crítica",
        "pregunta": "Lea: 'El mapa no es el territorio' (Alfred Korzybski). Esta frase célebre de la semántica general advierte sobre:",
        "opciones": ["A. Los errores de impresión en la cartografía.", "B. Confundir la representación simbólica de la realidad (palabras, modelos) con la realidad misma.", "C. Que los mapas siempre están desactualizados.", "D. La dificultad de viajar sin GPS."],
        "respuesta": "B. Confundir la representación simbólica de la realidad (palabras, modelos) con la realidad misma.",
        "explicacion_ia": "Nos recuerda que el lenguaje y los conceptos son abstracciones limitadas que no capturan la totalidad de la experiencia real."
    },
    {
        "materia": "Sociales y Ciudadanas",
        "pregunta": "En economía, ¿cuál es la diferencia entre el PIB Nominal y el PIB Real?",
        "opciones": ["A. El Nominal es en dólares y el Real en pesos.", "B. El Nominal incluye la inflación (precios corrientes), mientras que el Real descuenta la inflación (precios constantes) para medir el crecimiento verdadero de la producción.", "C. El Real es solo para empresas privadas.", "D. No hay diferencia."],
        "respuesta": "B. El Nominal incluye la inflación (precios corrientes), mientras que el Real descuenta la inflación (precios constantes) para medir el crecimiento verdadero de la producción.",
        "explicacion_ia": "Si el PIB sube 5% pero la inflación fue del 5%, el país no produjo más bienes (PIB Real 0%), solo subieron los precios (PIB Nominal sube)."
    },
    {
        "materia": "Ciencias Naturales",
        "pregunta": "Si un haz de luz pasa del aire al agua con un ángulo inclinado, cambia de dirección (se dobla). Este fenómeno se llama refracción y ocurre porque:",
        "opciones": ["A. La luz gana energía en el agua.", "B. La luz cambia de velocidad al cambiar de medio (es más lenta en el agua).", "C. La luz rebota en la superficie.", "D. El agua es azul."],
        "respuesta": "B. La luz cambia de velocidad al cambiar de medio (es más lenta en el agua).",
        "explicacion_ia": "La velocidad de la luz no es constante en todos los medios; al frenarse en uno más denso, el frente de onda cambia de ángulo (Ley de Snell)."
    },
    {
        "materia": "Matemáticas",
        "pregunta": "El valor de una máquina se deprecia un 10% cada año. Si hoy vale $1.000.000, ¿cuánto valdrá después de 2 años?",
        "opciones": ["A. $800.000", "B. $810.000", "C. $900.000", "D. $820.000"],
        "respuesta": "B. $810.000",
        "explicacion_ia": "Año 1: Pierde 100.000, queda en 900.000. Año 2: Pierde el 10% de 900.000 (que es 90.000). 900.000 - 90.000 = 810.000."
    },
    {
        "materia": "Sociales y Ciudadanas",
        "pregunta": "¿Qué es la 'Pérdida de Investidura' (Muerte Política) para un congresista en Colombia?",
        "opciones": ["A. Que pierda las elecciones.", "B. Una sanción disciplinaria que le quita el cargo y le prohíbe volver a ser elegido popularmente de por vida.", "C. Una multa económica.", "D. Un regaño del partido."],
        "respuesta": "B. Una sanción disciplinaria que le quita el cargo y le prohíbe volver a ser elegido popularmente de por vida.",
        "explicacion_ia": "Es la sanción más grave por violar el régimen de inhabilidades, incompatibilidades o conflicto de intereses (ej: inasistencia, tráfico de influencias)."
    },
    {
        "materia": "Ciencias Naturales",
        "pregunta": "En la evolución, ¿qué significa que dos estructuras sean 'homólogas' (ej: el ala de un murciélago y la mano de un humano)?",
        "opciones": ["A. Que sirven para lo mismo (volar).", "B. Que tienen un origen evolutivo común (mismo ancestro), aunque su función actual sea diferente.", "C. Que son idénticas visualmente.", "D. Que evolucionaron por separado (convergencia)."],
        "respuesta": "B. Que tienen un origen evolutivo común (mismo ancestro), aunque su función actual sea diferente.",
        "explicacion_ia": "La homología prueba la descendencia común (evolución divergente). Lo opuesto es la analogía (ala de mosca y ala de pájaro), que es función similar pero origen distinto."
    },
    {
        "materia": "Lectura Crítica",
        "pregunta": "Identifique la falacia: 'No se puede probar que los extraterrestres NO existen; por lo tanto, deben existir'.",
        "opciones": ["A. Ad Hominem.", "B. Ad Ignorantiam (Apelación a la ignorancia).", "C. Círculo vicioso.", "D. Generalización indebida."],
        "respuesta": "B. Ad Ignorantiam (Apelación a la ignorancia).",
        "explicacion_ia": "Consiste en afirmar que algo es verdadero solo porque no se ha podido demostrar que es falso (la ausencia de prueba no es prueba de ausencia)."
    },
    {
        "materia": "Matemáticas",
        "pregunta": "Si f(x) = 2x + 1 y g(x) = x², ¿cuál es el valor de f(g(3))?",
        "opciones": ["A. 13", "B. 19", "C. 37", "D. 49"],
        "respuesta": "B. 19",
        "explicacion_ia": "Primero hallamos g(3) = 3² = 9. Luego evaluamos f(9) = 2(9) + 1 = 18 + 1 = 19. Es una función compuesta."
    },
    {
        "materia": "Sociales y Ciudadanas",
        "pregunta": "El principio de 'No discriminación' en el Derecho Internacional Humanitario implica que:",
        "opciones": ["A. Se debe tratar mejor a los amigos.", "B. Al atender heridos en combate, no se distingue entre 'amigos' y 'enemigos', sino solo por la urgencia médica.", "C. No se puede disparar.", "D. Los prisioneros deben ser liberados."],
        "respuesta": "B. Al atender heridos en combate, no se distingue entre 'amigos' y 'enemigos', sino solo por la urgencia médica.",
        "explicacion_ia": "Un médico en guerra debe atender al soldado herido del bando contrario con la misma ética que al propio. La humanidad prevalece sobre el bando."
    },
    {
        "materia": "Ciencias Naturales",
        "pregunta": "¿Por qué los astronautas 'flotan' en la Estación Espacial Internacional?",
        "opciones": ["A. Porque allí no hay gravedad (gravedad cero).", "B. Porque están en 'caída libre' constante alrededor de la Tierra.", "C. Porque el aire los empuja hacia arriba.", "D. Porque usan zapatos magnéticos."],
        "respuesta": "B. Porque están en 'caída libre' constante alrededor de la Tierra.",
        "explicacion_ia": "Error común: Sí hay gravedad (casi la misma que en la Tierra). Flotan porque la estación se mueve lateralmente tan rápido que, aunque cae hacia la Tierra, la curvatura del planeta se aleja a la misma tasa. Caen perpetuamente."
    },
    {
        "materia": "Lectura Crítica",
        "pregunta": "En semiótica, un 'Ícono' se diferencia de un 'Símbolo' porque:",
        "opciones": ["A. El ícono se parece físicamente a lo que representa (ej: foto), y el símbolo es una convención arbitraria (ej: la palabra 'perro' o una bandera).", "B. El ícono es religioso.", "C. El símbolo es visual y el ícono auditivo.", "D. Son lo mismo."],
        "respuesta": "A. El ícono se parece físicamente a lo que representa (ej: foto), y el símbolo es una convención arbitraria (ej: la palabra 'perro' o una bandera).",
        "explicacion_ia": "Clasificación de Peirce: Ícono (semejanza), Índice (causa-efecto, humo-fuego), Símbolo (acuerdo social)."
    },
    {
        "materia": "Matemáticas",
        "pregunta": "En un triángulo, un ángulo exterior es siempre igual a:",
        "opciones": ["A. 180 grados.", "B. La suma de los dos ángulos interiores no adyacentes a él.", "C. Al ángulo interior adyacente.", "D. 360 grados."],
        "respuesta": "B. La suma de los dos ángulos interiores no adyacentes a él.",
        "explicacion_ia": "Teorema del ángulo exterior. Si los internos son A, B, C. El exterior de C es 180-C, que equivale a A+B (porque A+B+C=180)."
    },
    {
        "materia": "Sociales y Ciudadanas",
        "pregunta": "El 'Fracking' (fracturamiento hidráulico) genera debate ambiental por:",
        "opciones": ["A. El ruido que hace.", "B. El riesgo de contaminar aguas subterráneas y generar sismicidad inducida al inyectar agua y químicos a alta presión.", "C. Que produce carbón.", "D. Que es muy lento."],
        "respuesta": "B. El riesgo de contaminar aguas subterráneas y generar sismicidad inducida al inyectar agua y químicos a alta presión.",
        "explicacion_ia": "La técnica rompe la roca madre para sacar gas/petróleo, pero los químicos usados y la presión pueden afectar acuíferos y estabilidad geológica."
    },
    {
        "materia": "Ciencias Naturales",
        "pregunta": "Si se corta el nervio vago que conecta el cerebro con el corazón, el corazón:",
        "opciones": ["A. Se detiene inmediatamente.", "B. Sigue latiendo, incluso más rápido, porque tiene su propio marcapasos natural.", "C. Explota.", "D. Late al revés."],
        "respuesta": "B. Sigue latiendo, incluso más rápido, porque tiene su propio marcapasos natural.",
        "explicacion_ia": "El corazón tiene automatismo (Nódulo Sinusal). El nervio vago (sistema parasimpático) lo frena constantemente; si se corta, el corazón se acelera (taquicardia) pero no para."
    },
    {
        "materia": "Lectura Crítica",
        "pregunta": "¿Qué es una 'tautología'?",
        "opciones": ["A. Una mentira.", "B. Una afirmación que es verdadera por definición y no aporta información nueva (ej: 'subir arriba', 'lo que es, es').", "C. Un error gramatical.", "D. Una figura geométrica."],
        "respuesta": "B. Una afirmación que es verdadera por definición y no aporta información nueva (ej: 'subir arriba', 'lo que es, es').",
        "explicacion_ia": "Es un enunciado redundante que es lógicamente válido pero informativamente vacío."
    },
    {
        "materia": "Matemáticas",
        "pregunta": "¿Cuál es el dominio de la función f(x) = 1/x?",
        "opciones": ["A. Todos los números reales.", "B. Todos los reales excepto el 0.", "C. Solo los números positivos.", "D. Solo los números enteros."],
        "respuesta": "B. Todos los reales excepto el 0.",
        "explicacion_ia": "La división por cero no está definida. Por tanto, x puede tomar cualquier valor menos 0."
    },
    {
        "materia": "Sociales y Ciudadanas",
        "pregunta": "La 'Plusvalía' en la teoría marxista se refiere a:",
        "opciones": ["A. El impuesto a la tierra.", "B. El valor que el trabajo del obrero crea por encima de lo que se le paga como salario, y que se apropia el capitalista.", "C. El ahorro del trabajador.", "D. La inflación."],
        "respuesta": "B. El valor que el trabajo del obrero crea por encima de lo que se le paga como salario, y que se apropia el capitalista.",
        "explicacion_ia": "Es el concepto central de la explotación en El Capital: la ganancia empresarial proviene del trabajo no remunerado."
    },
    {
        "materia": "Ciencias Naturales",
        "pregunta": "En la tabla periódica, la 'electronegatividad' aumenta:",
        "opciones": ["A. De arriba a abajo y de derecha a izquierda.", "B. De abajo a arriba y de izquierda a derecha.", "C. Al azar.", "D. Hacia el centro."],
        "respuesta": "B. De abajo a arriba y de izquierda a derecha.",
        "explicacion_ia": "El Flúor (arriba derecha) es el más electronegativo. El Francio (abajo izquierda) el menos. Los átomos más pequeños y con más protones atraen mejor los electrones."
    },
    {
        "materia": "Lectura Crítica",
        "pregunta": "El 'Solipsismo' es la postura filosófica que afirma:",
        "opciones": ["A. Que solo existe el Sol.", "B. Que solo puedo estar seguro de la existencia de mi propia mente; todo lo demás podría ser una ilusión.", "C. Que todos somos uno.", "D. Que nada existe."],
        "respuesta": "B. Que solo puedo estar seguro de la existencia de mi propia mente; todo lo demás podría ser una ilusión.",
        "explicacion_ia": "Es el escepticismo extremo sobre el mundo exterior y las otras mentes."
    },
    {
        "materia": "Ciencias Naturales",
        "pregunta": "Los catalizadores (como las enzimas) aceleran las reacciones químicas porque:",
        "opciones": ["A. Aumentan la temperatura del sistema.", "B. Disminuyen la energía de activación necesaria para que inicie la reacción.", "C. Aumentan la cantidad de producto final.", "D. Eliminan los reactivos."],
        "respuesta": "B. Disminuyen la energía de activación necesaria para que inicie la reacción.",
        "explicacion_ia": "Crean un 'atajo' energético. No cambian el inicio ni el final de la reacción, solo hacen que la barrera para empezar sea más baja."
    },
    {
        "materia": "Lectura Crítica",
        "pregunta": "La ironía socrática ('Solo sé que nada sé') tiene como función:",
        "opciones": ["A. Demostrar ignorancia real.", "B. Fingir ignorancia para hacer preguntas que lleven al interlocutor a descubrir sus propias contradicciones.", "C. Evitar responder en un examen.", "D. Burlarse de los dioses."],
        "respuesta": "B. Fingir ignorancia para hacer preguntas que lleven al interlocutor a descubrir sus propias contradicciones.",
        "explicacion_ia": "Es un método pedagógico (Mayéutica). Sócrates se pone en el lugar del que no sabe para guiar la búsqueda de la verdad."
    },
    {
        "materia": "Ciencias Naturales",
        "pregunta": "La densidad se define como:",
        "opciones": ["A. Masa por unidad de volumen.", "B. Peso por altura.", "C. Volumen por temperatura.", "D. Velocidad por tiempo."],
        "respuesta": "A. Masa por unidad de volumen.",
        "explicacion_ia": "La fórmula de densidad es d = m/v. Indica qué tan compacta es la materia en un espacio determinado."
    }
]
banco_premium = [
    
    {
        "materia": "Matemáticas Avanzadas",
        "tema": "Cálculo Integral Aplicado",
        "pregunta": "Un tanque cónico invertido de altura 10m y radio 5m se llena de agua a razón de 2 m³/min. ¿A qué velocidad sube el nivel del agua cuando la profundidad es de 4m?",
        "opciones": ["A. 1/(2π) m/min", "B. 1/(8π) m/min", "C. 2/(5π) m/min", "D. 0.5 m/min"],
        "respuesta": "A. 1/(2π) m/min",
        "explicacion_ia": "Se usa derivadas relacionadas. Volumen cono: V=1/3πr²h. Por semejanza de triángulos r/h = 5/10 -> r=h/2. V=1/12πh³. Derivando: dV/dt = 1/4πh²(dh/dt). Despejando dh/dt con h=4 y dV/dt=2."
    },
    {
        "materia": "Matemáticas",
        "pregunta": "Si el radio de un círculo aumenta en un 100%, ¿en qué porcentaje aumenta su área?",
        "opciones": ["A. 100%", "B. 200%", "C. 300%", "D. 400%"],
        "respuesta": "C. 300%",
        "explicacion_ia": "📐 Geometría: Si r=1, Área=π. Si aumentas 100%, el nuevo radio es 2. Nueva Área = π(2)² = 4π. El área pasó de 1π a 4π. Creció 3π extra. Eso es un aumento del 300% respecto al original."
    },
    {
        "materia": "Ciencias Naturales",
        "pregunta": "Un gas ideal está en un recipiente cerrado a volumen constante. Si duplicas su temperatura absoluta (Kelvin), ¿qué pasa con la presión?",
        "opciones": ["A. Se reduce a la mitad.", "B. Se duplica.", "C. Permanece igual.", "D. Se cuadruplica."],
        "respuesta": "B. Se duplica.",
        "explicacion_ia": "⚗️ Ley de Gay-Lussac: A volumen constante, la presión es directamente proporcional a la temperatura. Si calientas el gas al doble, las moléculas golpean las paredes con el doble de fuerza."
    },
    {
        "materia": "Sociales y Ciudadanas",
        "pregunta": "El Congreso aprueba una ley que convoca a un Referendo para permitir la pena de muerte en Colombia. La Corte Constitucional tumba la ley argumentando que 'el Congreso no puede sustituir la Constitución'. ¿Qué principio está defendiendo la Corte?",
        "opciones": ["A. La soberanía popular.", "B. La rigidez constitucional y el bloque de constitucionalidad.", "C. El derecho a la vida de los congresistas.", "D. La libertad de cultos."],
        "respuesta": "B. La rigidez constitucional y el bloque de constitucionalidad.",
        "explicacion_ia": "⚖️ Derecho Constitucional: Aunque el pueblo es soberano, hay límites. La Corte ha dicho que el Congreso puede 'reformar' la Constitución pero no 'sustituirla' (cambiar sus ejes fundamentales, como los DD.HH. y la prohibición de la muerte)."
    },
    {
        "materia": "Lectura Crítica",
        "pregunta": "Nietzsche afirma: 'Dios ha muerto'. Con esta frase, el filósofo quiere expresar que:",
        "opciones": ["A. Existe una prueba forense de la muerte de una divinidad.", "B. Los valores morales absolutos y la religión han perdido su poder para dar sentido a la vida moderna.", "C. Se debe fundar una nueva iglesia atea.", "D. La ciencia ha demostrado que Dios nunca existió."],
        "respuesta": "B. Los valores morales absolutos y la religión han perdido su poder para dar sentido a la vida moderna.",
        "explicacion_ia": "🧠 Nihilismo: No es una afirmación literal ni científica. Es una metáfora sobre el colapso de los valores tradicionales de occidente, dejando al hombre solo frente al vacío existencial."
    },
    {
        "materia": "Matemáticas",
        "pregunta": "En una urna hay 4 balotas rojas y 6 azules. Si sacas dos balotas SIN devolverlas, ¿cuál es la probabilidad de que la primera sea roja y la segunda azul?",
        "opciones": ["A. 24/100", "B. 24/90", "C. 10/20", "D. 4/10"],
        "respuesta": "B. 24/90",
        "explicacion_ia": "Probabilidad condicional: P(Roja) = 4/10. Quedan 9 balotas. P(Azul) = 6/9. Multiplicamos: (4/10) * (6/9) = 24/90. (Simplificado sería 4/15)."
    },
    {
        "materia": "Ciencias Naturales",
        "pregunta": "Si un objeto se mueve en círculos a velocidad constante (MCU), ¿existe aceleración?",
        "opciones": ["A. No, porque la velocidad es constante.", "B. Sí, aceleración tangencial.", "C. Sí, aceleración centrípeta hacia el centro.", "D. No, porque vuelve al mismo punto."],
        "respuesta": "C. Sí, aceleración centrípeta hacia el centro.",
        "explicacion_ia": "🚀 Física Vectorial: ¡Cáscara clásica! Aunque la rapidez (número) no cambie, la DIRECCIÓN cambia todo el tiempo. Cambiar de dirección requiere una fuerza (y aceleración) que jale hacia el centro."
    },
    {
        "materia": "Sociales y Ciudadanas",
        "pregunta": "La 'Silla Vacía' es una reforma política que castiga a los partidos políticos cuando uno de sus congresistas es condenado por nexos con grupos ilegales o corrupción. El castigo consiste en:",
        "opciones": ["A. El partido debe pagar una multa.", "B. El partido pierde esa curul (puesto) y no puede reemplazar al congresista con otro de su lista.", "C. El congresista va a la cárcel pero su reemplazo sube.", "D. Se cierran las sesiones del Congreso."],
        "respuesta": "B. El partido pierde esa curul (puesto) y no puede reemplazar al congresista con otro de su lista.",
        "explicacion_ia": "Es una sanción dura para que los partidos revisen bien a quién avalan. Si tu senador es parapoletico, pierdes el voto y el poder de esa silla permanentemente."
    },
    {
        "materia": "Lectura Crítica",
        "pregunta": "Platón, en el 'Mito de la Caverna', describe prisioneros que solo ven sombras en la pared y creen que esa es la realidad. Las sombras representan:",
        "opciones": ["A. La verdad absoluta.", "B. El mundo de las apariencias y la ignorancia.", "C. El cine y la televisión.", "D. La sabiduría de los ancianos."],
        "respuesta": "B. El mundo de las apariencias y la ignorancia.",
        "explicacion_ia": "Las sombras son lo que percibimos con los sentidos (doxa/opinión). El filósofo debe salir de la caverna hacia la luz (el mundo de las ideas/razón) para ver la verdad."
    },
    {
        "materia": "Matemáticas",
        "pregunta": "¿Cuántos números de 3 cifras diferentes se pueden formar con los dígitos 1, 2, 3, 4 y 5?",
        "opciones": ["A. 125", "B. 60", "C. 10", "D. 20"],
        "respuesta": "B. 60",
        "explicacion_ia": "Permutación sin repetición: Tienes 5 opciones para la primera cifra, 4 para la segunda (porque no puedes repetir) y 3 para la tercera. 5 x 4 x 3 = 60."
    },
    {
        "materia": "Ciencias Naturales",
        "pregunta": "¿Qué sucede en la Fase S del ciclo celular?",
        "opciones": ["A. La célula se divide en dos.", "B. Se duplica el ADN.", "C. Se sintetizan proteínas.", "D. La célula muere."],
        "respuesta": "B. Se duplica el ADN.",
        "explicacion_ia": "🧬 Biología Molecular: Antes de la mitosis (división), la célula debe copiar su manual de instrucciones (ADN) para que cada hija tenga una copia completa. Esto ocurre en la Fase S (Síntesis)."
    },
    {
        "materia": "Sociales y Ciudadanas",
        "pregunta": "¿Cuál es la diferencia fundamental entre el Derecho Internacional Humanitario (DIH) y el Derecho Internacional de los Derechos Humanos (DIDH)?",
        "opciones": ["A. No hay diferencia.", "B. El DIH se aplica en tiempos de conflicto armado y el DIDH en todo momento (principalmente paz).", "C. El DIH lo aplican los jueces y el DIDH los militares.", "D. El DIDH es solo para Europa."],
        "respuesta": "B. El DIH se aplica en tiempos de conflicto armado y el DIDH en todo momento (principalmente paz).",
        "explicacion_ia": "El DIH (Convenios de Ginebra) son las reglas de la guerra. Los DD.HH. son universales y permanentes, aunque algunos pueden limitarse en estados de excepción, el DIH se activa cuando hay guerra."
    },
    {
        "materia": "Lectura Crítica",
        "pregunta": "Identifique la premisa menor en este silogismo: 'Ningún héroe es cobarde. Algunos soldados son cobardes. Por lo tanto, algunos soldados no son héroes'.",
        "opciones": ["A. Ningún héroe es cobarde.", "B. Algunos soldados son cobardes.", "C. Por lo tanto, algunos soldados no son héroes.", "D. Los soldados son valientes."],
        "respuesta": "B. Algunos soldados son cobardes.",
        "explicacion_ia": "Estructura lógica: Premisa Mayor (Universal) -> Premisa Menor (Particular) -> Conclusión. La opción A es la mayor, la B es la menor."
    },
    {
        "materia": "Matemáticas",
        "pregunta": "La suma de las edades de un padre y su hijo es 50 años. Dentro de 5 años, el padre tendrá el doble de la edad del hijo. ¿Qué edad tiene el hijo hoy?",
        "opciones": ["A. 10", "B. 15", "C. 20", "D. 12"],
        "respuesta": "B. 15",
        "explicacion_ia": "Sistema: P+H=50. Futuro: (P+5) = 2(H+5). Despejando: P = 50-H. Sustituimos: (50-H+5) = 2H + 10. 55-H = 2H+10. 45 = 3H. H = 15."
    },
    {
        "materia": "Ciencias Naturales",
        "pregunta": "Dos resistencias de 4 ohmios se conectan en PARALELO. ¿Cuál es la resistencia total del circuito?",
        "opciones": ["A. 8 ohmios.", "B. 4 ohmios.", "C. 2 ohmios.", "D. 1 ohmio."],
        "respuesta": "C. 2 ohmios.",
        "explicacion_ia": "⚡ Electricidad: En paralelo, la resistencia total disminuye. Fórmula: 1/Rt = 1/R1 + 1/R2. O truco: Si son iguales, divide el valor por el número de resistencias. 4 / 2 = 2."
    },
    {
        "materia": "Sociales y Ciudadanas",
        "pregunta": "El 'Neoliberalismo' económico promueve:",
        "opciones": ["A. Que el Estado controle todas las empresas.", "B. La reducción de la intervención del Estado en la economía y el libre mercado.", "C. Aumentar los aranceles para proteger lo nacional.", "D. Regalar dinero a todos."],
        "respuesta": "B. La reducción de la intervención del Estado en la economía y el libre mercado.",
        "explicacion_ia": "Es el modelo predominante desde los 90s (Apertura Económica). Busca privatizar empresas estatales, reducir impuestos a empresas y fomentar la competencia global."
    },
    {
        "materia": "Lectura Crítica",
        "pregunta": "En un texto, si el autor dice: 'Es innegable que la medida es impopular', está utilizando un recurso para:",
        "opciones": ["A. Mostrar duda.", "B. Anticiparse a una objeción del lector (Concesión).", "C. Mentir.", "D. Concluir el texto."],
        "respuesta": "B. Anticiparse a una objeción del lector (Concesión).",
        "explicacion_ia": "Es una estrategia retórica. Admite un punto en contra ('es impopular') para luego contraatacar ('pero es necesaria'), ganando credibilidad."
    },
    {
        "materia": "Matemáticas",
        "pregunta": "Si sen(x) = 1/2, ¿cuál es el valor de x (en el primer cuadrante)?",
        "opciones": ["A. 30 grados.", "B. 45 grados.", "C. 60 grados.", "D. 90 grados."],
        "respuesta": "A. 30 grados.",
        "explicacion_ia": "📐 Trigonometría básica: Debes memorizar los ángulos notables. Sen(30°) = 0.5. Sen(45°) = √2/2. Sen(60°) = √3/2."
    },
    {
        "materia": "Matemáticas",
        "pregunta": "Un padre reparte $120.000 entre sus dos hijos en razón de 3 a 2. ¿Cuánto dinero recibe el hijo que más gana?",
        "opciones": ["A. $60.000", "B. $72.000", "C. $80.000", "D. $48.000"],
        "respuesta": "B. $72.000",
        "explicacion_ia": "Razones y Proporciones: La suma de las partes es 3+2=5. Dividimos el total entre 5: 120.000 / 5 = 24.000. El que recibe 3 partes gana: 3 * 24.000 = 72.000."
    },
    {
        "materia": "Ciencias Naturales",
        "pregunta": "Si un carro se mueve en línea recta y su gráfica de Velocidad vs. Tiempo es una línea horizontal, esto significa que:",
        "opciones": ["A. El carro está quieto.", "B. El carro acelera constantemente.", "C. El carro se mueve a velocidad constante (Aceleración cero).", "D. El carro está frenando."],
        "respuesta": "C. El carro se mueve a velocidad constante (Aceleración cero).",
        "explicacion_ia": "En una gráfica V vs T, si la línea no sube ni baja (pendiente cero), significa que la velocidad no cambia. Por tanto, no hay aceleración (MRU)."
    },
    {
        "materia": "Sociales y Ciudadanas",
        "pregunta": "¿Qué fue la 'Apertura Económica' en Colombia durante los años 90?",
        "opciones": ["A. La prohibición de importar productos extranjeros.", "B. Un proceso de reducción de aranceles para facilitar la entrada de productos extranjeros y la competencia global.", "C. La creación de más bancos nacionales.", "D. El cierre de fronteras."],
        "respuesta": "B. Un proceso de reducción de aranceles para facilitar la entrada de productos extranjeros y la competencia global.",
        "explicacion_ia": "Fue un cambio de modelo (del proteccionismo al neoliberalismo) impulsado por César Gaviria, buscando modernizar la economía, aunque quebró a muchos sectores locales que no podían competir."
    },
    {
        "materia": "Lectura Crítica",
        "pregunta": "Si alguien dice 'No seas sapo', está utilizando el lenguaje con una función:",
        "opciones": ["A. Denotativa (literal).", "B. Connotativa (figurada/cultural).", "C. Científica.", "D. Formal."],
        "respuesta": "B. Connotativa (figurada/cultural).",
        "explicacion_ia": "No se refiere al animal anfibio (denotación), sino al significado cultural de 'ser chismoso o delator' (connotación)."
    },
    {
        "materia": "Matemáticas",
        "pregunta": "¿Cuál es la probabilidad de que al lanzar dos monedas al aire, ambas caigan en 'cara'?",
        "opciones": ["A. 50%", "B. 25%", "C. 75%", "D. 10%"],
        "respuesta": "B. 25%",
        "explicacion_ia": "Eventos independientes: Probabilidad moneda 1 (1/2) x Probabilidad moneda 2 (1/2) = 1/4. Y 1/4 equivale al 25%."
    },
    {
        "materia": "Ciencias Naturales",
        "pregunta": "La principal diferencia entre una mezcla homogénea y una heterogénea es:",
        "opciones": ["A. Las homogéneas son sólidas y las heterogéneas líquidas.", "B. En las homogéneas no se distinguen sus componentes a simple vista; en las heterogéneas sí.", "C. Las heterogéneas no se pueden separar.", "D. Las homogéneas pesan más."],
        "respuesta": "B. En las homogéneas no se distinguen sus componentes a simple vista; en las heterogéneas sí.",
        "explicacion_ia": "Ejemplo: Agua con sal disuelta es homogénea (una sola fase). Agua con aceite es heterogénea (dos fases visibles)."
    },
    {
        "materia": "Sociales y Ciudadanas",
        "pregunta": "La pérdida de Panamá en 1903 se debió principalmente a:",
        "opciones": ["A. Una invasión de España.", "B. El abandono centralista de Bogotá hacia esa región y los intereses de EE.UU. en construir el canal.", "C. Un terremoto que separó la tierra.", "D. La venta voluntaria del territorio."],
        "respuesta": "B. El abandono centralista de Bogotá hacia esa región y los intereses de EE.UU. en construir el canal.",
        "explicacion_ia": "Fue una mezcla de descontento local tras la Guerra de los Mil Días y la intervención oportunista de Estados Unidos (Teodoro Roosevelt) para controlar la zona del canal interoceánico."
    },
    {
        "materia": "Lectura Crítica",
        "pregunta": "En el texto: 'El acusado es inocente porque nadie ha podido probar lo contrario', se incurre en una falacia llamada:",
        "opciones": ["A. Ad Hominem.", "B. Ad Ignorantiam (Apelación a la ignorancia).", "C. De autoridad.", "D. Causa falsa."],
        "respuesta": "B. Ad Ignorantiam (Apelación a la ignorancia).",
        "explicacion_ia": "Esta falacia consiste en afirmar que algo es verdad solo porque no se ha demostrado que sea falso (o viceversa)."
    },
    {
        "materia": "Matemáticas",
        "pregunta": "Si el perímetro de un cuadrado es 20 cm, ¿cuál es su área?",
        "opciones": ["A. 20 cm²", "B. 25 cm²", "C. 16 cm²", "D. 10 cm²"],
        "respuesta": "B. 25 cm²",
        "explicacion_ia": "El perímetro es 4 veces el lado (4L = 20), así que el lado mide 5 cm. El área es lado al cuadrado (5² = 25)."
    },
    {
        "materia": "Ciencias Naturales",
        "pregunta": "¿Qué ley explica por qué un globo aerostático sube?",
        "opciones": ["A. Ley de Ohm.", "B. Principio de Arquímedes.", "C. Ley de la Gravedad.", "D. Efecto Invernadero."],
        "respuesta": "B. Principio de Arquímedes.",
        "explicacion_ia": "El aire caliente dentro del globo es menos denso que el aire frío de afuera. El empuje hacia arriba es mayor que el peso del globo, haciéndolo flotar."
    },
    {
        "materia": "Sociales y Ciudadanas",
        "pregunta": "¿Qué es la 'Revocatoria del Mandato'?",
        "opciones": ["A. Cuando el Presidente despide a un ministro.", "B. Un mecanismo donde los ciudadanos votan para sacar a un alcalde o gobernador que no cumplió su programa.", "C. Cuando un juez anula una ley.", "D. Renunciar al trabajo."],
        "respuesta": "B. Un mecanismo donde los ciudadanos votan para sacar a un alcalde o gobernador que no cumplió su programa.",
        "explicacion_ia": "Solo aplica para Alcaldes y Gobernadores (no Presidente). Se basa en el incumplimiento del plan de gobierno inscrito."
    },
    {
        "materia": "Lectura Crítica",
        "pregunta": "¿Qué es una 'Analogía'?",
        "opciones": ["A. Una mentira piadosa.", "B. Una relación de semejanza entre cosas distintas.", "C. Un estudio del pasado.", "D. Un error gramatical."],
        "respuesta": "B. Una relación de semejanza entre cosas distintas.",
        "explicacion_ia": "Ejemplo: 'Las alas son al pájaro lo que las piernas son al humano' (ambas sirven para desplazarse en su medio)."
    },
    {
        "materia": "Matemáticas",
        "pregunta": "Resuelve la inecuación: 2x < 10",
        "opciones": ["A. x > 5", "B. x < 5", "C. x = 5", "D. x < 20"],
        "respuesta": "B. x < 5",
        "explicacion_ia": "Pasamos el 2 a dividir. x < 10/2. Por lo tanto, x < 5. Significa que x puede ser cualquier número menor que 5."
    },
    {
        "materia": "Ciencias Naturales",
        "pregunta": "La 'Selección Natural' de Darwin se basa en:",
        "opciones": ["A. El más fuerte siempre mata al más débil.", "B. Los individuos con características más favorables para su entorno sobreviven y se reproducen más.", "C. Dios elige a los animales.", "D. Los animales deciden cambiar para mejorar."],
        "respuesta": "B. Los individuos con características más favorables para su entorno sobreviven y se reproducen más.",
        "explicacion_ia": "No es 'el más fuerte', sino el 'mejor adaptado'. Si hace frío, el que tenga pelaje más grueso sobrevive y pasa ese gen a sus hijos."
    },
    {
        "materia": "Sociales y Ciudadanas",
        "pregunta": "¿Qué es el 'PIB' (Producto Interno Bruto)?",
        "opciones": ["A. La cantidad de dinero que imprime el banco.", "B. El valor total de los bienes y servicios producidos en un país durante un tiempo determinado.", "C. La deuda externa del país.", "D. El dinero que tienen los ricos."],
        "respuesta": "B. El valor total de los bienes y servicios producidos en un país durante un tiempo determinado.",
        "explicacion_ia": "Es el termómetro de la economía. Si el PIB crece, la economía produce más riqueza; si baja, hay recesión."
    },
    {
        "materia": "Lectura Crítica",
        "pregunta": "En la frase 'El viento susurraba tu nombre', se atribuye una cualidad humana a un ser inanimado. Esto es una:",
        "opciones": ["A. Prosopopeya o Personificación.", "B. Hipérbole.", "C. Símil.", "D. Antítesis."],
        "respuesta": "A. Prosopopeya o Personificación.",
        "explicacion_ia": "El viento no tiene cuerdas vocales ni conciencia para 'susurrar'. Se le da una acción humana para crear un efecto poético."
    },
    {
        "materia": "Matemáticas",
        "pregunta": "Un ciclista recorre 15 km en 30 minutos. ¿Cuál es su velocidad media en km/h?",
        "opciones": ["A. 15 km/h", "B. 30 km/h", "C. 45 km/h", "D. 7.5 km/h"],
        "respuesta": "B. 30 km/h",
        "explicacion_ia": "30 minutos es 0.5 horas. Velocidad = Distancia / Tiempo. V = 15 / 0.5 = 30 km/h. (O lógica simple: si en media hora hace 15, en una hora hace el doble: 30)."
    },
    {
        "materia": "Ciencias Naturales",
        "pregunta": "¿Qué ocurre en una reacción 'Exotérmica'?",
        "opciones": ["A. Se absorbe frío.", "B. Se libera energía en forma de calor.", "C. Se necesita calentar para que ocurra.", "D. No pasa nada."],
        "respuesta": "B. Se libera energía en forma de calor.",
        "explicacion_ia": "Ejemplo: El fuego. Los reactivos tienen más energía que los productos, y esa diferencia se libera al ambiente como calor."
    },
    {
        "materia": "Sociales y Ciudadanas",
        "pregunta": "¿Cuál es el fin principal de los partidos políticos en una democracia?",
        "opciones": ["A. Repartir mercados.", "B. Canalizar la voluntad popular y competir por el poder para ejecutar un programa de gobierno.", "C. Organizar fiestas.", "D. Controlar a la policía."],
        "respuesta": "B. Canalizar la voluntad popular y competir por el poder para ejecutar un programa de gobierno.",
        "explicacion_ia": "Son el puente entre la gente y el Estado. Agrupan a personas con ideologías similares para representarlas."
    },
    {
        "materia": "Lectura Crítica",
        "pregunta": "¿Qué es la 'cohesión' en un texto?",
        "opciones": ["A. Que tenga buena ortografía.", "B. Que las ideas estén bien conectadas entre sí gramatical y léxicamente.", "C. Que sea divertido.", "D. Que tenga muchas páginas."],
        "respuesta": "B. Que las ideas estén bien conectadas entre sí gramatical y léxicamente.",
        "explicacion_ia": "La cohesión es el 'pegante' del texto (conectores, pronombres, sinónimos) que hace que las frases no sean una lista suelta, sino un tejido unido."
    },
    {
        "materia": "Matemáticas",
        "pregunta": "¿Cuál es el valor absoluto de -15?",
        "opciones": ["A. -15", "B. 15", "C. 0", "D. 1.5"],
        "respuesta": "B. 15",
        "explicacion_ia": "El valor absoluto mide la distancia de un número al cero, sin importar el signo. Siempre es positivo. |-15| = 15."
    },
    {
        "materia": "Ciencias Naturales",
        "pregunta": "La 'Clonación' consiste en:",
        "opciones": ["A. Crear un ser vivo genéticamente idéntico a otro.", "B. Mezclar dos especies diferentes.", "C. Modificar el ADN para tener superpoderes.", "D. Congelar a alguien."],
        "respuesta": "A. Crear un ser vivo genéticamente idéntico a otro.",
        "explicacion_ia": "Como la oveja Dolly. Se toma el ADN de una célula adulta y se usa para crear un nuevo organismo con la misma información genética exacta."
    },
    {
        "materia": "Inglés",
        "pregunta": "Complete the sentence: 'She ______ to the park yesterday.'",
        "opciones": ["A. go", "B. goes", "C. went", "D. gone"],
        "respuesta": "C. went",
        "explicacion_ia": "Gramática: La oración dice 'yesterday' (ayer), por lo que necesitamos el Pasado Simple. El pasado de 'go' es 'went'."
    },
    {
        "materia": "Inglés",
        "pregunta": "What is the synonym of 'Happy'?",
        "opciones": ["A. Sad", "B. Angry", "C. Joyful", "D. Bored"],
        "respuesta": "C. Joyful",
        "explicacion_ia": "Vocabulario: 'Joyful' significa lleno de alegría, que es lo mismo que 'Happy' (Feliz)."
    },
    {
        "materia": "Inglés",
        "pregunta": "Choose the correct question: '______ are you from?'",
        "opciones": ["A. When", "B. Where", "C. Who", "D. Which"],
        "respuesta": "B. Where",
        "explicacion_ia": "Para preguntar por el lugar de origen, usamos 'Where' (Dónde). 'Where are you from?' = ¿De dónde eres?"
    },
    {
        "materia": "Inglés",
        "pregunta": "Read: 'Please, keep off the grass'. Where can you see this sign?",
        "opciones": ["A. In a library.", "B. In a park.", "C. In a bedroom.", "D. In a kitchen."],
        "respuesta": "B. In a park.",
        "explicacion_ia": "Comprensión lectora: 'Keep off the grass' significa 'No pisar el césped'. Es un aviso típico de un parque o jardín."
    },
    {
        "materia": "Inglés",
        "pregunta": "If you have a toothache, you should see a:",
        "opciones": ["A. Lawyer.", "B. Dentist.", "C. Carpenter.", "D. Chef."],
        "respuesta": "B. Dentist.",
        "explicacion_ia": "Vocabulario lógico: Si tienes 'toothache' (dolor de muela), el profesional indicado es el dentista."
    },

    # --- MÁS PREGUNTAS VARIADAS ---
    {
        "materia": "Matemáticas",
        "pregunta": "Una pizza se divide en 8 porciones iguales. Si Juan se come 3 porciones y María se come 2, ¿qué fracción de la pizza sobra?",
        "opciones": ["A. 3/8", "B. 5/8", "C. 1/4", "D. 3/5"],
        "respuesta": "A. 3/8",
        "explicacion_ia": "Se comieron 3 + 2 = 5 porciones. Si había 8, sobran 8 - 5 = 3. La fracción sobrante es 3/8."
    },
    {
        "materia": "Ciencias Naturales",
        "pregunta": "¿Cuál es la función principal de la Capa de Ozono?",
        "opciones": ["A. Mantener el calor de la tierra.", "B. Proteger a los seres vivos de la radiación ultravioleta (UV) del sol.", "C. Generar oxígeno.", "D. Producir lluvia."],
        "respuesta": "B. Proteger a los seres vivos de la radiación ultravioleta (UV) del sol.",
        "explicacion_ia": "El ozono actúa como un escudo que filtra los rayos UV dañinos, evitando cáncer de piel y daños a los ecosistemas."
    },
    {
        "materia": "Sociales y Ciudadanas",
        "pregunta": "La 'Discriminación Positiva' (o Acción Afirmativa) consiste en:",
        "opciones": ["A. Discriminar a todos por igual.", "B. Dar trato preferencial temporal a grupos históricamente marginados para lograr equidad real.", "C. Ser amable al discriminar.", "D. Negar derechos a las minorías."],
        "respuesta": "B. Dar trato preferencial temporal a grupos históricamente marginados para lograr equidad real.",
        "explicacion_ia": "Ejemplo: Becas exclusivas para indígenas o cuotas de género. Busca nivelar el terreno de juego para quienes han estado en desventaja histórica."
    },
    {
        "materia": "Lectura Crítica",
        "pregunta": "Si en una caricatura política aparece un político con nariz de Pinocho, el autor sugiere que:",
        "opciones": ["A. El político es de madera.", "B. El político es un mentiroso.", "C. Al político le gustan los cuentos.", "D. El político tiene gripa."],
        "respuesta": "B. El político es un mentiroso.",
        "explicacion_ia": "Es una intertextualidad. Se usa el referente cultural de Pinocho (a quien le crecía la nariz al mentir) para calificar al personaje."
    },
    {
        "materia": "Matemáticas",
        "pregunta": "Si el área de un cuadrado es 100 m², ¿cuánto mide su perímetro?",
        "opciones": ["A. 10 m", "B. 20 m", "C. 40 m", "D. 100 m"],
        "respuesta": "C. 40 m",
        "explicacion_ia": "Si el área es 100, el lado es √100 = 10 m. El perímetro es la suma de los 4 lados: 10 + 10 + 10 + 10 = 40 m."
    },
    {
        "materia": "Ciencias Naturales",
        "pregunta": "La 'Evaporación' es un proceso del ciclo del agua donde:",
        "opciones": ["A. El agua cae como lluvia.", "B. El agua líquida de océanos y lagos se convierte en vapor por el calor del sol.", "C. El vapor se convierte en nubes.", "D. El agua se congela en los polos."],
        "respuesta": "B. El agua líquida de océanos y lagos se convierte en vapor por el calor del sol.",
        "explicacion_ia": "Es el paso de líquido a gas. Es fundamental para llevar el agua de la superficie a la atmósfera."
    },
    {
        "materia": "Sociales y Ciudadanas",
        "pregunta": "¿Qué es la 'Desobediencia Civil'?",
        "opciones": ["A. Romper vidrios en una marcha.", "B. El incumplimiento pacífico y público de una ley considerada injusta para presionar su cambio.", "C. No ir a votar.", "D. Robar bancos."],
        "respuesta": "B. El incumplimiento pacífico y público de una ley considerada injusta para presionar su cambio.",
        "explicacion_ia": "Ejemplos históricos: Gandhi o Martin Luther King. La clave es que es pacífica y busca un fin moral superior, aceptando el castigo legal para evidenciar la injusticia."
    },
    {
        "materia": "Lectura Crítica",
        "pregunta": "En el enunciado: 'Compré la blusa, pero no me la puse', el conector 'pero' indica:",
        "opciones": ["A. Una causa.", "B. Una consecuencia.", "C. Una oposición o restricción.", "D. Una condición."],
        "respuesta": "C. Una oposición o restricción.",
        "explicacion_ia": "Contrasta la acción de comprar con la acción esperada de usarla. Rompe la expectativa lógica."
    },
    {
        "materia": "Matemáticas",
        "pregunta": "¿Cuál de los siguientes números es primo?",
        "opciones": ["A. 9", "B. 15", "C. 17", "D. 21"],
        "respuesta": "C. 17",
        "explicacion_ia": "Un número primo solo tiene dos divisores: el 1 y él mismo. 9 se divide por 3. 15 por 5. 21 por 7. El 17 solo por 1 y 17."
    },
    {
        "materia": "Ciencias Naturales",
        "pregunta": "¿Qué es un 'Vector' en física?",
        "opciones": ["A. Un insecto que transmite enfermedades.", "B. Una magnitud que tiene valor numérico, dirección y sentido.", "C. Una medida de temperatura.", "D. Una fuerza que siempre es cero."],
        "respuesta": "B. Una magnitud que tiene valor numérico, dirección y sentido.",
        "explicacion_ia": "A diferencia de los escalares (que solo tienen número, como la temperatura), los vectores (como la velocidad o fuerza) necesitan decir 'hacia dónde' van."
    },
    {
        "materia": "Sociales y Ciudadanas",
        "pregunta": "En Colombia, la soberanía reside exclusivamente en:",
        "opciones": ["A. El Presidente.", "B. El Congreso.", "C. El Pueblo.", "D. El Ejército."],
        "respuesta": "C. El Pueblo.",
        "explicacion_ia": "Artículo 3 de la Constitución: 'La soberanía reside exclusivamente en el pueblo, del cual emana el poder público'."
    },
    {
        "materia": "Inglés",
        "pregunta": "Complete: 'They ______ watching TV right now.'",
        "opciones": ["A. is", "B. am", "C. are", "D. be"],
        "respuesta": "C. are",
        "explicacion_ia": "Presente Continuo: Para 'They' (ellos), el verbo to be correcto es 'are'. They are watching (Ellos están viendo)."
    },
    {
        "materia": "Matemáticas",
        "pregunta": "Un ángulo llano mide:",
        "opciones": ["A. 90 grados.", "B. 180 grados.", "C. 360 grados.", "D. 45 grados."],
        "respuesta": "B. 180 grados.",
        "explicacion_ia": "Es el ángulo que forma una línea recta plana. Medio círculo."
    },
    {
        "materia": "Ciencias Naturales",
        "pregunta": "La simbiosis donde ambas especies se benefician (ej: abeja y flor) se llama:",
        "opciones": ["A. Parasitismo.", "B. Mutualismo.", "C. Depredación.", "D. Competencia."],
        "respuesta": "B. Mutualismo.",
        "explicacion_ia": "En el mutualismo, los dos ganan (la abeja come néctar, la flor es polinizada). En el parasitismo uno gana y el otro pierde."
    },
    {
        "materia": "Lectura Crítica",
        "pregunta": "Si un texto empieza diciendo: 'En primer lugar... En segundo lugar... Finalmente...', su estructura es:",
        "opciones": ["A. Narrativa.", "B. Secuencial u organizada.", "C. Caótica.", "D. Dialogada."],
        "respuesta": "B. Secuencial u organizada.",
        "explicacion_ia": "Estos conectores de orden sirven para organizar la información paso a paso o jerárquicamente."
    },
    {
        "materia": "Matemáticas",
        "pregunta": "Si 5 obreros hacen una pared en 10 días, ¿cuánto tardarán 10 obreros (trabajando al mismo ritmo)?",
        "opciones": ["A. 20 días.", "B. 5 días.", "C. 10 días.", "D. 15 días."],
        "respuesta": "B. 5 días.",
        "explicacion_ia": "Es una regla de tres INVERSA. Si hay el DOBLE de obreros, tardarán la MITAD del tiempo. 10 / 2 = 5 días."
    },
    {
        "materia": "Ciencias Naturales",
        "pregunta": "¿Qué instrumento se usa para medir la masa de un objeto?",
        "opciones": ["A. Dinamómetro.", "B. Balanza.", "C. Termómetro.", "D. Cronómetro."],
        "respuesta": "B. Balanza.",
        "explicacion_ia": "La balanza mide masa (cantidad de materia). El dinamómetro mide peso (fuerza de gravedad). A veces se confunden, pero en física son distintos."
    },
    {
        "materia": "Sociales y Ciudadanas",
        "pregunta": "¿Qué es el 'Estado de Derecho'?",
        "opciones": ["A. Que el Estado siempre tiene la razón.", "B. Que todos, incluidos los gobernantes, están sometidos a la ley.", "C. Que los abogados mandan.", "D. Que no existen leyes."],
        "respuesta": "B. Que todos, incluidos los gobernantes, están sometidos a la ley.",
        "explicacion_ia": "Es lo opuesto al absolutismo. Aquí el Presidente no puede hacer lo que quiera, debe respetar la Constitución y las leyes como cualquier ciudadano."
    },
    {
        "materia": "Inglés",
        "pregunta": "Choose the correct translation for: 'The book is on the table'.",
        "opciones": ["A. El libro está bajo la mesa.", "B. El libro está sobre la mesa.", "C. El libro está en la mesa (adentro).", "D. El libro es la mesa."],
        "respuesta": "B. El libro está sobre la mesa.",
        "explicacion_ia": "La preposición 'ON' indica que algo está sobre una superficie, tocándola."
    },
    {
        "materia": "Lectura Crítica",
        "pregunta": "El prefijo 'bi-' en palabras como 'bicolor' o 'bimensual' significa:",
        "opciones": ["A. Vida.", "B. Dos o doble.", "C. Grande.", "D. Nuevo."],
        "respuesta": "B. Dos o doble.",
        "explicacion_ia": "Etimología básica: Bicolor = Dos colores. Bimensual = Dos veces al mes (o cada dos meses, según contexto, pero siempre refiere al dos)."
    },
    {
        "materia": "Inglés",
        "pregunta": "Where can you see this sign? 'DO NOT SWIM - SHARKS DETECTED'",
        "opciones": ["A. In a pool.", "B. At the beach.", "C. In a bathtub.", "D. In a forest."],
        "respuesta": "B. At the beach.",
        "explicacion_ia": "Contexto (Parte 1 ICFES): Si hay tiburones (sharks), necesariamente es en el mar (beach). En una piscina o bañera no hay tiburones."
    },
    {
        "materia": "Inglés",
        "pregunta": "Complete the conversation: \n- 'I am very hungry.' \n- '__________'",
        "opciones": ["A. You should sleep.", "B. Let's go to a restaurant.", "C. I am happy.", "D. It is raining."],
        "respuesta": "B. Let's go to a restaurant.",
        "explicacion_ia": "Conversación lógica (Parte 3 ICFES): Si alguien tiene hambre (hungry), la respuesta lógica es proponer comer."
    },
    {
        "materia": "Inglés",
        "pregunta": "Grammar: She ______ playing tennis right now.",
        "opciones": ["A. are", "B. am", "C. is", "D. be"],
        "respuesta": "C. is",
        "explicacion_ia": "Presente Continuo: Para la tercera persona singular (She), el auxiliar correcto del verbo To Be es 'is'."
    },
    {
        "materia": "Inglés",
        "pregunta": "Vocabulary: Which animal can fly?",
        "opciones": ["A. Snake.", "B. Eagle.", "C. Elephant.", "D. Shark."],
        "respuesta": "B. Eagle.",
        "explicacion_ia": "Vocabulario básico: 'Eagle' es águila. Las serpientes, elefantes y tiburones no vuelan."
    },
    {
        "materia": "Inglés",
        "pregunta": "Complete: 'If it rains tomorrow, I ______ stay at home.'",
        "opciones": ["A. will", "B. would", "C. did", "D. have"],
        "respuesta": "A. will",
        "explicacion_ia": "Primer Condicional: Se usa para situaciones reales en el futuro. Estructura: If + Presente Simple, + Will."
    },
    {
        "materia": "Inglés",
        "pregunta": "Choose the opposite of 'Fast'.",
        "opciones": ["A. Quick.", "B. Slow.", "C. Hard.", "D. Easy."],
        "respuesta": "B. Slow.",
        "explicacion_ia": "Antónimos: 'Fast' es rápido. Lo opuesto es 'Slow' (lento)."
    },
    {
        "materia": "Inglés",
        "pregunta": "Where can you see this notice? 'SILENCE PLEASE - EXAM IN PROGRESS'",
        "opciones": ["A. In a disco.", "B. In a classroom or school hall.", "C. At a football stadium.", "D. In a market."],
        "respuesta": "B. In a classroom or school hall.",
        "explicacion_ia": "Contexto: Se pide silencio por un examen. El único lugar lógico es un salón de clases o colegio."
    },
    {
        "materia": "Inglés",
        "pregunta": "Complete the sentence: 'My brother is _______ than me.'",
        "opciones": ["A. tall", "B. more tall", "C. taller", "D. the tallest"],
        "respuesta": "C. taller",
        "explicacion_ia": "Comparativos: Para adjetivos cortos como 'tall', se agrega '-er'. 'Taller than' significa 'más alto que'."
    },
    {
        "materia": "Inglés",
        "pregunta": "Definition: 'A place where you go to buy books.'",
        "opciones": ["A. Library.", "B. Bookshop / Bookstore.", "C. Pharmacy.", "D. Gym."],
        "respuesta": "B. Bookshop / Bookstore.",
        "explicacion_ia": "Falso amigo: 'Library' es biblioteca (donde prestan libros). Donde se COMPRAN ('buy') es 'Bookshop' o 'Bookstore'."
    },
    {
        "materia": "Inglés",
        "pregunta": "Choose the correct past tense: 'Yesterday, I ______ a pizza.'",
        "opciones": ["A. eat", "B. ate", "C. eaten", "D. eating"],
        "respuesta": "B. ate",
        "explicacion_ia": "Pasado Simple: El verbo es irregular. El pasado de 'eat' es 'ate'."
    },
    {
        "materia": "Inglés",
        "pregunta": "Complete: 'Do you like ______ movies?'",
        "opciones": ["A. watch", "B. watching", "C. to watching", "D. watched"],
        "respuesta": "B. watching",
        "explicacion_ia": "Gerundios: Después de verbos de gusto/preferencia como 'Like', 'Love', 'Hate', el siguiente verbo suele ir con -ing."
    },
    {
        "materia": "Inglés",
        "pregunta": "Conversation: \n- 'Thank you very much!' \n- '__________'",
        "opciones": ["A. You're welcome.", "B. I am sorry.", "C. Good bye.", "D. Yes, please."],
        "respuesta": "A. You're welcome.",
        "explicacion_ia": "Cortesía básica: La respuesta estándar a 'Thank you' es 'You're welcome' (De nada)."
    },
    {
        "materia": "Inglés",
        "pregunta": "What is the plural of 'Child'?",
        "opciones": ["A. Childs", "B. Children", "C. Childrens", "D. Childes"],
        "respuesta": "B. Children",
        "explicacion_ia": "Plurales irregulares: Child no agrega 's'. Su plural cambia totalmente a 'Children'."
    },
    {
        "materia": "Inglés",
        "pregunta": "Read: 'SALE! 50% OFF'. Where do you see this?",
        "opciones": ["A. In a hospital.", "B. In a store window.", "C. In a police station.", "D. In a church."],
        "respuesta": "B. In a store window.",
        "explicacion_ia": "Contexto: 'SALE' y descuentos (OFF) son típicos de tiendas comerciales."
    },
    {
        "materia": "Inglés",
        "pregunta": "Choose the correct preposition: 'I was born ______ 1995.'",
        "opciones": ["A. on", "B. at", "C. in", "D. to"],
        "respuesta": "C. in",
        "explicacion_ia": "Preposiciones de tiempo: Para AÑOS y MESES se usa 'IN'. Para días específicos se usa 'ON'."
    },
    {
        "materia": "Inglés",
        "pregunta": "Which word is a fruit?",
        "opciones": ["A. Carrot.", "B. Potato.", "C. Apple.", "D. Onion."],
        "respuesta": "C. Apple.",
        "explicacion_ia": "Vocabulario: Carrot (zanahoria), Potato (papa) y Onion (cebolla) son vegetales/tubérculos. Apple (manzana) es fruta."
    },
    {
        "materia": "Inglés",
        "pregunta": "Complete: 'She has ______ been to Paris.'",
        "opciones": ["A. never", "B. ever", "C. yet", "D. yesterday"],
        "respuesta": "A. never",
        "explicacion_ia": "Presente Perfecto: 'She has never been' significa 'Ella nunca ha estado'. 'Ever' se usa en preguntas y 'Yet' en negaciones al final."
    },
    {
        "materia": "Inglés",
        "pregunta": "Definition: 'A person who flies an airplane.'",
        "opciones": ["A. Driver.", "B. Pilot.", "C. Doctor.", "D. Chef."],
        "respuesta": "B. Pilot.",
        "explicacion_ia": "Definiciones (Parte 2 ICFES): Quien vuela un avión es un piloto."
    },
    {
        "materia": "Inglés",
        "pregunta": "Complete: 'This is the ______ book I have ever read.'",
        "opciones": ["A. good", "B. better", "C. best", "D. most good"],
        "respuesta": "C. best",
        "explicacion_ia": "Superlativos: 'Good' es irregular. El superlativo es 'The best' (El mejor)."
    },
    {
        "materia": "Inglés",
        "pregunta": "Conversation: \n- 'Can you swim?' \n- '__________'",
        "opciones": ["A. Yes, I do.", "B. Yes, I can.", "C. Yes, I am.", "D. Yes, I have."],
        "respuesta": "B. Yes, I can.",
        "explicacion_ia": "Gramática: Si la pregunta empieza con el modal 'Can', la respuesta corta debe usar el mismo modal: 'Yes, I can'."
    },
    {
        "materia": "Inglés",
        "pregunta": "Choose the synonym of 'Start'.",
        "opciones": ["A. Finish.", "B. Begin.", "C. End.", "D. Stop."],
        "respuesta": "B. Begin.",
        "explicacion_ia": "Sinónimos: 'Start' y 'Begin' significan comenzar/empezar."
    },
    {
        "materia": "Inglés",
        "pregunta": "Complete: 'We ______ study for the exam tomorrow.'",
        "opciones": ["A. must", "B. can to", "C. should to", "D. would"],
        "respuesta": "A. must",
        "explicacion_ia": "Modales: 'Must' indica deber/obligación. 'Can' y 'Should' nunca llevan 'to' después (error común)."
    },
    {
        "materia": "Inglés",
        "pregunta": "Read: 'Please, leave your bags at the counter.' Where are you?",
        "opciones": ["A. In a supermarket entrance.", "B. In your house.", "C. In a forest.", "D. In a taxi."],
        "respuesta": "A. In a supermarket entrance.",
        "explicacion_ia": "Contexto: Es la instrucción típica de guardar bolsos en paquetería al entrar a un supermercado."
    },
    {
        "materia": "Inglés",
        "pregunta": "Where can you see this sign? 'PLEASE, DO NOT FEED THE ANIMALS'",
        "opciones": ["A. In a zoo.", "B. In a bank.", "C. In a school.", "D. In a hospital."],
        "respuesta": "A. In a zoo.",
        "explicacion_ia": "Contexto: 'Feed the animals' significa 'Alimentar a los animales'. Esto es una regla típica de los zoológicos."
    },
    {
        "materia": "Inglés",
        "pregunta": "Definition: 'A machine used to wash clothes.'",
        "opciones": ["A. Fridge.", "B. Washing machine.", "C. Microwave.", "D. Blender."],
        "respuesta": "B. Washing machine.",
        "explicacion_ia": "Vocabulario de hogar: La máquina para lavar ropa es la 'Washing machine' (Lavadora)."
    },
    {
        "materia": "Inglés",
        "pregunta": "Complete: 'My sister ______ like coffee.'",
        "opciones": ["A. don't", "B. doesn't", "C. isn't", "D. aren't"],
        "respuesta": "B. doesn't",
        "explicacion_ia": "Presente Simple: Para la tercera persona (She/My sister) en negativo, se usa el auxiliar 'Doesn't'."
    },
    {
        "materia": "Inglés",
        "pregunta": "Conversation: \n- 'Can I help you?' \n- '__________'",
        "opciones": ["A. Yes, I am looking for a shirt.", "B. No, I am fine.", "C. Yes, I do.", "D. It is blue."],
        "respuesta": "A. Yes, I am looking for a shirt.",
        "explicacion_ia": "Situacional: Es la típica pregunta de un vendedor en una tienda. La respuesta lógica es decir qué estás buscando."
    },
    {
        "materia": "Inglés",
        "pregunta": "Where can you see this sign? 'FLIGHT 202 TO MIAMI - GATE 4'",
        "opciones": ["A. At a bus station.", "B. At an airport.", "C. At a train station.", "D. On a boat."],
        "respuesta": "B. At an airport.",
        "explicacion_ia": "Contexto: 'Flight' (Vuelo) y 'Gate' (Puerta de embarque) son palabras exclusivas de los aeropuertos."
    },
    {
        "materia": "Inglés",
        "pregunta": "Definition: 'The season when it is very hot and people go to the beach.'",
        "opciones": ["A. Winter.", "B. Summer.", "C. Spring.", "D. Autumn."],
        "respuesta": "B. Summer.",
        "explicacion_ia": "Estaciones: La estación caliente (hot) es el verano (Summer)."
    },
    {
        "materia": "Inglés",
        "pregunta": "Complete: 'We ______ to the cinema last night.'",
        "opciones": ["A. go", "B. going", "C. went", "D. gone"],
        "respuesta": "C. went",
        "explicacion_ia": "Pasado Simple: 'Last night' indica pasado. El pasado de 'go' es 'went'."
    },
    {
        "materia": "Inglés",
        "pregunta": "Vocabulary: Which one is NOT a color?",
        "opciones": ["A. Purple.", "B. Square.", "C. Yellow.", "D. Green."],
        "respuesta": "B. Square.",
        "explicacion_ia": "Categorización: Purple, Yellow y Green son colores. 'Square' (Cuadrado) es una forma geométrica."
    },
    {
        "materia": "Inglés",
        "pregunta": "Complete: 'I have been living here ______ 10 years.'",
        "opciones": ["A. since", "B. for", "C. ago", "D. in"],
        "respuesta": "B. for",
        "explicacion_ia": "Presente Perfecto: Usamos 'For' para periodos de tiempo (por 10 años). Usamos 'Since' para fechas de inicio (desde 2010)."
    },
    {
        "materia": "Inglés",
        "pregunta": "Conversation: \n- 'Nice to meet you.' \n- '__________'",
        "opciones": ["A. I am fine.", "B. Nice to meet you too.", "C. Good bye.", "D. You represent me."],
        "respuesta": "B. Nice to meet you too.",
        "explicacion_ia": "Saludo estándar: Cuando alguien dice 'Gusto en conocerte', se responde 'Gusto en conocerte también' (too)."
    },
    {
        "materia": "Inglés",
        "pregunta": "Where can you see this sign? 'QUIET ZONE - HOSPITAL'",
        "opciones": ["A. In a street near a medical center.", "B. In a stadium.", "C. In a disco.", "D. In a market."],
        "respuesta": "A. In a street near a medical center.",
        "explicacion_ia": "Contexto: Se pide silencio cerca de un hospital."
    },
    {
        "materia": "Inglés",
        "pregunta": "Definition: 'A person who designs buildings.'",
        "opciones": ["A. Bricklayer.", "B. Architect.", "C. Doctor.", "D. Mechanic."],
        "respuesta": "B. Architect.",
        "explicacion_ia": "Profesiones: Quien diseña edificios es el Arquitecto."
    },
    {
        "materia": "Inglés",
        "pregunta": "Complete: 'This car is ______ than that one.'",
        "opciones": ["A. expensive", "B. more expensive", "C. most expensive", "D. expensiver"],
        "respuesta": "B. more expensive",
        "explicacion_ia": "Comparativos largos: 'Expensive' es una palabra larga, así que no usa '-er', sino 'more ... than'."
    },
    {
        "materia": "Inglés",
        "pregunta": "Vocabulary: 'Breakfast' is a meal you eat in the:",
        "opciones": ["A. Morning.", "B. Afternoon.", "C. Evening.", "D. Night."],
        "respuesta": "A. Morning.",
        "explicacion_ia": "Vocabulario: 'Breakfast' es el desayuno, se come en la mañana."
    },
    {
        "materia": "Inglés",
        "pregunta": "Complete: 'If I ______ the lottery, I would buy a house.'",
        "opciones": ["A. win", "B. won", "C. winning", "D. wins"],
        "respuesta": "B. won",
        "explicacion_ia": "Segundo Condicional: Se usa para situaciones hipotéticas. Estructura: If + Pasado Simple, + Would."
    },
    {
        "materia": "Inglés",
        "pregunta": "Where can you see this sign? 'LUNCH SPECIAL $5.00'",
        "opciones": ["A. In a bank.", "B. In a restaurant.", "C. In a library.", "D. In a shoe shop."],
        "respuesta": "B. In a restaurant.",
        "explicacion_ia": "Contexto: 'Lunch' (Almuerzo) y precios de comida se ven en restaurantes."
    },
    {
        "materia": "Inglés",
        "pregunta": "Definition: 'The daughter of your brother.'",
        "opciones": ["A. Niece.", "B. Nephew.", "C. Cousin.", "D. Sister."],
        "respuesta": "A. Niece.",
        "explicacion_ia": "Familia: La hija de tu hermano es tu sobrina (Niece). Si fuera hijo (hombre) sería Nephew."
    },
    {
        "materia": "Inglés",
        "pregunta": "Complete: 'There ______ many people at the party.'",
        "opciones": ["A. is", "B. was", "C. were", "D. be"],
        "respuesta": "C. were",
        "explicacion_ia": "Pasado plural: 'People' es plural. 'There were' significa 'Hubo/Había' (plural)."
    },
    {
        "materia": "Inglés",
        "pregunta": "Conversation: \n- 'Whose bag is this?' \n- '__________'",
        "opciones": ["A. It is mine.", "B. It is me.", "C. It is I.", "D. It is my."],
        "respuesta": "A. It is mine.",
        "explicacion_ia": "Posesivos: Para decir 'es mío' al final de la frase, se usa el pronombre posesivo 'Mine'. ('My' siempre necesita un objeto después: It is my bag)."
    },
    {
        "materia": "Inglés",
        "pregunta": "Vocabulary: Which body part do you use to see?",
        "opciones": ["A. Ears.", "B. Nose.", "C. Eyes.", "D. Mouth."],
        "respuesta": "C. Eyes.",
        "explicacion_ia": "Cuerpo humano: Usas los ojos (Eyes) para ver."
    },
    {
        "materia": "Inglés",
        "pregunta": "Complete: 'You ______ smoke in the hospital. It is prohibited.'",
        "opciones": ["A. must", "B. mustn't", "C. should", "D. can"],
        "respuesta": "B. mustn't",
        "explicacion_ia": "Modales: 'Mustn't' indica prohibición. 'No debes'."
    },
    {
        "materia": "Inglés",
        "pregunta": "Where can you see this sign? 'SPEED LIMIT 30'",
        "opciones": ["A. On a road.", "B. In a bathroom.", "C. In a kitchen.", "D. On a sofa."],
        "respuesta": "A. On a road.",
        "explicacion_ia": "Contexto: Los límites de velocidad son señales de tránsito (carretera)."
    },
    {
        "materia": "Inglés",
        "pregunta": "Complete: 'I am interested ______ learning French.'",
        "opciones": ["A. on", "B. at", "C. in", "D. for"],
        "respuesta": "C. in",
        "explicacion_ia": "Colocaciones: La expresión correcta es siempre 'Interested IN' (interesado en)."
    },
    {
        "materia": "Inglés",
        "pregunta": "Definition: 'A piece of furniture where you sleep.'",
        "opciones": ["A. Table.", "B. Bed.", "C. Chair.", "D. Desk."],
        "respuesta": "B. Bed.",
        "explicacion_ia": "Muebles: Donde duermes es la cama (Bed)."
    },
    {
        "materia": "Inglés",
        "pregunta": "Conversation: \n- 'How old are you?' \n- '__________'",
        "opciones": ["A. I have 20 years.", "B. I am 20 years old.", "C. I has 20 years.", "D. I am fine."],
        "respuesta": "B. I am 20 years old.",
        "explicacion_ia": "Error común: En inglés la edad NO se 'tiene' (have), se 'es' (am/is/are). La forma correcta es 'I am 20'."
    },
    {
        "materia": "Inglés",
        "pregunta": "Complete: 'He drives very ______.'",
        "opciones": ["A. careful", "B. slow", "C. carefully", "D. good"],
        "respuesta": "C. carefully",
        "explicacion_ia": "Adverbios: Para describir cómo se hace una acción (verbo drive), necesitamos un adverbio (terminado en -ly). 'Carefully' = Cuidadosamente."
    },
    {
        "materia": "Inglés",
        "pregunta": "Vocabulary: 'Monday, Tuesday, Wednesday...' are days of the:",
        "opciones": ["A. Month.", "B. Year.", "C. Week.", "D. Weekend."],
        "respuesta": "C. Week.",
        "explicacion_ia": "Son los días de la semana (Week)."
    },
    {
        "materia": "Inglés",
        "pregunta": "Complete: 'This is the girl ______ lives next door.'",
        "opciones": ["A. which", "B. who", "C. where", "D. whose"],
        "respuesta": "B. who",
        "explicacion_ia": "Pronombres relativos: Para personas (the girl), usamos 'Who'. 'Which' es para cosas."
    },
    {
        "materia": "Inglés",
        "pregunta": "Read: 'Wet Paint'. What does it mean?",
        "opciones": ["A. You can touch the wall.", "B. The paint is dry.", "C. Don't touch, the paint is fresh.", "D. Paint the wall."],
        "respuesta": "C. Don't touch, the paint is fresh.",
        "explicacion_ia": "'Wet Paint' significa 'Pintura fresca/húmeda'. La advertencia es para no mancharse."
    },
    {
        "materia": "Inglés",
        "pregunta": "Complete: 'I usually drink coffee, but today I ______ tea.'",
        "opciones": ["A. drink", "B. am drinking", "C. drank", "D. drinks"],
        "respuesta": "B. am drinking",
        "explicacion_ia": "Contraste de tiempos: 'Usually' va con Presente Simple. 'Today' (una acción temporal ahora) va con Presente Continuo (am drinking)."
    },
    {
        "materia": "Inglés",
        "pregunta": "Definition: 'The opposite of Expensive.'",
        "opciones": ["A. Big.", "B. Cheap.", "C. Cold.", "D. Rich."],
        "respuesta": "B. Cheap.",
        "explicacion_ia": "Antónimos: 'Expensive' es costoso. 'Cheap' es barato."
    },
    {
        "materia": "Inglés",
        "pregunta": "Complete: 'We arrived ______ the airport at 6 PM.'",
        "opciones": ["A. to", "B. in", "C. at", "D. on"],
        "respuesta": "C. at",
        "explicacion_ia": "Preposiciones de lugar: 'Arrive AT' se usa para puntos específicos como aeropuertos o estaciones. 'Arrive IN' para ciudades o países."
    },
    {
        "materia": "Inglés",
        "pregunta": "Vocabulary: A 'Library' is a place where:",
        "opciones": ["A. You buy books.", "B. You borrow and read books.", "C. You dance.", "D. You eat."],
        "respuesta": "B. You borrow and read books.",
        "explicacion_ia": "Como vimos antes, 'Library' es biblioteca (préstamo/lectura), no librería."
    },
    {
        "materia": "Inglés",
        "pregunta": "Complete: 'They didn't ______ to the party.'",
        "opciones": ["A. go", "B. went", "C. gone", "D. going"],
        "respuesta": "A. go",
        "explicacion_ia": "Pasado Negativo: Cuando usas el auxiliar 'didn't', el verbo principal vuelve a su forma base. 'Didn't go' (No 'didn't went')."
    },
    {
        "materia": "Inglés",
        "pregunta": "What time is it? 'It is half past three.'",
        "opciones": ["A. 3:30", "B. 2:30", "C. 3:15", "D. 3:45"],
        "respuesta": "A. 3:30",
        "explicacion_ia": "Hora: 'Half past' significa 'y media'. Half past three = 3:30."
    },
    {
        "materia": "Inglés",
        "pregunta": "Complete: 'I promise I ______ call you tomorrow.'",
        "opciones": ["A. am going to", "B. will", "C. am", "D. have"],
        "respuesta": "B. will",
        "explicacion_ia": "Futuro con Will: Se usa para promesas, decisiones espontáneas o predicciones sin evidencia."
    },
    {
        "materia": "Inglés",
        "pregunta": "Conversation: \n- 'I failed my exam.' \n- '__________'",
        "opciones": ["A. Congratulations!", "B. I am sorry to hear that.", "C. Good luck.", "D. You are welcome."],
        "respuesta": "B. I am sorry to hear that.",
        "explicacion_ia": "Empatía: Si alguien reprueba (failed), lo correcto es expresar lástima o apoyo, no felicitarlo."
    },
    {
        "materia": "Inglés",
        "pregunta": "Which word is a verb?",
        "opciones": ["A. Beautiful.", "B. Quickly.", "C. Run.", "D. House."],
        "respuesta": "C. Run.",
        "explicacion_ia": "Gramática: Beautiful (adjetivo), Quickly (adverbio), House (sustantivo). Run (correr) es una acción, por tanto, un verbo."
    },
    {
        "materia": "Inglés",
        "pregunta": "Complete: 'I have ______ money than you.'",
        "opciones": ["A. less", "B. fewer", "C. little", "D. least"],
        "respuesta": "A. less",
        "explicacion_ia": "Cuantificadores: 'Money' es incontable. Para comparar incontables se usa 'Less' (menos). 'Fewer' es para contables."
    },
    {
        "materia": "Inglés",
        "pregunta": "Definition: 'The meal you eat in the evening.'",
        "opciones": ["A. Breakfast.", "B. Lunch.", "C. Dinner.", "D. Snack."],
        "respuesta": "C. Dinner.",
        "explicacion_ia": "Comidas: La cena (Dinner) es la comida de la noche (evening)."
    },
    {
        "materia": "Inglés",
        "pregunta": "Definition: 'The brother of your mother.'",
        "opciones": ["A. Cousin.", "B. Uncle.", "C. Nephew.", "D. Grandfather."],
        "respuesta": "B. Uncle.",
        "explicacion_ia": "Familia: El hermano de tu mamá es tu tío (Uncle)."
    },
    {
        "materia": "Inglés",
        "pregunta": "Complete: 'I usually ______ up at 6:00 AM.'",
        "opciones": ["A. get", "B. getting", "C. gets", "D. got"],
        "respuesta": "A. get",
        "explicacion_ia": "Presente Simple: Con el sujeto 'I' (yo), el verbo va en su forma base 'get'. 'Gets' es para ella/él."
    },
    {
        "materia": "Sociales y Ciudadanas",
        "pregunta": "¿Qué derecho protege el 'Debido Proceso'?",
        "opciones": ["A. Que los trámites sean rápidos.", "B. Que toda persona sea juzgada conforme a leyes preexistentes y con garantías de defensa.", "C. Que no haya cárcel.", "D. Que los jueces sean elegidos por voto."],
        "respuesta": "B. Que toda persona sea juzgada conforme a leyes preexistentes y con garantías de defensa.",
        "explicacion_ia": "Nadie puede ser condenado sin ser oído y vencido en juicio, con un abogado y bajo leyes que ya existían cuando cometió el acto (Artículo 29 Constitución)."
    },
    {
        "materia": "Lectura Crítica",
        "pregunta": "Si un texto dice: 'El 80% de los encuestados prefiere el producto A', el argumento se basa en:",
        "opciones": ["A. Datos y hechos.", "B. Emociones.", "C. Definiciones.", "D. Citas literarias."],
        "respuesta": "A. Datos y hechos.",
        "explicacion_ia": "Es un argumento racional basado en estadísticas verificables."
    },
    {
        "materia": "Matemáticas",
        "pregunta": "Si el radio de un círculo es r y su diámetro es d, entonces:",
        "opciones": ["A. r = 2d", "B. d = 2r", "C. d = r²", "D. r = d²"],
        "respuesta": "B. d = 2r",
        "explicacion_ia": "El diámetro es la línea que atraviesa el círculo pasando por el centro, y equivale a dos veces el radio."
    },
    {
        "materia": "Ciencias Naturales",
        "pregunta": "¿Qué ocurre si se daña el cerebelo de una persona?",
        "opciones": ["A. Pierde la memoria.", "B. Deja de respirar.", "C. Pierde el equilibrio y la coordinación motora fina.", "D. Pierde la visión."],
        "respuesta": "C. Pierde el equilibrio y la coordinación motora fina.",
        "explicacion_ia": "🧠 Neurociencia: El cerebelo no controla el pensamiento (cerebro) ni la respiración (bulbo raquídeo), se encarga de que los movimientos sean suaves, precisos y del equilibrio."
    },
    {
        "materia": "Sociales y Ciudadanas",
        "pregunta": "¿Qué es la 'Objeción de Conciencia'?",
        "opciones": ["A. Negarse a pagar impuestos.", "B. El derecho a no cumplir una obligación legal si esta contradice profundamente las convicciones morales o religiosas.", "C. Protestar en la calle.", "D. No ir al colegio."],
        "respuesta": "B. El derecho a no cumplir una obligación legal si esta contradice profundamente las convicciones morales o religiosas.",
        "explicacion_ia": "Ejemplo clásico: No prestar servicio militar obligatorio porque tu religión te prohíbe tocar armas. Es un derecho fundamental, pero debe probarse que la creencia es real y profunda."
    },
    {
        "materia": "Lectura Crítica",
        "pregunta": "El oxímoron es una figura literaria que combina dos conceptos opuestos en una sola expresión. Un ejemplo es:",
        "opciones": ["A. 'Correr rápido'.", "B. 'Silencio ensordecedor'.", "C. 'Blanco como la nieve'.", "D. 'El viento susurraba'."],
        "respuesta": "B. 'Silencio ensordecedor'.",
        "explicacion_ia": "El silencio no puede ensordecer (físicamente). Al juntar estos opuestos se crea un sentido poético de un silencio tan profundo que abruma."
    },
    {
        "materia": "Matemáticas",
        "pregunta": "Desde la punta de un faro de 60m de altura, se observa un barco con un ángulo de depresión de 30°. ¿A qué distancia horizontal se encuentra el barco del faro?",
        "opciones": ["A. 60 metros.", "B. 30 metros.", "C. 60√3 metros.", "D. 120 metros."],
        "respuesta": "C. 60√3 metros.",
        "explicacion_ia": "Se forma un triángulo rectángulo. Tan(30°) = Opuesto/Adyacente. Aquí, Tan(30°) = 1/√3. Si usamos el ángulo complementario (60°) en la base: Tan(60°) = x/60 -> x = 60 * √3."
    },
    {
        "materia": "Ciencias Naturales",
        "pregunta": "En una reacción de neutralización entre un ácido fuerte (HCl) y una base fuerte (NaOH), los productos principales son:",
        "opciones": ["A. Sal y Agua.", "B. Gas y Alcohol.", "C. Ácido débil y Base débil.", "D. Óxido y Metal."],
        "respuesta": "A. Sal y Agua.",
        "explicacion_ia": "Es la reacción clásica: Ácido + Base -> Sal + Agua. Ejemplo: HCl + NaOH -> NaCl (Sal de cocina) + H2O."
    },
    {
        "materia": "Sociales y Ciudadanas",
        "pregunta": "Una comunidad vecina a una fábrica de químicos nota que el río huele mal y los peces mueren. Quieren una solución rápida para proteger su derecho a un ambiente sano y evitar un perjuicio irremediable. ¿Qué mecanismo deben usar?",
        "opciones": ["A. Acción de Grupo.", "B. Acción Popular.", "C. Tutela.", "D. Denuncia penal."],
        "respuesta": "C. Tutela.",
        "explicacion_ia": "¡Cáscara! Normalmente los derechos colectivos (ambiente) se protegen con Acción Popular. PERO, si hay un 'perjuicio irremediable' o conexidad con la salud/vida (derechos fundamentales), la Tutela procede como mecanismo transitorio de emergencia."
    },
    {
        "materia": "Lectura Crítica",
        "pregunta": "Filosofía: 'Pienso, luego existo' (Descartes). Esta frase significa que:",
        "opciones": ["A. Pensar es la única actividad humana importante.", "B. La existencia física es una ilusión.", "C. La duda metódica prueba que, al dudar (pensar), confirmo mi propia existencia como sujeto pensante.", "D. Primero existo y después aprendo a pensar."],
        "respuesta": "C. La duda metódica prueba que, al dudar (pensar), confirmo mi propia existencia como sujeto pensante.",
        "explicacion_ia": "Descartes buscaba una verdad indudable. Puede dudar de todo (del mundo, del cuerpo), pero no puede dudar de que está dudando. Si duda, piensa; y si piensa, es algo que existe."
    },
    {
        "materia": "Matemáticas",
        "pregunta": "En una estadística, la 'Desviación Estándar' mide:",
        "opciones": ["A. El valor central de los datos.", "B. Qué tan dispersos o alejados están los datos del promedio.", "C. El dato que más se repite.", "D. El error de la encuesta."],
        "respuesta": "B. Qué tan dispersos o alejados están los datos del promedio.",
        "explicacion_ia": "Una desviación baja significa que los datos están muy juntos (homogéneos). Una alta significa que están muy regados (heterogéneos)."
    },
    {
        "materia": "Ciencias Naturales",
        "pregunta": "Un isótopo es un átomo que tiene:",
        "opciones": ["A. Diferente número de protones.", "B. Diferente número de electrones.", "C. El mismo número de protones pero diferente número de neutrones.", "D. Carga positiva."],
        "respuesta": "C. El mismo número de protones pero diferente número de neutrones.",
        "explicacion_ia": "Isótopo = Mismo lugar en la tabla periódica (mismo elemento/protones), pero diferente masa atómica (neutrones). Ejemplo: Carbono-12 y Carbono-14."
    },
    {
        "materia": "Sociales y Ciudadanas",
        "pregunta": "El 'Estado de Excepción' (antes Estado de Sitio) permite al Presidente:",
        "opciones": ["A. Cerrar el Congreso para siempre.", "B. Emitir decretos con fuerza de ley temporalmente para afrontar una crisis grave.", "C. Cambiar la Constitución.", "D. Juzgar a los ciudadanos como si fuera un juez."],
        "respuesta": "B. Emitir decretos con fuerza de ley temporalmente para afrontar una crisis grave.",
        "explicacion_ia": "Es una figura constitucional para emergencias (guerra, conmoción interior, emergencia económica). Tiene límites y control automático de la Corte Constitucional."
    },
    {
        "materia": "Lectura Crítica",
        "pregunta": "En el enunciado 'El novelista no es un historiador, pero es un testigo de su tiempo', se plantea una relación de:",
        "opciones": ["A. Identidad entre historia y novela.", "B. Contradicción total.", "C. Complementariedad desde la ficción.", "D. Superoridad de la novela."],
        "respuesta": "C. Complementariedad desde la ficción.",
        "explicacion_ia": "Aunque no narra hechos científicos (historiador), el novelista captura la esencia, costumbres y sentir de una época (testigo), complementando la visión histórica."
    },
    {
        "materia": "Matemáticas",
        "pregunta": "Si f(x) = 2x + 3. ¿Cuál es el valor de f(x+1)?",
        "opciones": ["A. 2x + 4", "B. 2x + 5", "C. 2x + 1", "D. 3x + 3"],
        "respuesta": "B. 2x + 5",
        "explicacion_ia": "Reemplazamos la 'x' por '(x+1)'. \nf(x+1) = 2(x+1) + 3 \n= 2x + 2 + 3 \n= 2x + 5."
    },
    {
        "materia": "Ciencias Naturales",
        "pregunta": "¿Qué ley de Mendel explica que los alelos se separan durante la formación de gametos?",
        "opciones": ["A. Ley de la Uniformidad.", "B. Ley de la Segregación Independiente.", "C. Ley de la Inercia.", "D. Ley de la Segregación."],
        "respuesta": "D. Ley de la Segregación.",
        "explicacion_ia": "La segunda ley de Mendel (Segregación) dice que cada individuo tiene un par de alelos para cada rasgo, y estos se segregan (separan) al formar óvulos o espermatozoides."
    },
    {
        "materia": "Sociales y Ciudadanas",
        "pregunta": "¿Qué es la 'Plusvalía' en el marxismo?",
        "opciones": ["A. El impuesto que se paga por tener casa.", "B. El valor extra que genera el trabajador con su labor y que se apropia el dueño del capital.", "C. El aumento de precio de la tierra.", "D. Un subsidio del estado."],
        "respuesta": "B. El valor extra que genera el trabajador con su labor y que se apropia el dueño del capital.",
        "explicacion_ia": "Es el concepto central de la explotación capitalista según Marx: el obrero produce más valor del que recibe en su salario; la diferencia es la ganancia del patrón."
    },
    {
        "materia": "Lectura Crítica",
        "pregunta": "Identifique el error de coherencia en: 'El niño subió arriba a buscar su juguete'.",
        "opciones": ["A. Solecismo.", "B. Pleonasmo.", "C. Cacofonía.", "D. Barbarismo."],
        "respuesta": "B. Pleonasmo.",
        "explicacion_ia": "Pleonasmo es el uso de palabras innecesarias. 'Subir' ya implica ir hacia 'arriba'. Es redundante."
    },
    {
        "materia": "Matemáticas",
        "pregunta": "Una población de bacterias se duplica cada hora. Si empieza con 100 bacterias, ¿cuántas habrá en 5 horas?",
        "opciones": ["A. 500", "B. 1600", "C. 3200", "D. 6400"],
        "respuesta": "C. 3200",
        "explicacion_ia": "Es crecimiento exponencial: 100 * 2^5. \n1h: 200, 2h: 400, 3h: 800, 4h: 1600, 5h: 3200."
    },
    {
        "materia": "Ciencias Naturales",
        "pregunta": "En un circuito eléctrico, según la Ley de Ohm, si aumentas la resistencia manteniendo el voltaje igual, ¿qué pasa con la corriente?",
        "opciones": ["A. Aumenta.", "B. Disminuye.", "C. Se mantiene igual.", "D. Se vuelve cero."],
        "respuesta": "B. Disminuye.",
        "explicacion_ia": "I = V/R. La corriente (I) es inversamente proporcional a la resistencia (R). Si hay más resistencia (oposición), pasa menos corriente."
    },
    {
        "materia": "Sociales y Ciudadanas",
        "pregunta": "La 'Descentralización Administrativa' en Colombia implica que:",
        "opciones": ["A. El país se divide en países más pequeños.", "B. Se transfieren funciones y recursos del gobierno central a municipios y departamentos para que se autogestionen.", "C. Se elimina la figura del Alcalde.", "D. Todo se decide en Bogotá."],
        "respuesta": "B. Se transfieren funciones y recursos del gobierno central a municipios y departamentos para que se autogestionen.",
        "explicacion_ia": "Busca que las regiones tengan autonomía para manejar sus propios problemas (salud, educación local), aunque sigan perteneciendo a un Estado unitario."
    },
    {
        "materia": "Lectura Crítica",
        "pregunta": "En un texto, la palabra 'Sin embargo' funciona como:",
        "opciones": ["A. Un conector de adición.", "B. Un conector de causa.", "C. Un conector de oposición o contraste.", "D. Un conector temporal."],
        "respuesta": "C. Un conector de oposición o contraste.",
        "explicacion_ia": "Introduce una idea que se opone o limita a la anterior. Ejemplo: 'Estudió mucho, sin embargo, perdió'."
    },
    {
        "materia": "Matemáticas",
        "pregunta": "¿Cuál es la probabilidad de sacar un As o un Rey de una baraja de 52 cartas?",
        "opciones": ["A. 1/13", "B. 2/13", "C. 8/52", "D. 4/52"],
        "respuesta": "B. 2/13",
        "explicacion_ia": "Hay 4 Ases y 4 Reyes. Total casos favorables = 8. Total cartas = 52. Probabilidad = 8/52. Simplificando (dividiendo por 4 arriba y abajo) = 2/13."
    },
    {
        "materia": "Ciencias Naturales",
        "pregunta": "¿Qué molécula lleva la información genética desde el núcleo hasta el ribosoma para fabricar proteínas?",
        "opciones": ["A. ADN.", "B. ARN mensajero (ARNm).", "C. ARN de transferencia (ARNt).", "D. Proteína."],
        "respuesta": "B. ARN mensajero (ARNm).",
        "explicacion_ia": "El ADN no sale del núcleo. Se transcribe a ARNm (mensajero), el cual sí sale al citoplasma y lleva el 'código' al ribosoma."
    },
    {
        "materia": "Sociales y Ciudadanas",
        "pregunta": "El conflicto armado en Colombia se ha financiado históricamente mediante:",
        "opciones": ["A. Impuestos legales.", "B. Narcotráfico, secuestro y extorsión.", "C. Donaciones internacionales.", "D. La venta de café."],
        "respuesta": "B. Narcotráfico, secuestro y extorsión.",
        "explicacion_ia": "Son las economías ilegales las que han permitido a los grupos armados sostener su guerra por más de 50 años."
    },
    {
        "materia": "Lectura Crítica",
        "pregunta": "¿Qué es una 'falacia de falsa equivalencia'?",
        "opciones": ["A. Mentir sobre datos.", "B. Presentar dos situaciones como iguales cuando en realidad son muy diferentes en magnitud o calidad.", "C. Insultar al oponente.", "D. Cambiar de tema."],
        "respuesta": "B. Presentar dos situaciones como iguales cuando en realidad son muy diferentes en magnitud o calidad.",
        "explicacion_ia": "Ejemplo: Decir que 'robar un pan por hambre es igual de grave que robar millones del erario público'. Ambos son delitos, pero no son equivalentes moral ni socialmente."
    },
    {
        "materia": "Matemáticas",
        "pregunta": "Si el lado de un cubo aumenta en un 50%, ¿en qué porcentaje aumenta su volumen?",
        "opciones": ["A. 50%", "B. 150%", "C. 237.5%", "D. 337.5%"],
        "respuesta": "C. 237.5%",
        "explicacion_ia": "Lado original = 1. Volumen = 1. Nuevo lado = 1.5. Nuevo volumen = 1.5³ = 3.375. El aumento es 3.375 - 1 = 2.375. En porcentaje es 237.5%."
    },
    {
        "materia": "Ciencias Naturales",
        "pregunta": "La eutrofización de un lago se produce por:",
        "opciones": ["A. Falta de nutrientes.", "B. Exceso de nutrientes (nitratos/fosfatos) que genera crecimiento desmedido de algas y agota el oxígeno.", "C. Enfriamiento del agua.", "D. Exceso de peces."],
        "respuesta": "B. Exceso de nutrientes (nitratos/fosfatos) que genera crecimiento desmedido de algas y agota el oxígeno.",
        "explicacion_ia": "Es contaminación común por fertilizantes. Las algas cubren la superficie, no entra luz, las plantas de fondo mueren, las bacterias las descomponen gastando todo el oxígeno y los peces mueren."
    },
    {
        "materia": "Sociales y Ciudadanas",
        "pregunta": "¿Cuál es la diferencia entre Derechos Humanos y Derecho Internacional Humanitario (DIH)?",
        "opciones": ["A. Son lo mismo.", "B. Los DD.HH. aplican siempre; el DIH solo aplica en conflictos armados (guerra).", "C. Los DD.HH. son para civiles y el DIH para militares.", "D. El DIH es para animales."],
        "respuesta": "B. Los DD.HH. aplican siempre; el DIH solo aplica en conflictos armados (guerra).",
        "explicacion_ia": "El DIH son las 'reglas de la guerra' (Convenios de Ginebra) para proteger a quienes no combaten y limitar métodos de guerra. Los DD.HH. aplican en paz y guerra."
    },
    {
        "materia": "Lectura Crítica",
        "pregunta": "Texto: 'Vendo zapatos de bebé, sin usar'. (Hemingway). Este es un ejemplo de:",
        "opciones": ["A. Un aviso clasificado sin valor literario.", "B. Un microrrelato o microcuento.", "C. Una novela larga.", "D. Un poema épico."],
        "respuesta": "B. Un microrrelato o microcuento.",
        "explicacion_ia": "Con solo 6 palabras, cuenta una historia trágica completa (el bebé murió o no nació), invitando al lector a completar la información. Es una obra maestra de la elipsis."
    },
    {
        "materia": "Matemáticas",
        "pregunta": "¿Cuánto es la mitad de 2 elevado a la 50?",
        "opciones": ["A. 2 elevado a la 25.", "B. 1 elevado a la 50.", "C. 2 elevado a la 49.", "D. 2 elevado a la 49.5"],
        "respuesta": "C. 2 elevado a la 49.",
        "explicacion_ia": "Propiedades de potencias: (2^50) / 2 = (2^50) / (2^1). Se restan los exponentes: 50 - 1 = 49. Resultado: 2^49."
    },
    {
        "materia": "Ciencias Naturales",
        "pregunta": "En una caída libre (sin aire), la energía mecánica total:",
        "opciones": ["A. Aumenta.", "B. Disminuye.", "C. Se conserva constante.", "D. Depende de la masa."],
        "respuesta": "C. Se conserva constante.",
        "explicacion_ia": "La energía potencial se transforma en cinética, pero la suma de ambas (Mecánica) permanece constante si no hay fricción."
    },
    {
        "materia": "Sociales y Ciudadanas",
        "pregunta": "El 'Control Político' en Colombia lo ejerce principalmente:",
        "opciones": ["A. El Presidente a los Ministros.", "B. El Congreso a la Rama Ejecutiva (Ministros/Directores) para verificar sus acciones.", "C. La Policía a los ciudadanos.", "D. Los jueces a los ladrones."],
        "respuesta": "B. El Congreso a la Rama Ejecutiva (Ministros/Directores) para verificar sus acciones.",
        "explicacion_ia": "El Congreso puede citar a Ministros a debates y, si su gestión es pésima, votar una Moción de Censura para sacarlos del cargo."
    },
    {
        "materia": "Lectura Crítica",
        "pregunta": "Si un texto defiende la idea de que 'La tecnología nos aísla', un contraargumento válido sería:",
        "opciones": ["A. La tecnología es cara.", "B. Las redes sociales permiten mantener contacto con familiares que viven en otros continentes.", "C. Antes la gente hablaba más.", "D. Los celulares dañan la vista."],
        "respuesta": "B. Las redes sociales permiten mantener contacto con familiares que viven en otros continentes.",
        "explicacion_ia": "Un contraargumento ataca la tesis central. Si la tesis es 'aislamiento', el ejemplo de 'conexión a distancia' demuestra que la tecnología también puede unir."
    },
    {
        "materia": "Matemáticas",
        "pregunta": "Un reloj se atrasa 2 minutos cada hora. Si se sincroniza a las 12:00 del día, ¿qué hora marcará cuando sean las 12:00 del día siguiente (real)?",
        "opciones": ["A. 11:12 AM", "B. 11:36 AM", "C. 12:48 PM", "D. 11:12 PM"],
        "respuesta": "A. 11:12 AM",
        "explicacion_ia": "Han pasado 24 horas. Se atrasa 2 min/h * 24 h = 48 minutos de atraso total. 12:00 - 48 minutos = 11:12 AM."
    },
    {
        "materia": "Ciencias Naturales",
        "pregunta": "¿Qué tipo de enlace químico une a los átomos en una molécula de agua (H2O)?",
        "opciones": ["A. Iónico.", "B. Covalente polar.", "C. Metálico.", "D. Puente de hidrógeno."],
        "respuesta": "B. Covalente polar.",
        "explicacion_ia": "Dentro de la molécula, el oxígeno y el hidrógeno comparten electrones (covalente), pero el oxígeno los atrae más fuerte, creando polos (polar). Los Puentes de Hidrógeno unen moléculas DISTINTAS, no los átomos de la misma molécula."
    },
    {
        "materia": "Ciencias Naturales",
        "pregunta": "Un sonido se propaga por el aire. Si aumenta la frecuencia de la onda sonora, ¿qué sucede con su tono?",
        "opciones": ["A. Se vuelve más grave.", "B. Se vuelve más agudo.", "C. Aumenta su volumen (intensidad).", "D. Viaja más rápido."],
        "respuesta": "B. Se vuelve más agudo.",
        "explicacion_ia": "🎶 Física de Ondas: El tono depende de la frecuencia. Alta frecuencia = Tono Agudo (chillido). Baja frecuencia = Tono Grave (voz ronca). El volumen depende de la amplitud, no de la frecuencia."
    },
    {
        "materia": "Matemáticas",
        "pregunta": "En una caja hay 5 bolas rojas y 3 azules. Se saca una bola y NO se devuelve a la caja. Luego se saca una segunda bola. ¿Cuál es la probabilidad de que ambas sean rojas?",
        "opciones": ["A. 25/64", "B. 5/14", "C. 20/56", "D. 1/2"],
        "respuesta": "B. 5/14",
        "explicacion_ia": "🎲 Probabilidad Sin Reemplazo: \n1ª bola roja: 5/8. \nComo no la devuelves, quedan 4 rojas y 7 bolas totales. \n2ª bola roja: 4/7. \nMultiplicamos: (5/8) * (4/7) = 20/56. Simplificando (dividiendo por 4) = 5/14."
    },
    {
        "materia": "Sociales y Ciudadanas",
        "pregunta": "El 'Clientelismo' es una práctica política corrupta que consiste en:",
        "opciones": ["A. Tratar al ciudadano como un cliente de una empresa.", "B. El intercambio de favores (puestos, contratos, tejas) por votos.", "C. La privatización de empresas públicas.", "D. La protección del consumidor."],
        "respuesta": "B. El intercambio de favores (puestos, contratos, tejas) por votos.",
        "explicacion_ia": "Es una relación transaccional donde el político usa recursos del Estado para 'comprar' lealtades y votos, en lugar de ganar elecciones por propuestas o mérito."
    },
    {
        "materia": "Lectura Crítica",
        "pregunta": "Lea: 'El mapa no es el territorio'. Esta frase de Alfred Korzybski implica que:",
        "opciones": ["A. Los mapas siempre están mal dibujados.", "B. Nuestra representación de la realidad (lenguaje/pensamiento) no es la realidad misma, es solo una abstracción.", "C. Debemos viajar más para conocer el territorio real.", "D. La geografía es una ciencia inexacta."],
        "respuesta": "B. Nuestra representación de la realidad (lenguaje/pensamiento) no es la realidad misma, es solo una abstracción.",
        "explicacion_ia": "🧠 Epistemología: Significa que confundimos la realidad con lo que pensamos o decimos de ella. Las palabras y modelos son solo guías limitadas, no la verdad absoluta."
    },
    {
        "materia": "Matemáticas",
        "pregunta": "Si un pantalón sube de precio un 20% y luego, en rebajas, baja un 20% sobre el nuevo precio. ¿Cómo queda el precio final comparado con el original?",
        "opciones": ["A. Queda igual.", "B. Queda un 4% más barato.", "C. Queda un 4% más caro.", "D. Queda un 1% más barato."],
        "respuesta": "B. Queda un 4% más barato.",
        "explicacion_ia": "Ejemplo con $100: Sube 20% -> $120. Baja 20% de 120 (que es $24) -> 120 - 24 = $96. Pasó de 100 a 96. Bajó un 4%."
    },
    {
        "materia": "Ciencias Naturales",
        "pregunta": "En química orgánica, ¿qué elemento es la base fundamental de todas las moléculas de la vida?",
        "opciones": ["A. Oxígeno.", "B. Carbono.", "C. Silicio.", "D. Hidrógeno."],
        "respuesta": "B. Carbono.",
        "explicacion_ia": "El Carbono tiene la capacidad única de formar 4 enlaces covalentes estables, permitiendo crear cadenas largas y complejas (ADN, proteínas, grasas) necesarias para la vida."
    },
    {
        "materia": "Sociales y Ciudadanas",
        "pregunta": "¿Qué diferencia hay entre 'Nación' y 'Estado'?",
        "opciones": ["A. Son sinónimos.", "B. Nación es el conjunto de personas con identidad cultural común; Estado es la organización política y jurídica (instituciones).", "C. Nación es el territorio y Estado es la gente.", "D. Nación son los ricos y Estado los pobres."],
        "respuesta": "B. Nación es el conjunto de personas con identidad cultural común; Estado es la organización política y jurídica (instituciones).",
        "explicacion_ia": "Puede haber naciones sin Estado (como los Kurdos) y Estados con varias naciones (Plurinacionales). El Estado es la estructura de poder (leyes, policía, gobierno)."
    },
    {
        "materia": "Lectura Crítica",
        "pregunta": "En la oración: 'El hombre es un lobo para el hombre', Thomas Hobbes utiliza una metáfora para expresar que:",
        "opciones": ["A. Los hombres descienden de los lobos.", "B. El ser humano es sociable y amable por naturaleza.", "C. En estado natural, el ser humano es egoísta y agresivo con sus semejantes para sobrevivir.", "D. Debemos proteger a los lobos."],
        "respuesta": "C. En estado natural, el ser humano es egoísta y agresivo con sus semejantes para sobrevivir.",
        "explicacion_ia": "Hobbes justifica la necesidad de un Gobierno fuerte (Leviatán) para controlar ese instinto salvaje y evitar la guerra de todos contra todos."
    },
    {
        "materia": "Matemáticas",
        "pregunta": "¿Cuál es el dominio de la función f(x) = 1/x?",
        "opciones": ["A. Todos los números reales.", "B. Todos los reales excepto el 0.", "C. Solo los números positivos.", "D. Solo los números enteros."],
        "respuesta": "B. Todos los reales excepto el 0.",
        "explicacion_ia": "No se puede dividir por cero. Por lo tanto, x puede tomar cualquier valor menos el 0, ya que 1/0 es una indeterminación."
    },
    {
        "materia": "Ciencias Naturales",
        "pregunta": "Si un cuerpo se mueve con Movimiento Rectilíneo Uniforme (MRU), significa que:",
        "opciones": ["A. Su velocidad cambia constantemente.", "B. Su aceleración es constante y positiva.", "C. Su velocidad es constante y su aceleración es cero.", "D. Se mueve en círculos."],
        "respuesta": "C. Su velocidad es constante y su aceleración es cero.",
        "explicacion_ia": "En MRU recorre distancias iguales en tiempos iguales. Al no cambiar la velocidad (ni en magnitud ni dirección), no hay aceleración."
    },
    {
        "materia": "Sociales y Ciudadanas",
        "pregunta": "La 'Consulta Previa' es un derecho fundamental de:",
        "opciones": ["A. Los empresarios antes de pagar impuestos.", "B. Las comunidades indígenas y afrodescendientes antes de que se realicen proyectos que afecten sus territorios.", "C. Los estudiantes antes de un examen.", "D. Los congresistas antes de votar."],
        "respuesta": "B. Las comunidades indígenas y afrodescendientes antes de que se realicen proyectos que afecten sus territorios.",
        "explicacion_ia": "El Estado debe consultarles si aceptan que pase una carretera o se haga minería en su tierra ancestral, garantizando su supervivencia cultural."
    },
    {
        "materia": "Lectura Crítica",
        "pregunta": "Identifique la tesis en: 'Aunque los videojuegos violentos son criticados, estudios sugieren que pueden mejorar los reflejos y la toma de decisiones rápidas bajo presión'.",
        "opciones": ["A. Los videojuegos son malos.", "B. Los videojuegos violentos tienen beneficios cognitivos específicos.", "C. Jugar videojuegos causa presión alta.", "D. Todos deberían jugar."],
        "respuesta": "B. Los videojuegos violentos tienen beneficios cognitivos específicos.",
        "explicacion_ia": "La oración concesiva ('Aunque...') introduce el contraargumento, pero la cláusula principal defiende los beneficios (reflejos, decisión). Esa es la postura."
    },
    {
        "materia": "Matemáticas",
        "pregunta": "En un restaurante hay 3 opciones de entrada, 4 de plato fuerte y 2 de postre. ¿Cuántos menús diferentes se pueden armar?",
        "opciones": ["A. 9", "B. 12", "C. 24", "D. 14"],
        "respuesta": "C. 24",
        "explicacion_ia": "Principio multiplicativo: 3 x 4 x 2 = 24 combinaciones posibles."
    },
    {
        "materia": "Ciencias Naturales",
        "pregunta": "¿Qué gas se libera como producto de la fotosíntesis?",
        "opciones": ["A. Dióxido de carbono (CO2).", "B. Metano (CH4).", "C. Oxígeno (O2).", "D. Nitrógeno (N2)."],
        "respuesta": "C. Oxígeno (O2).",
        "explicacion_ia": "Las plantas toman CO2 y Agua, y con la luz solar producen Glucosa (comida) y liberan Oxígeno como desecho (afortunadamente para nosotros)."
    },
    {
        "materia": "Sociales y Ciudadanas",
        "pregunta": "¿Qué fue el 'Apartheid'?",
        "opciones": ["A. Un festival de música en Alemania.", "B. Un sistema de segregación racial legalizado en Sudáfrica.", "C. Un tratado de paz en Medio Oriente.", "D. Un partido político en Colombia."],
        "respuesta": "B. Un sistema de segregación racial legalizado en Sudáfrica.",
        "explicacion_ia": "Fue un régimen donde la minoría blanca tenía todos los derechos y la mayoría negra estaba marginada y separada, hasta que líderes como Nelson Mandela lograron abolirlo en los 90s."
    },
    {
        "materia": "Lectura Crítica",
        "pregunta": "Si un texto habla sobre 'Las ventajas de la energía nuclear' y solo presenta datos positivos ignorando los riesgos, podemos decir que el texto es:",
        "opciones": ["A. Objetivo.", "B. Sesgado o parcializado.", "C. Completo.", "D. Ficticio."],
        "respuesta": "B. Sesgado o parcializado.",
        "explicacion_ia": "El sesgo ocurre cuando se muestra solo una cara de la moneda para favorecer una postura, ocultando la información que la contradice."
    },
    {
        "materia": "Matemáticas",
        "pregunta": "¿Cuál es el volumen de un cubo de lado 3 cm?",
        "opciones": ["A. 9 cm³", "B. 18 cm³", "C. 27 cm³", "D. 81 cm³"],
        "respuesta": "C. 27 cm³",
        "explicacion_ia": "Volumen = Lado x Lado x Lado (L³). 3 x 3 x 3 = 27."
    },
    {
        "materia": "Ciencias Naturales",
        "pregunta": "La ley de la gravedad de Newton establece que la fuerza de atracción entre dos cuerpos depende de:",
        "opciones": ["A. Solo de sus masas.", "B. Solo de la distancia.", "C. Directamente de las masas e inversamente del cuadrado de la distancia.", "D. De su temperatura."],
        "respuesta": "C. Directamente de las masas e inversamente del cuadrado de la distancia.",
        "explicacion_ia": "Más masa = Más atracción. Más lejos = Menos atracción (pero disminuye muy rápido, al cuadrado)."
    },
    {
        "materia": "Sociales y Ciudadanas",
        "pregunta": "¿Cuál es la capital del departamento del Chocó?",
        "opciones": ["A. Quibdó.", "B. Buenaventura.", "C. Tumaco.", "D. Mocoa."],
        "respuesta": "A. Quibdó.",
        "explicacion_ia": "Geografía de Colombia: Quibdó es la capital del Chocó, departamento en la región del Pacífico."
    },
    {
        "materia": "Lectura Crítica",
        "pregunta": "En la frase: 'Le costó un ojo de la cara', la función del lenguaje es:",
        "opciones": ["A. Referencial (informa un dato médico).", "B. Expresiva o emotiva (comunica exageración/sentimiento).", "C. Metalingüística.", "D. Fática."],
        "respuesta": "B. Expresiva o emotiva (comunica exageración/sentimiento).",
        "explicacion_ia": "Es una hipérbole (exageración) para expresar que algo fue extremadamente costoso, no literalmente que perdió un ojo."
    },
    {
        "materia": "Matemáticas",
        "pregunta": "En una tienda, una camisa cuesta $80.000. Si le aplican un descuento del 25%, ¿cuánto dinero se ahorra el comprador?",
        "opciones": ["A. $10.000", "B. $20.000", "C. $25.000", "D. $60.000"],
        "respuesta": "B. $20.000",
        "explicacion_ia": "El 25% es la cuarta parte de algo (100/4 = 25). La cuarta parte de 80.000 es 20.000. Ese es el ahorro."
    },
    {
        "materia": "Ciencias Naturales",
        "pregunta": "La fotosíntesis es el proceso mediante el cual las plantas producen su alimento. ¿Qué gas necesitan tomar del aire para realizar este proceso?",
        "opciones": ["A. Oxígeno (O2).", "B. Nitrógeno (N2).", "C. Dióxido de Carbono (CO2).", "D. Helio (He)."],
        "respuesta": "C. Dióxido de Carbono (CO2).",
        "explicacion_ia": "Las plantas absorben CO2 y agua, y con la energía del sol los transforman en glucosa y liberan oxígeno."
    },
    {
        "materia": "Sociales y Ciudadanas",
        "pregunta": "¿Qué mecanismo protege el derecho fundamental a la salud cuando una EPS niega un medicamento vital?",
        "opciones": ["A. Derecho de Petición.", "B. Acción de Tutela.", "C. Denuncia ante la Fiscalía.", "D. Queja en el buzón de sugerencias."],
        "respuesta": "B. Acción de Tutela.",
        "explicacion_ia": "La Tutela es el mecanismo rey para proteger derechos fundamentales (como la vida y la salud) de manera inmediata (máximo 10 días)."
    },
    {
        "materia": "Lectura Crítica",
        "pregunta": "En la frase 'Es un volcán de pasiones', la figura literaria empleada es:",
        "opciones": ["A. Símil.", "B. Metáfora.", "C. Hipérbole.", "D. Anáfora."],
        "respuesta": "B. Metáfora.",
        "explicacion_ia": "Se sustituye el término real (persona muy emocional) por uno imaginario (volcán) sin usar la palabra 'como'."
    },
    {
        "materia": "Matemáticas",
        "pregunta": "¿Cuál es el siguiente número en la secuencia: 1, 1, 2, 3, 5, 8, ...?",
        "opciones": ["A. 10", "B. 11", "C. 13", "D. 12"],
        "respuesta": "C. 13",
        "explicacion_ia": "Es la sucesión de Fibonacci. Cada número es la suma de los dos anteriores. 5 + 8 = 13."
    },
    {
        "materia": "Ciencias Naturales",
        "pregunta": "¿Cuál es la función de los glóbulos rojos en la sangre?",
        "opciones": ["A. Defender al cuerpo de virus.", "B. Transportar oxígeno a los tejidos.", "C. Coagular la sangre.", "D. Filtrar la orina."],
        "respuesta": "B. Transportar oxígeno a los tejidos.",
        "explicacion_ia": "Los glóbulos rojos contienen hemoglobina, que se une al oxígeno en los pulmones y lo lleva a todas las células."
    },
    {
        "materia": "Sociales y Ciudadanas",
        "pregunta": "La 'Revolución Industrial' trajo consigo:",
        "opciones": ["A. La invención de la agricultura.", "B. El paso de la producción manual a la producción mecanizada en fábricas.", "C. La caída del Imperio Romano.", "D. El descubrimiento de América."],
        "respuesta": "B. El paso de la producción manual a la producción mecanizada en fábricas.",
        "explicacion_ia": "Inició en el siglo XVIII con la máquina de vapor, transformando la economía agraria en industrial y urbana."
    },
    {
        "materia": "Lectura Crítica",
        "pregunta": "Si un texto argumentativo defiende que 'Fumar debe prohibirse en parques', un argumento a favor sería:",
        "opciones": ["A. El humo afecta la salud de los niños que juegan allí (fumadores pasivos).", "B. Los cigarrillos son caros.", "C. A los fumadores les relaja fumar.", "D. Los parques son verdes."],
        "respuesta": "A. El humo afecta la salud de los niños que juegan allí (fumadores pasivos).",
        "explicacion_ia": "Es un argumento de salud pública y protección a terceros, lo cual es válido para justificar una prohibición en espacio público."
    },
    {
        "materia": "Matemáticas",
        "pregunta": "Si x + 5 = 12, entonces 2x es igual a:",
        "opciones": ["A. 7", "B. 14", "C. 24", "D. 10"],
        "respuesta": "B. 14",
        "explicacion_ia": "Primero despejamos x: x = 12 - 5 -> x = 7. Luego hallamos 2x: 2 * 7 = 14."
    },
    {
        "materia": "Ciencias Naturales",
        "pregunta": "La evaporación del agua es un cambio:",
        "opciones": ["A. Químico.", "B. Físico.", "C. Nuclear.", "D. Biológico."],
        "respuesta": "B. Físico.",
        "explicacion_ia": "Sigue siendo agua (H2O), solo cambió su estado de líquido a gas. No se formó una sustancia nueva."
    },
    {
        "materia": "Sociales y Ciudadanas",
        "pregunta": "¿Qué es la 'Rama Legislativa' en Colombia?",
        "opciones": ["A. El Presidente y sus ministros.", "B. El Congreso (Senado y Cámara) encargado de hacer las leyes.", "C. Los Jueces y Fiscales.", "D. La Policía y el Ejército."],
        "respuesta": "B. El Congreso (Senado y Cámara) encargado de hacer las leyes.",
        "explicacion_ia": "Su función principal es legislar (hacer leyes) y ejercer control político sobre el gobierno."
    },
    {
        "materia": "Lectura Crítica",
        "pregunta": "En el refrán 'Más vale pájaro en mano que cien volando', la idea implícita es:",
        "opciones": ["A. Hay que cazar pájaros.", "B. Es mejor tener algo seguro, aunque sea poco, que arriesgarse por algo mucho mejor pero incierto.", "C. Los pájaros vuelan muy rápido.", "D. No hay que ser ambicioso."],
        "respuesta": "B. Es mejor tener algo seguro, aunque sea poco, que arriesgarse por algo mucho mejor pero incierto.",
        "explicacion_ia": "Valora la seguridad y la certeza sobre el riesgo desmedido."
    },
    {
        "materia": "Matemáticas",
        "pregunta": "¿Cuál es el área de un triángulo de base 4 cm y altura 5 cm?",
        "opciones": ["A. 20 cm²", "B. 10 cm²", "C. 9 cm²", "D. 40 cm²"],
        "respuesta": "B. 10 cm²",
        "explicacion_ia": "Fórmula: Área = (Base * Altura) / 2. A = (4 * 5) / 2 = 20 / 2 = 10."
    },
    {
        "materia": "Ciencias Naturales",
        "pregunta": "¿Qué órgano del cuerpo humano filtra la sangre y produce orina?",
        "opciones": ["A. Hígado.", "B. Páncreas.", "C. Riñones.", "D. Vejiga."],
        "respuesta": "C. Riñones.",
        "explicacion_ia": "Los riñones eliminan los desechos y el exceso de líquido del cuerpo a través de la orina."
    },
    {
        "materia": "Sociales y Ciudadanas",
        "pregunta": "El 'Bogotazo' fue consecuencia del asesinato de:",
        "opciones": ["A. Simón Bolívar.", "B. Jorge Eliécer Gaitán.", "C. Luis Carlos Galán.", "D. Gustavo Rojas Pinilla."],
        "respuesta": "B. Jorge Eliécer Gaitán.",
        "explicacion_ia": "Ocurrió el 9 de abril de 1948 y desató una ola de violencia partidista en todo el país."
    },
    {
        "materia": "Lectura Crítica",
        "pregunta": "¿Qué es una 'hipérbole'?",
        "opciones": ["A. Una comparación.", "B. Una exageración evidente para dar énfasis.", "C. Un sonido repetitivo.", "D. Una contradicción."],
        "respuesta": "B. Una exageración evidente para dar énfasis.",
        "explicacion_ia": "Ejemplo: 'Te he llamado mil veces'. No fueron mil, pero se exagera para mostrar insistencia."
    },
    {
        "materia": "Matemáticas",
        "pregunta": "Si lanzas un dado, ¿cuál es la probabilidad de sacar un número mayor a 4?",
        "opciones": ["A. 1/6", "B. 1/3", "C. 1/2", "D. 2/3"],
        "respuesta": "B. 1/3",
        "explicacion_ia": "Los números mayores a 4 son el 5 y el 6. Son 2 casos favorables de 6 posibles. 2/6 se simplifica a 1/3."
    },
    {
        "materia": "Ciencias Naturales",
        "pregunta": "La 'Ley de la Inercia' establece que:",
        "opciones": ["A. Todo objeto tiende a mantener su estado de reposo o movimiento a menos que una fuerza actúe sobre él.", "B. La fuerza es igual a masa por aceleración.", "C. A toda acción corresponde una reacción.", "D. La energía se conserva."],
        "respuesta": "A. Todo objeto tiende a mantener su estado de reposo o movimiento a menos que una fuerza actúe sobre él.",
        "explicacion_ia": "Es la Primera Ley de Newton. Por eso te vas hacia adelante cuando el bus frena de golpe."
    },
    {
        "materia": "Sociales y Ciudadanas",
        "pregunta": "¿Cuál es la capital del departamento del Amazonas?",
        "opciones": ["A. Florencia.", "B. Mocoa.", "C. Leticia.", "D. Mitú."],
        "respuesta": "C. Leticia.",
        "explicacion_ia": "Leticia es el puerto colombiano sobre el río Amazonas, en el extremo sur del país."
    },
    {
        "materia": "Lectura Crítica",
        "pregunta": "En un texto, los conectores como 'porque', 'debido a', 'ya que', indican una relación de:",
        "opciones": ["A. Consecuencia.", "B. Causa.", "C. Oposición.", "D. Tiempo."],
        "respuesta": "B. Causa.",
        "explicacion_ia": "Introducen la razón o el motivo de lo que se dijo antes. 'No fui porque llovió' (la lluvia es la causa)."
    },
    {
        "materia": "Matemáticas",
        "pregunta": "¿Cuánto suman los ángulos internos de un cuadrado?",
        "opciones": ["A. 180 grados.", "B. 360 grados.", "C. 90 grados.", "D. 270 grados."],
        "respuesta": "B. 360 grados.",
        "explicacion_ia": "Un cuadrado tiene 4 ángulos rectos (90°). 90 * 4 = 360. Cualquier cuadrilátero suma 360°."
    },
    {
        "materia": "Ciencias Naturales",
        "pregunta": "¿Qué tipo de carga tiene un electrón?",
        "opciones": ["A. Positiva.", "B. Negativa.", "C. Neutra.", "D. No tiene carga."],
        "respuesta": "B. Negativa.",
        "explicacion_ia": "Los electrones son partículas subatómicas con carga negativa que orbitan el núcleo."
    },
    {
        "materia": "Sociales y Ciudadanas",
        "pregunta": "La Constitución de 1991 define a Colombia como un Estado:",
        "opciones": ["A. Federal.", "B. Monárquico.", "C. Social de Derecho.", "D. Comunista."],
        "respuesta": "C. Social de Derecho.",
        "explicacion_ia": "Significa que el Estado debe garantizar no solo la ley, sino también los derechos sociales, económicos y la dignidad humana."
    },
    {
        "materia": "Lectura Crítica",
        "pregunta": "Si un autor critica algo pero usa un tono de burla y exageración, está usando:",
        "opciones": ["A. La sátira.", "B. La tragedia.", "C. La oda.", "D. El resumen."],
        "respuesta": "A. La sátira.",
        "explicacion_ia": "La sátira es un género que usa la ironía, el ridículo y la exageración para criticar vicios o defectos sociales."
    },
    {
        "materia": "Matemáticas",
        "pregunta": "Un kilo de arroz cuesta $3.000. Si compro 2.5 kilos, ¿cuánto pago?",
        "opciones": ["A. $6.000", "B. $7.500", "C. $9.000", "D. $8.500"],
        "respuesta": "B. $7.500",
        "explicacion_ia": "2 kilos cuestan $6.000. Medio kilo cuesta $1.500. Total: 6.000 + 1.500 = 7.500."
    },
    {
        "materia": "Ciencias Naturales",
        "pregunta": "El ADN se encuentra principalmente en:",
        "opciones": ["A. La membrana celular.", "B. El núcleo celular.", "C. El citoplasma.", "D. Los lisosomas."],
        "respuesta": "B. El núcleo celular.",
        "explicacion_ia": "En las células eucariotas, el material genético (ADN) está protegido dentro del núcleo."
    },
    {
        "materia": "Sociales y Ciudadanas",
        "pregunta": "¿Qué es la 'inflación'?",
        "opciones": ["A. La bajada de precios.", "B. El aumento generalizado y sostenido de los precios de bienes y servicios.", "C. El aumento de salarios.", "D. La falta de dinero."],
        "respuesta": "B. El aumento generalizado y sostenido de los precios de bienes y servicios.",
        "explicacion_ia": "Es el fenómeno económico donde el dinero pierde valor adquisitivo porque las cosas cuestan más."
    },
    {
        "materia": "Lectura Crítica",
        "pregunta": "¿Qué es un 'texto expositivo'?",
        "opciones": ["A. El que cuenta una historia.", "B. El que intenta convencer de una opinión.", "C. El que informa y explica un tema de manera objetiva.", "D. El que expresa sentimientos."],
        "respuesta": "C. El que informa y explica un tema de manera objetiva.",
        "explicacion_ia": "Su meta es transmitir conocimiento (ej: una enciclopedia, un libro de texto), no entretener ni convencer."
    },
    {
        "materia": "Matemáticas",
        "pregunta": "¿Cuál es la raíz cuadrada de 144?",
        "opciones": ["A. 10", "B. 11", "C. 12", "D. 14"],
        "respuesta": "C. 12",
        "explicacion_ia": "Porque 12 multiplicado por sí mismo (12 x 12) da 144."
    },
    {
        "materia": "Ciencias Naturales",
        "pregunta": "¿Cuál es el planeta más grande del sistema solar?",
        "opciones": ["A. Tierra.", "B. Marte.", "C. Saturno.", "D. Júpiter."],
        "respuesta": "D. Júpiter.",
        "explicacion_ia": "Júpiter es un gigante gaseoso y es, por mucho, el planeta con mayor masa y volumen del sistema solar."
    },
    {
        "materia": "Sociales y Ciudadanas",
        "pregunta": "El derecho al voto en Colombia es:",
        "opciones": ["A. Obligatorio para todos.", "B. Un deber y un derecho voluntario.", "C. Solo para los hombres.", "D. Solo para los que pagan impuestos."],
        "respuesta": "B. Un deber y un derecho voluntario.",
        "explicacion_ia": "En Colombia el voto no es obligatorio (no te multan si no votas), pero es un deber ciudadano participar."
    },
    {
        "materia": "Lectura Crítica",
        "pregunta": "En la oración 'Lloraba ríos de lágrimas', hay una:",
        "opciones": ["A. Metáfora.", "B. Hipérbole.", "C. Personificación.", "D. Paradoja."],
        "respuesta": "B. Hipérbole.",
        "explicacion_ia": "Es una exageración desmedida (nadie llora tanta agua como un río) para expresar gran dolor."
    },
    {
        "materia": "Matemáticas",
        "pregunta": "Si un tren viaja a 80 km/h, ¿cuántos kilómetros recorre en 3 horas?",
        "opciones": ["A. 160 km", "B. 240 km", "C. 320 km", "D. 83 km"],
        "respuesta": "B. 240 km",
        "explicacion_ia": "Distancia = Velocidad x Tiempo. D = 80 x 3 = 240 km."
    },
    {
        "materia": "Ciencias Naturales",
        "pregunta": "¿Qué es la 'celulosa'?",
        "opciones": ["A. Un tipo de célula.", "B. Un carbohidrato que forma la pared celular de las plantas.", "C. Una proteína animal.", "D. Una grasa."],
        "respuesta": "B. Un carbohidrato que forma la pared celular de las plantas.",
        "explicacion_ia": "Es lo que le da rigidez a las plantas y a la madera. Los humanos no podemos digerirla (es la fibra)."
    },
    {
        "materia": "Sociales y Ciudadanas",
        "pregunta": "¿Qué fue la 'Guerra de los Mil Días'?",
        "opciones": ["A. Una guerra contra España.", "B. Una guerra civil entre Liberales y Conservadores a finales del siglo XIX.", "C. La guerra contra el narcotráfico.", "D. Una guerra mundial."],
        "respuesta": "B. Una guerra civil entre Liberales y Conservadores a finales del siglo XIX.",
        "explicacion_ia": "Fue el conflicto civil más sangriento de Colombia (1899-1902) y resultó en la pérdida de Panamá."
    },
    {
        "materia": "Lectura Crítica",
        "pregunta": "El antónimo de 'altruista' es:",
        "opciones": ["A. Generoso.", "B. Egoísta.", "C. Amable.", "D. Alto."],
        "respuesta": "B. Egoísta.",
        "explicacion_ia": "Altruista es quien busca el bien ajeno sin interés. Egoísta es quien solo piensa en su propio beneficio."
    },
    {
        "materia": "Matemáticas",
        "pregunta": "¿Cuál es el 10% de 500?",
        "opciones": ["A. 10", "B. 50", "C. 100", "D. 5"],
        "respuesta": "B. 50",
        "explicacion_ia": "Para sacar el 10%, basta con dividir por 10 o quitar un cero. 500 / 10 = 50."
    },
    {
        "materia": "Ciencias Naturales",
        "pregunta": "La unidad básica para medir la fuerza en el sistema internacional es:",
        "opciones": ["A. Julio.", "B. Newton.", "C. Watio.", "D. Pascal."],
        "respuesta": "B. Newton.",
        "explicacion_ia": "En honor a Isaac Newton. El Julio mide energía, el Watio potencia y el Pascal presión."
    },
    {
        "materia": "Sociales y Ciudadanas",
        "pregunta": "El 'Mecanismo de Participación' para reformar la Constitución mediante votación popular es:",
        "opciones": ["A. El Cabildo Abierto.", "B. El Referendo.", "C. La Consulta Popular.", "D. La Tutela."],
        "respuesta": "B. El Referendo.",
        "explicacion_ia": "El Referendo es la convocatoria al pueblo para que apruebe o rechace un proyecto de norma jurídica o derogue una norma vigente."
    },
    {
        "materia": "Lectura Crítica",
        "pregunta": "¿Cuál es el propósito de un 'editorial' en un periódico?",
        "opciones": ["A. Contar una noticia objetivamente.", "B. Expresar la opinión institucional del medio sobre un tema de actualidad.", "C. Vender productos.", "D. Entrevistar a un famoso."],
        "respuesta": "B. Expresar la opinión institucional del medio sobre un tema de actualidad.",
        "explicacion_ia": "A diferencia de la noticia (que informa), el editorial opina y argumenta la postura del periódico."
    },
    {
        "materia": "Matemáticas",
        "pregunta": "Se lanzan dos dados. Si se sabe que la suma de los resultados es mayor o igual a 10, ¿cuál es la probabilidad de que en uno de los dados haya salido un 6?",
        "opciones": ["A. 1/6", "B. 5/6", "C. 6/36", "D. 1/2"],
        "respuesta": "B. 5/6",
        "explicacion_ia": "🎲 Probabilidad Condicional: Los casos donde la suma es >= 10 son: (4,6), (5,5), (5,6), (6,4), (6,5), (6,6). Son 6 casos en total (Espacio muestral reducido). De esos 6, ¿en cuántos aparece el número 6? En 5 de ellos (todos menos el 5,5). Por tanto, 5/6."
    },
    {
        "materia": "Lectura Crítica",
        "pregunta": "Immanuel Kant propone el 'Imperativo Categórico' con la fórmula: 'Obra solo según aquella máxima por la cual puedas querer que al mismo tiempo se convierta en ley universal'. Esto implica que una acción es moralmente correcta si:",
        "opciones": ["A. Me beneficia a mí y a mi familia.", "B. Produce la mayor felicidad para el mayor número de personas (Utilitarismo).", "C. Es universalizable, es decir, sería aceptable que todos los seres humanos hicieran lo mismo en esa situación.", "D. Sigue los mandamientos religiosos."],
        "respuesta": "C. Es universalizable, es decir, sería aceptable que todos los seres humanos hicieran lo mismo en esa situación.",
        "explicacion_ia": "🧠 Ética Kantiana: No importa la consecuencia (felicidad) ni la autoridad (religión), sino el deber racional. Si mientes, ¿te gustaría que mentir fuera una ley universal? Si la respuesta es no, entonces mentir es inmoral."
    },
    {
        "materia": "Ciencias Naturales",
        "pregunta": "En una reacción química, tienes 2 moles de Hidrógeno (H2) y 1 mol de Oxígeno (O2) para formar agua (H2O). Si repentinamente duplicas la cantidad de Hidrógeno a 4 moles, pero mantienes el Oxígeno en 1 mol, ¿cuánta agua se produce?",
        "opciones": ["A. El doble de agua.", "B. La misma cantidad de agua.", "C. La mitad de agua.", "D. Cuatro veces más agua."],
        "respuesta": "B. La misma cantidad de agua.",
        "explicacion_ia": "⚗️ Reactivo Límite: La ecuación es 2H2 + O2 -> 2H2O. Se necesitan 2 de H por 1 de O. Si tienes 1 mol de O2, este solo puede reaccionar con 2 moles de H2. Aunque agregues más Hidrógeno, el Oxígeno se acabó (es el reactivo límite) y la reacción se detiene ahí."
    },
    {
        "materia": "Sociales y Ciudadanas",
        "pregunta": "El Presidente de la República decreta un 'Estado de Conmoción Interior' para controlar una ola de violencia. Bajo este estado, decide suspender el derecho al Habeas Corpus para facilitar capturas. ¿Es esto constitucional?",
        "opciones": ["A. Sí, porque en Estado de Excepción el Presidente tiene poderes ilimitados.", "B. Sí, porque la seguridad nacional prima sobre los derechos individuales.", "C. No, porque los Derechos Humanos fundamentales y las garantías judiciales indispensables (como el Habeas Corpus) no pueden suspenderse ni siquiera en Estados de Excepción.", "D. No, a menos que el Congreso le dé permiso."],
        "respuesta": "C. No, porque los Derechos Humanos fundamentales y las garantías judiciales indispensables (como el Habeas Corpus) no pueden suspenderse ni siquiera en Estados de Excepción.",
        "explicacion_ia": "⚖️ Derecho Internacional Humanitario: Hay un núcleo duro de derechos (vida, integridad, debido proceso básico) que son intocables, sin importar la gravedad de la crisis."
    },
    {
        "materia": "Matemáticas",
        "pregunta": "Una bacteria se reproduce por bipartición cada 20 minutos. Si colocamos una sola bacteria en un frasco a las 8:00 AM y el frasco se llena a las 12:00 PM, ¿a qué hora estaba el frasco lleno exactamente a la mitad?",
        "opciones": ["A. 10:00 AM", "B. 11:40 AM", "C. 11:59 AM", "D. 11:20 AM"],
        "respuesta": "B. 11:40 AM",
        "explicacion_ia": "🦠 Crecimiento Exponencial: Si se duplica cada 20 minutos, significa que 20 minutos ANTES de estar lleno, estaba a la mitad. Si se llenó a las 12:00, estaba a la mitad a las 11:40."
    },
    {
        "materia": "Ciencias Naturales",
        "pregunta": "Un objeto se lanza verticalmente hacia arriba. Despreciando la resistencia del aire, ¿cuál de las siguientes afirmaciones sobre su aceleración es verdadera?",
        "opciones": ["A. La aceleración es cero en el punto más alto.", "B. La aceleración disminuye mientras sube.", "C. La aceleración es constante y apunta hacia abajo durante todo el trayecto.", "D. La aceleración cambia de dirección cuando empieza a bajar."],
        "respuesta": "C. La aceleración es constante y apunta hacia abajo durante todo el trayecto.",
        "explicacion_ia": "🚀 Física Mecánica: La única fuerza actuando es la gravedad. La gravedad siempre es constante (9.8 m/s²) y siempre apunta hacia abajo, sin importar si el objeto sube, baja o está quieto un instante en la cima."
    },
    {
        "materia": "Sociales y Ciudadanas",
        "pregunta": "La 'Teoría de la Dependencia', popular en América Latina en los años 60 y 70, explicaba el subdesarrollo de la región argumentando que:",
        "opciones": ["A. Los latinos son perezosos por el clima tropical.", "B. La economía mundial está diseñada para que los países del centro (ricos) se enriquezcan a costa de la explotación de los recursos de la periferia (pobres).", "C. Falta inversión extranjera.", "D. El problema es la falta de educación religiosa."],
        "respuesta": "B. La economía mundial está diseñada para que los países del centro (ricos) se enriquezcan a costa de la explotación de los recursos de la periferia (pobres).",
        "explicacion_ia": "Propone que el subdesarrollo no es una etapa previa al desarrollo, sino una consecuencia estructural del capitalismo global que subordina a unos países para beneficiar a otros."
    },
    {
        "materia": "Lectura Crítica",
        "pregunta": "Lea: 'La historia de todas las sociedades hasta nuestros días es la historia de la lucha de clases'. (Marx). Esta frase implica una visión de la historia basada en:",
        "opciones": ["A. La armonía y el progreso continuo.", "B. El conflicto económico entre opresores y oprimidos como motor del cambio.", "C. La voluntad de grandes líderes individuales.", "D. El destino divino."],
        "respuesta": "B. El conflicto económico entre opresores y oprimidos como motor del cambio.",
        "explicacion_ia": "Es el materialismo histórico. Marx plantea que lo que mueve la historia no son las ideas, sino la tensión material entre quienes tienen los medios de producción y quienes trabajan."
    },
    {
        "materia": "Matemáticas",
        "pregunta": "Si sen(x) = 0.6 y cos(x) = 0.8, ¿cuánto vale tan(x)?",
        "opciones": ["A. 0.48", "B. 1.33", "C. 0.75", "D. 1.4"],
        "respuesta": "C. 0.75",
        "explicacion_ia": "📐 Identidad Trigonométrica: Tan(x) = Sen(x) / Cos(x). Entonces, 0.6 / 0.8. Simplificamos (6/8) -> 3/4 -> 0.75."
    },
    {
        "materia": "Ciencias Naturales",
        "pregunta": "Si se cruza una planta de flores rojas (RR - dominante) con una de flores blancas (rr - recesivo), y luego se cruzan dos hijos de esa generación (F1) entre sí. ¿Qué probabilidad hay de obtener una flor blanca en la segunda generación (F2)?",
        "opciones": ["A. 0%", "B. 25%", "C. 50%", "D. 75%"],
        "respuesta": "B. 25%",
        "explicacion_ia": "🧬 Genética Mendeliana: F1 serán todos heterocigotos (Rr - Rojos). Al cruzar Rr x Rr, el cuadro de Punnett da: RR, Rr, Rr, rr. Solo 'rr' es blanca. 1 de 4 casos = 25%."
    },
    {
        "materia": "Lectura Crítica Élite",
        "tema": "Filosofía Moderna",
        "pregunta": "Lea: 'El hombre está condenado a ser libre; porque una vez arrojado al mundo, es responsable de todo lo que hace'. (Sartre). Esta afirmación existencialista implica que:",
        "opciones": ["A. La libertad es un castigo divino.", "B. No existe una naturaleza humana predeterminada ni excusas deterministas para nuestros actos.", "C. Las cárceles no deberían existir.", "D. El destino está escrito."],
        "respuesta": "B. No existe una naturaleza humana predeterminada ni excusas deterministas para nuestros actos.",
        "explicacion_ia": "Para el existencialismo, la existencia precede a la esencia. No hay 'naturaleza' o 'dios' que nos defina; nos definimos nosotros mismos con cada elección, cargando con la angustia de esa responsabilidad total."
    },
    {
        "materia": "Ciencias - Física Cuántica",
        "tema": "Dualidad Onda-Partícula",
        "pregunta": "En el experimento de la doble rendija, cuando se observa (mide) por cuál rendija pasa el electrón, el patrón de interferencia desaparece. Esto demuestra:",
        "opciones": ["A. Que los electrones son tímidos.", "B. El colapso de la función de onda debido a la interacción con el sistema de medición.", "C. Que la luz siempre es una partícula.", "D. Que el equipo estaba defectuoso."],
        "respuesta": "B. El colapso de la función de onda debido a la interacción con el sistema de medición.",
        "explicacion_ia": "Es el principio fundamental de la mecánica cuántica: el acto de medir altera el sistema, forzando a la partícula a 'elegir' un estado definido y perder su comportamiento ondulatorio."
    },
    {
        "materia": "Sociales - Geopolítica",
        "tema": "Conflictos Contemporáneos",
        "pregunta": "La 'Trampa de Tucídides' es un término usado en relaciones internacionales para describir la tensión estructural cuando:",
        "opciones": ["A. Un país pobre pide dinero al FMI.", "B. Una potencia emergente amenaza con desplazar a una potencia hegemónica establecida, haciendo probable la guerra.", "C. Se firman tratados de paz falsos.", "D. Grecia ataca a Roma."],
        "respuesta": "B. Una potencia emergente amenaza con desplazar a una potencia hegemónica establecida, haciendo probable la guerra.",
        "explicacion_ia": "Concepto popularizado por Graham Allison (ej: el ascenso de China frente a EE.UU.), basado en la guerra del Peloponeso entre Atenas (emergente) y Esparta (hegemónica)."
    },
    {
        "materia": "Lectura Crítica",
        "pregunta": "Lea el fragmento: 'La tiranía de la meritocracia radica en que quienes tienen éxito creen que se lo han ganado por completo gracias a su esfuerzo, olvidando la suerte y las ayudas recibidas. Esto los lleva a mirar con desdén a los que fracasan, asumiendo que su pobreza es culpa de su pereza'. (Michael Sandel). \n\n¿Cuál es la premisa implícita (lo que el autor asume pero no dice) en este argumento?",
        "opciones": ["A. Que el esfuerzo individual no existe y todo es suerte.", "B. Que el éxito no depende exclusivamente del esfuerzo individual.", "C. Que los pobres son perezosos y por eso fracasan.", "D. Que la meritocracia es el sistema más justo posible."],
        "respuesta": "B. Que el éxito no depende exclusivamente del esfuerzo individual.",
        "explicacion_ia": "🧠 Análisis Profundo: Esta es una pregunta de inferencia compleja. El autor critica la meritocracia porque esta ignora factores externos (suerte, ayuda). Por lo tanto, asume implícitamente que el éxito es multifactorial y no solo fruto del esfuerzo. La opción A es una exageración (falacia), y la C es lo que el autor critica, no lo que piensa."
    },
    {
        "materia": "Matemáticas",
        "pregunta": "Un tanque cónico (forma de cono invertido) se está llenando de agua a una velocidad constante. A medida que el nivel del agua sube, ¿qué sucede con la velocidad a la que aumenta la altura del agua?",
        "opciones": ["A. Aumenta constantemente.", "B. Disminuye, porque el área de la superficie es mayor arriba.", "C. Se mantiene constante.", "D. Aumenta y luego disminuye."],
        "respuesta": "B. Disminuye, porque el área de la superficie es mayor arriba.",
        "explicacion_ia": "📐 Razonamiento Cuantitativo: Imagina un cono al revés. Abajo es estrecho, así que con poca agua la altura sube rápido. Arriba es ancho, así que necesitas mucha más agua para subir el mismo centímetro de altura. Por ende, la velocidad de subida DISMINUYE."
    },
    {
        "materia": "Sociales y Ciudadanas",
        "pregunta": "En un resguardo indígena, un miembro de la comunidad comete un delito grave contra otro miembro dentro del territorio. La justicia ordinaria quiere juzgarlo, pero las autoridades indígenas reclaman su derecho a hacerlo bajo sus propios usos y costumbres. Según la Constitución de 1991, ¿qué principio debe prevalecer?",
        "opciones": ["A. La unidad legal, por tanto debe ser juzgado por la Fiscalía General.", "B. La Jurisdicción Especial Indígena, siempre que se respete el derecho a la vida y la integridad.", "C. La autonomía territorial, permitiendo cualquier castigo que la comunidad decida.", "D. El fuero penal militar, si había ejército cerca."],
        "respuesta": "B. La Jurisdicción Especial Indígena, siempre que se respete el derecho a la vida y la integridad.",
        "explicacion_ia": "⚖️ Constitucional Avanzado: La Constitución reconoce la Jurisdicción Especial Indígena. Sin embargo, la Corte Constitucional ha establecido límites: pueden juzgar a sus miembros en su territorio, PERO no pueden imponer penas que violen DD.HH. (como tortura o pena de muerte). Es un equilibrio entre diversidad étnica y derechos humanos."
    },
    {
        "materia": "Ciencias Naturales",
        "pregunta": "Se tienen dos plantas de la misma especie. A la Planta 1 se le corta el tallo principal (poda apical). A la Planta 2 se le deja intacta. Después de dos semanas, se observa que la Planta 1 ha desarrollado muchas ramas laterales y es más frondosa, mientras la Planta 2 creció solo hacia arriba. ¿Qué hormona vegetal explica este fenómeno?",
        "opciones": ["A. Etileno (maduración).", "B. Auxina (dominancia apical).", "C. Giberelina (germinación).", "D. Ácido abscísico (estrés)."],
        "respuesta": "B. Auxina (dominancia apical).",
        "explicacion_ia": "🌿 Biología Celular: Las auxinas se producen en la punta (ápice) e inhiben el crecimiento de los lados para que la planta crezca hacia arriba (busca luz). Al cortar la punta, eliminas las auxinas, permitiendo que las ramas laterales 'despierten' y crezcan."
    },
    {
        "materia": "Matemáticas",
        "pregunta": "Se lanzan dos dados honestos de 6 caras. ¿Cuál es la probabilidad de que la suma de sus resultados sea mayor o igual a 10?",
        "opciones": ["A. 1/6", "B. 1/12", "C. 6/36", "D. 5/36"],
        "respuesta": "C. 6/36",
        "explicacion_ia": "🎲 Probabilidad Compuesta: Total de combinaciones: 6x6 = 36. Casos favorables (suma >= 10): (4,6), (5,5), (5,6), (6,4), (6,5), (6,6). Son 6 casos. La probabilidad es 6/36 (que simplificado es 1/6). Ojo: hay que contar bien los pares."
    },
    {
        "materia": "Sociales y Ciudadanas",
        "pregunta": "El 'Fenómeno de la Enfermedad Holandesa' en economía ocurre cuando un país descubre grandes reservas de un recurso natural (ej: petróleo), exporta mucho y entran muchos dólares. ¿Cuál es el efecto negativo principal de esto para la industria nacional?",
        "opciones": ["A. Aumenta la pobreza extrema inmediatamente.", "B. Se revalúa la moneda local (dólar baja), haciendo que los otros productos nacionales sean muy caros para exportar.", "C. Se acaba el recurso natural en pocos meses.", "D. Aumenta la inversión en agricultura."],
        "respuesta": "B. Se revalúa la moneda local (dólar baja), haciendo que los otros productos nacionales sean muy caros para exportar.",
        "explicacion_ia": "💰 Economía Global: Al entrar muchos dólares, el dólar se vuelve 'barato'. Esto es bueno para importar, pero PÉSIMO para la industria y el agro local, porque sus productos se vuelven caros para los extranjeros, llevando a la quiebra a los sectores no petroleros."
    },
    {
        "materia": "Ciencias Naturales",
        "pregunta": "Un paracaidista salta de un avión. Al principio acelera, pero luego alcanza una 'velocidad terminal' constante antes de abrir el paracaídas. En ese momento de velocidad constante, ¿cómo es la suma de fuerzas (fuerza neta) sobre él?",
        "opciones": ["A. La fuerza neta es cero.", "B. La fuerza neta es hacia abajo (gravedad).", "C. La fuerza neta es hacia arriba (resistencia).", "D. La fuerza neta es igual a la masa."],
        "respuesta": "A. La fuerza neta es cero.",
        "explicacion_ia": "🚀 Física Mecánica: Según la 1ª Ley de Newton, si la velocidad es constante (no acelera), la fuerza neta debe ser CERO. Esto pasa porque la fuerza de gravedad (hacia abajo) se cancela exactamente con la resistencia del aire (hacia arriba)."
    },
    {
        "materia": "Lectura Crítica",
        "pregunta": "En un debate sobre el aborto, un participante dice: 'Usted no puede opinar sobre el embarazo porque es hombre'. ¿Qué falacia argumentativa está cometiendo?",
        "opciones": ["A. Falacia de Autoridad.", "B. Falacia Ad Hominem (contra el hombre).", "C. Falacia de Generalización.", "D. Falacia de Pendiente Resbaladiza."],
        "respuesta": "B. Falacia Ad Hominem (contra el hombre).",
        "explicacion_ia": "🗣️ Argumentación: El Ad Hominem ocurre cuando, en lugar de atacar el argumento o la idea (ej: si el feto siente o no), se ataca a la persona que habla (su género, su raza, su pasado) para invalidar su opinión."
    },
    {
        "materia": "Matemáticas",
        "pregunta": "Tienes una tarjeta de crédito que cobra el 2% de interés mensual compuesto. Si haces una compra de $1.000.000 y no pagas nada durante 2 meses, ¿cuánto debes al final del segundo mes?",
        "opciones": ["A. $1.040.000", "B. $1.040.400", "C. $1.020.000", "D. $1.200.000"],
        "respuesta": "B. $1.040.400",
        "explicacion_ia": "💸 Finanzas: Interés compuesto es 'interés sobre interés'. \nMes 1: 1.000.000 + 2% = 1.020.000. \nMes 2: El 2% se calcula sobre 1.020.000 (no sobre el millón inicial). 2% de 1.020.000 es 20.400. \nTotal: 1.020.000 + 20.400 = 1.040.400."
    },
    {
        "materia": "Ciencias Naturales",
        "pregunta": "El principio de Le Chatelier establece que si perturbamos un sistema químico en equilibrio, el sistema reaccionará para contrarrestar la perturbación. Si tenemos la reacción: N2 + 3H2 ↔ 2NH3 + Calor (Exotérmica), ¿qué pasa si aumentamos la temperatura?",
        "opciones": ["A. Se produce más NH3.", "B. El sistema se desplaza hacia los reactivos (izquierda) para consumir calor.", "C. La reacción se detiene.", "D. No pasa nada."],
        "respuesta": "B. El sistema se desplaza hacia los reactivos (izquierda) para consumir calor.",
        "explicacion_ia": "⚗️ Química Analítica: Como la reacción libera calor (es un producto), si tú agregas calor (subes temperatura), al sistema 'le estorba' ese exceso y tratará de consumirlo, moviéndose hacia el lado contrario (hacia la izquierda), disminuyendo la producción de amoníaco."
    },
    {
        "materia": "Matemáticas",
        "pregunta": "En una tienda de ropa, por la compra de 3 camisetas te regalan la cuarta. ¿A qué porcentaje de descuento equivale esta promoción sobre el total de las 4 prendas?",
        "opciones": ["A. 20%", "B. 25%", "C. 33%", "D. 40%"],
        "respuesta": "B. 25%",
        "explicacion_ia": "Si llevas 4 y pagas 3, te estás ahorrando 1 de 4. La fracción es 1/4. En porcentaje, 1 dividido 4 es 0.25, es decir, el 25%."
    },
    {
        "materia": "Ciencias Naturales",
        "pregunta": "Un carro viaja a 60 km/h y frena hasta detenerse en 10 segundos. ¿Qué ocurre con su aceleración?",
        "opciones": ["A. Es positiva porque el carro avanza.", "B. Es cero porque se detiene.", "C. Es negativa porque la velocidad disminuye.", "D. Es igual a la gravedad."],
        "respuesta": "C. Es negativa porque la velocidad disminuye.",
        "explicacion_ia": "La aceleración es el cambio de velocidad en el tiempo. Si la velocidad final es menor que la inicial (frenado), el cambio es negativo, por lo tanto la aceleración es negativa (desaceleración)."
    },
    {
        "materia": "Sociales y Ciudadanas",
        "pregunta": "En Colombia, los afrodescendientes tienen derecho a la propiedad colectiva de sus territorios ancestrales. ¿Qué ley o norma garantiza este derecho?",
        "opciones": ["A. La Ley 100 de 1993.", "B. La Ley 70 de 1993.", "C. El Código de Policía.", "D. La Séptima Papeleta."],
        "respuesta": "B. La Ley 70 de 1993.",
        "explicacion_ia": "La Ley 70 de 1993 reconoce a las comunidades negras que han venido ocupando tierras baldías en las zonas rurales ribereñas de los ríos de la Cuenca del Pacífico, de acuerdo con sus prácticas tradicionales de producción."
    },
    {
        "materia": "Lectura Crítica",
        "pregunta": "Si un texto dice: 'La democracia es la peor forma de gobierno, a excepción de todas las demás', el autor quiere decir que:",
        "opciones": ["A. La democracia es un sistema perfecto.", "B. No debería existir ningún gobierno.", "C. La democracia tiene fallas, pero es la mejor opción disponible comparada con otras.", "D. Las dictaduras son mejores que la democracia."],
        "respuesta": "C. La democracia tiene fallas, pero es la mejor opción disponible comparada con otras.",
        "explicacion_ia": "Es una cita famosa de Churchill. Utiliza la ironía para aceptar las imperfecciones del sistema, pero reafirma su superioridad frente a alternativas como la tiranía."
    },
    {
        "materia": "Matemáticas",
        "pregunta": "El promedio de notas de 4 estudiantes es 3.5. Si un quinto estudiante se une al grupo y tiene una nota de 4.5, ¿cuál es el nuevo promedio?",
        "opciones": ["A. 3.7", "B. 4.0", "C. 3.8", "D. 3.5"],
        "respuesta": "A. 3.7",
        "explicacion_ia": "Suma total inicial: 4 estudiantes * 3.5 = 14. Sumamos al nuevo: 14 + 4.5 = 18.5. Nuevo total de estudiantes: 5. Promedio: 18.5 / 5 = 3.7."
    },
    {
        "materia": "Ciencias Naturales",
        "pregunta": "En la tabla periódica, los elementos del mismo grupo (columna vertical) tienen en común:",
        "opciones": ["A. El mismo número de protones.", "B. El mismo peso atómico.", "C. El mismo número de electrones de valencia.", "D. El mismo estado físico."],
        "respuesta": "C. El mismo número de electrones de valencia.",
        "explicacion_ia": "Los grupos o familias comparten la configuración electrónica externa (electrones de valencia), lo que les da propiedades químicas similares."
    },
    {
        "materia": "Sociales y Ciudadanas",
        "pregunta": "El 'Frente Nacional' (1958-1974) fue un acuerdo político en Colombia que consistió en:",
        "opciones": ["A. La unión de todos los partidos para luchar contra España.", "B. La alternancia del poder exclusiva entre Liberales y Conservadores.", "C. La creación de las guerrillas de las FARC.", "D. La dictadura de Rojas Pinilla."],
        "respuesta": "B. La alternancia del poder exclusiva entre Liberales y Conservadores.",
        "explicacion_ia": "Fue un pacto para acabar con la violencia bipartidista, donde se turnaron la presidencia por 16 años y se repartieron los cargos públicos, excluyendo a otras fuerzas políticas."
    },
    {
        "materia": "Lectura Crítica",
        "pregunta": "En el contexto de la tecnología, ¿qué significa la palabra 'obsoleto'?",
        "opciones": ["A. Que es muy rápido y moderno.", "B. Que es costoso.", "C. Que ha dejado de usarse porque hay algo más nuevo o mejor.", "D. Que está roto."],
        "respuesta": "C. Que ha dejado de usarse porque hay algo más nuevo o mejor.",
        "explicacion_ia": "La obsolescencia se refiere a la caída en desuso de máquinas, equipos o tecnologías motivada no por un mal funcionamiento, sino por un insuficiente desempeño comparado con las nuevas tecnologías."
    },
    {
        "materia": "Matemáticas",
        "pregunta": "Un edificio proyecta una sombra de 10 metros. Al mismo tiempo, un poste de 2 metros proyecta una sombra de 1 metro. ¿Cuál es la altura del edificio?",
        "opciones": ["A. 10 metros.", "B. 20 metros.", "C. 5 metros.", "D. 15 metros."],
        "respuesta": "B. 20 metros.",
        "explicacion_ia": "Es un problema de semejanza de triángulos (Teorema de Tales). La relación altura/sombra del poste es 2/1 = 2. Por tanto, la altura del edificio debe ser el doble de su sombra. 10 * 2 = 20."
    },
    {
        "materia": "Ciencias Naturales",
        "pregunta": "¿Qué ocurre durante el proceso de ósmosis en una célula?",
        "opciones": ["A. El soluto se mueve de donde hay menos a donde hay más.", "B. El agua se mueve a través de la membrana desde una zona de menor concentración de soluto a una de mayor.", "C. La célula gasta energía para mover agua.", "D. La membrana se rompe."],
        "respuesta": "B. El agua se mueve a través de la membrana desde una zona de menor concentración de soluto a una de mayor.",
        "explicacion_ia": "La ósmosis es el transporte pasivo de agua para equilibrar concentraciones. El agua viaja hacia donde hay más 'sal' (soluto) para diluirlo."
    },
    {
        "materia": "Sociales y Ciudadanas",
        "pregunta": "¿Cuál es la diferencia entre un Estado Centralista y uno Federal?",
        "opciones": ["A. En el centralista hay presidente y en el federal hay rey.", "B. En el centralista las decisiones políticas y administrativas se toman desde la capital; en el federal, los estados tienen autonomía.", "C. El centralista es comunista y el federal es capitalista.", "D. No hay diferencia."],
        "respuesta": "B. En el centralista las decisiones políticas y administrativas se toman desde la capital; en el federal, los estados tienen autonomía.",
        "explicacion_ia": "Colombia hoy es centralista con descentralización administrativa. EE.UU. es federal (cada estado tiene sus propias leyes penales, por ejemplo)."
    },
    {
        "materia": "Lectura Crítica",
        "pregunta": "Identifique el tipo de texto: 'Instrucciones para llorar: Dejando de lado los motivos, aténgase a la manera correcta de llorar...'.",
        "opciones": ["A. Periodístico.", "B. Literario / Narrativo.", "C. Instructivo (Manual técnico).", "D. Científico."],
        "respuesta": "B. Literario / Narrativo.",
        "explicacion_ia": "Aunque el título dice 'Instrucciones', es un texto de Julio Cortázar. Es literatura que juega con la forma de instrucción para crear un efecto poético, no un manual técnico real."
    },
    {
        "materia": "Matemáticas",
        "pregunta": "¿Cuántas combinaciones diferentes de ropa puedes hacer con 3 pantalones y 4 camisas?",
        "opciones": ["A. 7", "B. 12", "C. 34", "D. 10"],
        "respuesta": "B. 12",
        "explicacion_ia": "Principio multiplicativo: Si tienes N opciones de una cosa y M de otra, el total es N x M. 3 x 4 = 12 combinaciones."
    },
    {
        "materia": "Ciencias Naturales",
        "pregunta": "En física, la energía cinética de un cuerpo depende de:",
        "opciones": ["A. Su altura y gravedad.", "B. Su masa y su velocidad.", "C. Su temperatura.", "D. Su elasticidad."],
        "respuesta": "B. Su masa y su velocidad.",
        "explicacion_ia": "La fórmula es Ec = 1/2 * masa * velocidad al cuadrado. Si no se mueve (velocidad 0), no tiene energía cinética."
    },
    {
        "materia": "Sociales y Ciudadanas",
        "pregunta": "Si el Congreso aprueba una ley que prohíbe a las mujeres estudiar ingeniería, ¿qué principio constitucional viola principalmente?",
        "opciones": ["A. El derecho a la propiedad privada.", "B. El derecho a la igualdad y no discriminación.", "C. La libertad de prensa.", "D. El derecho de asilo."],
        "respuesta": "B. El derecho a la igualdad y no discriminación.",
        "explicacion_ia": "El Artículo 13 de la Constitución establece que todas las personas nacen libres e iguales ante la ley y no pueden ser discriminadas por razones de sexo, raza, origen, etc."
    },
    {
        "materia": "Lectura Crítica",
        "pregunta": "En la oración 'Juan es un león en los negocios', la palabra 'león' connota:",
        "opciones": ["A. Que tiene mucho pelo.", "B. Que es un animal salvaje.", "C. Que es agresivo, fuerte o dominante.", "D. Que vive en la selva."],
        "respuesta": "C. Que es agresivo, fuerte o dominante.",
        "explicacion_ia": "Es una metáfora que transfiere las características atribuidas al león (fuerza, ferocidad, liderazgo) a Juan en el contexto empresarial."
    },
    {
        "materia": "Matemáticas",
        "pregunta": "Si lanzas una moneda 3 veces, ¿cuál es la probabilidad de que salgan 3 caras seguidas?",
        "opciones": ["A. 1/3", "B. 1/6", "C. 1/8", "D. 50%"],
        "respuesta": "C. 1/8",
        "explicacion_ia": "Cada lanzamiento es independiente y tiene probabilidad 1/2. Para que pasen los tres: 1/2 x 1/2 x 1/2 = 1/8."
    },
    {
        "materia": "Ciencias Naturales",
        "pregunta": "¿Cuál es el gas más abundante en la atmósfera terrestre?",
        "opciones": ["A. Oxígeno.", "B. Dióxido de Carbono.", "C. Nitrógeno.", "D. Hidrógeno."],
        "respuesta": "C. Nitrógeno.",
        "explicacion_ia": "A menudo se cree que es el oxígeno, pero el Nitrógeno ocupa aproximadamente el 78% de la atmósfera, mientras el oxígeno solo el 21%."
    },
    {
        "materia": "Sociales y Ciudadanas",
        "pregunta": "¿Qué es el 'Déficit Fiscal'?",
        "opciones": ["A. Cuando el gobierno gasta más dinero del que recibe por impuestos.", "B. Cuando sobran impuestos.", "C. Cuando hay mucha inflación.", "D. El robo de dinero público."],
        "respuesta": "A. Cuando el gobierno gasta más dinero del que recibe por impuestos.",
        "explicacion_ia": "Es un concepto económico clave. Ocurre cuando los egresos (gastos) del Estado superan a sus ingresos en un periodo determinado."
    },
    {
        "materia": "Lectura Crítica",
        "pregunta": "Si un autor dice 'El agua es el petróleo del futuro', ¿qué pretende comunicar?",
        "opciones": ["A. Que el agua será negra y viscosa.", "B. Que el agua será un recurso escaso, costoso y motivo de conflictos.", "C. Que podremos mover carros con agua.", "D. Que el agua contamina."],
        "respuesta": "B. Que el agua será un recurso escaso, costoso y motivo de conflictos.",
        "explicacion_ia": "Es una analogía. Compara el valor estratégico y económico que tuvo el petróleo en el siglo XX con el que tendrá el agua debido a su escasez."
    },
    {
        "materia": "Matemáticas",
        "pregunta": "En un triángulo rectángulo, si un ángulo agudo mide 30 grados, ¿cuánto mide el otro ángulo agudo?",
        "opciones": ["A. 30 grados.", "B. 60 grados.", "C. 90 grados.", "D. 45 grados."],
        "respuesta": "B. 60 grados.",
        "explicacion_ia": "La suma de los ángulos internos es 180°. Un ángulo es recto (90°). Quedan 90° para los otros dos. 90 - 30 = 60."
    },
    {
        "materia": "Ciencias Naturales",
        "pregunta": "La mitocondria es un organelo celular conocido como:",
        "opciones": ["A. El cerebro de la célula.", "B. La planta de energía de la célula.", "C. El basurero de la célula.", "D. El borde de la célula."],
        "respuesta": "B. La planta de energía de la célula.",
        "explicacion_ia": "La mitocondria es responsable de la respiración celular, proceso donde se genera ATP, la moneda energética de la vida."
    },
    {
        "materia": "Sociales y Ciudadanas",
        "pregunta": "¿Cuál es la función de la Corte Constitucional?",
        "opciones": ["A. Juzgar a los ladrones.", "B. Velar por la integridad y supremacía de la Constitución.", "C. Hacer las leyes.", "D. Dirigir el ejército."],
        "respuesta": "B. Velar por la integridad y supremacía de la Constitución.",
        "explicacion_ia": "Es el máximo guardián de la Carta Magna. Decide si las leyes aprobadas o los decretos se ajustan o no a la Constitución (Control de Constitucionalidad)."
    },
    {
        "materia": "Lectura Crítica",
        "pregunta": "Lea: 'No por mucho madrugar amanece más temprano'. Este refrán sugiere que:",
        "opciones": ["A. Hay que levantarse tarde.", "B. Los sucesos tienen su propio tiempo y no se pueden acelerar por más que uno se apresure.", "C. El sol sale a distintas horas.", "D. Es bueno ser perezoso."],
        "respuesta": "B. Los sucesos tienen su propio tiempo y no se pueden acelerar por más que uno se apresure.",
        "explicacion_ia": "Es una enseñanza popular sobre la paciencia y la imposibilidad de forzar el curso natural de ciertos eventos."
    },
    {
        "materia": "Matemáticas",
        "pregunta": "El conjunto de todos los posibles resultados de un experimento aleatorio se llama:",
        "opciones": ["A. Evento.", "B. Espacio Muestral.", "C. Probabilidad.", "D. Frecuencia."],
        "respuesta": "B. Espacio Muestral.",
        "explicacion_ia": "Definición básica de estadística. Por ejemplo, en un dado, el espacio muestral es {1, 2, 3, 4, 5, 6}."
    },
    {
        "materia": "Ciencias Naturales",
        "pregunta": "En una red trófica, ¿quiénes son los productores?",
        "opciones": ["A. Los leones.", "B. Los hongos.", "C. Las plantas y algas.", "D. Los humanos."],
        "respuesta": "C. Las plantas y algas.",
        "explicacion_ia": "Son organismos autótrofos (hacen fotosíntesis) que inician la cadena alimenticia transformando energía solar en química."
    },
    {
        "materia": "Sociales y Ciudadanas",
        "pregunta": "¿Qué es el 'Habeas Corpus'?",
        "opciones": ["A. Un impuesto a los cuerpos.", "B. Un derecho fundamental para pedir la libertad inmediata si la captura fue ilegal.", "C. Una ceremonia religiosa.", "D. Un tipo de contrato laboral."],
        "respuesta": "B. Un derecho fundamental para pedir la libertad inmediata si la captura fue ilegal.",
        "explicacion_ia": "Es una acción constitucional que protege la libertad personal contra arrestos arbitrarios. Debe resolverse en máximo 36 horas."
    },
    {
        "materia": "Lectura Crítica",
        "pregunta": "En un texto, la 'Idea Principal' se diferencia de las 'Ideas Secundarias' porque:",
        "opciones": ["A. Es más larga.", "B. Aparece siempre al final.", "C. Es la base global del texto, mientras las secundarias solo amplían o ejemplifican.", "D. Es la más difícil de leer."],
        "respuesta": "C. Es la base global del texto, mientras las secundarias solo amplían o ejemplifican.",
        "explicacion_ia": "La idea principal es la tesis o núcleo. Si la quitas, el texto pierde sentido. Las secundarias son detalles, ejemplos o justificaciones."
    },
    {
        "materia": "Matemáticas",
        "pregunta": "Si un círculo tiene radio 3 cm, ¿cuál es su área? (Usa π ≈ 3.14)",
        "opciones": ["A. 9.42 cm²", "B. 28.26 cm²", "C. 18.84 cm²", "D. 6 cm²"],
        "respuesta": "B. 28.26 cm²",
        "explicacion_ia": "Fórmula del área: A = π * r². A = 3.14 * (3)². A = 3.14 * 9 = 28.26."
    },
    {
        "materia": "Ciencias Naturales",
        "pregunta": "La Primera Ley de la Termodinámica afirma que:",
        "opciones": ["A. El calor va del frío al caliente.", "B. La energía no se crea ni se destruye, solo se transforma.", "C. Todo sistema tiende al desorden.", "D. La temperatura absoluta es inalcanzable."],
        "respuesta": "B. La energía no se crea ni se destruye, solo se transforma.",
        "explicacion_ia": "Es el principio de conservación de la energía aplicado a sistemas térmicos."
    },
    {
        "materia": "Sociales y Ciudadanas",
        "pregunta": "¿Qué sector de la economía agrupa las actividades de extracción de recursos naturales (minería, agricultura)?",
        "opciones": ["A. Sector Primario.", "B. Sector Secundario.", "C. Sector Terciario.", "D. Sector Cuaternario."],
        "respuesta": "A. Sector Primario.",
        "explicacion_ia": "El primario extrae (campo/minas). El secundario transforma (industria). El terciario ofrece servicios (comercio/bancos)."
    },
    {
        "materia": "Lectura Crítica",
        "pregunta": "¿Qué es un 'eufemismo'?",
        "opciones": ["A. Una mentira.", "B. Una palabra suave o decorosa para sustituir una que puede ofender o sonar mal.", "C. Un insulto.", "D. Un sonido fuerte."],
        "respuesta": "B. Una palabra suave o decorosa para sustituir una que puede ofender o sonar mal.",
        "explicacion_ia": "Ejemplo: Decir 'pasó a mejor vida' en lugar de 'murió', o 'establecimiento penitenciario' en lugar de 'cárcel'."
    },
    {
        "materia": "Matemáticas",
        "pregunta": "La suma de dos números es 20 y su resta es 4. ¿Cuáles son los números?",
        "opciones": ["A. 10 y 10", "B. 15 y 5", "C. 12 y 8", "D. 14 y 6"],
        "respuesta": "C. 12 y 8",
        "explicacion_ia": "Sistema de ecuaciones: x+y=20 y x-y=4. Sumamos ambas: 2x=24 -> x=12. Si x es 12, entonces y es 8."
    },
    {
        "materia": "Ciencias Naturales",
        "pregunta": "¿Qué partícula subatómica tiene carga neutra?",
        "opciones": ["A. Protón.", "B. Electrón.", "C. Neutrón.", "D. Fotón."],
        "respuesta": "C. Neutrón.",
        "explicacion_ia": "El neutrón se encuentra en el núcleo del átomo y, como su nombre indica, no tiene carga eléctrica neta."
    },
    {
        "materia": "Sociales y Ciudadanas",
        "pregunta": "La Séptima Papeleta fue un movimiento estudiantil que dio origen a:",
        "opciones": ["A. La Independencia de Colombia.", "B. El Bogotazo.", "C. La Constitución de 1991.", "D. El proceso de paz."],
        "respuesta": "C. La Constitución de 1991.",
        "explicacion_ia": "En 1990, estudiantes promovieron incluir una papeleta extra en las elecciones para convocar una Asamblea Nacional Constituyente, que redactó la actual constitución."
    },
    {
        "materia": "Lectura Crítica",
        "pregunta": "En un texto narrativo, el 'narrador omnisciente' es aquel que:",
        "opciones": ["A. Es el protagonista de la historia.", "B. Sabe todo lo que hacen, piensan y sienten los personajes.", "C. Solo cuenta lo que ve desde afuera como una cámara.", "D. Miente al lector."],
        "respuesta": "B. Sabe todo lo que hacen, piensan y sienten los personajes.",
        "explicacion_ia": "Omnisciente viene de 'omni' (todo) y 'ciencia' (saber). Es como un dios dentro del relato que conoce el pasado, presente, futuro y la interioridad de los personajes."
    },
    {
        "materia": "Matemáticas",
        "pregunta": "¿Qué número es solución de la ecuación x² - 9 = 0?",
        "opciones": ["A. Solo 3", "B. Solo -3", "C. 3 y -3", "D. 9"],
        "respuesta": "C. 3 y -3",
        "explicacion_ia": "x² = 9. Para quitar el cuadrado sacamos raíz, pero debemos considerar tanto el positivo como el negativo. 3*3=9 y (-3)*(-3)=9."
    },
    {
        "materia": "Ciencias Naturales",
        "pregunta": "Si colocas una célula animal en agua destilada (hipotónica), ¿qué le pasa?",
        "opciones": ["A. Se arruga (crenación).", "B. Se hincha y puede explotar (lisis).", "C. No le pasa nada.", "D. Se divide."],
        "respuesta": "B. Se hincha y puede explotar (lisis).",
        "explicacion_ia": "Por ósmosis, el agua entrará a la célula (donde hay más sales) para intentar equilibrar. Como la célula animal no tiene pared celular rígida, se hincha hasta reventar."
    },
    {
        "materia": "Sociales y Ciudadanas",
        "pregunta": "¿Qué es el 'Voto Programático'?",
        "opciones": ["A. Votar por un programa de televisión.", "B. La obligación de alcaldes y gobernadores de cumplir su plan de gobierno propuesto en campaña.", "C. Votar por internet.", "D. Votar obligatoriamente."],
        "respuesta": "B. La obligación de alcaldes y gobernadores de cumplir su plan de gobierno propuesto en campaña.",
        "explicacion_ia": "En Colombia, al elegir alcalde/gobernador, impones el mandato de que cumpla su programa. Si no lo hace, se puede iniciar una Revocatoria del Mandato."
    },
    {
        "materia": "Química Orgánica",
        "tema": "Isomería",
        "pregunta": "Dos moléculas tienen la misma fórmula molecular C4H10 pero diferentes puntos de ebullición. Una es el butano (lineal) y la otra el metilpropano (ramificada). ¿Por qué el isómero ramificado tiene menor punto de ebullición?",
        "opciones": ["A. Tiene menos carbonos.", "B. Al ser más esférica, tiene menor superficie de contacto, lo que debilita las fuerzas de Van der Waals entre moléculas.", "C. Es más pesado.", "D. Tiene enlaces iónicos."],
        "respuesta": "B. Al ser más esférica, tiene menor superficie de contacto, lo que debilita las fuerzas de Van der Waals entre moléculas.",
        "explicacion_ia": "Las fuerzas de dispersión de London dependen del área superficial. Las moléculas lineales se 'apilan' mejor (más contacto) que las ramificadas (esferas), requiriendo más energía para separarlas (ebullición)."
    }
    
]

def iniciar_nuevo_examen(modo, cantidad_preguntas):
    banco = banco_premium if modo == "Elite" else banco_estandar
    cantidad = min(cantidad_preguntas, len(banco))
    
    st.session_state.preguntas_examen = random.sample(banco, cantidad)
    st.session_state.indice = 0
    st.session_state.puntaje = 0
    st.session_state.temas_fallados = [] 
    st.session_state.historial_respuestas = []
    st.session_state.examen_iniciado = True
    st.session_state.respondida = False
    st.session_state.modo_actual = modo
    
    if not st.session_state.es_premium:
        st.session_state.intentos_usados += 1
        guardar_datos_usuario(st.session_state.user_id, st.session_state.intentos_usados, False)

def mostrar_analisis_inteligente(historial):
    errores = [h for h in historial if not h['c']]
    if not errores:
        st.success("🎉 ¡Excelente! No tuviste errores. Estás dominando los temas.")
        return

    st.write("### 🧠 Análisis Quirúrgico de Errores")
    st.info(f"Detectamos **{len(errores)} errores**. Hemos seleccionado consejos variados y específicos para cada pregunta fallada:")

    # --- BANCO DE TIPS (MULTITUD DE ESTRATEGIAS) ---
    tips_db = {
        "Probabilidad": ["🎲 **Estrategia:** Diferencia eventos independientes (dados) de dependientes.", "🎲 **Hack:** P(al menos 1) = 1 - P(ninguno).", "🎲 **Ojo:** 'O' suma, 'Y' multiplica."],
        "Geometría": ["📐 **Estrategia:** Área crece al cuadrado ($x^2$).", "📐 **Hack:** Dibuja siempre (Tales).", "📐 **Ojo:** Busca ternas pitagóricas."],
        "Álgebra": ["➗ **Estrategia:** Traduce el texto a ecuación.", "➗ **Hack:** Prueba las opciones de respuesta.", "➗ **Ojo:** Cuidado con los signos."],
        "Estadística": ["📊 **Estrategia:** Mediana = Centro ordenado.", "📊 **Hack:** Desviación = Dispersión.", "📊 **Ojo:** Promedio engaña con extremos."],
        "Física": ["⚛️ **Estrategia:** Suma fuerzas = ma.", "⚛️ **Hack:** DCL (Diagrama Cuerpo Libre).", "⚛️ **Ojo:** Energía se conserva."],
        "Química": ["⚗️ **Estrategia:** Balancea la ecuación.", "⚗️ **Hack:** Le Chatelier es contreras.", "⚗️ **Ojo:** Reactivo límite manda."],
        "Biología": ["🧬 **Estrategia:** Dogma Central (ADN->Prot).", "🧬 **Hack:** Mitosis=Clon, Meiosis=Sexo.", "🧬 **Ojo:** Usa Punnett."],
        "Constitución": ["📜 **Estrategia:** Tutela=Fundamental.", "📜 **Hack:** Popular=Colectivo.", "📜 **Ojo:** Estado Social de Derecho."],
        "Historia": ["🌍 **Estrategia:** Contexto > Fechas.", "🌍 **Hack:** Guerra Fría = Proxy Wars.", "🌍 **Ojo:** Frente Nacional = Bipartidismo."],
        "Lectura": ["📖 **Estrategia:** Busca la inferencia.", "📖 **Hack:** Identifica la voz (Subj/Obj).", "📖 **Ojo:** Tesis = Opinión central."],
        "Inglés": ["🇬🇧 **Estrategia:** Keywords first.", "🇬🇧 **Hack:** Time words (Yesterday/Now).", "🇬🇧 **Ojo:** Modals no llevan 'to'."]
    }

    for error in errores:
        pregunta = error['p']
        tema = pregunta.get('tema', 'General')
        
        # Lógica de selección de tip
        tip_seleccionado = pregunta.get('tip')
        if not tip_seleccionado:
            lista_tips = next((v for k, v in tips_db.items() if k in tema), ["🎓 **Refuerzo:** Revisa los conceptos fundamentales."])
            tip_seleccionado = random.choice(lista_tips)

        with st.expander(f"❌ Error en {tema}: {pregunta['pregunta'][:40]}...", expanded=True):
            st.markdown(f"**Tu respuesta:** {error['u']} | **Correcta:** {pregunta['respuesta']}")
            st.warning(f"💡 **Explicación:** {pregunta['explicacion_ia']}")
            st.success(f"{tip_seleccionado}")

# --- 6. INTERFAZ GRÁFICA ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/2232/2232688.png", width=100)
    st.header("Zona de Entrenamiento")
    st.caption(f"ID: {st.session_state.user_id}")
    
    modo = st.radio("Nivel:", ["Estándar", "🏆 Élite (Pro)"], index=0 if not st.session_state.es_premium else 1)
    st.divider()
    
    if st.session_state.es_premium:
        dias = (datetime.fromisoformat(datos_guardados["fecha_inicio"]) + timedelta(days=30) - datetime.now()).days if datos_guardados["fecha_inicio"] else 30
        st.success(f"✅ PLAN PRO ACTIVO\nVence en: {max(0, dias)} días")
        cant = st.select_slider("Preguntas:", [10, 20, 50, 100], value=20)
        st.session_state.cantidad_preguntas = cant
    else:
        st.info(f"Plan Gratuito ({st.session_state.intentos_usados}/{LIMITE_INTENTOS_GRATIS})")
        
        st.markdown("### 💎 Pásate a PRO")
        # --- BOTÓN DE PAGO ---
        st.link_button("👉 Adquirir Premium ($50.000)", LINK_DE_PAGO, type="primary")
        
        st.caption("¿Ya pagaste? Ingresa tu código:")
        codigo = st.text_input("Código de Acceso:", type="password")
        
        if st.button("Activar Plan"):
            if codigo == CODIGO_SECRETO:
                st.session_state.es_premium = True
                guardar_datos_usuario(st.session_state.user_id, st.session_state.intentos_usados, True, datetime.now().isoformat())
                st.balloons()
                st.success("¡Bienvenido al Élite!")
                time.sleep(2)
                st.rerun()
            else:
                st.error("Código inválido")
        st.session_state.cantidad_preguntas = 10

st.title("🤖 Entrenador ICFES Adaptativo 2.0")

if not st.session_state.examen_iniciado:
    if "Élite" in modo and not st.session_state.es_premium:
        st.warning("🔒 El modo Élite es solo para usuarios PRO.")
    else:
        st.markdown(f"### 🚀 Modo: {modo}")
        if st.session_state.es_premium or st.session_state.intentos_usados < LIMITE_INTENTOS_GRATIS:
            if st.button("🏁 Iniciar Simulacro"):
                iniciar_nuevo_examen("Elite" if "Élite" in modo else "Estandar", st.session_state.cantidad_preguntas)
                st.rerun()
        else:
            st.error("🚫 Intentos agotados.")

else:
    preguntas = st.session_state.preguntas_examen
    if st.session_state.indice < len(preguntas):
        p = preguntas[st.session_state.indice]
        st.progress((st.session_state.indice)/len(preguntas))
        st.caption(f"Pregunta {st.session_state.indice+1}/{len(preguntas)} | {p.get('tema', p['materia'])}")
        st.subheader(p["pregunta"])
        opcion = st.radio("Tu respuesta:", p["opciones"], key=f"p{st.session_state.indice}", disabled=st.session_state.respondida)
        
        if not st.session_state.respondida:
            if st.button("Validar"):
                st.session_state.respondida = True
                correcta = (opcion == p["respuesta"])
                if correcta: st.session_state.puntaje += 1; st.success("¡Correcto!")
                else: st.error(f"Incorrecto. Era: {p['respuesta']}"); st.session_state.temas_fallados.append(p.get("tema", p['materia']))
                st.session_state.historial_respuestas.append({"p": p, "u": opcion, "c": correcta})
                st.rerun()
        else:
            with st.expander("Explicación", expanded=True): st.info(p["explicacion_ia"])
            if st.button("Siguiente"): st.session_state.indice += 1; st.session_state.respondida = False; st.rerun()
    else:
        st.balloons()
        st.title("Resultados")
        c1, c2 = st.columns(2)
        c1.metric("Puntaje", f"{st.session_state.puntaje}/{len(preguntas)}")
        if len(preguntas) > 0: c2.metric("Efectividad", f"{int(st.session_state.puntaje/len(preguntas)*100)}%")
        
        st.divider()
        mostrar_analisis_inteligente(st.session_state.historial_respuestas)
        
        st.divider()
        if st.button("🏠 Inicio"): st.session_state.examen_iniciado = False; st.rerun()