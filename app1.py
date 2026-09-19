import streamlit as st
from datetime import datetime
import json
import os

# ============================================================
# CONFIGURACIÓN DE LA PÁGINA
# ============================================================
st.set_page_config(
    page_title="Mini Market Express",
    page_icon="🛒",
    layout="wide"
)

# ============================================================
# PERSISTENCIA - Archivo JSON
# ============================================================
ARCHIVO_DATOS = "datos_minimarket.json"


def guardar_datos():
    """Guarda el estado actual en un archivo JSON."""
    datos = {
        "productos": st.session_state.productos,
        "ventas": st.session_state.ventas,
        "detalle_ventas": st.session_state.detalle_ventas,
        "contador_producto": st.session_state.contador_producto,
        "contador_venta": st.session_state.contador_venta
    }
    with open(ARCHIVO_DATOS, "w", encoding="utf-8") as f:
        json.dump(datos, f, ensure_ascii=False, indent=2)


def cargar_datos():
    """Carga el estado desde el archivo JSON si existe."""
    if os.path.exists(ARCHIVO_DATOS):
        with open(ARCHIVO_DATOS, "r", encoding="utf-8") as f:
            datos = json.load(f)
        st.session_state.productos = datos.get("productos", [])
        st.session_state.ventas = datos.get("ventas", [])
        st.session_state.detalle_ventas = datos.get("detalle_ventas", [])
        st.session_state.contador_producto = datos.get("contador_producto", 11)
        st.session_state.contador_venta = datos.get("contador_venta", 1)
        return True
    return False


# ============================================================
# CAPA DE DATOS - Simula BD relacional
# ============================================================
if "productos" not in st.session_state:
    if not cargar_datos():
        # Datos por defecto si no existe el archivo
        st.session_state.productos = [
            {"id": 1, "codigo": "P001", "nombre": "Café expreso", "stock": 50,
             "precio_compra": 0.80, "precio_venta": 1.50, "stock_minimo": 10},
            {"id": 2, "codigo": "P002", "nombre": "Pan de jamón", "stock": 30,
             "precio_compra": 1.80, "precio_venta": 2.80, "stock_minimo": 8},
            {"id": 3, "codigo": "P003", "nombre": "Refresco 350ml", "stock": 60,
             "precio_compra": 0.60, "precio_venta": 1.20, "stock_minimo": 15},
            {"id": 4, "codigo": "P004", "nombre": "Chocolates", "stock": 40,
             "precio_compra": 0.45, "precio_venta": 0.90, "stock_minimo": 12},
            {"id": 5, "codigo": "P005", "nombre": "Agua mineral 500ml", "stock": 80,
             "precio_compra": 0.35, "precio_venta": 0.75, "stock_minimo": 20},
            {"id": 6, "codigo": "P006", "nombre": "Papas fritas", "stock": 25,
             "precio_compra": 0.55, "precio_venta": 1.10, "stock_minimo": 10},
            {"id": 7, "codigo": "P007", "nombre": "Galletas", "stock": 45,
             "precio_compra": 0.30, "precio_venta": 0.60, "stock_minimo": 15},
            {"id": 8, "codigo": "P008", "nombre": "Jugo natural", "stock": 20,
             "precio_compra": 1.20, "precio_venta": 2.00, "stock_minimo": 8},
            {"id": 9, "codigo": "P009", "nombre": "Sándwich", "stock": 15,
             "precio_compra": 2.00, "precio_venta": 3.50, "stock_minimo": 5},
            {"id": 10, "codigo": "P010", "nombre": "Helado", "stock": 18,
             "precio_compra": 1.00, "precio_venta": 1.80, "stock_minimo": 6},
        ]
        st.session_state.ventas = []
        st.session_state.detalle_ventas = []
        st.session_state.contador_producto = 11
        st.session_state.contador_venta = 1
        guardar_datos()

if "carrito" not in st.session_state:
    st.session_state.carrito = []
if "ultima_venta" not in st.session_state:
    st.session_state.ultima_venta = None
if "mensaje_producto" not in st.session_state:
    st.session_state.mensaje_producto = None


# ============================================================
# FUNCIONES DE DATOS
# ============================================================
def obtener_productos():
    return st.session_state.productos


def obtener_producto_por_id(id_producto):
    for p in st.session_state.productos:
        if p["id"] == id_producto:
            return p
    return None


def obtener_producto_por_codigo(codigo):
    for p in st.session_state.productos:
        if p["codigo"] == codigo:
            return p
    return None


def agregar_producto(codigo, nombre, stock, precio_compra, precio_venta, stock_minimo):
    if obtener_producto_por_codigo(codigo):
        return False, f"❌ Ya existe un producto con el código {codigo}"
    nuevo = {
        "id": st.session_state.contador_producto,
        "codigo": codigo,
        "nombre": nombre,
        "stock": stock,
        "precio_compra": precio_compra,
        "precio_venta": precio_venta,
        "stock_minimo": stock_minimo
    }
    st.session_state.productos.append(nuevo)
    st.session_state.contador_producto += 1
    guardar_datos()  # 💾 Guardar
    return True, f"✅ Producto '{nombre}' agregado correctamente"


def modificar_producto(id_producto, codigo, nombre, stock, precio_compra, precio_venta, stock_minimo):
    p = obtener_producto_por_id(id_producto)
    if not p:
        return False, "❌ Producto no encontrado"
    existente = obtener_producto_por_codigo(codigo)
    if existente and existente["id"] != id_producto:
        return False, f"❌ El código {codigo} ya está en uso"
    p["codigo"] = codigo
    p["nombre"] = nombre
    p["stock"] = stock
    p["precio_compra"] = precio_compra
    p["precio_venta"] = precio_venta
    p["stock_minimo"] = stock_minimo
    guardar_datos()  # 💾 Guardar
    return True, f"✅ Producto '{nombre}' modificado correctamente"


