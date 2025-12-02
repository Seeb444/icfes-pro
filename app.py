import streamlit as st
import time
import random
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime, timedelta

# --- 1. CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Simulacro ICFES Pro", page_icon="🇨🇴", layout="wide")

# --- CONSTANTES DE NEGOCIO ---
# Agrega aquí los códigos que quieras habilitar
CODIGOS_VALIDOS = ["ICFES2025", "PROMO_LANZAMIENTO", "ESTUDIANTE_VIP"] 
LINK_DE_PAGO = "https://mpago.li/1goqyK6" # Tu link de pago
LIMITE_GRATIS = 3

# ==========================================
# ☁️ CONEXIÓN A GOOGLE SHEETS (BASE DE DATOS)
# ==========================================
def conectar_db():
    """Conecta a Google Sheets usando los secretos de Streamlit"""
    try:
        scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
        creds_dict = st.secrets["gcp_service_account"]
        creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
        client = gspread.authorize(creds)
        return client.open("DB_ICFES")
    except Exception as e:
        st.error(f"🚨 Error conectando a la base de datos: {e}")
        st.stop()

# ==========================================
# 🧠 GESTIÓN DE PREGUNTAS (DESDE LA NUBE)
# ==========================================
@st.cache_data(ttl=600)
def cargar_banco_preguntas():
    libro = conectar_db()
    try:
        worksheet = libro.worksheet("PREGUNTAS")
        datos = worksheet.get_all_records()
        
        # Filtramos preguntas por nivel
        banco_gratis = [p for p in datos if str(p.get('nivel', '')).strip().lower() == 'gratis']
        banco_premium = [p for p in datos if str(p.get('nivel', '')).strip().lower() == 'premium']
        
        # Si no hay premium, rellenamos con gratis por seguridad
        if not banco_premium: banco_premium = banco_gratis
        return banco_gratis, banco_premium
    except:
        return [], []

# ==========================================
# 👤 GESTIÓN DE USUARIOS (CON HISTORIAL DE CÓDIGOS)
# ==========================================
def gestionar_usuario(uid, accion="leer", intentos=0, es_premium=False, fecha=None, nuevo_codigo=None):
    libro = conectar_db()
    try:
        sheet_users = libro.worksheet("USUARIOS")
    except:
        st.error("Falta la pestaña USUARIOS en el Excel.")
        return {"intentos": 0, "premium": False, "fecha_inicio": None, "codigos": ""}

    try:
        cell = sheet_users.find(uid)
    except:
        cell = None

    if accion == "leer":
        if cell:
            row = sheet_users.row_values(cell.row)
            # row: [uid, intentos, premium, fecha, codigos_usados]
            while len(row) < 5: row.append("") # Evitar error si falta columna
            
            estado_premium = str(row[2]).upper() == "TRUE"
            historial_codigos = str(row[4])
            
            # Verificar vencimiento (30 días)
            fecha_guardada = row[3]
            if estado_premium and fecha_guardada and fecha_guardada != "None":
                try:
                    inicio = datetime.fromisoformat(fecha_guardada)
                    if (datetime.now() - inicio).days >= 30:
                        st.toast("⚠️ Tu suscripción ha vencido.", icon="📅")
                        # Quitamos premium pero MANTENEMOS el historial
                        gestionar_usuario(uid, "guardar", int(row[1]), False, None)
                        return {"intentos": int(row[1]), "premium": False, "fecha_inicio": None, "codigos": historial_codigos}
                except: pass

            return {"intentos": int(row[1]), "premium": estado_premium, "fecha_inicio": fecha_guardada, "codigos": historial_codigos}
        else:
            return {"intentos": 0, "premium": False, "fecha_inicio": None, "codigos": ""}

    elif accion == "guardar":
        prem_str = "TRUE" if es_premium else "FALSE"
        fecha_str = str(fecha) if fecha else "None"
        
        if cell:
            # Recuperar historial actual para no borrarlo
            try:
                codigos_actuales = sheet_users.cell(cell.row, 5).value or ""
            except: 
                codigos_actuales = ""
            
            if nuevo_codigo:
                # Si ya había códigos, agrega coma. Si no, pone el nuevo.
                if codigos_actuales:
                    codigos_actuales = f"{codigos_actuales},{nuevo_codigo}"
                else:
                    codigos_actuales = nuevo_codigo
            
            # Actualizamos celdas
            sheet_users.update_cell(cell.row, 2, str(intentos))
            sheet_users.update_cell(cell.row, 3, prem_str)
            if fecha: sheet_users.update_cell(cell.row, 4, fecha_str)
            sheet_users.update_cell(cell.row, 5, codigos_actuales) # Columna 5
        else:
            # Usuario nuevo
            codigos_iniciales = nuevo_codigo if nuevo_codigo else ""
            sheet_users.append_row([uid, str(intentos), prem_str, fecha_str, codigos_iniciales])

