from playwright.sync_api import sync_playwright
import pandas as pd
import os
import re
from datetime import datetime

def scrape_tecnoempleo_multipage(max_paginas=3):
  with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    
    all_results = []
    
    for p_num in range(1, max_paginas + 1):
      # La URL de Tecnoempleo suele usar /p/numero-pagina/ o un parametro ?pagina=
      # Ajustamos a la estructura de búsqueda:
      url = f"https://www.tecnoempleo.com/ofertas-trabajo/?te=data&pagina={p_num}"
      
      print(f"📄 Procesando Página {p_num}...")
      try:
        page.goto(url, wait_until="domcontentloaded", timeout=20000)
        
        # Buscamos los contenedores de las ofertas con el onclick que descubriste
        ofertas_loc = page.locator("div[onclick*='location.href']").all()
        
        urls_pagina = []
        for oferta in ofertas_loc:
          onclick_text = oferta.get_attribute("onclick")
          url_match = re.search(r"location.href='(.*?)'", onclick_text)
          if url_match:
            urls_pagina.append(url_match.group(1))
        
        print(f"✅ Encontradas {len(urls_pagina)} URLs en la página {p_num}")
        
        # Navegación profunda en cada URL de esta página
        for i, detail_url in enumerate(urls_pagina):
          try:
            page.goto(detail_url, wait_until="domcontentloaded", timeout=15000)
            
            titulo = page.locator("h1").inner_text()
            # Tu hallazgo del itemprop="description"
            descripcion = page.locator('div[itemprop="description"]').inner_text()
            
            all_results.append({
              "Puesto": titulo,
              "contenido": descripcion.replace("\n", " "),
              "url": detail_url,
              "fuente": "Tecnoempleo",
              "fecha_captura": datetime.now().strftime("%Y-%m-%d")
            })
            # Feedback visual para saber que no se ha colgado
            if (i+1) % 5 == 0: print(f"   > Procesadas {i+1}/{len(urls_pagina)} ofertas...")

          except Exception as e:
            print(f"   ❌ Error en oferta {i+1}: {e}")
            continue

      except Exception as e:
        print(f"❌ Error cargando la página {p_num}: {e}")
        break
    
    browser.close()
    
    df = pd.DataFrame(all_results)
    df.to_csv("../../data/ofertas_tecnoempleo_raw.csv", index=False, encoding='utf-8-sig')
    print(f"🚀 ¡Misión cumplida! Total: {len(df)} ofertas de Tecnoempleo.")

if __name__ == "__main__":
  scrape_tecnoempleo_multipage(3) # Número de páginas a scrapear, 30 ofertas por página