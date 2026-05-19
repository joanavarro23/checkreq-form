import streamlit as st
import fitz  # PyMuPDF
import os
from datetime import datetime

# Para ejecutar script: python -m streamlit run app.py

# =====================================================================
# CONFIGURACIÓN DE COORDENADAS (COORDINATES_MAP)
# =====================================================================
# INSTRUCCIONES PARA EL USUARIO:
# Deberás ajustar estos valores (x, y) mediante ensayo y error hasta que
# el texto encaje perfectamente en las líneas de tu PDF real.
# 
# NOTA SOBRE LAS COORDENADAS:
# - (0, 0) corresponde a la esquina superior izquierda del PDF.
# - Incrementa el valor 'x' para mover el texto hacia la derecha.
# - Incrementa el valor 'y' para mover el texto hacia abajo.
#
# Los valores a continuación son aproximados/de relleno para que 
# el código sea funcional desde el primer intento.
# =====================================================================

COORDINATES_MAP = {
    # ---------------- Campos de Texto ----------------
    "Customer Name": (325, 212),
    "Address": (325, 234),
    "Type of Service": (325, 254),
    "Subcontractor Name": (325, 275),
    
    # ---------------- Montos Financieros ----------------
    "Total Job": (340, 337),
    "Amount Paid to Date": (340, 358),
    "Subcontractor Total Invoice": (340, 379),
    "Subcontractor Current Invoice": (340, 400),
    
    # ---------------- Verificaciones y Firmas ----------------
    "Person Requesting Payment": (300, 552),
    "Date of Request": (265, 599),
    
    # ---------------- Casillas (Checkbox / Radio Buttons) ----------------
    "Branch_SD": (346, 191),

    "Type of Work_WTR": (353, 295),
    "Type of Work_MLD": (402, 295),
    "Type of Work_RCN": (451, 295),
    "Type of Work_FIR": (498, 295),
    "Type of Work_CON": (543, 295),

    "Who Pays for Claim_INS.": (357, 316),
    "Who Pays for Claim_WA SIGNED": (430, 316),
    "Who Pays for Claim_SELF PAID": (520, 316),

    "Type of Payment_1ST": (354, 420),
    "Type of Payment_2ND": (407, 420),
    "Type of Payment_3RD": (458, 420),
    "Type of Payment_FINAL": (517, 420),

    "Credential on File_YES": (293, 661),
    "Credential on File_NO": (341, 661),

    "QB Verified_YES": (293, 695),
    "QB Verified_NO": (341, 695),
}

st.set_page_config(page_title="Generador de PDF de Pago", layout="wide")

def format_currency(value):
    """Formatea un número a string con formato de moneda (#,##0.00)."""
    return f"{value:,.2f}"

