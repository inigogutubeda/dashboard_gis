import pdfplumber        # Librería para manejar la extracción de datos desde PDFs
import json              # Librería estándar para convertir estructuras Python a JSON
import os                # Para manejo de rutas de archivos, si fuera necesario

def process_pdf(pdf_path: str, output_json: str) -> None:
    """
    Procesa un archivo PDF y extrae:
    1. Texto por página
    2. Tablas por página

    Parámetros:
    - pdf_path: ruta del archivo PDF a procesar
    - output_json: ruta del archivo JSON de salida con la información extraída

    Retorno:
    - No retorna nada, pero crea un archivo JSON con la información.
    """

    # Validamos que el archivo PDF exista
    if not os.path.isfile(pdf_path):
        print(f"ERROR: El archivo {pdf_path} no existe.")
        return

    # Abrimos el PDF con pdfplumber
    with pdfplumber.open(pdf_path) as pdf:

        # Estructura principal que guardará la info de todo el PDF
        pdf_data = {
            "file_name": os.path.basename(pdf_path),  # Nombre del archivo PDF
            "total_pages": len(pdf.pages),            # Número total de páginas
            "pages": []                               # Lista de páginas con su contenido
        }

        # Recorremos cada página del PDF
        for page_index, page in enumerate(pdf.pages):
            
            # ---------------------
            # 1. Extraer el texto
            # ---------------------
            page_text = page.extract_text() if page.extract_text() else ""
            # "page.extract_text()" devuelve el texto de la página o None. 
            # Usamos un condicional para evitar errores si es None.
            
            # ---------------------
            # 2. Extraer tablas
            # ---------------------
            # pdfplumber proporciona "extract_tables", que intenta detectar tablas 
            # dentro del PDF. Retorna una lista de tablas, donde cada tabla 
            # es una lista de filas, y cada fila es una lista de strings.
            tables = page.extract_tables()
            
            # Convertimos la estructura de tablas en algo más amigable para JSON.
            formatted_tables = []
            for table in tables:
                if len(table) > 1:
                    # La primera fila la consideramos encabezado
                    headers = table[0]
                    rows_data = table[1:]
                    
                    # Construir una lista de diccionarios donde cada diccionario 
                    # representa una fila con 'columna: valor'
                    table_as_list_of_dicts = [
                        dict(zip(headers, row)) for row in rows_data
                    ]
                    formatted_tables.append(table_as_list_of_dicts)
                else:
                    # Si la tabla es muy pequeña, o no tiene encabezado claro,
                    # simplemente la añadimos como está
                    formatted_tables.append(table)
            
            # Guardamos la información recopilada de la página en el diccionario principal
            pdf_data["pages"].append({
                "page_number": page_index + 1,
                "text": page_text,
                "tables": formatted_tables
            })

    # Finalmente, convertimos el diccionario a JSON y lo guardamos en disco
    with open(output_json, "w", encoding="utf-8") as f:
        json.dump(pdf_data, f, ensure_ascii=False, indent=2)

    print(f"Procesado finalizado. Archivo JSON generado: {output_json}")


if __name__ == "__main__":
    """
    Definimos aquí mismo las rutas para Opción 2 (hardcodeadas):
    """
    # TODO: Ajusta las rutas a tu archivo PDF de entrada y a tu archivo JSON de salida
    pdf_path_arg = r"data/pdfs/Informe-GEM-Euskadi-2022-2023.pdf"      # <---- Cambia aquí la ruta de tu PDF
    output_json_arg = r"C:\Users\marti\UrbegiGIS\data\test.json"   # <---- Cambia aquí la ruta de tu JSON

    process_pdf(pdf_path_arg, output_json_arg)
