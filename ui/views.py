import os
import streamlit as st
import matplotlib.pyplot as plt
from database.db_manager import (
    guardar_imagen_local,
    insertar_infusion,
    obtener_todas_infusiones,
    eliminar_infusion,
    obtener_categorias,
    agregar_categoria,
    obtener_horarios,
    agregar_horario,
    obtener_ingredientes_catalogo,
    agregar_ingrediente_catalogo,
    obtener_bases_liquidas,
    agregar_base_liquida,
    obtener_tiempos_reposo,
    agregar_tiempo_reposo,
    get_connection,
)

# =========================================================
# 📋 CATÁLOGOS FIJOS DE APOYO
# =========================================================
METODOS_PREP_OPCIONES = [
    "Infusión directa (verter agua caliente sobre hojas/flores y tapar)",
    "Decocción suave (hervir raíces, cortezas o semillas a fuego bajo)",
    "Maceración en frío (reposar en agua fría o ambiente por varias horas)",
    "Disolución directa (polvos como Matcha o Cacao)",
]

TEMPERATURAS_OPCIONES = [
    "75°C - 80°C (Té verde y hojas muy delicadas)",
    "85°C - 90°C (Antes de hervir - ideal para hojas y flores)",
    "100°C (Punto de ebullición - raíces, semillas y cortezas)",
    "Agua fría / Temperatura ambiente",
]

BENEFICIOS_OPCIONES = [
    "Alivia la pesadez estomacal y mejora la digestión",
    "Reduce gases, hinchazón y espasmos abdominales",
    "Calma el estrés, la ansiedad leve y relaja el sistema nervioso",
    "Favorece el descanso profundo y la conciliación del sueño",
    "Aporta energía sostenida y mejora el enfoque mental",
    "Potente efecto antiinflamatorio y antioxidante",
    "Refuerza el sistema inmunológico y despeja vías respiratorias",
    "Efecto diurético suave y depurativo",
]

CUIDADOS_OPCIONES = [
    "Evitar durante el embarazo y periodo de lactancia",
    "No administrar a niños menores de 12 años sin indicación",
    "Precaución en personas con hipertensión arterial",
    "Contraindicado en gastritis aguda, reflujo severo o úlceras",
    "Contraindicado en obstrucción de vías biliares o cálculos",
    "Precaución en personas con hipotiroidismo",
    "Puede interactuar con medicamentos anticoagulantes o sedantes",
    "Evitar su consumo después de las 16:00 hrs (contiene cafeína/teína)",
    "No consumir en exceso por periodos prolongados (máx. 2 semanas seguidas)",
]

