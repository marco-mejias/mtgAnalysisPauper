import pandas as pd
import joblib
import random
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from src.text_parser import TextParser

class MLEngine:
    def __init__(self):
        self.parser = TextParser()
        self.model = None
        self.feature_columns = None

    def _extract_features(self, card_data, deck_colors_str):
        parsed = self.parser.analyze(card_data.get('oracle_text', ''))
        
        # 1. Features Numéricas
        features = {
            'cmc': float(card_data.get('cmc', 0)),
            'power': self._safe_int(card_data.get('power', 0)),
            'toughness': self._safe_int(card_data.get('toughness', 0)),
        }

        # 2. Contexto de Color
        features['deck_is_W'] = 1 if 'W' in deck_colors_str else 0
        features['deck_is_U'] = 1 if 'U' in deck_colors_str else 0
        features['deck_is_B'] = 1 if 'B' in deck_colors_str else 0
        features['deck_is_R'] = 1 if 'R' in deck_colors_str else 0
        features['deck_is_G'] = 1 if 'G' in deck_colors_str else 0

        # 3. Keywords
        keywords = [
            "effect_draw", "effect_counter", "effect_destroy", "effect_damage",
            "mechanic_cost_reduction_dynamic", "mechanic_affinity", 
            "flying", "haste", "flash", "mechanic_land_cycling",
            "effect_hard_removal", "effect_hard_counter", "self_mill"
        ]
        
        all_tags = set(parsed['mechanics']) | set(parsed['actions'].keys())
        
        for kw in keywords:
            features[kw] = 1 if kw in all_tags else 0

        return features

    def train_model(self, decks_data):
        print("🤖 Entrenando IA con Scikit-Learn...")
        
        X = []
        y = []
        
        all_cards_pool = []
        for deck in decks_data:
            for card in deck['cards']:
                all_cards_pool.append(card)

        if not all_cards_pool:
            print("⚠️ No hay cartas para entrenar.")
            return

        for deck in decks_data:
            colors = deck['colors']
            deck_card_names = {c['name'] for c in deck['cards']}
            
            # Positivos
            for card in deck['cards']:
                feats = self._extract_features(card, colors)
                X.append(list(feats.values()))
                y.append(1)

            # Negativos
            for _ in range(len(deck['cards'])):
                random_card = random.choice(all_cards_pool)
                if random_card['name'] not in deck_card_names:
                    feats = self._extract_features(random_card, colors)
                    X.append(list(feats.values()))
                    y.append(0)

        # Guardar nombres de columnas
        dummy_feats = self._extract_features(all_cards_pool[0], "WUBRG")
        self.feature_columns = list(dummy_feats.keys())

        # Random Forest
        self.model = RandomForestClassifier(n_estimators=100, max_depth=12, random_state=42)
        self.model.fit(X, y)
        
        joblib.dump(self.model, 'data/ml_model.pkl')
        joblib.dump(self.feature_columns, 'data/ml_columns.pkl')
        print("✅ Modelo entrenado y guardado en 'data/ml_model.pkl'")

    def load_model(self):
        try:
            self.model = joblib.load('data/ml_model.pkl')
            self.feature_columns = joblib.load('data/ml_columns.pkl')
            return True
        except:
            return False

    def predict_probability(self, card_data, deck_colors):
        if not self.model: return 0.0
        
        feats = self._extract_features(card_data, deck_colors)
        vector = [feats.get(col, 0) for col in self.feature_columns]
        
        probs = self.model.predict_proba([vector])[0]
        return round(probs[1] * 100, 1)

    def _safe_int(self, val):
        try: return int(val)
        except: return 0