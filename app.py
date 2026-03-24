# app.py
from flask import Flask, render_template, request, jsonify
import requests

# Importamos tu IA real
from src.data_loader import load_archetypes_from_csv
from src.text_parser import TextParser
from src.evaluator import CardEvaluator
from src.archetype_manager import ArchetypeManager

app = Flask(__name__)

# 1. Cargamos el meta de Pauper en memoria al arrancar el servidor
ARCHETYPES = load_archetypes_from_csv("data/archetypes_review.csv")

# 2. Inicializamos el cerebro de la IA de forma global
parser = TextParser()
evaluator = CardEvaluator()
manager = ArchetypeManager(ARCHETYPES)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/search', methods=['GET'])
def search_card():
    card_name = request.args.get('name')
    if not card_name:
        return jsonify({"error": "No name provided"}), 400

    # Usamos la URL base y dejamos que 'requests' monte los parámetros y los espacios
    scryfall_url = "https://api.scryfall.com/cards/named"
    
    # 'fuzzy' es mucho más inteligente que 'exact' para buscar
    parametros = {"fuzzy": card_name}
    
    # Scryfall agradece que los bots se identifiquen para no bloquearlos
    cabeceras = {'User-Agent': 'PauperAI-App/1.0'} 

    response = requests.get(scryfall_url, params=parametros, headers=cabeceras)
    
    if response.status_code == 200:
        data = response.json()
        card_data = {
            "name": data.get("name"),
            "colors": data.get("colors", []),
            "cmc": data.get("cmc", 0.0),
            "type_line": data.get("type_line", ""),
            "power": data.get("power", "0"),
            "toughness": data.get("toughness", "0"),
            "oracle_text": data.get("oracle_text", ""),
            "image_url": data.get("image_uris", {}).get("normal", "")
        }
        return jsonify(card_data)
    else:
        # Imprimimos en consola qué ha fallado para futuras depuraciones
        print(f"❌ Scryfall no encontró: {card_name} | Código: {response.status_code}")
        return jsonify({"error": "Carta no encontrada en Scryfall"}), 404

@app.route('/api/evaluate', methods=['POST'])
def evaluate():
    card_data = request.json
    if not card_data:
        return jsonify({"error": "No data provided"}), 400

    parsed_data = parser.analyze(card_data.get('oracle_text', ''))
    base_score = evaluator.calculate_base_power(card_data, parsed_data)
    
    # El manager ahora devuelve {"accepted": {...}, "rejected": {...}} con todas las explicaciones
    report = manager.evaluate_fit(card_data, parsed_data, base_score)
    
    top_fits = []
    rejected = []
    
    # Procesamos las cartas Aceptadas
    for deck, res in report.get("accepted", {}).items():
        top_fits.append({
            "deck": deck,
            "score": res['score'],
            "status": res['status'],
            "role": res['meta_stats']['role'],
            "notes": res['notes'],
            "audit_log": res['audit_log'], # Pasamos la auditoría a la web
            "meta_stats": res['meta_stats']
        })
        
    # Procesamos las cartas Rechazadas (con las explicaciones pro)
    for deck, reason in report.get("rejected", {}).items():
        rejected.append({
            "deck": deck,
            "reason": reason
        })
            
    # Ordenar resultados
    top_fits = sorted(top_fits, key=lambda x: x['score'], reverse=True)
    rejected = sorted(rejected, key=lambda x: x['deck'])

    return jsonify({
        "top_fits": top_fits,
        "rejected": rejected,
        "analysis": {
            "base_score": base_score,
            "mechanics": list(parsed_data.get("mechanics", [])),
            "actions": list(parsed_data.get("actions", {}).keys())
        }
    })

if __name__ == '__main__':
    app.run(debug=True, port=5000)