def eliminar_producto(id_producto):
    p = obtener_producto_por_id(id_producto)
    if not p:
        return False, "❌ Producto no encontrado"
    st.session_state.productos = [prod for prod in st.session_state.productos if prod["id"] != id_producto]
    guardar_datos()  # 💾 Guardar
    return True, f"✅ Producto '{p['nombre']}' eliminado correctamente"


def registrar_venta(items):
    if not items:
        return False, "❌ No hay items en la venta", None
    for item in items:
        p = obtener_producto_por_id(item["producto_id"])
        if not p:
            return False, "❌ Producto no encontrado", None
        if p["stock"] < item["cantidad"]:
            return False, f"❌ Stock insuficiente para '{p['nombre']}' (disponible: {p['stock']})", None

    total = 0
    detalles = []
    for item in items:
        p = obtener_producto_por_id(item["producto_id"])
        subtotal = p["precio_venta"] * item["cantidad"]
        total += subtotal
        detalles.append({
            "producto_id": p["id"],
            "codigo": p["codigo"],
            "nombre": p["nombre"],
            "cantidad": item["cantidad"],
            "precio_unitario": p["precio_venta"],
            "subtotal": subtotal
        })

    venta = {
        "id": st.session_state.contador_venta,
        "fecha": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "total": total,
        "items": detalles
    }
    st.session_state.ventas.append(venta)

    for item in items:
        p = obtener_producto_por_id(item["producto_id"])
        p["stock"] -= item["cantidad"]

    for d in detalles:
        st.session_state.detalle_ventas.append({
            "id": len(st.session_state.detalle_ventas) + 1,
            "venta_id": venta["id"],
            **d
        })

    st.session_state.contador_venta += 1
    guardar_datos()  # 💾 Guardar
    return True, f"✅ Venta #{venta['id']} registrada por ${total:,.2f}", venta


def productos_con_stock_bajo():
    return [p for p in st.session_state.productos if p["stock"] <= p["stock_minimo"]]


def valor_inventario():
    vc = sum(p["stock"] * p["precio_compra"] for p in st.session_state.productos)
    vv = sum(p["stock"] * p["precio_venta"] for p in st.session_state.productos)
    return vc, vv


def total_ventas():
    return sum(v["total"] for v in st.session_state.ventas)


def ganancia_total():
    gan = 0
    for d in st.session_state.detalle_ventas:
        p = obtener_producto_por_id(d["producto_id"])
        if p:
            gan += (d["precio_unitario"] - p["precio_compra"]) * d["cantidad"]
    return gan


def producto_mas_vendido():
    if not st.session_state.detalle_ventas:
        return []
    conteo = {}
    for d in st.session_state.detalle_ventas:
        conteo[d["nombre"]] = conteo.get(d["nombre"], 0) + d["cantidad"]
    if not conteo:
        return []
    max_cantidad = max(conteo.values())
    ganadores = [(nombre, cant) for nombre, cant in conteo.items() if cant == max_cantidad]
    return ganadores


# ============================================================
# CAPA DE IA - Asistente inteligente
# ============================================================
def responder_consulta(pregunta):
    pregunta = pregunta.lower()

    if "stock bajo" in pregunta or "reponer" in pregunta or "agotado" in pregunta:
        bajos = productos_con_stock_bajo()
        if not bajos:
            return "✅ No hay productos con stock bajo. Todo está en orden."
        respuesta = "⚠️ **Productos con stock bajo que necesitan reposición:**\n\n"
        for p in bajos:
            respuesta += f"- **{p['nombre']}** ({p['codigo']}): {p['stock']} uds (mínimo: {p['stock_minimo']})\n"
        return respuesta

    if "venta" in pregunta and ("total" in pregunta or "cuánto" in pregunta or "cuanto" in pregunta):
        return f"💰 El total de ventas es **${total_ventas():,.2f}**"

    if "ganancia" in pregunta or "utilidad" in pregunta:
        return f"📈 La ganancia total es **${ganancia_total():,.2f}**"

    if "más vendido" in pregunta or "mas vendido" in pregunta or "top" in pregunta:
        ganadores = producto_mas_vendido()
        if not ganadores:
            return "ℹ️ Aún no hay ventas registradas."
        if len(ganadores) == 1:
            nombre, cant = ganadores[0]
            return f"🏆 El producto más vendido es **{nombre}** con **{cant} unidades**"
        else:
            cantidad = ganadores[0][1]
            respuesta = f"🏆 **Hay un EMPATE en el primer lugar con {cantidad} unidades cada uno:**\n\n"
            for i, (nombre, cant) in enumerate(ganadores, 1):
                respuesta += f"{i}. **{nombre}** — {cant} unidades\n"
            respuesta += f"\n💡 **Nota:** Hay {len(ganadores)} productos empatados en el primer lugar."
            return respuesta

    if "inventario" in pregunta or "valor" in pregunta:
        vc, vv = valor_inventario()
        return (f"💼 **Valor del inventario:**\n"
                f"- Compra: **${vc:,.2f}**\n"
                f"- Venta: **${vv:,.2f}**\n"
                f"- Ganancia potencial: **${vv-vc:,.2f}**")

    if "cuántos productos" in pregunta or "cuantos productos" in pregunta:
        return f"📦 Hay **{len(obtener_productos())} productos** registrados."

    if "sugerencia" in pregunta or "recomendación" in pregunta or "recomendacion" in pregunta:
        sugerencias = ["🧠 **Sugerencias:**\n"]
        bajos = productos_con_stock_bajo()
        if bajos:
            sugerencias.append(f"⚠️ Reponer {len(bajos)} productos con stock bajo")
        else:
            sugerencias.append("✅ Stock saludable")
        prods = obtener_productos()
        if prods:
            margenes = [(p["nombre"], (p["precio_venta"]-p["precio_compra"])/p["precio_compra"]*100) for p in prods]
            margenes.sort(key=lambda x: x[1], reverse=True)
            sugerencias.append(f"💎 Mejor margen: {margenes[0][0]} ({margenes[0][1]:.1f}%)")
            sugerencias.append(f"📉 Menor margen: {margenes[-1][0]} ({margenes[-1][1]:.1f}%)")
        if st.session_state.ventas:
            sugerencias.append(f"📈 Ganancia acumulada: ${ganancia_total():,.2f}")
        return "\n".join(sugerencias)

    return ("🤖 No entendí. Prueba:\n"
            "- '¿Qué productos tienen stock bajo?'\n"
            "- '¿Cuál es el total de ventas?'\n"
            "- '¿Cuál es la ganancia?'\n"
            "- '¿Cuál es el producto más vendido?'\n"
            "- '¿Cuánto vale el inventario?'\n"
            "- 'Dame sugerencias'")


