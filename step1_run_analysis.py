import pandas as pd
import os
from scrapping.meta_analyzer import MetaAnalyzer

def main():
    if not os.path.exists("data"):
        os.makedirs("data")
        
    # 1. Inicamos el scraper y analizamos el meta
    scraper = MetaAnalyzer()
    
    print("Conectando con MTGGoldfish... (Analizando los 15 mazos Top)")
    results = scraper.analyze_decks(limit=15)
    
    if not results:
        print("\n ERROR: No se pudieron extraer datos de los mazos.")
        print("Revisa tu conexión a internet o si la web ha bloqueado el acceso.")
        return

    # Creamos el DataFrame con la info procesada
    df = pd.DataFrame(results)
    
    output_path = "data/archetypes_review.csv"
    df.to_csv(output_path, index=False)
    
    print("\n" + "X"*50)
    print(f"¡Hecho! Meta actualizado en: {output_path}")
    print("X"*50)
    
    # Reviamos head con las columnas que queremos mostrar (si existen)
    cols_to_show = ['Archetype', 'Plan', 'Avg_CMC', 'Top_Capabilities']
    existing_cols = [c for c in cols_to_show if c in df.columns]
    
    if existing_cols:
        print(df[existing_cols].head().to_string())
    else:
        print("Columnas detectadas:", df.columns.tolist())
        print(df.head().to_string())

if __name__ == "__main__":
    main()