# =========================================================
# 1. VISTA: CONSULTOR DE RECETAS
# =========================================================
def render_consultor():
    st.markdown("<h1 style='color: #2E5558;'>🍵 Consultor de Infusiones Saludables</h1>", unsafe_allow_html=True)
    df = obtener_todas_infusiones()
    
    if df.empty:
        st.info("No hay recetas registradas. Ve a Registrar Nueva Receta para crear la primera.")
        return

    categorias_bd = obtener_categorias()
    horarios_bd = obtener_horarios()

    c1, c2, c3 = st.columns([1.2, 1, 1])
    with c1:
        busqueda = st.text_input("🔎 Filtrar por palabra clave (Opcional):", placeholder="Ej. cedrón, digestión, dormir...")
    with c2:
        cat_sel = st.selectbox("🎯 Filtrar por Categoría:", ["Todas"] + categorias_bd, placeholder="Elige una categoría...")
    with c3:
        hor_sel = st.selectbox("⏰ Filtrar por Horario:", ["Todos"] + horarios_bd, placeholder="Elige un horario...")

    df_filt = df.copy()
    if busqueda.strip():
        mask = (
            df_filt["nombre"].str.contains(busqueda, case=False, na=False)
            | df_filt["ingredientes"].str.contains(busqueda, case=False, na=False)
            | df_filt["beneficios"].str.contains(busqueda, case=False, na=False)
        )
        df_filt = df_filt[mask]
    if cat_sel != "Todas":
        df_filt = df_filt[df_filt["categoria"] == cat_sel]
    if hor_sel != "Todos":
        df_filt = df_filt[df_filt["horario"] == hor_sel]

    if df_filt.empty:
        st.warning("No hay infusiones que coincidan con esos filtros.")
        return

    opciones_recetas = df_filt["nombre"].tolist()
    receta_seleccionada = st.selectbox(
        "🌿 Selecciona la infusión que deseas consultar:",
        options=opciones_recetas,
        index=None,
        placeholder="Elige una infusión de la lista..."
    )

    if not receta_seleccionada:
        return

    row = df_filt[df_filt["nombre"] == receta_seleccionada].iloc[0]

    st.write("---")
    st.markdown(f"""
    <div class="receta-card">
        <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 10px;">
            <h2 style="margin: 0; color: #2E5558;">{row['nombre']}</h2>
            <span class="badge-horario">{row['horario']}</span>
        </div>
        <p style="color: #833A5E; font-size: 0.95em; margin-top: 6px;">Categoría: <b style="color: #261E37;">{row['categoria']}</b></p>
    </div>
    """, unsafe_allow_html=True)

    col_img, col_ing, col_prep = st.columns([1, 1.1, 1.3])
    with col_img:
        img_path = str(row["imagen_path"]).replace("\\", "/") if row["imagen_path"] else ""
        if img_path and os.path.exists(img_path):
            st.image(img_path, use_container_width=True)
        else:
            st.markdown(
                "<div style='height:190px; background:#E8CBD0; border-radius:10px; display:flex; flex-direction:column; align-items:center; justify-content:center; border:1px dashed #BC7087; color:#591721;'>"
                "<span style='font-size:2em;'>🌿</span><span style='font-weight:500;'>Sin fotografía</span></div>",
                unsafe_allow_html=True,
            )
    with col_ing:
        st.markdown("<h4 style='color: #2E5558;'>🧺 Ingredientes</h4>", unsafe_allow_html=True)
        st.markdown(row["ingredientes"].replace("\n", "  \n"))
    with col_prep:
        st.markdown("<h4 style='color: #833A5E;'>🫖 Preparación</h4>", unsafe_allow_html=True)
        st.markdown(row["preparacion"].replace("\n", "  \n"))

    col_ben, col_cui = st.columns(2)
    with col_ben:
        st.markdown(f"""
        <div class="beneficio-box">
            <h4 style="margin-top:0; color:#2E5558;">✨ Beneficios Principales</h4>
            <div style="font-size: 0.95em; line-height: 1.5; color: #261E37;">{row['beneficios'].replace(chr(10), '<br>')}</div>
        </div>
        """, unsafe_allow_html=True)
    with col_cui:
        st.markdown(f"""
        <div class="alerta-cuidado">
            <h4 style="margin-top:0; color:#591721;">⚠️ Cuidados y Contraindicaciones</h4>
            <div style="font-size: 0.95em; line-height: 1.5; color: #261E37;">{row['cuidados'].replace(chr(10), '<br>')}</div>
        </div>
        """, unsafe_allow_html=True)

    if "observaciones" in row and row["observaciones"] and str(row["observaciones"]).strip():
        st.markdown(f"""
        <div style="background-color: #FFFFFF; border: 1px solid #638E8E; border-left: 5px solid #BC7087; border-radius: 8px; padding: 15px; margin-top: 15px;">
            <h4 style="margin-top:0; color:#833A5E;">💡 Observaciones, Tips y Notas del Autor</h4>
            <div style="font-size: 0.95em; line-height: 1.5; color: #261E37;">{str(row['observaciones']).replace(chr(10), '<br>')}</div>
        </div>
        """, unsafe_allow_html=True)

    # =========================================================
    # 📊 GRÁFICAS DE PASTEL ARMÓNICAS CON LA PALETA CLARA
    # =========================================================
    st.write("---")
    st.markdown("<h3 style='color: #2E5558;'>📊 Análisis Gráfico de Proporción e Impacto</h3>", unsafe_allow_html=True)
    
    ingredientes_raw = str(row["ingredientes"]).split("\n")
    lista_ingredientes_limpia = [i.replace("•", "").strip() for i in ingredientes_raw if i.strip()]
    
    beneficios_raw = str(row["beneficios"]).split("\n")
    lista_beneficios_limpia = [b.replace("•", "").strip() for b in beneficios_raw if b.strip()]

    g_col1, g_col2 = st.columns(2)
    colores_palette = [
        '#638E8E',  # Verde salvia
        '#BC7087',  # Frambuesa suave
        '#D8A2B6',  # Rosa floral
        '#2E5558',  # Verde bosque
        '#833A5E',  # Ciruela medio
        '#E8CBD0',  # Rosa pastel
        '#4E3B5A',  # Violeta ahumado
        '#591721',  # Borgoña
    ]

    with g_col1:
        st.markdown("<h4 style='color: #638E8E;'>🌿 Proporción de Ingredientes</h4>", unsafe_allow_html=True)
        st.markdown("<p style='font-size: 0.9em; color: #833A5E;'>Distribución porcentual estimada:</p>", unsafe_allow_html=True)
        if lista_ingredientes_limpia:
            fig, ax = plt.subplots(figsize=(6, 6))
            fig.patch.set_facecolor('#F4F2EC')
            ax.set_facecolor('#F4F2EC')
            
            n = len(lista_ingredientes_limpia)
            sizes = [max(10, 100 - (i * 18)) for i in range(n)]
            
            wedges, texts, autotexts = ax.pie(
                sizes, autopct='%1.0f%%', startangle=140,
                colors=colores_palette[:n],
                wedgeprops=dict(edgecolor='#F4F2EC', linewidth=2),
                textprops=dict(color="#FFFFFF", fontsize=9, weight='bold')
            )
            
            leg = ax.legend(
                wedges, lista_ingredientes_limpia, title="Ingredientes", 
                loc="upper center", bbox_to_anchor=(0.5, -0.05), 
                facecolor='#FFFFFF', edgecolor='#638E8E', labelcolor='#261E37', fontsize=8.5, ncol=1
            )
            leg.get_title().set_color('#2E5558')
            leg.get_title().set_weight('bold')
            
            ax.axis('equal')
            plt.subplots_adjust(bottom=0.35)
            st.pyplot(fig)
        else:
            st.info("Sin datos para graficar.")

    with g_col2:
        st.markdown("<h4 style='color: #833A5E;'>✨ Distribución de Beneficios</h4>", unsafe_allow_html=True)
        st.markdown("<p style='font-size: 0.9em; color: #638E8E;'>Peso terapéutico asociado:</p>", unsafe_allow_html=True)
        if lista_beneficios_limpia:
            fig2, ax2 = plt.subplots(figsize=(6, 6))
            fig2.patch.set_facecolor('#F4F2EC')
            ax2.set_facecolor('#F4F2EC')
            
            m = len(lista_beneficios_limpia)
            sizes2 = [max(15, 100 - (i * 15)) for i in range(m)]
            paleta_ben = ['#BC7087', '#638E8E', '#833A5E', '#D8A2B6', '#2E5558', '#4E3B5A', '#E8CBD0', '#591721']
            
            wedges2, texts2, autotexts2 = ax2.pie(
                sizes2, autopct='%1.0f%%', startangle=90,
                colors=paleta_ben[:m],
                wedgeprops=dict(edgecolor='#F4F2EC', linewidth=2),
                textprops=dict(color="#FFFFFF", fontsize=9, weight='bold')
            )
            
            leg2 = ax2.legend(
                wedges2, lista_beneficios_limpia, title="Beneficios", 
                loc="upper center", bbox_to_anchor=(0.5, -0.05), 
                facecolor='#FFFFFF', edgecolor='#BC7087', labelcolor='#261E37', fontsize=8.5, ncol=1
            )
            leg2.get_title().set_color('#833A5E')
            leg2.get_title().set_weight('bold')
            
            ax2.axis('equal')
            plt.subplots_adjust(bottom=0.35)
            st.pyplot(fig2)
        else:
            st.info("Sin datos para graficar.")