# ==========================================
# ⚙️ LÓGICA PRINCIPAL
# ==========================================

# 1. Identificar Usuario
if "uid" not in st.query_params: 
    st.query_params["uid"] = str(random.randint(100000, 999999))
st.session_state.user_id = st.query_params["uid"]

# 2. Cargar Datos del Usuario (Solo una vez por sesión)
if "datos_usuario" not in st.session_state:
    st.session_state.datos_usuario = gestionar_usuario(st.session_state.user_id, "leer")

# 3. Inicializar Variables de Sesión
if 'examen_iniciado' not in st.session_state: st.session_state.examen_iniciado = False
if 'es_premium' not in st.session_state: st.session_state.es_premium = st.session_state.datos_usuario["premium"]
if 'intentos_usados' not in st.session_state: st.session_state.intentos_usados = st.session_state.datos_usuario["intentos"]

# 4. Cargar Preguntas
BANCO_GRATIS, BANCO_PREMIUM = cargar_banco_preguntas()

# --- BARRA LATERAL ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/2232/2232688.png", width=80)
    st.header("Zona de Entrenamiento")
    st.caption(f"ID: {st.session_state.user_id}")
    
    # Selector de Modo
    index_modo = 1 if st.session_state.es_premium else 0
    modo = st.radio("Nivel:", ["Estándar", "🏆 Élite (Pro)"], index=index_modo)
    st.divider()
    
    if st.session_state.es_premium:
        # VISTA PREMIUM
        dias = 30
        if st.session_state.datos_usuario["fecha_inicio"]:
            try:
                ini = datetime.fromisoformat(str(st.session_state.datos_usuario["fecha_inicio"]))
                dias = 30 - (datetime.now() - ini).days
            except: pass
            
        st.success(f"✅ PLAN PRO ACTIVO\nVence en: {max(0, dias)} días")
        cant_preguntas = st.select_slider("Preguntas:", [10, 20, 50, 100], value=20)
    else:
        # VISTA GRATIS
        restantes = max(0, LIMITE_GRATIS - st.session_state.intentos_usados)
        st.info(f"Plan Gratuito ({restantes} intentos restantes)")
        
        st.markdown("### 💎 Pásate a PRO")
        st.markdown("Desbloquea preguntas Élite y análisis profundo.")
        
        # --- BOTÓN DE PAGO ACTUALIZADO A $50.000 ---
        st.link_button("👉 Adquirir Premium ($50.000)", LINK_DE_PAGO, type="primary")
        
        # ACTIVACIÓN DE CÓDIGO
        st.divider()
        st.caption("¿Ya tienes tu código? Ingrésalo:")
        codigo_input = st.text_input("Código de Acceso:", type="password")
        
        if st.button("Activar Plan"):
            codigo_limpio = codigo_input.strip().upper()
            historial = str(st.session_state.datos_usuario.get("codigos", ""))
            
            if codigo_limpio in historial:
                st.error("🚫 Este código ya fue usado por ti.")
            elif codigo_limpio in CODIGOS_VALIDOS:
                st.session_state.es_premium = True
                
                # Guardar en nube: Premium + Fecha + Registrar Código
                gestionar_usuario(
                    st.session_state.user_id, 
                    "guardar", 
                    st.session_state.intentos_usados, 
                    True, 
                    datetime.now().isoformat(),
                    nuevo_codigo=codigo_limpio
                )
                
                st.balloons()
                st.success("¡Bienvenido al Élite!")
                time.sleep(2)
                st.rerun()
            else:
                st.error("Código inválido")
        
        cant_preguntas = 10

# --- PANTALLA PRINCIPAL ---
st.title("🤖 Entrenador ICFES Inteligente 2.0")