# ============================================================
# FUNCIONES AUXILIARES GUI
# ============================================================
def badge_stock(stock, stock_minimo):
    if stock == 0:
        return "🔴 AGOTADO"
    elif stock <= stock_minimo:
        return "🟡 STOCK BAJO"
    elif stock <= stock_minimo * 1.5:
        return "🟠 MODERADO"
    return "🟢 OK"


def barra_stock(stock, stock_minimo, stock_max=100):
    porcentaje = min(100, (stock / stock_max) * 100)
    if stock == 0:
        color = "#f44336"
    elif stock <= stock_minimo:
        color = "#ff9800"
    elif stock <= stock_minimo * 1.5:
        color = "#ffc107"
    else:
        color = "#4caf50"
    return (f'<div style="background-color:#e0e0e0;border-radius:5px;height:20px;width:100%;margin:3px 0;">'
            f'<div style="background-color:{color};border-radius:5px;height:20px;width:{porcentaje}%;'
            f'display:flex;align-items:center;justify-content:center;color:white;font-size:11px;font-weight:bold;">'
            f'{stock}</div></div>')


# ============================================================
# INTERFAZ PRINCIPAL
# ============================================================
st.title("🛒 Mini Market Express")
st.markdown("---")

st.sidebar.title("🛒 Mini Market Express")
st.sidebar.markdown("### 🧭 Navegación")
seccion = st.sidebar.radio(
    "Selecciona un módulo:",
    ["🏠 Inicio", "📦 Productos", "💰 Punto de Venta", "📊 Reportes", "🤖 Asistente IA"]
)

# Botón para reiniciar datos
st.sidebar.markdown("---")
if st.sidebar.button("🔄 Reiniciar todos los datos"):
    if os.path.exists(ARCHIVO_DATOS):
        os.remove(ARCHIVO_DATOS)
    st.session_state.clear()
    st.rerun()



bajos = productos_con_stock_bajo()
if bajos:
    st.sidebar.markdown("---")
    st.sidebar.error(f"⚠️ **{len(bajos)} producto(s) con stock bajo**")
    for p in bajos[:5]:
        st.sidebar.caption(f"• {p['nombre']} ({p['stock']} uds)")


# ============================================================
# SECCIÓN: INICIO
# ============================================================
if seccion == "🏠 Inicio":
    st.header("🏠 Panel Principal - Mini Market Express")

    st.markdown("""
    ### 👋 ¡Bienvenido a Mini Market Express!

    Esta **página web** es un sistema de **gestión de stock y ventas** diseñado para pequeños
    comercios como kioscos, bodegas o minimarkets. Permite llevar un control ordenado del
    inventario, registrar ventas y analizar el desempeño del negocio en tiempo real.

    **¿Para qué sirve esta página?**  
    - 📦 **Administrar productos:** agregar, modificar y eliminar artículos del inventario.  
    - 💰 **Registrar ventas:** generar tickets que descuentan el stock automáticamente.  
    - ⚠️ **Alertar sobre stock bajo:** avisa cuando un producto necesita reposición.  
    - 📊 **Analizar el negocio:** reportes de ventas, ganancias y valor del inventario.  
    - 🤖 **Consultar con IA:** un asistente que responde preguntas en lenguaje natural.
    """)

    st.markdown("---")

    prods = obtener_productos()
    vc, vv = valor_inventario()
    total_v = total_ventas()
    gan = ganancia_total()
    bajos = productos_con_stock_bajo()

    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("📦 Productos", len(prods))
    col2.metric("💰 Ventas Totales", f"${total_v:,.2f}")
    col3.metric("📈 Ganancia", f"${gan:,.2f}")
    col4.metric("💼 Valor Inventario", f"${vc:,.2f}")
    col5.metric("⚠️ Stock Bajo", len(bajos))

    st.markdown("---")
    st.subheader("⚠️ Alertas de Stock")
    if bajos:
        for p in bajos:
            st.warning(f"🔔 **{p['nombre']}** ({p['codigo']}) — Stock: **{p['stock']}** | Mínimo: **{p['stock_minimo']}**")
    else:
        st.success("✅ Todos los productos tienen stock suficiente.")

    st.markdown("---")
    st.subheader("📋 Estado del Inventario")
    tabla = "| Código | Producto | Stock | Estado | Precio Venta |\n"
    tabla += "|--------|----------|-------|--------|--------------|\n"
    for p in prods:
        badge = badge_stock(p["stock"], p["stock_minimo"])
        tabla += f"| {p['codigo']} | {p['nombre']} | {p['stock']} | {badge} | ${p['precio_venta']:.2f} |\n"
    st.markdown(tabla)


