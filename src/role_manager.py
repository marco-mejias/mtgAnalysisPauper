class RoleManager:
    def __init__(self):
        self.roles = ["THREAT", "INTERACTION", "ENABLER", "MANA"]

    def determine_roles(self, card_data, parsed_data):

        possible_roles = []
        
        name = card_data.get("name", "")
        type_line = card_data.get("type_line", "")
        actions = parsed_data["actions"]
        mechanics = parsed_data["mechanics"]
        triggers = parsed_data["triggers"]
        
        # Cogemos el oracle text completo, incluyendo ambas caras si es una carta con varias caras, para detectar triggers o mecánicas que solo aparezcan en la otra cara
        oracle_text = card_data.get("oracle_text", "").lower()
        if "card_faces" in card_data:
            for face in card_data["card_faces"]:
                oracle_text += " " + face.get("oracle_text", "").lower()

        power = 0
        try:
            p_str = str(card_data.get("power", "0"))
            if "card_faces" in card_data:
                p1 = card_data["card_faces"][0].get("power", "0")
                if p1.isdigit(): p_str = p1
                if len(card_data["card_faces"]) > 1:
                    p2 = card_data["card_faces"][1].get("power", "0")
                    if p2.isdigit() and int(p2) > int(p_str): p_str = p2
            if p_str.isdigit(): power = int(p_str)
        except: power = 0

        # Calificamos como interacción
        is_interaction = False
        if "effect_counter" in actions or "effect_destroy" in actions or "effect_exile" in actions: is_interaction = True
        if "effect_edict" in actions or "effect_board_wipe" in actions or "effect_bounce" in actions: is_interaction = True
        if "effect_discard" in actions and "self" not in name: is_interaction = True
        if "effect_damage" in actions: is_interaction = True 
        
        if is_interaction:
            possible_roles.append("INTERACTION")

        # Calificamos como amenaza
        is_threat = False
        # Criaturas grandes
        if "Creature" in type_line and power >= 3: is_threat = True
        # Daño a la cara (Burn)
        if "effect_burn_face" in actions: is_threat = True
        # Tokens masivos
        if "effect_token" in actions and actions["effect_token"] >= 2: is_threat = True
        # Amenazas de Tempo
        if "ninjutsu" in mechanics or "transform" in oracle_text: is_threat = True
        # Affinity/Cost Reduction en criaturas
        if ("mechanic_affinity" in mechanics or "mechanic_cost_reduction_dynamic" in mechanics) and "Creature" in type_line: is_threat = True
        
        # EXCEPCIÓN: Board Wipes NO son Threats
        if "effect_board_wipe_damage" in actions or "effect_board_wipe" in actions:
            is_threat = False

        if is_threat:
            possible_roles.append("THREAT")

        # Calificamos como enabler
        is_enabler = False
        if "effect_draw" in actions or "effect_cantrip" in actions or "effect_impulse_draw" in actions: is_enabler = True
        if "effect_tutor" in actions or "mechanic_land_cycling" in mechanics: is_enabler = True
        if "effect_ramp" in actions or "effect_lifegain" in actions: is_enabler = True
        if "effect_scry" in actions or "self_mill" in actions: is_enabler = True
        
        # Value engines
        if "trigger_spellslinger" in triggers: is_enabler = True

        # Criaturas pequeñas
        if "Creature" in type_line and not is_threat and not is_interaction:
            is_enabler = True

        if is_enabler:
            possible_roles.append("ENABLER")
            
        # Tierras o enabler
        if not possible_roles:
            if "Land" in type_line: possible_roles.append("MANA")
            else: possible_roles.append("ENABLER") 

        return list(set(possible_roles))