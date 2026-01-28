"""
EXPRESIONES REGULARES PARA DETECTAR SALARIOS EN OFERTAS DE EMPLEO
Basadas en el análisis completo de la base de datos ofertas_tecnoempleo_raw.csv

Patrones de salario encontrados en las ofertas:
- Salario exacto: "28.000 euros brutos anuales", "42.000 € brutos anuales"
- Rango salarial: "50.000 EUR - 60.000 EUR", "45.000 y 46.000 € brutos anuales"
- Salario sin especificar moneda: "38-40k b/año", "4 000 – 5 000 EUR net/month"
- Salario con "hasta": "Hasta €35K", "Hasta €45K", "Hasta €70K"
- Salario con formato variable: "€55-65K", "€45-55K"
"""

import re

# =====================================================================
# EXPRESIONES REGULARES PARA DETECTAR SALARIOS
# =====================================================================

REGEX_SALARIOS = [
    # 1. SALARIO EXACTO CON PUNTO O SIN (formato: 28.000 euros brutos anuales)
    {
        "nombre": "Salario exacto con punto y unidad",
        "patron": r"(?:SALARIO|salario|Salario)\s*:?\s*(\d{1,3}[\.,]\d{3})\s*(?:€|EUR|euros?)\s*(?:bruto|net|anuales?|al\s*año)",
        "ejemplo": "SALARIO: 28.000 euros brutos anuales"
    },
    
    # 2. SALARIO EN RANGO (formato: 50.000 EUR - 60.000 EUR)
    {
        "nombre": "Rango salarial con puntos y separador",
        "patron": r"(?:salario|SALARIO)\s*:?\s*(\d{1,3}[\.,]\d{3})\s*(?:€|EUR|euros?)\s*[-–]\s*(\d{1,3}[\.,]\d{3})\s*(?:€|EUR|euros?)",
        "ejemplo": "salario: 50.000 EUR - 60.000 EUR"
    },
    
    # 3. RANGO CORTO EN K (formato: €55-65K, €45-55K)
    {
        "nombre": "Rango corto en K",
        "patron": r"(?:salario|SALARIO|Rango\s*salarial)\s*:?\s*(?:€|EUR)?\s*(\d{2})[,.\-–]+(\d{2})\s*[Kk]",
        "ejemplo": "SALARIO: €55-65K"
    },
    
    # 4. SALARIO EXACTO EN K (formato: 42.000 € brutos anuales)
    {
        "nombre": "Salario exacto en formato numérico con K",
        "patron": r"(?:salario|SALARIO|Rango)\s*:?\s*(\d{2}[,.\s]?\d{3})\s*(?:€|EUR|k|K)\s*(?:bruto|net|anual|b/año|al\s*año)?",
        "ejemplo": "Salario: 42.000 € brutos anuales"
    },
    
    # 5. HASTA CANTIDAD (formato: Hasta €35K, Hasta €45K)
    {
        "nombre": "Salario con 'Hasta'",
        "patron": r"(?:hasta|HASTA|Up\s*to)\s+(?:€|EUR)?\s*(\d+(?:[Kk]|[\.,]\d{3})(?![%\w]))",
        "ejemplo": "SALARIO | Hasta €35K"
    },
    
    # 6. RANGO CON SALARIO VARIABLE (formato: €55-65K | VARIABLE)
    {
        "nombre": "Rango con componente variable",
        "patron": r"(?:salario|SALARIO)\s*\|\s*(?:€|EUR)?\s*(\d{2})[,.\-–](\d{2})[Kk]?\s*\|\s*VARIABLE",
        "ejemplo": "SALARIO | €55-65K | VARIABLE"
    },
    
    # 7. SALARIO EN FORMATO MENSUAL (formato: 4 000 – 5 000 EUR net/month)
    {
        "nombre": "Salario mensual",
        "patron": r"(\d+\s*\d{3})\s*(?:[-–]\s*(\d+\s*\d{3}))?\s*(?:€|EUR|euros?)\s*(?:net|brut|mensual|/month)",
        "ejemplo": "4 000 – 5 000 EUR net/month"
    },
    
    # 8. COMPONENTE VARIABLE SEPARADO (formato: €2,838K)
    {
        "nombre": "Componente variable",
        "patron": r"VARIABLE\s*\|\s*(?:€|EUR)?\s*([\d,\.]+[Kk]?)",
        "ejemplo": "VARIABLE | €2,838K"
    },
    
    # 9. SALARIO ENTRE X E Y (formato: entre 45.000 y 46.000 € brutos anuales)
    {
        "nombre": "Salario con 'entre...y'",
        "patron": r"entre\s+(\d+[\.,]?\d*)\s*(?:€|EUR|euros?)?\s*y\s*(\d+[\.,]?\d*)\s*(?:€|EUR|euros?)",
        "ejemplo": "entre 45.000 y 46.000 € brutos anuales"
    },
    
    # 10. RANGO FORMATOS ALTERNATIVOS (formato: 38-40k b/año)
    {
        "nombre": "Rango corto alternativo",
        "patron": r"(\d{2})[,.\-–](\d{2})[kK]?\s*(?:b/año|b/ano|bruto|EUR|€)",
        "ejemplo": "38-40k b/año"
    },
    
    # 11. SALARIO COMPETITIVO CON RANGO (formato: Salario competitivo entre 70.000 € y 75.000 € anuales)
    {
        "nombre": "Salario competitivo con rango",
        "patron": r"(?:salario|competitivo)\s+(?:entre)?\s+(\d+[\.,]\d{3})\s*(?:€|EUR)\s*(?:y|[-–])\s*(\d+[\.,]\d{3})\s*(?:€|EUR)",
        "ejemplo": "Salario competitivo entre 70.000 € y 75.000 € anuales"
    },
    
    # 12. RANGO SALARIAL CON TEXTO (formato: Rango salarial competitivo: 50.000 EUR - 60.000 EUR)
    {
        "nombre": "Rango salarial competitivo",
        "patron": r"rango\s+salarial\s+(?:competitivo)?\s*:?\s*(\d+[\.,]\d{3})\s*(?:€|EUR)\s*[-–]\s*(\d+[\.,]\d{3})\s*(?:€|EUR)",
        "ejemplo": "Rango salarial competitivo: 50.000 EUR - 60.000 EUR"
    },
    
    # 13. SALARIO B2B MENSUAL (formato: 4 000 – 5 000 EUR net/month)
    {
        "nombre": "Salario B2B contrato",
        "patron": r"(?:contract|B2B|freelance)\s+(\d+\s*\d{3})\s*(?:€|EUR|euros?)?\s*(?:[-–]\s*(\d+\s*\d{3}))?\s*(?:net|brut)?.*(?:month|mes|mensual)",
        "ejemplo": "B2B contract 4 000 – 5 000 EUR net/month"
    },
    
    # 14. SALARIO NEGOCIABLE/SEGÚN EXPERIENCIA
    {
        "nombre": "Salario según experiencia sin cantidad exacta",
        "patron": r"(?:salario|compensación|retribución)\s*(?:a\s+)?(?:negociar|según|acorde|competitivo)\s+(?:según|con|a)\s+(?:experiencia|valía|conocimientos)",
        "ejemplo": "Salario a negociar según experiencia"
    },
    
    # 15. SALARIO CON DESCRIPCIÓN Y VALOR (formato: Salario: 36-38K bruto/año)
    {
        "nombre": "Salario corto con descripción",
        "patron": r"(?:salario|Salario)\s*:?\s*(\d{2})[,.\-–](\d{2})[Kk]?\s*(?:bruto|neto|b/año|b/ano)",
        "ejemplo": "Salario: 36-38K bruto/año"
    },
    
    # 16. RANGO SIN PALABRAS CLAVE (formato: 50.000-60.000 o 50000-60000) - MÁS FLEXIBLE
    {
        "nombre": "Rango flexible sin palabras clave",
        "patron": r"(?:^|\s|[\|,])(\d{2,3}[\.,]\d{3})\s*[-–]\s*(\d{2,3}[\.,]\d{3})(?:\s|€|EUR|$)",
        "ejemplo": "50.000-60.000"
    },
    
    # 17. EXACTO CON EUR SIN CONTEXTO (formato: 50.000 EUR) - MÁS FLEXIBLE
    {
        "nombre": "Exacto flexible con EUR",
        "patron": r"(?:^|\s|[\|,])(\d{2,3}[\.,]\d{3})\s*(?:€|EUR)(?:\s|$|[^%\w])",
        "ejemplo": "50.000 EUR"
    },
]

