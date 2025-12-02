import streamlit as st
import time
import random
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime, timedelta

# --- 1. CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Simulacro ICFES Pro", page_icon="🇨🇴", layout="wide")

# --- CONSTANTES DE NEGOCIO ---
CODIGO_SECRETO = "ICFES2025"
LINK_DE_PAGO = "https://mpago.li/1goqyK6"
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
# 🧠 GESTIÓN DE PREGUNTAS
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
        
        if not banco_premium: banco_premium = banco_gratis
        return banco_gratis, banco_premium
    except:
        return [], []

# ==========================================
# 👤 GESTIÓN DE USUARIOS
# ==========================================
def gestionar_usuario(uid, accion="leer", intentos=0, es_premium=False, fecha=None):
    libro = conectar_db()
    try:
        sheet_users = libro.worksheet("USUARIOS")
    except:
        st.error("Falta la pestaña USUARIOS en el Excel.")
        return {"intentos": 0, "premium": False, "fecha_inicio": None}

    try:
        cell = sheet_users.find(uid)
    except:
        cell = None

    if accion == "leer":
        if cell:
            row = sheet_users.row_values(cell.row)
            # row = [uid, intentos, premium, fecha]
            estado_premium = str(row[2]).upper() == "TRUE"
            
            # Verificar vencimiento (30 días)
            fecha_guardada = row[3]
            if estado_premium and fecha_guardada and fecha_guardada != "None":
                try:
                    inicio = datetime.fromisoformat(fecha_guardada)
                    if (datetime.now() - inicio).days >= 30:
                        st.toast("⚠️ Tu suscripción ha vencido.", icon="📅")
                        gestionar_usuario(uid, "guardar", int(row[1]), False, None)
                        return {"intentos": int(row[1]), "premium": False, "fecha_inicio": None}
                except: pass

            return {"intentos": int(row[1]), "premium": estado_premium, "fecha_inicio": fecha_guardada}
        else:
            return {"intentos": 0, "premium": False, "fecha_inicio": None}

    elif accion == "guardar":
        prem_str = "TRUE" if es_premium else "FALSE"
        fecha_str = str(fecha) if fecha else "None"
        
        if cell:
            sheet_users.update_cell(cell.row, 2, str(intentos))
            sheet_users.update_cell(cell.row, 3, prem_str)
            if fecha: sheet_users.update_cell(cell.row, 4, fecha_str)
        else:
            sheet_users.append_row([uid, str(intentos), prem_str, fecha_str])

# ==========================================
# ⚙️ LÓGICA DE LA APP
# ==========================================

# 1. Identificar Usuario
if "uid" not in st.query_params: 
    st.query_params["uid"] = str(random.randint(100000, 999999))
st.session_state.user_id = st.query_params["uid"]

# 2. Cargar Datos
if "datos_usuario" not in st.session_state:
    st.session_state.datos_usuario = gestionar_usuario(st.session_state.user_id, "leer")

# 3. Inicializar Variables
if 'examen_iniciado' not in st.session_state: st.session_state.examen_iniciado = False
if 'es_premium' not in st.session_state: st.session_state.es_premium = st.session_state.datos_usuario["premium"]
if 'intentos_usados' not in st.session_state: st.session_state.intentos_usados = st.session_state.datos_usuario["intentos"]

BANCO_GRATIS, BANCO_PREMIUM = cargar_banco_preguntas()