# ============================================================
# SECCIÓN: PRODUCTOS (CRUD)
# ============================================================
elif seccion == "📦 Productos":
    st.header("📦 Gestión de Productos - Mini Market Express")

    if st.session_state.get("mensaje_producto"):
        tipo, texto = st.session_state.mensaje_producto
        if tipo == "success":
            st.success(texto)
        elif tipo == "error":
            st.error(texto)
        elif tipo == "warning":
            st.warning(texto)
        st.session_state.mensaje_producto = None

    tab_lista, tab_alta, tab_mod, tab_baja = st.tabs(["📋 Lista", "➕ Alta", "✏️ Modificar", "🗑️ Baja"])

    with tab_lista:
        st.subheader("📋 Lista de Productos")
        prods = obtener_productos()
        if not prods:
            st.info("ℹ️ No hay productos registrados.")
        else:
            for p in prods:
                col1, col2 = st.columns([3, 1])
                with col1:
                    badge = badge_stock(p["stock"], p["stock_minimo"])
                    st.markdown(f"**{p['codigo']}** — {p['nombre']} — {badge}")
                    st.caption(f"Stock: {p['stock']} | Mín: {p['stock_minimo']} | "
                               f"Compra: ${p['precio_compra']:.2f} | Venta: ${p['precio_venta']:.2f}")
                with col2:
                    st.html(barra_stock(p["stock"], p["stock_minimo"]))
                st.markdown("---")

    with tab_alta:
        st.subheader("➕ Dar de Alta un Producto")
        with st.form("form_alta"):
            col1, col2 = st.columns(2)
            with col1:
                codigo = st.text_input("Código *", placeholder="Ej: P011")
                nombre = st.text_input("Nombre *", placeholder="Ej: Chicle menta")
                stock = st.number_input("Stock inicial *", min_value=0, value=10)
            with col2:
                precio_compra = st.number_input("Precio compra ($) *", min_value=0.0, value=0.50, step=0.10)
                precio_venta = st.number_input("Precio venta ($) *", min_value=0.0, value=1.00, step=0.10)
                stock_minimo = st.number_input("Stock mínimo *", min_value=0, value=5)

            submitted = st.form_submit_button("✅ Agregar Producto")
            if submitted:
                if not codigo or not nombre:
                    st.session_state.mensaje_producto = ("error", "❌ Código y nombre son obligatorios")
                    st.rerun()
                elif precio_venta < precio_compra:
                    st.session_state.mensaje_producto = ("error", "❌ El precio de venta no puede ser menor al de compra")
                    st.rerun()
                else:
                    ok, msg = agregar_producto(codigo, nombre, stock, precio_compra, precio_venta, stock_minimo)
                    if ok:
                        st.session_state.mensaje_producto = ("success", f'✅ "{nombre}" agregado exitosamente')
                        st.rerun()
                    else:
                        st.session_state.mensaje_producto = ("error", msg)
                        st.rerun()

    with tab_mod:
        st.subheader("✏️ Modificar Producto")
        prods = obtener_productos()
        if not prods:
            st.info("ℹ️ No hay productos para modificar.")
        else:
            opciones = {f"{p['codigo']} - {p['nombre']}": p for p in prods}
            seleccionado = st.selectbox("Selecciona un producto:", list(opciones.keys()))
            p = opciones[seleccionado]
            with st.form("form_mod"):
                col1, col2 = st.columns(2)
                with col1:
                    codigo = st.text_input("Código", value=p["codigo"])
                    nombre = st.text_input("Nombre", value=p["nombre"])
                    stock = st.number_input("Stock", min_value=0, value=p["stock"])
                with col2:
                    precio_compra = st.number_input("Precio compra ($)", min_value=0.0,
                                                    value=float(p["precio_compra"]), step=0.10)
                    precio_venta = st.number_input("Precio venta ($)", min_value=0.0,
                                                   value=float(p["precio_venta"]), step=0.10)
                    stock_minimo = st.number_input("Stock mínimo", min_value=0, value=p["stock_minimo"])
                submitted = st.form_submit_button("💾 Guardar Cambios")
                if submitted:
                    nombre_original = p["nombre"]
                    ok, msg = modificar_producto(p["id"], codigo, nombre, stock, precio_compra, precio_venta, stock_minimo)
                    if ok:
                        if nombre != nombre_original:
                            st.session_state.mensaje_producto = (
                                "success",
                                f'✅ "{nombre_original}" renombrado a "{nombre}" exitosamente'
                            )
                        else:
                            st.session_state.mensaje_producto = ("success", f'✅ "{nombre}" modificado exitosamente')
                        st.rerun()
                    else:
                        st.session_state.mensaje_producto = ("error", msg)
                        st.rerun()

    with tab_baja:
        st.subheader("🗑️ Dar de Baja un Producto")
        prods = obtener_productos()
        if not prods:
            st.info("ℹ️ No hay productos para eliminar.")
        else:
            opciones = {f"{p['codigo']} - {p['nombre']}": p for p in prods}
            seleccionado = st.selectbox("Selecciona un producto a eliminar:", list(opciones.keys()), key="baja")
            p = opciones[seleccionado]
            st.warning(f"⚠️ ¿Estás seguro de eliminar **{p['nombre']}**?")
            if st.button("🗑️ Confirmar Eliminación", type="primary"):
                nombre_a_borrar = p["nombre"]
                ok, msg = eliminar_producto(p["id"])
                if ok:
                    st.session_state.mensaje_producto = (
                        "success",
                        f'✅ "{nombre_a_borrar}" dado de baja exitosamente'
                    )
                    st.rerun()
                else:
                    st.session_state.mensaje_producto = ("error", msg)
                    st.rerun()


