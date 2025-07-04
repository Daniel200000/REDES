import streamlit as st
import pandas as pd
import random
from datetime import datetime, timedelta

# Paleta de colores
PRIMARY = "#4F46E5"  # Azul-violeta
BG = "#F7F8FA"       # Fondo claro
ACCENT = "#6366F1"   # Acento
TEXT = "#22223B"

st.set_page_config(page_title="OhMyWatts!", layout="centered")
st.markdown(f"""
<style>
    body {{background-color: {BG};}}
    .title {{color: {PRIMARY}; font-size: 2.2rem; font-weight: bold; margin-bottom: 0.5rem;}}
    .boleta {{background: #f3f3ff; border-radius: 10px; padding: 1.5rem; margin-top: 1.5rem; box-shadow: 0 2px 8px #e0e0e0;}}
    .boleta-title {{color: {PRIMARY}; font-size: 1.5rem; font-weight: bold; margin-bottom: 1rem;}}
    .boleta-total {{font-size: 1.2rem; font-weight: bold; color: {TEXT};}}
    .nav-bar {{display: flex; justify-content: space-around; align-items: center; background: #fff; border-top: 2px solid #e0e0e0; padding: 0.5rem 0; position: fixed; bottom: 0; left: 0; width: 100vw; z-index: 100;}}
    .nav-icon {{font-size: 2rem; color: {PRIMARY};}}
    .stDataFrame, .stTable {{background: #fff; border-radius: 8px;}}
    .stButton>button {{background-color: {PRIMARY}; color: white; border-radius: 8px; border: none;}}
    .stButton>button:hover {{background-color: {ACCENT};}}
</style>
""", unsafe_allow_html=True)

# Parámetros
N_ENCHUFES = 5
TARIFA = 80  # $/kWh

# Estado inicial de nombres/dispositivos
if 'nombres' not in st.session_state:
    st.session_state['nombres'] = [
        ["Enchufe 1", "Hervidor"],
        ["Enchufe 2", "Refrigerador"],
        ["Enchufe 3", "Lavadora"],
        ["Enchufe 4", "Microondas"],
        ["Enchufe 5", "Computador"]
    ]

# Estado de encendido/apagado
if 'estados' not in st.session_state:
    st.session_state['estados'] = [True]*N_ENCHUFES

# Simulación de datos (función para permitir refresco)
def simular_datos():
    hoy = datetime.now()
    dias = [(hoy - timedelta(days=i)).strftime('%d-%b') for i in range(29, -1, -1)]
    datos = []
    for _ in range(N_ENCHUFES):
        consumo_diario = [round(random.uniform(0.5, 3.5), 2) for _ in dias]
        datos.append(consumo_diario)
    return datos, dias

if 'datos' not in st.session_state or st.button('Actualizar datos'):
    st.session_state['datos'], st.session_state['dias'] = simular_datos()

datos = st.session_state['datos']
dias = st.session_state['dias']

# Título
st.markdown(f'<div class="title">OhMyWatts!</div>', unsafe_allow_html=True)

# Edición de nombres/dispositivos
tabla_edit = []
col1, col2 = st.columns(2)
for i in range(N_ENCHUFES):
    with col1 if i < N_ENCHUFES//2+N_ENCHUFES%2 else col2:
        nombre = st.text_input(f"Nombre Enchufe {i+1}", st.session_state['nombres'][i][0], key=f"nombre_{i}")
        dispositivo = st.text_input(f"Dispositivo {i+1}", st.session_state['nombres'][i][1], key=f"disp_{i}")
        st.session_state['nombres'][i] = [nombre, dispositivo]

# Encendido/apagado y tabla
st.markdown("<b>Estado y consumo actual</b>", unsafe_allow_html=True)
tabla = []
col_estado = st.columns(N_ENCHUFES)
for i in range(N_ENCHUFES):
    estado = st.session_state['estados'][i]
    consumo = datos[i][-1] if estado else 0.0
    btn = col_estado[i].button("🔌 Encendido" if estado else "❌ Apagado", key=f"btn_{i}")
    if btn:
        st.session_state['estados'][i] = not estado
        st.rerun()
    tabla.append({
        "Enchufe": st.session_state['nombres'][i][0],
        "Dispositivo": st.session_state['nombres'][i][1],
        "Estado": "Encendido" if st.session_state['estados'][i] else "Apagado",
        "Consumo actual (kWh)": f"{consumo:.2f}"
    })
st.table(pd.DataFrame(tabla))

# Selector de gráfico y enchufe
st.markdown("<b>Consumo diario de los últimos 30 días</b>", unsafe_allow_html=True)
tipo_graf = st.selectbox("Tipo de gráfico", ["Líneas", "Barras"])
opciones = ["Todos"] + [st.session_state['nombres'][i][0] for i in range(N_ENCHUFES)]
sel_enchufe = st.selectbox("Selecciona enchufe", opciones)

# Datos para gráfico
if sel_enchufe == "Todos":
    df_graf = pd.DataFrame({
        st.session_state['nombres'][i][0]: [d if st.session_state['estados'][i] else 0 for d in datos[i]]
        for i in range(N_ENCHUFES)
    }, index=dias)
else:
    idx = opciones.index(sel_enchufe)-1
    df_graf = pd.DataFrame({
        st.session_state['nombres'][idx][0]: [d if st.session_state['estados'][idx] else 0 for d in datos[idx]]
    }, index=dias)

df_graf.index.name = "Día"
if tipo_graf == "Líneas":
    st.line_chart(df_graf, use_container_width=True)
else:
    st.bar_chart(df_graf, use_container_width=True)

# Consumo total de la casa
consumo_total_diario = [sum([datos[i][j] if st.session_state['estados'][i] else 0 for i in range(N_ENCHUFES)]) for j in range(30)]
consumo_total_mes = sum(consumo_total_diario)
costo_total = consumo_total_mes * TARIFA
st.markdown(f"<b>Consumo total de la casa (mes):</b> {consumo_total_mes:.2f} kWh &nbsp;&nbsp;|&nbsp;&nbsp; <b>${costo_total:,.0f}</b>", unsafe_allow_html=True)

# Boleta del mes pasado
st.markdown('<div class="boleta">', unsafe_allow_html=True)
st.markdown(f'<div class="boleta-title">Boleta del mes pasado</div>', unsafe_allow_html=True)
tabla_boleta = pd.DataFrame([
    {"Enchufe": st.session_state['nombres'][i][0], "Dispositivo": st.session_state['nombres'][i][1], "Total kWh": f"{sum([d if st.session_state['estados'][i] else 0 for d in datos[i]]):.2f}", "Total $": f"${sum([d if st.session_state['estados'][i] else 0 for d in datos[i]])*TARIFA:,.0f}"}
    for i in range(N_ENCHUFES)
])
st.dataframe(tabla_boleta, hide_index=True, use_container_width=True)
st.markdown(f'<div class="boleta-total">Total mes: <b>{consumo_total_mes:.2f} kWh</b> &nbsp;&nbsp;|&nbsp;&nbsp; <b>${costo_total:,.0f}</b></div>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# Barra de navegación inferior
st.markdown(f"""
<div class="nav-bar">
    <span class="nav-icon">&#8592;</span>
    <span class="nav-icon">&#8962;</span>
    <span class="nav-icon">&#128100;</span>
</div>
""", unsafe_allow_html=True) 