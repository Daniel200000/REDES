import streamlit as st
import pandas as pd
import random
from datetime import datetime, timedelta

st.set_page_config(page_title="OhMyWatts!", layout="centered")
st.markdown("""
<style>
    .title {color: #3a1aff; font-size: 2.2rem; font-weight: bold; margin-bottom: 0.5rem;}
    .nav-bar {display: flex; justify-content: space-around; align-items: center; background: #fff; border-top: 2px solid #e0e0e0; padding: 0.5rem 0; position: fixed; bottom: 0; left: 0; width: 100vw; z-index: 100;}
    .nav-icon {font-size: 2rem; color: #3a1aff;}
    .stDataFrame, .stTable {background: #fff; border-radius: 8px;}
    .boleta {background: #f3f3ff; border-radius: 10px; padding: 1.5rem; margin-top: 1.5rem; box-shadow: 0 2px 8px #e0e0e0;}
    .boleta-title {color: #3a1aff; font-size: 1.5rem; font-weight: bold; margin-bottom: 1rem;}
    .boleta-total {font-size: 1.2rem; font-weight: bold; color: #222;}
</style>
""", unsafe_allow_html=True)

# Parámetros
N_ENCHUFES = 5
TARIFA = 80  # $/kWh

NOMBRES = [
    ("Enchufe 1", "Hervidor"),
    ("Enchufe 2", "Refrigerador"),
    ("Enchufe 3", "Lavadora"),
    ("Enchufe 4", "Microondas"),
    ("Enchufe 5", "Computador")
]

# Simulación de datos (función para permitir refresco)
def simular_datos():
    hoy = datetime.now()
    dias = [(hoy - timedelta(days=i)).strftime('%d-%b') for i in range(29, -1, -1)]
    datos = {}
    for idx, (nombre, dispositivo) in enumerate(NOMBRES):
        # Simula consumo diario (kWh)
        consumo_diario = [round(random.uniform(0.5, 3.5), 2) for _ in dias]
        datos[f'enchufe{idx+1}'] = {
            'nombre': nombre,
            'dispositivo': dispositivo,
            'consumo_diario': consumo_diario,
            'consumo_actual': consumo_diario[-1]
        }
    return datos, dias

if 'datos' not in st.session_state or st.button('Actualizar datos'):
    st.session_state['datos'], st.session_state['dias'] = simular_datos()

datos = st.session_state['datos']
dias = st.session_state['dias']

# Título
st.markdown('<div class="title">OhMyWatts!</div>', unsafe_allow_html=True)

# Tabla de enchufes
tabla = pd.DataFrame([
    {"Enchufe": datos[e]['nombre'], "Dispositivo": datos[e]['dispositivo'], "Consumo actual (kWh)": f"{datos[e]['consumo_actual']:.2f}"}
    for e in datos
])
st.table(tabla)

# Gráfico de consumo diario
df_graf = pd.DataFrame({
    datos[e]['nombre']: datos[e]['consumo_diario'] for e in datos
}, index=dias)
st.markdown("<b>Consumo diario de los últimos 30 días</b>", unsafe_allow_html=True)
st.line_chart(df_graf, use_container_width=True)

# Boleta del mes pasado
st.markdown('<div class="boleta">', unsafe_allow_html=True)
st.markdown('<div class="boleta-title">Boleta del mes pasado</div>', unsafe_allow_html=True)
consumo_total = sum([sum(datos[e]['consumo_diario']) for e in datos])
costo_total = consumo_total * TARIFA
tabla_boleta = pd.DataFrame([
    {"Enchufe": datos[e]['nombre'], "Dispositivo": datos[e]['dispositivo'], "Total kWh": f"{sum(datos[e]['consumo_diario']):.2f}", "Total $": f"${sum(datos[e]['consumo_diario'])*TARIFA:,.0f}"}
    for e in datos
])
st.dataframe(tabla_boleta, hide_index=True, use_container_width=True)
st.markdown(f'<div class="boleta-total">Total mes: <b>{consumo_total:.2f} kWh</b> &nbsp;&nbsp;|&nbsp;&nbsp; <b>${costo_total:,.0f}</b></div>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# Barra de navegación inferior
st.markdown("""
<div class="nav-bar">
    <span class="nav-icon">&#8592;</span>
    <span class="nav-icon">&#8962;</span>
    <span class="nav-icon">&#128100;</span>
</div>
""", unsafe_allow_html=True) 