def main():
    st.title("Generador de Check Request PDF")
    st.write("Completa el formulario para generar el PDF rellenado.")
    
    with st.form("pdf_form"):
        # --- SECCIÓN 1: DATOS GENERALES ---
        st.subheader("Datos Generales")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            # Checkbox para Branch SD
            branch_sd = st.checkbox("Branch Location: SD", value=True) 
            customer_name = st.text_input("Customer Name")
            address = st.text_input("Address")
            type_of_service = st.text_input("Type of Service")
            
        with col2:
            subcontractor_name = st.text_input("Subcontractor Name")
            notes = st.text_area("Notes")
            
        with col3:
            st.write("Opciones del Trabajo")
            type_of_work = st.radio("Type of Work", ["WTR", "MLD", "RCN", "FIR", "CON"])
            who_pays = st.radio("Who Pays for Claim", ["INS.", "WA SIGNED", "SELF PAID"])
            type_of_payment = st.radio("Type of Payment", ["1ST", "2ND", "3RD", "FINAL"])
            
        st.divider()
            
        # --- SECCIÓN 2: MONTOS FINANCIEROS ---
        st.subheader("Montos Financieros")
        col_fin1, col_fin2, col_fin3, col_fin4 = st.columns(4)
        
        with col_fin1:
            total_job = st.number_input("Total Job", min_value=0.0, format="%.2f", step=100.0)
        with col_fin2:
            amount_paid = st.number_input("Amount Paid to Date", min_value=0.0, format="%.2f", step=100.0)
        with col_fin3:
            sub_total_invoice = st.number_input("Subcontractor Total Invoice", min_value=0.0, format="%.2f", step=100.0)
        with col_fin4:
            sub_current_invoice = st.number_input("Subcontractor Current Invoice", min_value=0.0, format="%.2f", step=100.0)
            
        st.divider()
            
        # --- SECCIÓN 3: VERIFICACIONES Y FIRMAS ---
        st.subheader("Verificaciones y Firmas")
        col_ver1, col_ver2, col_ver3, col_ver4, col_ver5 = st.columns(5)
        
        with col_ver1:
            person_requesting = st.text_input("Person Requesting Payment")
        with col_ver2:
            date_request = st.date_input("Date of Request", datetime.today())
        with col_ver3:
            credential = st.selectbox("Credential on File", ["YES", "NO"])
        with col_ver4:
            qb_verified = st.selectbox("QB Verified", ["YES", "NO"])
        with col_ver5:
            gp_percent = st.text_input("GP %")
            
        st.divider()
        
        # Botón para generar el PDF
        submitted = st.form_submit_button("Generar PDF", use_container_width=True)
        
        if submitted:
            # Validar que exista el nombre del subcontratista para el nombre del archivo
            safe_sub_name = subcontractor_name.strip().replace(" ", "_")
            if not safe_sub_name:
                safe_sub_name = "Desconocido"
                
            # Diccionario para agrupar los datos de texto a estampar
            text_data = {
                "Customer Name": customer_name,
                "Address": address,
                "Type of Service": type_of_service,
                "Subcontractor Name": subcontractor_name,
                "Total Job": format_currency(total_job),
                "Amount Paid to Date": format_currency(amount_paid),
                "Subcontractor Total Invoice": format_currency(sub_total_invoice),
                "Subcontractor Current Invoice": format_currency(sub_current_invoice),
                "Person Requesting Payment": person_requesting,
                "Date of Request": date_request.strftime("%m/%d/%Y")
            }
            
            # Diccionario para estampar la "X" en las coordenadas correctas según los Radio Buttons
            radio_data = {
                f"Type of Work_{type_of_work}": "X",
                f"Who Pays for Claim_{who_pays}": "X",
                f"Type of Payment_{type_of_payment}": "X",
                f"Credential on File_{credential}": "X",
                f"QB Verified_{qb_verified}": "X"
            }
            
            if branch_sd:
                radio_data["Branch_SD"] = "X"
            
            # Ruta del PDF estático
            template_path = "TEMPLATE_ESTATICO.pdf"
            
            # Verificamos si existe el PDF de plantilla en el directorio actual
            if not os.path.exists(template_path):
                st.error(f"⚠️ Error: No se encontró el archivo '{template_path}'. Por favor, asegúrate de colocar el archivo PDF de plantilla original en el mismo directorio que este script.")
            else:
                try:
                    # Abrir el PDF de plantilla original
                    doc = fitz.open(template_path)
                    
                    # Asumimos que los datos van en la primera página
                    page = doc[0] 
                    
                    # Estampar los Textos
                    for key, value in text_data.items():
                        if key in COORDINATES_MAP and value:  # Solo si el valor no está vacío
                            x, y = COORDINATES_MAP[key]
                            page.insert_text(fitz.Point(x, y), str(value), fontsize=11, fontname="hebo")
                    
                    # Estampar las Casillas ("X")
                    for key, value in radio_data.items():
                        if key in COORDINATES_MAP:
                            x, y = COORDINATES_MAP[key]
                            page.insert_text(fitz.Point(x, y), value, fontsize=11, fontname="hebo")
                            
                    # Estampar GP % (Formato especial)
                    if gp_percent:
                        gp_clean = gp_percent.replace("%", "").strip()
                        gp_text = f"%{gp_clean}"
                        # Coordenadas en la esquina inferior derecha y tamaño de fuente más grande (ej. 18)
                        page.insert_text(fitz.Point(520, 770), gp_text, fontsize=25, fontname="hebo")
                        
                    # Estampar Notes (Formato especial: centrado, multi-línea y más grande)
                    if notes:
                        # Rectángulo aproximado para la caja de notas: (x0, y0, x1, y1)
                        notes_rect = fitz.Rect(335, 445, 540, 520)
                        page.insert_textbox(notes_rect, str(notes), fontsize=16, fontname="hebo", align=fitz.TEXT_ALIGN_CENTER)
                            
                    # Guardar el nuevo PDF
                    output_filename = f"Check_Request_{safe_sub_name}.pdf"
                    doc.save(output_filename)
                    doc.close()
                    
                    st.success(f"✅ ¡PDF generado exitosamente! Nombre del archivo: **{output_filename}**")
                    st.info(f"📂 Ruta completa de guardado: `{os.path.abspath(output_filename)}`")
                    
                except Exception as e:
                    st.error(f"❌ Ocurrió un error al procesar el PDF: {str(e)}")

if __name__ == "__main__":
    main()
