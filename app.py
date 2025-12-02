import streamlit as st
import time
import random
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime, timedelta

# --- 1. CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Simulacro ICFES Pro", page_icon="🇨🇴", layout="wide")

# ==========================================
# ☁️ CONEXIÓN A GOOGLE SHEETS (BASE DE DATOS)
# ==========================================
def conectar_db():
    """Conecta a Google Sheets usando los secretos de Streamlit"""
    try:
        scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
        # Accedemos a los secretos que pegaste en el paso anterior
        creds_dict = st.secrets["gcp_service_account"]
        creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
        client = gspread.authorize(creds)
        # Abre tu archivo por nombre. ¡Asegúrate que se llame DB_ICFES en Google!
        return client.open("DB_ICFES")
    except Exception as e:
        st.error(f"🚨 Error conectando a la base de datos: {e}")
        st.stop() # Detiene la app si no hay conexión

# ==========================================
# 🧠 GESTIÓN DE PREGUNTAS (DESDE LA PESTAÑA 'PREGUNTAS')
# ==========================================
@st.cache_data(ttl=600) # Guarda en memoria 10 mins para no saturar Google
def cargar_banco_preguntas():
    libro = conectar_db()
    try:
        # Asegúrate de que la pestaña en el Excel se llame "PREGUNTAS"
        worksheet = libro.worksheet("PREGUNTAS")
        datos = worksheet.get_all_records()
        
        # Filtramos preguntas por nivel (ignorando mayúsculas/minúsculas)
        # Asegúrate de tener la columna 'nivel' en tu Excel
        banco_gratis = [p for p in datos if str(p.get('nivel', '')).strip().lower() == 'gratis']
        banco_premium = [p for p in datos if str(p.get('nivel', '')).strip().lower() == 'premium']
        
        # Si no hay preguntas premium cargadas aún, usamos las gratis para que no falle
        if not banco_premium: banco_premium = banco_gratis
            
        return banco_gratis, banco_premium
    except gspread.exceptions.WorksheetNotFound:
        st.error("❌ No encontré la pestaña 'PREGUNTAS' en tu Excel. Por favor créala.")
        return [], []
    except Exception as e:
        st.error(f"Error leyendo preguntas: {e}")
        return [], []

# ==========================================
# 👤 GESTIÓN DE USUARIOS (DESDE LA PESTAÑA 'USUARIOS')
# ==========================================
def gestionar_usuario(uid, accion="leer", intentos=0, es_premium=False, fecha=None):
    libro = conectar_db()
    try:
        sheet_users = libro.worksheet("USUARIOS")
    except gspread.exceptions.WorksheetNotFound:
        st.error("❌ No encontré la pestaña 'USUARIOS' en tu Excel.")
        return {"intentos": 0, "premium": False, "fecha_inicio": None}

    try:
        cell = sheet_users.find(uid) # Busca si el ID ya existe en la hoja
    except:
        cell = None

    if accion == "leer":
        # Si existe, devolvemos sus datos. Si no, datos por defecto.
        if cell:
            row = sheet_users.row_values(cell.row)
            # Suponemos orden columnas: [uid, intentos, premium, fecha]
            # Convertimos texto "TRUE"/"FALSE" a booleano real
            estado_premium = str(row[2]).upper() == "TRUE"
            
            # Revisar si el premium venció (30 días)
            fecha_guardada = row[3]
            if estado_premium and fecha_guardada and fecha_guardada != "None":
                try:
                    inicio = datetime.fromisoformat(fecha_guardada)
                    if (datetime.now() - inicio).days >= 30:
                        st.toast("⚠️ Tu suscripción ha vencido.", icon="📅")
                        # Actualizamos a False en la nube
                        gestionar_usuario(uid, "guardar", int(row[1]), False, None)
                        return {"intentos": int(row[1]), "premium": False, "fecha_inicio": None}
                except: pass

            return {"intentos": int(row[1]), "premium": estado_premium, "fecha_inicio": fecha_guardada}
        else:
            return {"intentos": 0, "premium": False, "fecha_inicio": None}

    elif accion == "guardar":
        # Preparamos datos para escribir
        prem_str = "TRUE" if es_premium else "FALSE"
        fecha_str = str(fecha) if fecha else "None"
        
        if cell:
            # Si el usuario ya existe, actualizamos solo sus celdas
            # Col 2: Intentos, Col 3: Premium, Col 4: Fecha
            sheet_users.update_cell(cell.row, 2, str(intentos))
            sheet_users.update_cell(cell.row, 3, prem_str)
            if fecha: sheet_users.update_cell(cell.row, 4, fecha_str)
        else:
            # Si es nuevo, creamos una fila nueva al final
            sheet_users.append_row([uid, str(intentos), prem_str, fecha_str])