# =====================================================================
# FUNCIÓN PARA BUSCAR SALARIOS
# =====================================================================

def detectar_salarios(texto):
    """
    Busca todos los patrones de salario en un texto.
    
    Args:
        texto (str): Texto de la oferta de empleo
        
    Returns:
        list: Lista de diccionarios con salarios encontrados
    """
    salarios_encontrados = []
    
    for regex_info in REGEX_SALARIOS:
        patron = regex_info["patron"]
        try:
            coincidencias = re.finditer(patron, texto, re.IGNORECASE)
            for match in coincidencias:
                salarios_encontrados.append({
                    "tipo": regex_info["nombre"],
                    "valor": match.group(0),
                    "grupos": match.groups(),
                    "inicio": match.start(),
                    "fin": match.end()
                })
        except Exception as e:
            print(f"Error en patrón {regex_info['nombre']}: {e}")
    
    return salarios_encontrados

# =====================================================================
# EJEMPLOS DE USO
# =====================================================================

if __name__ == "__main__":
    # Ejemplos de textos con diferentes formatos de salario
    ejemplos = [
        "SALARIO: 28.000 euros brutos anuales (en 12 pagas)",
        "Salario: 42.000 € brutos anuales",
        "Rango salarial competitivo: 50.000 EUR - 60.000 EUR",
        "SALARIO | Hasta €35K | VARIABLE | €2,838K",
        "Salario competitivo entre 70.000 € y 75.000 € anuales",
        "Entre 45.000 y 46.000 € brutos anuales, según experiencia",
        "4 000 – 5 000 EUR net/month - pure B2B contract",
        "Rango salarial: 38-40k b/año",
        "💶 Salario: entre 45.000 y 46.000 € brutos anuales, según experiencia",
        "SALARIO | €55-65K | UBICACIÓN | Madrid",
    ]
    
    print("=" * 80)
    print("PRUEBAS DE EXPRESIONES REGULARES PARA DETECTAR SALARIOS")
    print("=" * 80)
    
    for i, ejemplo in enumerate(ejemplos, 1):
        print(f"\n{i}. Texto: {ejemplo}")
        salarios = detectar_salarios(ejemplo)
        if salarios:
            for salario in salarios:
                print(f"   ✓ Tipo: {salario['tipo']}")
                print(f"   ✓ Valor: {salario['valor']}")
        else:
            print("   ✗ No se encontraron salarios")
    
    print("\n" + "=" * 80)
