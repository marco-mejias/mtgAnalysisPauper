import math
from src.config import EFFECT_VALUES, MECHANIC_BONUSES

class CardEvaluator:
    def calculate_base_power(self, card_data, parsed_data):
        score = 0.0
        actions = parsed_data["actions"]
        mechanics = parsed_data["mechanics"]
        triggers = parsed_data["triggers"]
        
        # --- 1. STATS ---
        power = 0.0
        toughness = 0.0
        try:
            power = float(card_data.get("power", 0))
            toughness = float(card_data.get("toughness", 0))
            score += (power * 0.6) + (toughness * 0.4)
        except:
            pass

        # --- 2. EFECTOS ---
        effects_score = 0.0
        for action, value in actions.items():
            base_val = EFFECT_VALUES.get(action, 1.0)
            multiplier = value
            if value >= 2 and action in ["effect_draw", "effect_damage", "effect_burn_face", "effect_token"]:
                multiplier = value ** 1.2
            effects_score += base_val * multiplier
        score += effects_score

        # --- 3. MECÁNICAS ---
        mechanics_score = 0.0
        for feat in mechanics:
            bonus = MECHANIC_BONUSES.get(feat, 0.0)
            evasion_skills = ["flying", "trample", "menace", "unblockable"]
            if feat in evasion_skills and power >= 3:
                bonus *= 1.5
            mechanics_score += bonus
        score += mechanics_score

        # --- 4. MOTORES (ENGINES) ---
        is_engine = False
        valuable_repeatable_effects = [
            "effect_token", "effect_draw", "effect_damage", 
            "effect_pump", "effect_lifegain", "mechanic_monarch",
            "effect_initiative"
        ]
        if triggers and any(eff in actions for eff in valuable_repeatable_effects):
            is_engine = True
        
        # SUPER BONUS para Spellslinger
        if "trigger_spellslinger" in triggers:
            is_engine = True
            score += 3.0 

        if is_engine:
            score = score * 1.5 + 5.0

        # --- 5. COSTE REAL ---
        cmc = float(card_data.get("cmc", 1.0))
        real_cost = cmc
        
        all_features = set(mechanics) | set(actions.keys()) | set(triggers)

        cheat_mechanics = [
            "mechanic_affinity", "affinity", 
            "mechanic_delve", "delve", 
            "mechanic_cost_reduction_dynamic"
        ]
        if any(m in all_features for m in cheat_mechanics):
            real_cost = 1.5
        if "mechanic_free_spell" in all_features:
            real_cost = 0.5
        if "mechanic_land_cycling" in all_features:
            real_cost = 1.5

        real_cost = max(0.5, real_cost)

        # --- 6. EFICIENCIA FINAL ---
        # Exponente normal: 0.75
        # Si es un motor, penalizamos menos el coste alto, para favorecer cartas con efectos repetibles potentes aunque tengan coste alto.
        exponent = 0.5 if is_engine else 0.75
        
        divisor = real_cost ** exponent
        efficiency_score = score / divisor
        
        if "Instant" in card_data.get("type_line", "") or "flash" in mechanics:
            efficiency_score *= 1.15 

        # Red de Seguridad
        if efficiency_score < 0.5 and cmc > 0:
            efficiency_score = cmc * 1.5 

        return round(efficiency_score, 2)