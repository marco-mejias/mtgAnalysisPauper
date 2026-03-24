import requests
from bs4 import BeautifulSoup
import time
from src.text_parser import TextParser
from src.ml_engine import MLEngine

class MetaAnalyzer:
    def __init__(self):
        # Configuramos URLs, headers y herramientas necesarias para el scraping y análisis
        self.base_url = "https://www.mtggoldfish.com"
        self.meta_url = f"{self.base_url}/metagame/pauper#paper"
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        self.parser = TextParser()
        self.ml_engine = MLEngine()
        self.last_deck_cards = []

    def analyze_decks(self, limit=15):
        # Recorremos el top mazos para sacar dos cosas: 1) Un perfil detallado de cada mazo (colores, plan, capacidades clave) y 2) Un dataset de cartas para entrenar el ML, que deducirá patrones en las cartas
        print(f"--- Scrapeando los {limit} primeros mazos ---")
        deck_results = []
        ml_training_data = []

        try:
            response = requests.get(self.meta_url, headers=self.headers)
            soup = BeautifulSoup(response.text, 'html.parser')
            deck_tiles = soup.find_all('div', class_='archetype-tile', limit=limit)

            for idx, tile in enumerate(deck_tiles):
                title_elem = tile.find('span', class_='deck-price-paper').find_previous('a')
                deck_name = title_elem.text.strip()
                link = title_elem['href']
                deck_url = self.base_url + link

                print(f"[{idx+1}/{limit}] Analizando: {deck_name}...")
                deck_profile = self._process_single_deck(deck_name, deck_url)

                if deck_profile:
                    deck_results.append(deck_profile)
                    
                    if hasattr(self, 'last_deck_cards') and self.last_deck_cards:
                        ml_training_data.append({
                            "colors": deck_profile.get('color_dominance', {}), 
                            "cards": self.last_deck_cards
                        })
                
                time.sleep(1) # Cortesía con el servidor (para eviutar bloqueos)

            if ml_training_data:
                print("Entrenando el motor de Machine Learning con el nuevo Meta...")
                self.ml_engine.train_model(ml_training_data)

            return deck_results

        except Exception as e:
            print(f"Error crítico en analyze_decks: {e}")
            return []

    def _process_single_deck(self, deck_name, url):
        #Procesamos un mazo individual para extraer su perfil y las cartas que lo componen. 
        resp = requests.get(url, headers=self.headers)
        if resp.status_code != 200: return None
        soup = BeautifulSoup(resp.text, 'html.parser')

        # Extraemos los enlaces a las cartas (filtrando por patrones comunes en la URL de MTGGoldfish), para evitar errores si cambian el HTML y mayor rapidez.
        all_links = soup.find_all('a', href=True)
        cards = []
        nombres_vistos = set()
        
        for a in all_links:
            href = a['href']
            # Filtramos que sea un link a una carta
            if '/price/' in href and 'index' not in href and 'paper' not in href:
                card_name = a.text.strip()
                if card_name and len(card_name) > 2 and card_name not in nombres_vistos:
                    nombres_vistos.add(card_name)
                    cards.append({"name": card_name, "qty": 2})

        if not cards: 
            print("No se encontró ningún enlace a cartas. HTML vacío.")
            return None

        # Consultar Scryfall en lote (Límite 75 cartas, estandar en Pauper)
        identifiers = [{"name": c["name"]} for c in cards[:75]] 
        scryfall_resp = requests.post("https://api.scryfall.com/cards/collection", json={"identifiers": identifiers}).json()
        
        if "data" not in scryfall_resp: return None
        card_data_map = {c["name"]: c for c in scryfall_resp["data"]}

        cards_data_buffer = []
        total_cmc = 0
        total_non_lands = 0
        color_counts = {"U": 0, "B": 0, "R": 0, "G": 0, "W": 0}
        type_counts = {"Creature": 0, "Instant": 0, "Sorcery": 0}
        feature_weights = {}
        clean_cards_for_ml = []

        for item in cards:
            c_name = item["name"]
            qty = item["qty"]
            
            if c_name not in card_data_map: continue
            c_data = card_data_map[c_name]
            
            parsed = self.parser.analyze(c_data.get("oracle_text", ""))
            
            cards_data_buffer.append((qty, c_name, c_data, parsed))
            clean_cards_for_ml.append(c_data)

            type_line = c_data.get("type_line", "")
            is_land = "Land" in type_line
            mana_cost = c_data.get("mana_cost", "")
            
            for color in color_counts.keys():
                color_counts[color] += mana_cost.count(color) * qty
                
            if not is_land:
                total_cmc += c_data.get("cmc", 0) * qty
                total_non_lands += qty
                
                if "Creature" in type_line: type_counts["Creature"] += qty
                if "Instant" in type_line: type_counts["Instant"] += qty
                if "Sorcery" in type_line: type_counts["Sorcery"] += qty
                
                all_features = set(parsed["mechanics"]) | set(parsed["triggers"]) | set(parsed["actions"].keys())
                for feature in all_features:
                    feature_weights[feature] = feature_weights.get(feature, 0) + qty

        self.last_deck_cards = clean_cards_for_ml

        avg_cmc = total_cmc / total_non_lands if total_non_lands > 0 else 0
        
        total_devotion = sum(color_counts.values())
        color_dominance = {k: round(v / total_devotion, 2) if total_devotion > 0 else 0.0 for k, v in color_counts.items()}
        
        plan = "Midrange"
        spell_density = (type_counts["Instant"] + type_counts["Sorcery"]) / max(1, total_non_lands)
        creature_density = type_counts["Creature"] / max(1, total_non_lands)
        
        if avg_cmc < 2.0 and creature_density > 0.4: plan = "Aggro"
        elif spell_density > 0.5: plan = "Control"
        if "combo" in deck_name.lower() or "storm" in deck_name.lower() or "dredge" in deck_name.lower() or "elves" in deck_name.lower(): plan = "Combo"
        
        sorted_features = sorted(feature_weights.items(), key=lambda x: x[1], reverse=True)
        top_capabilities = [f[0] for f in sorted_features[:4]]
        
        max_weight = max(feature_weights.values()) if feature_weights else 1
        normalized_weights = {k: round((v / max_weight) * 5.0, 1) for k, v in feature_weights.items() if v > 1}
        
        print(f" Extraídas {len(clean_cards_for_ml)} cartas únicas para ML.")
        
        return {
            "Archetype": deck_name,
            "Plan": plan,
            "Avg_CMC": round(avg_cmc, 2),
            "Colors": color_dominance,
            "Top_Capabilities": str(top_capabilities),
            "weights": str(normalized_weights)
        }