# ============================================================
# SECCIÓN: PUNTO DE VENTA
# ============================================================
elif seccion == "💰 Punto de Venta":
    st.header("💰 Punto de Venta - Mini Market Express")
    st.info("""
    ℹ️ **¿Cómo funciona?**  
    1. Selecciona el producto y la cantidad  
    2. Agrégalo al carrito  
    3. Presiona **Generar Ticket**  
    4. El stock se actualizará automáticamente
    """)

    col1, col2, col3 = st.columns([2, 1, 1])
    prods = obtener_productos()
    opciones = {f"{p['codigo']} - {p['nombre']} (stock: {p['stock']}) - ${p['precio_venta']:.2f}": p for p in prods}

    with col1:
        seleccionado = st.selectbox("Producto:", list(opciones.keys()))
    with col2:
        cantidad = st.number_input("Cantidad:", min_value=1, value=1)
    with col3:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("➕ Agregar"):
            p = opciones[seleccionado]
            if p["stock"] < cantidad:
                st.error(f"❌ Stock insuficiente (disponible: {p['stock']})")
            else:
                st.session_state.carrito.append({
                    "producto_id": p["id"], "codigo": p["codigo"], "nombre": p["nombre"],
                    "cantidad": cantidad, "precio": p["precio_venta"],
                    "subtotal": p["precio_venta"] * cantidad
                })
                st.success(f"✅ {p['nombre']} x{cantidad} agregado")
                st.rerun()

    st.markdown("---")
    st.subheader("🛒 Carrito")
    if not st.session_state.carrito:
        st.info("ℹ️ El carrito está vacío.")
    else:
        tabla = "| Código | Producto | Cantidad | Precio | Subtotal |\n"
        tabla += "|--------|----------|----------|--------|----------|\n"
        total = 0
        for item in st.session_state.carrito:
            tabla += f"| {item['codigo']} | {item['nombre']} | {item['cantidad']} | ${item['precio']:.2f} | ${item['subtotal']:.2f} |\n"
            total += item["subtotal"]
        st.markdown(tabla)
        st.markdown(f"### 💵 **TOTAL: ${total:,.2f}**")

        with st.form("acciones_carrito"):
            col1, col2 = st.columns(2)
            with col1:
                vaciar = st.form_submit_button("🗑️ Vaciar Carrito")
            with col2:
                generar = st.form_submit_button("✅ Generar Ticket", type="primary")

            if vaciar:
                st.session_state.carrito = []
                st.rerun()

            if generar:
                ok, msg, venta = registrar_venta(st.session_state.carrito)
                if ok:
                    st.session_state.carrito = []
                    st.session_state.ultima_venta = venta
                    st.success(msg)
                else:
                    st.error(msg)

    if st.session_state.ultima_venta:
        venta = st.session_state.ultima_venta

        st.markdown("---")
        st.subheader("🧾 Ticket de Venta")

        subtotal_sin_iva = venta['total'] / 1.16
        iva = venta['total'] - subtotal_sin_iva

        html_ticket = f"""
        <div style="font-family:'Courier New',monospace;background-color:#ffffff;color:#000000;padding:30px;border-radius:8px;max-width:450px;margin:0 auto;box-shadow:0 4px 15px rgba(0,0,0,0.15);border:1px solid #ddd;">

        <div style="text-align:center;margin-bottom:15px;">
        <div style="font-size:22px;font-weight:bold;">MINI MARKET EXPRESS</div>
        <div style="font-size:12px;">Sistema de Gestión de Stock</div>
        <div style="font-size:11px;margin-top:5px;">RIF: J-12345678-9</div>
        <div style="font-size:11px;">Av. Principal, Ciudad Bolívar</div>
        <div style="font-size:11px;">Telf: 0285-6312346</div>
        </div>

        <div style="border-top:2px dashed #000;border-bottom:2px dashed #000;padding:8px 0;margin:10px 0;text-align:center;font-size:12px;">
        <strong>COMPROBANTE DE VENTA</strong>
        </div>

        <div style="font-size:12px;line-height:1.6;">
        <div><strong>Ticket N°:</strong> {venta['id']:05d}</div>
        <div><strong>Fecha:</strong> {venta['fecha']}</div>
        <div><strong>Cajero:</strong> Operador 01</div>
        <div><strong>Cliente:</strong> Consumidor Final</div>
        </div>

        <div style="border-top:1px dashed #000;margin:12px 0;"></div>

        <table style="width:100%;font-size:12px;font-family:'Courier New',monospace;border-collapse:collapse;">
        <thead>
        <tr style="border-bottom:1px solid #000;">
        <th style="text-align:left;padding:4px 0;">Cant</th>
        <th style="text-align:left;padding:4px 0;">Descripción</th>
        <th style="text-align:right;padding:4px 0;">P.Unit</th>
        <th style="text-align:right;padding:4px 0;">Total</th>
        </tr>
        </thead>
        <tbody>
        """

        for d in venta["items"]:
            html_ticket += (
                f'<tr>'
                f'<td style="padding:3px 0;">{d["cantidad"]}</td>'
                f'<td style="padding:3px 0;">{d["nombre"][:18]}</td>'
                f'<td style="text-align:right;padding:3px 0;">${d["precio_unitario"]:.2f}</td>'
                f'<td style="text-align:right;padding:3px 0;">${d["subtotal"]:.2f}</td>'
                f'</tr>'
            )

        html_ticket += f"""
        </tbody>
        </table>

        <div style="border-top:1px dashed #000;margin:12px 0;"></div>

        <div style="font-size:12px;line-height:1.8;">
        <div style="display:flex;justify-content:space-between;">
        <span>SUBTOTAL:</span>
        <span>${subtotal_sin_iva:.2f}</span>
        </div>
        <div style="display:flex;justify-content:space-between;">
        <span>IVA (16%):</span>
        <span>${iva:.2f}</span>
        </div>
        <div style="display:flex;justify-content:space-between;font-size:16px;font-weight:bold;border-top:2px solid #000;padding-top:8px;margin-top:8px;">
        <span>TOTAL:</span>
        <span>${venta['total']:.2f}</span>
        </div>
        </div>

        <div style="border-top:1px dashed #000;margin:12px 0;"></div>

        <div style="text-align:center;font-size:11px;line-height:1.6;">
        <div><strong>Forma de pago:</strong> Efectivo</div>
        <div><strong>Artículos:</strong> {len(venta['items'])}</div>
        <div style="margin-top:10px;">-----------------------------</div>
        <div style="margin-top:8px;font-size:12px;"><strong>¡GRACIAS POR SU COMPRA!</strong></div>
        <div style="margin-top:5px;">Vuelva pronto</div>
        <div style="margin-top:10px;font-size:10px;">Conserve este ticket para cambios</div>
        <div style="margin-top:5px;font-size:10px;">www.minimarketexpress.com</div>
        <div style="margin-top:10px;">=============================</div>
        </div>

        </div>
        """

        st.html(html_ticket)

        if st.button("✔️ Cerrar Ticket", key="cerrar_ticket_realista"):
            st.session_state.ultima_venta = None
            st.rerun()