# ==========================================
# ⚙️ LÓGICA DE LA APLICACIÓN
# ==========================================

# 1. Identificar Usuario
if "uid" not in st.query_params: 
    st.query_params["uid"] = str(random.randint(100000, 999999))
st.session_state.user_id = st.query_params["uid"]

# 2. Cargar Datos del Usuario desde la Nube
if "datos_usuario" not in st.session_state:
    st.session_state.datos_usuario = gestionar_usuario(st.session_state.user_id, "leer")

# 3. Variables de Sesión
LIMITE_GRATIS = 3
if 'examen_iniciado' not in st.session_state: st.session_state.examen_iniciado = False
if 'es_premium' not in st.session_state: st.session_state.es_premium = st.session_state.datos_usuario["premium"]
if 'intentos_usados' not in st.session_state: st.session_state.intentos_usados = st.session_state.datos_usuario["intentos"]

# 4. Cargar el Banco de Preguntas
BANCO_GRATIS, BANCO_PREMIUM = cargar_banco_preguntas()

# --- BARRA LATERAL ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/2232/2232688.png", width=80)
    st.title("Panel de Control")
    st.caption(f"Usuario ID: {st.session_state.user_id}")
    
    modo_seleccionado = st.radio("Nivel:", ["Estándar (Gratis)", "🏆 Élite (Premium)"], 
                                 index=1 if st.session_state.es_premium else 0)
    
    st.divider()
    
    if st.session_state.es_premium:
        st.success("✅ ERES PREMIUM")
        cant_preguntas = st.slider("Cantidad de preguntas:", 5, 50, 10)
    else:
        intentos_restantes = LIMITE_GRATIS - st.session_state.intentos_usados
        st.info(f"Plan Gratuito: {max(0, intentos_restantes)} intentos restantes")
        st.markdown("### 🔓 Desbloquear Todo")
        st.write("Acceso ilimitado + Análisis inteligente.")
        codigo = st.text_input("Código de acceso:", type="password")
        if st.button("Activar Premium"):
            if codigo == "ICFES2025": # Tu código secreto
                st.session_state.es_premium = True
                gestionar_usuario(st.session_state.user_id, "guardar", st.session_state.intentos_usados, True, datetime.now().isoformat())
                st.balloons()
                st.success("¡Bienvenido al nivel Élite!")
                time.sleep(2)
                st.rerun()
            else:
                st.error("Código incorrecto")
        cant_preguntas = 10

# --- PANTALLA PRINCIPAL ---
st.title("🤖 Entrenador ICFES Inteligente 2.0")

def iniciar_examen():
    # Elegir banco según el modo
    banco = BANCO_PREMIUM if "Élite" in modo_seleccionado else BANCO_GRATIS
    
    if not banco:
        st.error("⚠️ El banco de preguntas está vacío. Revisa tu Excel.")
        return

    # Validar permisos
    if "Élite" in modo_seleccionado and not st.session_state.es_premium:
        st.warning("🔒 El modo Élite es exclusivo para usuarios Premium.")
        return
    
    if not st.session_state.es_premium and st.session_state.intentos_usados >= LIMITE_GRATIS:
        st.error("🚫 Has agotado tus intentos gratuitos. Activa el plan Premium.")
        return

    # Configurar examen
    seleccion = random.sample(banco, min(cant_preguntas, len(banco)))
    
    # Formatear para que la app entienda las columnas del Excel
    preguntas_formateadas = []
    for p in seleccion:
        # Aquí mapeamos las columnas de tu Excel a variables
        preguntas_formateadas.append({
            "materia": p.get('materia', 'General'),
            "tema": p.get('tema', 'General'),
            "pregunta": p.get('pregunta', 'Pregunta sin texto'),
            "opciones": [
                str(p.get('opcion_a', '')), 
                str(p.get('opcion_b', '')), 
                str(p.get('opcion_c', '')), 
                str(p.get('opcion_d', ''))
            ],
            "respuesta": str(p.get('respuesta', '')),
            "explicacion": p.get('explicacion', 'Sin explicación disponible'),
            "consejo": p.get('consejo', 'Revisa el tema general.')
        })

    st.session_state.quiz_data = preguntas_formateadas
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
    st.markdown("""
    Bienvenido al simulador más avanzado.  
    **Características:**
    * 🧠 Preguntas adaptativas.
    * ☁️ Guardado en la nube.
    * 💡 Retroalimentación inmediata con consejos de estudio.
    """)
    if st.button("🚀 Comenzar Simulacro", type="primary"):
        iniciar_examen()