# --- BARRA LATERAL (AQUÍ ESTÁ TU BOTÓN DE PAGO) ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/2232/2232688.png", width=80)
    st.header("Zona de Entrenamiento")
    st.caption(f"ID: {st.session_state.user_id}")
    
    modo = st.radio("Nivel:", ["Estándar", "🏆 Élite (Pro)"], index=1 if st.session_state.es_premium else 0)
    st.divider()
    
    if st.session_state.es_premium:
        # VISTA PARA USUARIOS PREMIUM
        dias = 30 # Calculo simplificado visual
        if st.session_state.datos_usuario["fecha_inicio"]:
            try:
                ini = datetime.fromisoformat(st.session_state.datos_usuario["fecha_inicio"])
                dias = 30 - (datetime.now() - ini).days
            except: pass
            
        st.success(f"✅ PLAN PRO ACTIVO\nVence en: {max(0, dias)} días")
        cant_preguntas = st.select_slider("Preguntas:", [10, 20, 50, 100], value=20)
    else:
        # VISTA PARA USUARIOS GRATIS
        st.info(f"Plan Gratuito ({st.session_state.intentos_usados}/{LIMITE_GRATIS})")
        
        st.markdown("### 💎 Pásate a PRO")
        st.markdown("Desbloquea preguntas Élite y análisis profundo.")
        
        # --- BOTÓN DE PAGO RESTAURADO ---
        st.link_button("👉 Adquirir Premium ($20.000)", LINK_DE_PAGO, type="primary")
        
        st.caption("¿Ya pagaste? Ingresa tu código:")
        codigo_input = st.text_input("Código de Acceso:", type="password")
        
        if st.button("Activar Plan"):
            if codigo_input == CODIGO_SECRETO:
                st.session_state.es_premium = True
                # Guardamos en Google Sheets que ya es Premium
                gestionar_usuario(
                    st.session_state.user_id, 
                    "guardar", 
                    st.session_state.intentos_usados, 
                    True, 
                    datetime.now().isoformat()
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
        st.error("El banco de preguntas está vacío.")
        return

    seleccion = random.sample(banco, min(cant_preguntas, len(banco)))
    
    # Formatear preguntas del Excel
    preguntas_formateadas = []
    for p in seleccion:
        preguntas_formateadas.append({
            "materia": p.get('materia', 'General'),
            "tema": p.get('tema', 'General'),
            "pregunta": p.get('pregunta', ''),
            "opciones": [str(p.get('opcion_a','')), str(p.get('opcion_b','')), str(p.get('opcion_c','')), str(p.get('opcion_d',''))],
            "respuesta": str(p.get('respuesta', '')),
            "explicacion": p.get('explicacion', ''),
            "consejo": p.get('consejo', '')
        })

    st.session_state.preguntas_examen = preguntas_formateadas
    st.session_state.indice = 0
    st.session_state.puntaje = 0
    st.session_state.errores = []
    st.session_state.examen_iniciado = True
    st.session_state.respondida = False
    
    if not st.session_state.es_premium:
        st.session_state.intentos_usados += 1
        gestionar_usuario(st.session_state.user_id, "guardar", st.session_state.intentos_usados, False)
    st.rerun()

if not st.session_state.examen_iniciado:
    st.write("Bienvenido. Configura tu examen en el panel izquierdo.")
    if st.button("🏁 Iniciar Simulacro", type="primary"):
        iniciar_examen_func()

else:
    # Lógica del Quiz
    preguntas = st.session_state.preguntas_examen
    if st.session_state.indice < len(preguntas):
        p = preguntas[st.session_state.indice]
        st.progress((st.session_state.indice + 1) / len(preguntas))
        st.caption(f"Pregunta {st.session_state.indice+1}/{len(preguntas)} | {p['materia']}")
        st.markdown(f"### {p['pregunta']}")
        
        opcion = st.radio("Tu respuesta:", p["opciones"], key=f"p{st.session_state.indice}", disabled=st.session_state.respondida)
        
        if not st.session_state.respondida:
            if st.button("Validar"):
                st.session_state.respondida = True
                if opcion == p["respuesta"]:
                    st.success("✅ ¡Correcto!")
                    st.session_state.puntaje += 1
                    with st.expander("Ver explicación"):
                        st.info(p["explicacion"])
                else:
                    st.error(f"❌ Era: {p['respuesta']}")
                    st.session_state.errores.append(p)
                    # Retroalimentación
                    col1, col2 = st.columns(2)
                    col1.warning(f"💡 **Explicación:**\n{p['explicacion']}")
                    col2.info(f"📚 **Estudia esto:**\n{p['consejo']}")
                st.rerun()
        else:
            if st.button("Siguiente ➡️"):
                st.session_state.indice += 1
                st.session_state.respondida = False
                st.rerun()
    else:
        st.balloons()
        st.title("📊 Resultados")
        st.metric("Puntaje Final", f"{st.session_state.puntaje}/{len(preguntas)}")
        
        if st.session_state.errores:
            st.divider()
            st.subheader("Repaso Personalizado")
            for err in st.session_state.errores:
                with st.expander(f"🔴 {err['tema']}"):
                    st.write(f"**Pregunta:** {err['pregunta']}")
                    st.info(f"**Consejo:** {err['consejo']}")
        
        if st.button("🏠 Volver al Inicio"):
            st.session_state.examen_iniciado = False
            st.rerun()