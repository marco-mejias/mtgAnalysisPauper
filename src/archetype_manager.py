from src.config import MECHANIC_DEPENDENCIES, PARASITIC_MECHANICS
from src.role_manager import RoleManager
import json

class ArchetypeManager:
    def __init__(self, archetypes_data):
        self.archetypes = archetypes_data
        self.role_manager = RoleManager()

    # Función auxiliar para traducir colores a texto legible en la web
    def _translate_colors(self, color_list):
        color_map = {'W': 'Blanco', 'U': 'Azul', 'B': 'Negro', 'R': 'Rojo', 'G': 'Verde'}
        return [color_map.get(c, c) for c in color_list]

    def evaluate_fit(self, card_data, parsed_data, base_score):
        # --- NUEVA ESTRUCTURA DE RETORNO (AUDITORÍA) ---
        accepted = {}
        rejected = {}
        
        my_possible_roles = self.role_manager.determine_roles(card_data, parsed_data)
        if not my_possible_roles or (len(my_possible_roles) == 1 and "MANA" in my_possible_roles):
            # Rechazo global si es una tierra básica o no hace nada relevante
            return {"accepted": {}, "rejected": {"Todos los mazos": "La carta es una tierra básica o no tiene un rol competitivo definido."}}

        card_name = card_data.get("name", "")
        card_colors = card_data.get("colors", [])
        if card_colors is None: card_colors = []
        card_cmc = float(card_data.get("cmc", 0))
        
        all_features = set(parsed_data["mechanics"]) | set(parsed_data["actions"].keys()) | set(parsed_data.get("triggers", []))
        cheats_mana = any(m in all_features for m in ["mechanic_affinity", "affinity", "mechanic_delve", "delve", "mechanic_cost_reduction_dynamic", "mechanic_land_cycling", "mechanic_free_spell"])
        is_sideboard_tech = any(f in all_features for f in ["effect_grave_hate", "effect_artifact_hate", "effect_color_hate", "effect_protection", "storm"])

        for deck_name, profile in self.archetypes.items():
            notes = []
            audit_log = [] # Registro de la IA para explicar matemáticamente la nota
            if is_sideboard_tech: notes.append("🛠️ SIDEBOARD TECH")
            
            # --- 1. FILTRO DE COLOR ---
            deck_dominance = profile.get("color_dominance", {})
            valid_colors = True
            
            if card_colors:
                for c in card_colors:
                    presence = deck_dominance.get(c, 0.0)
                    if presence == 0.0:
                        valid_colors = False; break
                    if presence < 0.08:
                        valid_colors = False; break
                    if presence < 0.15 and not is_sideboard_tech: 
                        is_key_card = any(f in profile["capabilities"] for f in all_features)
                        if not is_key_card:
                            valid_colors = False; break
            
            if not valid_colors: 
                # Registramos el rechazo cromático con detalle
                deck_colors_translated = ", ".join(self._translate_colors(profile.get("colors", [])))
                card_colors_translated = ", ".join(self._translate_colors(card_colors))
                rejected[deck_name] = f"Bloqueo Cromático: Esta carta requiere maná {card_colors_translated}. El mazo '{deck_name}' basa su estrategia en los colores {deck_colors_translated}. Introducir esta carta desestabilizaría la base de maná y los robos tempranos."
                continue

            # --- 2. DEPENDENCIAS ESTRICTAS ---
            synergy_mult = 1.0
            broken_synergy = False
            for feature in all_features:
                if feature in MECHANIC_DEPENDENCIES:
                    reqs = MECHANIC_DEPENDENCIES[feature]
                    if isinstance(reqs, tuple): reqs = list(reqs)
                    has_support = any(r in profile.get("capabilities", []) for r in reqs)
                    if has_support: synergy_mult *= 1.3
                    else:
                        synergy_mult = 0.0
                        broken_synergy = True
                        break 
            
            if broken_synergy: 
                rejected[deck_name] = f"Falta de Soporte: La carta necesita sinergias específicas (ej. sacrificar artefactos o poner contadores) que el mazo '{deck_name}' no puede proporcionarle de forma consistente."
                continue

            # Definimos combo ANTES de la lógica de banquillo para usarlo bien
            is_combo = profile.get("plan") == "Combo" or "Combo" in deck_name or "Dredge" in deck_name or "Storm" in deck_name

            # --- 3. LÓGICA DE BANQUILLO HUMANA ---
            if is_sideboard_tech:
                # A. Suicidio de Cementerio
                uses_graveyard = any(cap in profile["capabilities"] for cap in ["self_mill", "mechanic_delve", "flashback", "effect_recursion_graveyard"])
                if card_name == "Relic of Progenitus" and uses_graveyard: 
                    rejected[deck_name] = f"Fuego Amigo Estratégico: El mazo '{deck_name}' utiliza intensivamente su propio cementerio. Jugar una carta de odio de cementerio asimétrico destruiría tu propio plan de juego."
                    continue
                
                # B. Fuego Amigo (Mejorado)
                # Si el mazo tiene afinidad O muchos artefactos, no destruyas artefactos.
                if "effect_artifact_hate" in all_features and any(cap in profile["capabilities"] for cap in ["mechanic_affinity", "high_artifact_count"]): 
                    rejected[deck_name] = f"Fuego Amigo Estratégico: No se recomienda incluir destrucción masiva de artefactos en un mazo que depende de sus propios artefactos para ganar."
                    continue
                
                # C. Tempo y Sinergia de Combos All-In (Spy, Dredge)
                # Los combos basados en cementerio/criaturas no quieren interacción reactiva ni ganar vidas.
                if is_combo and "high_spell_density" not in profile["capabilities"]:
                    if card_name == "Pyroblast": 
                        rejected[deck_name] = f"Conflicto de Tempo: Los mazos de Combo All-In prefieren robar piezas de combo antes que interacción reactiva."
                        continue
                    if card_name == "Weather the Storm": 
                        rejected[deck_name] = f"Conflicto de Tempo: Ganar vidas no avanza el plan principal de este combo lineal."
                        continue

                # D. Upgrades Estrictos
                if card_name == "Relic of Progenitus" and deck_dominance.get("B", 0) > 0.15:
                    notes.append("💡 Nihil Spellbomb / Faerie Macabre es mejor en Negro")
                    base_score *= 0.4 
                if card_name == "Gorilla Shaman" and deck_dominance.get("W", 0) > 0.15:
                    notes.append("💡 Dust to Dust es muy superior en Blanco")
                    base_score *= 0.4

            # --- 4. MAZOS LINEALES / COMBOS ---
            parasitic_tags_in_deck = [m for m in PARASITIC_MECHANICS if profile.get("weights", {}).get(m, 0) > 0.1 or m in profile.get("capabilities", [])]
            
            is_tribe_member = any(m in all_features for m in parasitic_tags_in_deck)
            
            is_engine_piece = False
            for feature in all_features:
                if feature in MECHANIC_DEPENDENCIES:
                    reqs = MECHANIC_DEPENDENCIES[feature]
                    if isinstance(reqs, tuple): reqs = list(reqs)
                    if any(r in profile.get("capabilities", []) for r in reqs):
                        is_engine_piece = True

            blocked_by_linear = False
            
            if not is_sideboard_tech:
                # REGLA A: Combos All-in
                if is_combo:
                    if not (is_tribe_member or is_engine_piece):
                        if any(f in all_features for f in ["effect_draw", "effect_cantrip", "effect_tutor", "effect_ramp", "self_mill", "effect_loot", "effect_dig_creatures"]):
                            pass 
                        elif "INTERACTION" in my_possible_roles:
                            if "mechanic_free_spell" in all_features: pass
                            elif card_cmc <= 1 and any(f in all_features for f in ["effect_counter", "effect_discard"]): pass
                            else: blocked_by_linear = True 
                        else: blocked_by_linear = True
                        
                # REGLA B: Tribales (Affinity) odian intrusos
                if parasitic_tags_in_deck and not is_tribe_member:
                    if "ENABLER" in my_possible_roles and not any(f in all_features for f in ["effect_cantrip", "effect_draw", "mechanic_free_spell", "self_mill", "effect_loot"]):
                        blocked_by_linear = True

            if blocked_by_linear: 
                rejected[deck_name] = f"Filtro de Sinergia Lineal: Este mazo es un arquetipo parasítico/combo. Como la carta no es una pieza del motor principal ni ayuda a buscarlo de manera eficiente, solo serviría para estorbar."
                continue

            # --- 5. CÁLCULO FINAL Y CURVA ---
            total_weight_points = 0
            deck_weights = profile["weights"]
            matched_features = [] # Guardamos qué le ha gustado a la IA para el Audit Log
            
            for feature in all_features:
                weight = deck_weights.get(feature, 0)
                if feature == "effect_impulse_draw" and "effect_draw" in deck_weights: weight = deck_weights["effect_draw"] * 0.8
                elif feature == "effect_burn_face" and "effect_damage" in deck_weights: weight = deck_weights["effect_damage"]
                
                if weight > 0:
                    total_weight_points += weight
                    matched_features.append(feature.replace('effect_', '').upper())
            
            weight_factor = 1.0 + (total_weight_points / 8.0)

            curve_penalty = 1.0
            threshold = profile["avg_cmc"] + 2.0
            if not cheats_mana and not is_sideboard_tech:
                if "triggers" in parsed_data and parsed_data["triggers"]: threshold += 1.0 
                if card_cmc > threshold:
                    diff = card_cmc - threshold
                    curve_penalty = max(0.2, 1.0 - (diff * 0.3))

            tech_bonus = 2.0 if is_sideboard_tech else 1.0
            fit_score = base_score * synergy_mult * weight_factor * curve_penalty * tech_bonus

            # Redactamos el Audit Log matemático para la web
            audit_log.append(f"Poder Base Evaluado: {round(base_score, 1)}")
            if matched_features: audit_log.append(f"Bonus de Arquetipo (x{round(weight_factor, 2)}): Recompensa por {', '.join(matched_features[:3])}")
            if curve_penalty < 1.0: audit_log.append(f"Penalización de Curva (x{round(curve_penalty, 2)}): CMC {card_cmc} vs Curva ideal {round(threshold, 1)}")
            if tech_bonus > 1.0: audit_log.append(f"Sideboard Tech (x{tech_bonus}): Valor duplicado por efectividad asimétrica.")

            # --- 6. SELECCIÓN DE ROL (NUEVO SISTEMA SIN CSV) ---
            best_role_name = my_possible_roles[0] if my_possible_roles else "Unknown"
            
            # Umbrales estándar de la IA
            threshold_avg = 5.0
            threshold_min = 2.5

            # Filtro de Insuficiencia de Poder
            if fit_score < threshold_min:
                rejected[deck_name] = f"Insuficiencia de Poder: La carta encaja teóricamente, pero su puntuación final de {round(fit_score, 1)} es demasiado baja. Necesita un mínimo de {threshold_min} para competir en el rol de {best_role_name} en este formato."
                continue

            competitiveness = "Outclassed"
            if fit_score >= threshold_avg:
                competitiveness = "STAPLE / UPGRADE" + (" (SIDEBOARD)" if is_sideboard_tech else "")
            elif fit_score >= threshold_min:
                competitiveness = "Playable Option" + (" (SIDEBOARD)" if is_sideboard_tech else "")
            
            # Veredicto Narrativo Final
            verdict = "Adición sólida al mazo."
            if fit_score >= threshold_avg and curve_penalty == 1.0:
                verdict = "Eficiencia ultra-alta. Aprovecha las sinergias del mazo sin frenar el tempo. Indispensable."
            elif curve_penalty < 1.0:
                verdict = "Potente, pero su alto coste de maná requiere jugarla con precaución para no estancarse."
            
            audit_log.append(f"Veredicto Final: {verdict}")
            
            # Guardamos los datos de las que sí pasan
            accepted[deck_name] = {
                "score": round(fit_score, 1),
                "status": competitiveness,
                "notes": notes,
                "audit_log": audit_log,
                "meta_stats": {
                    "role": best_role_name,
                    "avg": threshold_avg,
                    "min": threshold_min
                }
            }
            
        return {"accepted": accepted, "rejected": rejected}