else:
    # --- LÓGICA DEL EXAMEN ---
    datos = st.session_state.quiz_data
    idx = st.session_state.indice
    
    if idx < len(datos):
        p_actual = datos[idx]
        
        # Barra de progreso
        st.progress((idx + 1) / len(datos))
        st.caption(f"Pregunta {idx + 1} de {len(datos)} | 📚 {p_actual['materia']} - {p_actual['tema']}")
        
        st.markdown(f"### {p_actual['pregunta']}")
        
        # Mostrar opciones
        opcion = st.radio("Selecciona tu respuesta:", p_actual['opciones'], key=f"q{idx}", disabled=st.session_state.respondida)
        
        # Botón Validar
        if not st.session_state.respondida:
            if st.button("Validar Respuesta"):
                st.session_state.respondida = True
                if opcion == p_actual['respuesta']:
                    st.success("✅ ¡Correcto!")
                    st.session_state.puntaje += 1
                    with st.expander("Ver explicación"):
                        st.info(p_actual['explicacion'])
                else:
                    st.error(f"❌ Incorrecto. La respuesta era: {p_actual['respuesta']}")
                    # Guardamos el error para el reporte final
                    st.session_state.errores.append(p_actual)
                    
                    # --- AQUÍ ESTÁ TU REQUISITO DE RETROALIMENTACIÓN ---
                    st.markdown("---")
                    col1, col2 = st.columns(2)
                    with col1:
                        st.warning("💡 **Explicación del error:**")
                        st.write(p_actual['explicacion'])
                    with col2:
                        st.info("📘 **¿Qué debes estudiar?**")
                        st.write(p_actual['consejo'])
                    st.markdown("---")
                
                st.rerun()
        else:
            # Botón Siguiente
            if st.button("Siguiente Pregunta ➡️"):
                st.session_state.indice += 1
                st.session_state.respondida = False
                st.rerun()
    else:
        # --- PANTALLA FINAL DE RESULTADOS ---
        st.balloons()
        st.title("📊 Resultados Finales")
        
        score = st.session_state.puntaje
        total = len(datos)
        porcentaje = (score / total) * 100
        
        col1, col2, col3 = st.columns(3)
        col1.metric("Puntaje", f"{score}/{total}")
        col2.metric("Efectividad", f"{porcentaje:.1f}%")
        
        if porcentaje >= 80:
            col3.success("¡Excelente desempeño! 🌟")
        elif porcentaje >= 60:
            col3.warning("Buen trabajo, pero puedes mejorar. 📈")
        else:
            col3.error("Necesitas reforzar varios temas. 📚")
            
        if st.session_state.errores:
            st.divider()
            st.subheader("📝 Plan de Estudio Personalizado")
            st.write("Basado en tus errores, enfócate en estos temas:")
            
            for err in st.session_state.errores:
                with st.expander(f"🔴 Fallaste en: {err['tema']} ({err['materia']})"):
                    st.markdown(f"**Pregunta:** {err['pregunta']}")
                    st.info(f"**Consejo Clave:** {err['consejo']}")
        
        st.divider()
        if st.button("🏠 Volver al Inicio"):
            st.session_state.examen_iniciado = False
            st.rerun()