# ============================================================
# SECCIÓN: REPORTES
# ============================================================
elif seccion == "📊 Reportes":
    st.header("📊 Reportes y Análisis - Mini Market Express")
    tab1, tab2, tab3 = st.tabs(["📈 Ventas", "📦 Inventario", "⚠️ Stock Bajo"])

    with tab1:
        st.subheader("📈 Reporte de Ventas")
        ventas = st.session_state.ventas
        if not ventas:
            st.info("ℹ️ No hay ventas registradas todavía.")
        else:
            total_v = total_ventas()
            gan = ganancia_total()
            num_ventas = len(ventas)
            ticket_promedio = total_v / num_ventas if num_ventas else 0

            col1, col2, col3, col4 = st.columns(4)
            col1.metric("💰 Total Vendido", f"${total_v:,.2f}")
            col2.metric("📈 Ganancia", f"${gan:,.2f}")
            col3.metric("🧾 N° Ventas", num_ventas)
            col4.metric("📊 Ticket Promedio", f"${ticket_promedio:,.2f}")

            st.markdown("---")

            st.subheader("🥧 Distribución de Productos Vendidos")

            conteo_productos = {}
            for d in st.session_state.detalle_ventas:
                conteo_productos[d["nombre"]] = conteo_productos.get(d["nombre"], 0) + d["cantidad"]

            if conteo_productos:
                total_unidades = sum(conteo_productos.values())

                colores = [
                    "#FF6B6B", "#4ECDC4", "#45B7D1", "#FFA07A", "#98D8C8",
                    "#F7DC6F", "#BB8FCE", "#85C1E2", "#F8B739", "#52BE80",
                    "#EC7063", "#5DADE2", "#F4D03F", "#A569BD", "#48C9B0"
                ]

                gradientes = []
                acumulado = 0
                for i, (nombre, cant) in enumerate(conteo_productos.items()):
                    porcentaje = (cant / total_unidades) * 100
                    inicio = acumulado
                    acumulado += porcentaje
                    color = colores[i % len(colores)]
                    gradientes.append(f"{color} {inicio}% {acumulado}%")

                gradiente_css = ", ".join(gradientes)

                leyenda = ""
                for i, (nombre, cant) in enumerate(conteo_productos.items()):
                    color = colores[i % len(colores)]
                    porcentaje = (cant / total_unidades) * 100
                    leyenda += (
                        f'<div style="display:flex;align-items:center;margin:6px 0;">'
                        f'<div style="width:16px;height:16px;background-color:{color};border-radius:3px;margin-right:8px;"></div>'
                        f'<span><b>{nombre}</b>: {cant} uds ({porcentaje:.1f}%)</span>'
                        f'</div>'
                    )

                html_circular = (
                    f'<div style="display:flex;align-items:center;gap:40px;flex-wrap:wrap;padding:20px;background-color:#f9f9f9;border-radius:10px;">'
                    f'<div style="width:280px;height:280px;border-radius:50%;'
                    f'background:conic-gradient({gradiente_css});'
                    f'box-shadow:0 4px 10px rgba(0,0,0,0.2);"></div>'
                    f'<div>{leyenda}</div>'
                    f'</div>'
                )

                st.html(html_circular)
                st.caption(f"📊 **Total de unidades vendidas:** {total_unidades}")

            st.markdown("---")
            st.subheader("📋 Historial de Ventas")
            for v in reversed(ventas):
                with st.expander(f"🧾 Venta #{v['id']} — {v['fecha']} — ${v['total']:,.2f}"):
                    t = "| Producto | Cant. | Precio | Subtotal |\n"
                    t += "|----------|-------|--------|----------|\n"
                    for d in v["items"]:
                        t += f"| {d['nombre']} | {d['cantidad']} | ${d['precio_unitario']:.2f} | ${d['subtotal']:.2f} |\n"
                    st.markdown(t)

    with tab2:
        st.subheader("📦 Reporte de Inventario")
        prods = obtener_productos()
        vc, vv = valor_inventario()

        col1, col2, col3 = st.columns(3)
        col1.metric("📦 Total Productos", len(prods))
        col2.metric("💼 Valor Compra", f"${vc:,.2f}")
        col3.metric("💵 Valor Venta", f"${vv:,.2f}")

        st.markdown("---")
        tabla = "| Código | Producto | Stock | P.Compra | P.Venta | Valor |\n"
        tabla += "|--------|----------|-------|----------|---------|-------|\n"
        for p in prods:
            valor = p["stock"] * p["precio_compra"]
            tabla += f"| {p['codigo']} | {p['nombre']} | {p['stock']} | ${p['precio_compra']:.2f} | ${p['precio_venta']:.2f} | ${valor:.2f} |\n"
        st.markdown(tabla)

    with tab3:
        st.subheader("⚠️ Productos con Stock Bajo")
        bajos = productos_con_stock_bajo()
        if not bajos:
            st.success("✅ No hay productos con stock bajo.")
        else:
            for p in bajos:
                st.error(f"🔔 **{p['nombre']}** ({p['codigo']}) — Stock: **{p['stock']}** | Mínimo: **{p['stock_minimo']}**")

            st.markdown("---")
            st.subheader("💡 Sugerencia de Reposición")
            tabla = "| Producto | Stock Actual | Mínimo | Reponer |\n"
            tabla += "|----------|--------------|--------|---------|\n"
            for p in bajos:
                reponer = p["stock_minimo"] * 2 - p["stock"]
                tabla += f"| {p['nombre']} | {p['stock']} | {p['stock_minimo']} | {reponer} uds |\n"
            st.markdown(tabla)


