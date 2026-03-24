import sys
from src.text_parser import TextParser
from src.evaluator import CardEvaluator
from src.archetype_manager import ArchetypeManager
from src.data_loader import load_archetypes_from_csv
from src.ml_engine import MLEngine

# Cartas de prueba
test_cards = [
    {
        "name": "Pyroblast",
        "colors": ["R"], "cmc": 1.0, "type_line": "Instant",
        "power": "0", "toughness": "0",
        "oracle_text": "Choose one — • Counter target spell if it's blue. • Destroy target permanent if it's blue."
    },
    {
        "name": "Relic of Progenitus", 
        "colors": [], "cmc": 1.0, "type_line": "Artifact",
        "power": "0", "toughness": "0",
        "oracle_text": "{T}: Target player exiles a card from their graveyard. {1}, Exile Relic of Progenitus: Exile all graveyards. Draw a card."
    },
    {
        "name": "Gorilla Shaman",
        "colors": ["R"], "cmc": 1.0, "type_line": "Creature — Ape Shaman",
        "power": "1", "toughness": "1",
        "oracle_text": "{X}{X}{1}: Destroy target noncreature artifact with mana value X."
    },
    {
        "name": "Weather the Storm",
        "colors": ["G"], "cmc": 2.0, "type_line": "Instant",
        "power": "0", "toughness": "0",
        "oracle_text": "You gain 3 life. Storm (When you cast this spell, copy it for each spell cast before it this turn.)"
    },
    {
        "name": "Dust to Dust",
        "colors": ["W"], "cmc": 3.0, "type_line": "Sorcery",
        "power": "0", "toughness": "0",
        "oracle_text": "Exile two target artifacts."
    }
]

def main():
    print("PAUPER AI: testing...")
    
    archetypes = load_archetypes_from_csv() # Cargamos el meta de Pauper desde CSV generado por el scraper.
    if not archetypes: return

    parser = TextParser() # Analizador de texto para extraer mecánicas, disparadores y acciones de las cartas.
    evaluator = CardEvaluator() # Calcula la potencia base de la carta según sus características (colores, tipo, texto).
    manager = ArchetypeManager(archetypes) # Evalúa la idoneidad de la carta para cada arquetipo del meta, aplicando lógica de sinergias, roles, etc...
    
    # Cargar Cerebro ML (Modelo de Machine Learning entrenado para predecir la probabilidad de que una carta encaje bien en un arquetipo según sus colores y texto).
    ml_engine = MLEngine()
    ml_loaded = ml_engine.load_model()
    if ml_loaded:
        print("Machine Learning listo para predecir.")
    else:
        print("No hay modelo ML. Ejecuta step1 para entrenar.")

    print(f"Meta cargado: {len(archetypes)} mazos.\n")

    for card in test_cards:
        print(f"{card['name'].upper()}")
        print("-" * 60)

        parsed = parser.analyze(card['oracle_text'])
        base_score = evaluator.calculate_base_power(card, parsed)
        
        # 1. ANÁLISIS LÓGICO
        report = manager.evaluate_fit(card, parsed, base_score)

        sorted_results = sorted(report.items(), key=lambda x: x[1]['score'], reverse=True)
        top_results = [res for res in sorted_results if res[1]['score'] > 5.0]

        if not top_results:
            print(" No supera el corte competitivo.")
        else:
            for deck, res in top_results:
                score = res['score']
                status = res['status']
                meta = res['meta_stats']
                role = meta.get('role', 'Unknown')
                
                # 2. ANÁLISIS ML (PROBABILIDAD)
                ml_prob = 0.0
                ml_tag = ""
                if ml_loaded:
                    deck_colors_str = "".join(archetypes[deck]['colors'])
                    ml_prob = ml_engine.predict_probability(card, deck_colors_str)
                    
                    if ml_prob > 80: ml_tag = "🤖 IA: ¡Me encanta!"
                    elif ml_prob > 50: ml_tag = "🤖 IA: Posible"
                    elif ml_prob < 30: ml_tag = "🤖 IA: Dudoso"

                # Iconografía Lógica
                icon = "❓"
                if "STAPLE" in status: icon = "🏆"
                elif "Playable" in status: icon = "✅"
                elif "Outclassed" in status: icon = "🔻"
                elif "Synergy" in status: icon = "⚠️"

                print(f"   -> {deck:<25} | Score: {score:>5} | {icon} {status}")
                print(f"      [Rol: {role:<11}] (Meta Avg: {meta['avg']} | ML Confianza: {ml_prob}%) {ml_tag}")
                
                if res['notes']:
                    print(f"      💡 {', '.join(res['notes'])}")
        print("\n")

if __name__ == "__main__":
    main()