def iniciar_examen_func():
    banco = BANCO_PREMIUM if "Élite" in modo else BANCO_GRATIS
    
    if "Élite" in modo and not st.session_state.es_premium:
        st.warning("🔒 El modo Élite es solo para usuarios PRO.")
        return

    if not st.session_state.es_premium and st.session_state.intentos_usados >= LIMITE_GRATIS:
        st.error("🚫 Intentos agotados. Adquiere Premium para continuar.")
        return

    if not banco:
        st.error("El banco de preguntas está vacío o no se pudo cargar.")
        return

    # Selección aleatoria
    seleccion = random.sample(banco, min(cant_preguntas, len(banco)))
    
    # Formatear preguntas
    preguntas_formateadas = []
    for p in seleccion:
        preguntas_formateadas.append({
            "materia": p.get('materia', 'General'),
            "tema": p.get('tema', 'General'),
            "pregunta": p.get('pregunta', 'Pregunta sin texto'),
            "opciones": [
                str(p.get('opcion_a','')), str(p.get('opcion_b','')), 
                str(p.get('opcion_c','')), str(p.get('opcion_d',''))
            ],
            "respuesta": str(p.get('respuesta', '')),
            "explicacion": p.get('explicacion', 'Sin explicación'),
            "consejo": p.get('consejo', 'Revisa el tema.')
        })

    st.session_state.preguntas_examen = preguntas_formateadas
    st.session_state.indice = 0
    st.session_state.puntaje = 0
    st.session_state.errores = []
    st.session_state.examen_iniciado = True
    st.session_state.respondida = False
    
    # Consumir intento si es gratis
    if not st.session_state.es_premium:
        st.session_state.intentos_usados += 1
        gestionar_usuario(st.session_state.user_id, "guardar", st.session_state.intentos_usados, False)
    st.rerun()

if not st.session_state.examen_iniciado:
    st.write("Bienvenido a tu simulador. Configura tu examen en el panel izquierdo.")
    if st.button("🏁 Iniciar Simulacro", type="primary"):
        iniciar_examen_func()

else:
    # --- LOGICA DEL QUIZ (CORREGIDA) ---
    preguntas = st.session_state.preguntas_examen
    if st.session_state.indice < len(preguntas):
        p = preguntas[st.session_state.indice]
        
        # Barra de progreso
        st.progress((st.session_state.indice + 1) / len(preguntas))
        st.caption(f"Pregunta {st.session_state.indice+1}/{len(preguntas)} | 📚 {p['materia']} - {p['tema']}")
        
        st.markdown(f"### {p['pregunta']}")
        
        opcion = st.radio("Selecciona tu respuesta:", p["opciones"], key=f"p{st.session_state.indice}", disabled=st.session_state.respondida)
        
        # --- ZONA DE ACCIONES ---
        
        # ESTADO 1: Aún no ha respondido
        if not st.session_state.respondida:
            if st.button("Validar Respuesta"):
                st.session_state.respondida = True
                if opcion == p["respuesta"]:
                    st.session_state.puntaje += 1
                else:
                    st.session_state.errores.append(p)
                st.rerun() # Recargamos para mostrar la explicación fija

        # ESTADO 2: Ya respondió (Mostrar Retroalimentación Fija)
        else:
            es_correcta = (opcion == p["respuesta"])
            
            if es_correcta:
                st.success("✅ ¡Correcto!")
                with st.expander("Ver explicación", expanded=True):
                    st.info(f"💡 **Explicación:** {p['explicacion']}")
            else:
                st.error(f"❌ Incorrecto. La respuesta correcta era: {p['respuesta']}")
                
                # Mostrar Retroalimentación completa visible
                st.markdown("---")
                col1, col2 = st.columns(2)
                with col1:
                    st.warning(f"💡 **¿Por qué fallaste?**\n\n{p['explicacion']}")
                with col2:
                    st.info(f"📘 **Consejo de Estudio:**\n\n{p['consejo']}")
                st.markdown("---")

            # Botón para avanzar
            if st.button("Siguiente Pregunta ➡️"):
                st.session_state.indice += 1
                st.session_state.respondida = False
                st.rerun()

    else:
        # --- PANTALLA FINAL ---
        st.balloons()
        st.title("📊 Resultados Finales")
        
        score = st.session_state.puntaje
        total = len(preguntas)
        st.metric("Puntaje", f"{score}/{total}", delta=f"{int(score/total*100)}% Efectividad")
        
        if st.session_state.errores:
            st.divider()
            st.subheader("📝 Plan de Mejora")
            for err in st.session_state.errores:
                with st.expander(f"🔴 Fallo en: {err['tema']}"):
                    st.write(f"**Pregunta:** {err['pregunta']}")
                    st.info(f"**Consejo:** {err['consejo']}")
        
        st.divider()
        if st.button("🏠 Volver al Inicio"):
            st.session_state.examen_iniciado = False
            st.rerun()