# ============================================================
# SECCIÓN: ASISTENTE IA
# ============================================================
elif seccion == "🤖 Asistente IA":
    st.header("🤖 Asistente IA - Mini Market Express")
    st.info("""
    ℹ️ **¿Qué hace?**  
    Es un asistente que responde preguntas sobre tu inventario y ventas 
    usando lenguaje natural. Basado en reglas (sin ML).
    """)

    st.subheader("💡 Consultas Rápidas")

    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("⚠️ Stock bajo"):
            st.session_state.consulta_ia = "¿Qué productos tienen stock bajo?"
        if st.button("💰 Total ventas"):
            st.session_state.consulta_ia = "¿Cuál es el total de ventas?"
    with col2:
        if st.button("📈 Ganancia"):
            st.session_state.consulta_ia = "¿Cuál es la ganancia?"
        if st.button("🏆 Más vendido"):
            st.session_state.consulta_ia = "¿Cuál es el producto más vendido?"
    with col3:
        if st.button("💼 Valor inventario"):
            st.session_state.consulta_ia = "¿Cuánto vale el inventario?"
        if st.button("🧠 Sugerencias"):
            st.session_state.consulta_ia = "Dame sugerencias"

    st.markdown("---")
    st.markdown("### 📊 Visualización Gráfica")
    if st.button("📈 Mostrar gráfica de ventas (X=Producto, Y=Ganancia)"):
        st.session_state.mostrar_grafica_ia = True

    if st.session_state.get("mostrar_grafica_ia", False):
        st.markdown("#### 📈 Gráfica de Ganancia por Producto")

        ganancia_por_producto = {}
        for d in st.session_state.detalle_ventas:
            p = obtener_producto_por_id(d["producto_id"])
            if p:
                ganancia_unitaria = d["precio_unitario"] - p["precio_compra"]
                ganancia_total_prod = ganancia_unitaria * d["cantidad"]
                ganancia_por_producto[d["nombre"]] = ganancia_por_producto.get(d["nombre"], 0) + ganancia_total_prod

        if not ganancia_por_producto:
            st.warning("⚠️ No hay ventas registradas todavía. Registra una venta primero para ver la gráfica.")
        else:
            productos_grafica = list(ganancia_por_producto.keys())
            ganancias_grafica = list(ganancia_por_producto.values())

            n = len(productos_grafica)
            ancho = max(700, n * 100)
            alto = 420
            padding_izq = 90
            padding_der = 40
            padding_sup = 60
            padding_inf = 100

            max_valor = max(ganancias_grafica) * 1.15 if max(ganancias_grafica) > 0 else 1
            min_valor = 0
            alto_util = alto - padding_sup - padding_inf
            ancho_util = ancho - padding_izq - padding_der

            if n == 1:
                puntos_x = [ancho / 2]
            else:
                puntos_x = [padding_izq + i * ancho_util / (n - 1) for i in range(n)]

            puntos_y = [
                alto - padding_inf - ((g - min_valor) / (max_valor - min_valor)) * alto_util
                for g in ganancias_grafica
            ]

            path_linea = "M " + " L ".join([f"{x},{y}" for x, y in zip(puntos_x, puntos_y)])
            path_area = path_linea + f" L {puntos_x[-1]},{alto - padding_inf} L {puntos_x[0]},{alto - padding_inf} Z"

            circulos = ""
            etiquetas_x = ""
            for x, y, prod, gan in zip(puntos_x, puntos_y, productos_grafica, ganancias_grafica):
                circulos += f'<circle cx="{x}" cy="{y}" r="7" fill="#4CAF50" stroke="white" stroke-width="2"/>'
                circulos += (
                    f'<text x="{x}" y="{y - 14}" font-size="12" text-anchor="middle" '
                    f'fill="#1a1a1a" font-weight="bold">${gan:,.2f}</text>'
                )
                partes = prod.split()
                if len(prod) > 12 and len(partes) > 1:
                    mitad = len(partes) // 2 + len(partes) % 2
                    linea1 = " ".join(partes[:mitad])
                    linea2 = " ".join(partes[mitad:])
                    etiquetas_x += (
                        f'<text x="{x}" y="{alto - padding_inf + 25}" font-size="11" '
                        f'text-anchor="middle" fill="#333">{linea1}</text>'
                        f'<text x="{x}" y="{alto - padding_inf + 40}" font-size="11" '
                        f'text-anchor="middle" fill="#333">{linea2}</text>'
                    )
                else:
                    etiquetas_x += (
                        f'<text x="{x}" y="{alto - padding_inf + 25}" font-size="11" '
                        f'text-anchor="middle" fill="#333">{prod}</text>'
                    )

            guias = ""
            for i in range(6):
                y_g = padding_sup + i * alto_util / 5
                valor_g = max_valor - i * (max_valor - min_valor) / 5
                guias += (
                    f'<line x1="{padding_izq}" y1="{y_g}" x2="{ancho - padding_der}" y2="{y_g}" '
                    f'stroke="#e0e0e0" stroke-width="1" stroke-dasharray="3,3"/>'
                    f'<text x="{padding_izq - 10}" y="{y_g + 4}" font-size="10" '
                    f'text-anchor="end" fill="#666">${valor_g:.2f}</text>'
                )

            svg_grafica = (
                f'<div style="background-color:#ffffff;border-radius:10px;padding:15px;overflow-x:auto;border:1px solid #ddd;">'
                f'<svg width="{ancho}" height="{alto}" viewBox="0 0 {ancho} {alto}" xmlns="http://www.w3.org/2000/svg" style="background-color:#ffffff;display:block;">'
                f'{guias}'
                f'<line x1="{padding_izq}" y1="{alto - padding_inf}" x2="{ancho - padding_der}" y2="{alto - padding_inf}" stroke="#333" stroke-width="2"/>'
                f'<line x1="{padding_izq}" y1="{padding_sup}" x2="{padding_izq}" y2="{alto - padding_inf}" stroke="#333" stroke-width="2"/>'
                f'<text x="{(padding_izq + ancho - padding_der) / 2}" y="{alto - 15}" '
                f'font-size="13" text-anchor="middle" fill="#333" font-weight="bold">PRODUCTOS</text>'
                f'<text x="25" y="{alto / 2}" font-size="13" text-anchor="middle" fill="#333" font-weight="bold" '
                f'transform="rotate(-90 25 {alto / 2})">GANANCIA ($)</text>'
                f'<path d="{path_area}" fill="#4CAF50" opacity="0.15"/>'
                f'<path d="{path_linea}" fill="none" stroke="#4CAF50" stroke-width="3" stroke-linejoin="round"/>'
                f'{circulos}'
                f'{etiquetas_x}'
                f'</svg>'
                f'</div>'
            )

            st.markdown(svg_grafica, unsafe_allow_html=True)

            st.caption(
                f"📊 **Ganancia total mostrada:** ${sum(ganancias_grafica):,.2f} | "
                f"**Productos:** {len(productos_grafica)}"
            )

            if st.button("❌ Ocultar gráfica"):
                st.session_state.mostrar_grafica_ia = False
                st.rerun()

    st.markdown("---")

    pregunta = st.text_input("Escribe tu consulta:",
                             value=st.session_state.get("consulta_ia", ""),
                             placeholder="Ej: ¿Qué productos tienen stock bajo?")

    if st.button("🚀 Consultar", type="primary"):
        if pregunta:
            respuesta = responder_consulta(pregunta)
            st.markdown("---")
            st.subheader("🤖 Respuesta del Asistente")
            st.markdown(respuesta)
        else:
            st.warning("⚠️ Escribe una consulta primero")

    st.markdown("---")
    with st.expander("📖 Ver todas las consultas disponibles"):
        st.markdown("""
        | Consulta | Descripción |
        |----------|-------------|
        | ¿Qué productos tienen stock bajo? | Alertas de reposición |
        | ¿Cuál es el total de ventas? | Total vendido |
        | ¿Cuál es la ganancia? | Utilidad acumulada |
        | ¿Cuál es el producto más vendido? | Top ventas (con empates) |
        | ¿Cuánto vale el inventario? | Valor del stock |
        | ¿Cuántos productos hay? | Total de productos |
        | Dame sugerencias | Recomendaciones inteligentes |
        """)


# ============================================================
# PIE DE PÁGINA
# ============================================================
st.markdown("---")
st.caption("🛒 Mini Market Express | Contáctenos por 0285-6312346 -- 0414-5432109 | Ciudad Bolívar - Venezuela")
