import fitz  # PyMuPDF
import json
import re


def extract_text_and_tables_from_pdf(pdf_path):
    """Extrae texto plano y tablas de un PDF."""
    document = fitz.open(pdf_path)
    extracted_data = []

    for page_num in range(len(document)):
        page = document[page_num]
        text = page.get_text("text")  # Extrae el texto plano

        # Intentamos identificar tablas (líneas que tienen estructura tabular)
        tables = extract_tables_from_text(text)

        # Almacenamos los datos organizados
        page_data = {
            "numero_pagina": page_num + 1,
            "texto": text.strip(),
            "tablas": tables
        }
        extracted_data.append(page_data)

    document.close()
    return extracted_data


def extract_tables_from_text(text):
    """Identifica posibles tablas en el texto."""
    tables = []
    lines = text.split("\n")  # Dividimos el texto en líneas
    for line in lines:
        # Detecta líneas tabulares con separación por comas, tabulaciones o espacios múltiples
        if re.search(r"(,|\t|\s{2,})", line):
            tables.append(line.strip())
    return tables


def save_to_json(data, output_path):
    """Guarda los datos en un archivo JSON."""
    with open(output_path, "w", encoding="utf-8") as json_file:
        json.dump(data, json_file, ensure_ascii=False, indent=4)


if __name__ == "__main__":
    pdf_path = "data/pdfs/Informe-GEM-Euskadi-2022-2023.pdf"  # Ruta al PDF
    output_path = "data/extracted_data_structured.json"  # Donde se guardará el JSON estructurado

    print("Extrayendo texto y tablas del PDF...")
    structured_data = extract_text_and_tables_from_pdf(pdf_path)

    print("Guardando datos estructurados en un archivo JSON...")
    save_to_json(structured_data, output_path)

    print(f"Datos guardados en {output_path}")
