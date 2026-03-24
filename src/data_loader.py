import csv
import json
import os

# Cargamos los decks generados por el scraper, con sus perfiles y estadísticas, para que la IA pueda evaluarlos.
def load_archetypes_from_csv(filepath="data/archetypes_review.csv"):
    if not os.path.exists(filepath):
        print(f"Error: No se encuentra el archivo {filepath}")
        return {}

    archetypes = {}
    
    try:
        with open(filepath, mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            
            for row in reader:
                name = row['Archetype']
                
                # 1. Limpiamos comillas dobles (AHORA EN LA COLUMNA 'Colors')
                # El scraper nuevo guarda la dominancia en la columna 'Colors'
                raw_dom = row.get('Colors', '{}')
                if raw_dom.startswith('"') and raw_dom.endswith('"'):
                    raw_dom = raw_dom[1:-1]
                # Reemplazamos las comillas dobles escapadas y las simples por dobles reales para el JSON
                raw_dom = raw_dom.replace('""', '"').replace("'", '"')
                
                try:
                    color_dominance = json.loads(raw_dom)
                except:
                    color_dominance = {"U": 0, "B": 0, "R": 0, "G": 0, "W": 0}

                # Deducimos la lista pura de colores a partir de la dominancia (ej: ['U', 'R'])
                pure_colors = [color for color, dom in color_dominance.items() if float(dom) > 0]

                # 2. Convertimos pesos en floats (AHORA EN LA COLUMNA 'weights')
                try:
                    weights_str = row.get('weights', '{}').replace('""', '"').replace("'", '"')
                    weights = json.loads(weights_str)
                except:
                    weights = {}
                
                # Fix común: Role_Stats_JSON ya no existe en tu nuevo CSV, lo inicializamos vacío para que no rompa el Evaluator
                role_stats = {}

                # 2.5 Extraemos Top_Capabilities, que ahora viene como un string tipo "['effect_cantrip', 'flying']"
                raw_cap = row.get('Top_Capabilities', '[]').replace('""', '"').replace("'", '"')
                try:
                    capabilities = json.loads(raw_cap)
                except:
                    capabilities = []

                # 3. Calculamos max_cmc (coste mana maximo) dinámicamente (ejemplo: avg + 3.5, con un mínimo de 5.0 para cubrir aggro)
                avg_cmc = float(row.get('Avg_CMC', 2.0))
                max_cmc = max(5.0, avg_cmc + 3.5)

                archetypes[name] = {
                    "plan": row.get('Plan', 'Midrange'),
                    "colors": pure_colors, # Usamos la lista de colores que extrajimos de la dominancia
                    "color_dominance": color_dominance,
                    "avg_cmc": avg_cmc,
                    "max_cmc": max_cmc,
                    "capabilities": capabilities, # Pasamos la lista real, no el string
                    "weights": weights,
                    "role_stats": role_stats
                }
                
    except Exception as e:
        print(f"❌ Error leyendo CSV: {e}")
        return {}

    return archetypes