# =========================================================
# 2. VISTA: FORMULARIO GUIADO DE REGISTRO
# =========================================================
def render_formulario_registro():
    st.markdown("<h1 style='color: #2E5558;'>📝 Registrar Nueva Receta de Infusión</h1>", unsafe_allow_html=True)
    st.write("---")
    categorias_bd = obtener_categorias() + ["➕ [Agregar nueva categoría...]"]
    horarios_bd = obtener_horarios() + ["➕ [Agregar nuevo horario...]"]
    ingredientes_bd = obtener_ingredientes_catalogo() + ["➕ [Agregar nuevo ingrediente...]"]
    bases_bd = obtener_bases_liquidas() + ["➕ [Agregar nueva base líquida...]"]
    tiempos_bd = obtener_tiempos_reposo() + ["➕ [Agregar nuevo tiempo de reposo...]"]

    with st.form("form_receta_guiada"):
        nombre = st.text_input("Nombre de la Infusión *")
        sel_cat = st.selectbox("Categoría *", categorias_bd, placeholder="Selecciona una categoría...")
        categoria_nueva = st.text_input("Nueva categoría:") if sel_cat == "➕ [Agregar nueva categoría...]" else ""
        sel_hor = st.selectbox("Horario *", horarios_bd, placeholder="Selecciona un horario...")
        horario_nuevo = st.text_input("Nuevo horario:") if sel_hor == "➕ [Agregar nuevo horario...]" else ""
        foto_subida = st.file_uploader("Fotografía", type=["jpg", "jpeg", "png", "webp"])
        
        hierbas_sel = st.multiselect("Ingredientes del catálogo:", ingredientes_bd[:-1], placeholder="Elige los ingredientes...")
        ingrediente_extra = st.text_input("Agregar ingrediente extra:")
        sel_base = st.selectbox("Base líquida:", bases_bd, placeholder="Selecciona la base líquida...")
        base_nueva = st.text_input("Nueva base líquida:") if sel_base == "➕ [Agregar nueva base líquida...]" else ""
        ingredientes_extra_txt = st.text_area("Notas adicionales de ingredientes:")

        metodo = st.selectbox("Método de Extracción:", METODOS_PREP_OPCIONES, placeholder="Selecciona el método...")
        temperatura = st.selectbox("Temperatura:", TEMPERATURAS_OPCIONES, placeholder="Selecciona la temperatura...")
        sel_tiempo = st.selectbox("Tiempo de Reposo:", tiempos_bd, placeholder="Selecciona el tiempo de reposo...")
        tiempo_nuevo = st.text_input("Nuevo tiempo de reposo:") if sel_tiempo == "➕ [Agregar nuevo tiempo de reposo...]" else ""
        pasos_extra = st.text_area("Pasos adicionales:")

        beneficios_sel = st.multiselect("Beneficios:", BENEFICIOS_OPCIONES, placeholder="Elige los beneficios...")
        beneficios_extra = st.text_input("Otro beneficio:")
        cuidados_sel = st.multiselect("Cuidados:", CUIDADOS_OPCIONES, placeholder="Elige las precauciones...")
        cuidados_extra = st.text_input("Otra precaución:")
        observaciones = st.text_area("Observaciones:")

        submitted = st.form_submit_button("💾 Guardar Receta", type="primary", use_container_width=True)
        if submitted:
            if not nombre.strip():
                st.error("⚠️ El nombre de la infusión es obligatorio.")
                return

            cat_final = categoria_nueva.strip() if sel_cat == "➕ [Agregar nueva categoría...]" else sel_cat
            hor_final = horario_nuevo.strip() if sel_hor == "➕ [Agregar nuevo horario...]" else sel_hor
            base_final = base_nueva.strip() if sel_base == "➕ [Agregar nueva base líquida...]" else sel_base
            tiempo_final = tiempo_nuevo.strip() if sel_tiempo == "➕ [Agregar nuevo tiempo de reposo...]" else sel_tiempo

            if categoria_nueva.strip():
                agregar_categoria(cat_final)
            if horario_nuevo.strip():
                agregar_horario(hor_final)
            if ingrediente_extra.strip():
                agregar_ingrediente_catalogo(ingrediente_extra.strip())
                hierbas_sel.append(ingrediente_extra.strip())
            if base_nueva.strip():
                agregar_base_liquida(base_final)
            if tiempo_nuevo.strip():
                agregar_tiempo_reposo(tiempo_final)

            lista_ing = [f"• {h}" for h in hierbas_sel]
            if ingredientes_extra_txt.strip():
                for l in ingredientes_extra_txt.strip().splitlines():
                    if l.strip():
                        lista_ing.append(f"• {l.strip().lstrip('•-* ')}")
            lista_ing.append(f"• Base: {base_final}")
            
            lista_prep = [f"• Método: {metodo}", f"• Temperatura: {temperatura}", f"• Tiempo de reposo: {tiempo_final}"]
            if pasos_extra.strip():
                lista_prep.append(f"• Adicional: {pasos_extra.strip()}")

            lista_ben = [f"• {b}" for b in beneficios_sel]
            if beneficios_extra.strip():
                lista_ben.append(f"• {beneficios_extra.strip()}")
            
            lista_cui = [f"• {c}" for c in cuidados_sel]
            if cuidados_extra.strip():
                lista_cui.append(f"• {cuidados_extra.strip()}")

            ruta_img = guardar_imagen_local(foto_subida)
            insertar_infusion(
                nombre.strip(),
                cat_final,
                hor_final,
                ruta_img,
                "\n".join(lista_ing),
                "\n".join(lista_prep),
                "\n".join(lista_ben),
                "\n".join(lista_cui),
                observaciones.strip(),
            )
            st.success("✅ ¡Receta guardada con éxito!")

