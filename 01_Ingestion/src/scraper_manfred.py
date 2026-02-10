from playwright.sync_api import sync_playwright
import pandas as pd
import os
from datetime import datetime

def scrape():
  with sync_playwright() as p:
    browser = p.chromium.launch(headless=True, slow_mo=300)
    context = browser.new_context()
    page = context.new_page()
    
    print("🚀 Navegando...")
    page.goto("https://www.getmanfred.com/ofertas-empleo", wait_until="load")
    
    # TRUCO GENÉRICO: Esperamos a que aparezca cualquier enlace que hable de trabajos
    # En lugar de una clase CSS, buscamos por "rol" de accesibilidad
    print("Buscando elementos de oferta...")
    ofertas_locator = page.get_by_role("link").filter(has_text="Analyst") # O simplemente has_text="" para todos
    
    # Forzamos una espera a que al menos uno sea visible
    try:
      page.wait_for_selector("a[href*='/ofertas-empleo/']", timeout=10000)
    except:
      print("No se encontraron enlaces con /ofertas-empleo/. Intentando captura genérica...")
    
    # CAPTURA GENÉRICA: Buscamos todos los enlaces que parecen ser ofertas
    # Usamos una expresión regular para el enlace (href)
    links = page.locator("a[href*='/ofertas-empleo/']").all()
    
    results = []
    print(f"📦 Se han detectado {len(links)} posibles ofertas.")
    
    for link in links:
      # Extraemos TODO el texto que hay dentro del enlace, sea cual sea su estructura
      texto_completo = link.inner_text()
      url = link.get_attribute("href")
      
      if len(texto_completo.strip()) > 10:
        results.append({
          "contenido": texto_completo.replace("\n", " | "),
          "url": f"https://www.getmanfred.com{url}",
          "fecha_captura": datetime.now().strftime("%Y-%m-%d")
        })
    
    browser.close()
    
    # Lógica de guardado (BI Ready)
    if results:
      df = pd.DataFrame(results)
      if not os.path.exists('../../data'): os.makedirs('../../data')
      df.to_csv("../../data/ofertas_generico.csv", index=False, encoding='utf-8-sig')
      print(f"✅ Guardadas {len(df)} filas.")
    else:
      print("❌ No se pudo extraer nada. El DOM podría estar vacío o bloqueado.")

if __name__ == "__main__":
  scrape()