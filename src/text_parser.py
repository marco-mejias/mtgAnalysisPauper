import re

class TextParser:
    def __init__(self):

        # Patrones Regex para detectar efectos
        self.patterns = [
            # MOTORES
            (r"exile .* then return .* to the battlefield", "effect_blink"), 
            (r"return .* from your graveyard to the battlefield", "effect_recursion_graveyard"),
            (r"return target .* from your graveyard to your hand", "effect_recursion"),
            (r"reveal .* top .* put .* into your hand", "effect_dig_creatures"),
            (r"look at the top .* put .* into your hand", "effect_dig_spells"),

            # EFECTOS DE CONTROL
            (r"you become the monarch", "effect_monarch"),
            (r"take the initiative", "effect_initiative"),
            (r"untap .* lands", "effect_untap"), 

            # REMOVAL
            (r"destroy target (?:nonlegendary )?creature[\.,]", "effect_hard_removal"), 
            (r"exile target (?:nonlegendary )?creature[\.,]", "effect_hard_exile"),
            
            # TRIGGERS
            (r"whenever you cast an instant or sorcery spell", "trigger_spellslinger"),
            (r"whenever .* enters the battlefield", "trigger_etb"),
            (r"at the beginning of your upkeep", "trigger_upkeep"),
            (r"whenever .* deals combat damage", "trigger_combat_hit"),

            # OTROS EFECTOS
            (r"counter target spell", "effect_counter"),
            (r"counter target .* unless .* pays", "effect_soft_counter"),
            (r"counter target noncreature spell", "effect_conditional_counter"),
            (r"destroy target", "effect_destroy"),
            (r"exile target", "effect_exile"),
            (r"deals? \d+ damage", "effect_damage"),
            (r"damage to any target", "effect_burn_face"),
            (r"target player sacrifices", "effect_edict"),
            (r"draw \d+ cards?", "effect_draw"),
            (r"draw a card", "effect_cantrip"),
            (r"exile the top \d+ cards? .* play them", "effect_impulse_draw"),
            (r"search your library", "effect_tutor"),
            (r"return target .* to its owner's hand", "effect_bounce"),
            (r"discard \d+ cards?", "effect_discard"),
            (r"create .* token", "effect_token"),
            (r"\+1/\+1 counter", "effect_pump_counter"),
            (r"gets? [+-]\d+/[+-]\d+", "effect_pump"),
            (r"gain \d+ life", "effect_lifegain"),
            (r"add \{", "effect_ramp"), 
            (r"search .* land .* battlefield", "effect_ramp"),
            (r"scry \d+", "effect_scry"),
            (r"surveil \d+", "effect_surveil"),
            (r"mill \d+ cards", "self_mill"),
            (r"put the top \d+ cards of your library into your graveyard", "self_mill"),
            
            # BOARD WIPES
            (r"destroy all creatures", "effect_board_wipe"),
            (r"deals? \d+ damage to each creature", "effect_board_wipe_damage"),
            (r"deals? \d+ damage to all creatures", "effect_board_wipe_damage"),

            # HATE CARDS
            (r"exile all graveyards", "effect_grave_hate"),
            (r"exile target player's graveyard", "effect_grave_hate"),
            (r"exiles? .* from a graveyard", "effect_grave_hate"),
            (r"exile .* artifacts?", "effect_artifact_hate"),
            (r"destroy .* artifacts?", "effect_artifact_hate"),
            (r"if it's (?:blue|red|green|white|black)", "effect_color_hate"),
            (r"protection from", "effect_protection"),
        ]
        
        self.keywords = [
            "flying", "trample", "haste", "flash", "vigilance", "deathtouch", "lifelink",
            "ward", "hexproof", "indestructible", "reach", "menace", "defender",
            "affinity", "delve", "storm", "cycling", "ninjutsu", "flashback",
            "madness", "convoke", "transmute", "cascade", "retrace", "buyback"
        ]

    def analyze(self, text):
        text = text.lower() #todo en minúscula para facilitar matching
        result = {
            "actions": {},
            "mechanics": [],
            "triggers": []
        }
        
        # 1. Buscar Acciones y Triggers (Regex)
        for pattern, tag in self.patterns:
            matches = re.findall(pattern, text) #Busca en el text pasado los patrones que hemos creado antes
            if matches:
                # Separamos si es un trigger o una acción normal para guardarlo en la estructura correcta. Ej: Destruir criatura de un sorcery o destruir criatura cada vez que x, que lo hace una criatura
                if tag.startswith("trigger_"):
                    if tag not in result["triggers"]:
                        result["triggers"].append(tag)
                else:
                    count = len(matches)
                    nums = re.findall(r'\d+', matches[0])
                    if nums:
                        val = int(nums[0])
                        if count == 1: count = val
                    
                    result["actions"][tag] = result["actions"].get(tag, 0) + count

        # 2. Buscar Keywords (Exact Match)
        for kw in self.keywords:
            if kw in text:
                result["mechanics"].append(kw)
                
        # 3. Detectar Mecánicas Especiales
        if "affinity for artifacts" in text: result["mechanics"].append("mechanic_affinity")
        if "cost {1} less to cast" in text or "costs {1} less to cast" in text: 
            result["mechanics"].append("mechanic_cost_reduction_dynamic")
        if "landcycling" in text: result["mechanics"].append("mechanic_land_cycling")
        if "you may cast this spell without paying its mana cost" in text:
             result["mechanics"].append("mechanic_free_spell")
        if "gate" in text and ("control" in text or "battlefield" in text):
             result["mechanics"].append("mechanic_gates")
        if "enchant creature" in text and "hexproof" in text:
             result["mechanics"].append("mechanic_bogles")

        return result