# =========================================================
# 3. VISTA: EDITAR RECETA EXISTENTE
# =========================================================
def render_editar_receta():
    st.markdown("<h1 style='color: #2E5558;'>✏️ Editar Receta Existente</h1>", unsafe_allow_html=True)
    df = obtener_todas_infusiones()
    if df.empty:
        st.info("No hay recetas registradas para editar.")
        return

    opciones = {f"ID {row['id']} - {row['nombre']}": row["id"] for _, row in df.iterrows()}
    seleccion_edit = st.selectbox("Selecciona la receta a modificar:", options=list(opciones.keys()), index=None, placeholder="Elige una receta de la lista...")
    if not seleccion_edit:
        return

    id_receta = opciones[seleccion_edit]
    row_actual = df[df["id"] == id_receta].iloc[0]
    categorias_bd = obtener_categorias() + ["➕ [Agregar nueva categoría...]"]
    horarios_bd = obtener_horarios() + ["➕ [Agregar nuevo horario...]"]

    with st.form("form_editar_receta"):
        nuevo_nombre = st.text_input("Nombre", value=row_actual["nombre"])
        cat_actual = row_actual["categoria"]
        idx_cat = categorias_bd.index(cat_actual) if cat_actual in categorias_bd else 0
        nueva_cat_sel = st.selectbox("Categoría", categorias_bd, index=idx_cat, placeholder="Selecciona una categoría...")
        nueva_cat_texto = st.text_input("Nueva categoría:") if nueva_cat_sel == "➕ [Agregar nueva categoría...]" else ""

        hor_actual = row_actual["horario"]
        idx_hor = horarios_bd.index(hor_actual) if hor_actual in horarios_bd else 0
        nuevo_hor_sel = st.selectbox("Horario", horarios_bd, index=idx_hor, placeholder="Selecciona un horario...")
        nuevo_hor_texto = st.text_input("Nuevo horario:") if nuevo_hor_sel == "➕ [Agregar nuevo horario...]" else ""

        nueva_foto = st.file_uploader("Actualizar Fotografía", type=["jpg", "jpeg", "png", "webp"])
        nuevos_ing = st.text_area("Ingredientes", value=row_actual["ingredientes"], height=120)
        nueva_prep = st.text_area("Preparación", value=row_actual["preparacion"], height=120)
        nuevos_ben = st.text_area("Beneficios", value=row_actual["beneficios"], height=100)
        nuevos_cui = st.text_area("Cuidados", value=row_actual["cuidados"], height=100)
        nuevas_obs = st.text_area("Observaciones", value=row_actual["observaciones"] if "observaciones" in row_actual and row_actual["observaciones"] else "", height=100)

        actualizar_btn = st.form_submit_button("💾 Guardar Cambios", type="primary", use_container_width=True)
        if actualizar_btn:
            cat_final = nueva_cat_texto.strip() if nueva_cat_sel == "➕ [Agregar nueva categoría...]" else nueva_cat_sel
            hor_final = nuevo_hor_texto.strip() if nuevo_hor_sel == "➕ [Agregar nuevo horario...]" else nuevo_hor_sel

            if nueva_cat_texto.strip():
                agregar_categoria(cat_final)
            if nuevo_hor_texto.strip():
                agregar_horario(hor_final)

            conn = get_connection()
            cursor = conn.cursor()
            ruta_img_final = str(row_actual["imagen_path"]).replace("\\", "/") if row_actual["imagen_path"] else None
            if nueva_foto is not None:
                ruta_img_final = guardar_imagen_local(nueva_foto)

            cursor.execute("""
                UPDATE infusiones
                SET nombre = ?, categoria = ?, horario = ?, imagen_path = ?, ingredientes = ?, preparacion = ?, beneficios = ?, cuidados = ?, observaciones = ?
                WHERE id = ?
            """, (nuevo_nombre, cat_final, hor_final, ruta_img_final, nuevos_ing, nueva_prep, nuevos_ben, nuevos_cui, nuevas_obs.strip(), id_receta))
            conn.commit()
            conn.close()
            st.success("✅ ¡Receta actualizada con éxito!")
            st.rerun()

# =========================================================
# 4. VISTA: ADMINISTRAR BASE DE DATOS
# =========================================================
def render_admin():
    st.markdown("<h1 style='color: #2E5558;'>🗂️ Administración del Recetario</h1>", unsafe_allow_html=True)
    df = obtener_todas_infusiones()
    if df.empty:
        st.info("No hay recetas almacenadas.")
        return
    st.dataframe(df[["id", "nombre", "categoria", "horario"]], use_container_width=True, hide_index=True)
    opciones = {f"ID {row['id']} - {row['nombre']}": row["id"] for _, row in df.iterrows()}
    sel = st.selectbox("Eliminar receta:", list(opciones.keys()), placeholder="Selecciona una receta...")
    if st.button("Eliminar Registro Definitivamente", type="secondary"):
        eliminar_infusion(opciones[sel])
        st.success("Receta eliminada.")
        st.rerun()
