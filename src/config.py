# VALORES BASE DE EFECTOS (Puntos por cada ocurrencia)
EFFECT_VALUES = {
    "effect_draw": 3.0,
    "effect_cantrip": 1.5,
    "effect_impulse_draw": 2.5,
    "effect_scry": 1.0,
    "effect_surveil": 1.2,
    "effect_loot": 1.2,
    "effect_tutor": 4.0,
    
    # --- NUEVOS EFECTOS COMPLEJOS ---
    "effect_blink": 4.0,       # Ghostly Flicker / Ephemerate
    "effect_dig_creatures": 4.0, # Lead the Stampede
    "effect_dig_spells": 4.0,    # Pieces of the Puzzle
    "effect_recursion_graveyard": 3.5, # Reanimate / Return to hand
    "effect_untap": 3.0,       # Snap / Frantic Search
    "effect_monarch": 10.0,    # Monarch es ORO puro
    "effect_initiative": 8.0,

    # ... (debajo de effect_initiative)
    "effect_grave_hate": 10.0,     # Relic, Nihil Spellbomb
    "effect_artifact_hate": 9.0,   # Dust to Dust, Gorilla Shaman
    "effect_color_hate": 6.0,      # Pyroblast
    "effect_protection": 5.0,
    
    # Interacción
    "effect_counter": 5.0,
    "effect_hard_counter": 10.0,      # Counterspell
    "effect_soft_counter": 3.0,       # Spell Pierce
    "effect_conditional_counter": 4.0, # Negate
    
    "effect_destroy": 5.0,
    "effect_hard_removal": 8.0,       # Cast Down / Murder
    "effect_hard_exile": 9.0,         # Exile incondicional
    "effect_exile": 6.0,
    "effect_damage": 3.0,
    "effect_burn_face": 3.0,
    "effect_edict": 4.5,
    "effect_board_wipe": 8.0,
    "effect_board_wipe_damage": 6.0,
    "effect_bounce": 3.0,
    "effect_discard": 3.5,
    
    # Utilidad
    "effect_ramp": 3.0,
    "effect_fix_mana": 1.5,
    "effect_lifegain": 1.0,
    "effect_token": 2.5,
    "effect_pump": 2.0,
    "effect_recursion": 3.0,
    "self_mill": 2.0

    
}

# BONUS POR MECÁNICAS (Keywords)
MECHANIC_BONUSES = {
    "flying": 2.0,
    "trample": 1.0,
    "haste": 1.5,
    "flash": 2.0,
    "vigilance": 0.5,
    "deathtouch": 1.5,
    "lifelink": 1.0,
    "ward": 1.5,
    "hexproof": 3.0,
    "indestructible": 3.0,
    "mechanic_monarch": 10.0,
    "mechanic_initiative": 8.0,
    "mechanic_affinity": 4.0,
    "mechanic_delve": 4.0,
    "mechanic_cost_reduction_dynamic": 5.0, # Terror / Gurmag
    "mechanic_free_spell": 6.0,             # Snuff Out
    "mechanic_land_cycling": 3.0,
    "mechanic_gates": 2.0,
    "ninjutsu": 3.0,
    "flashback": 2.0,
    "madness": 3.0,
    "cycling": 1.0,
    "storm": 8.0, # Weather the Storm es una locura
}

# DEPENDENCIAS ESTRICTAS
# TUPLA ("A", "B") significa que requiere A *Y* B (AND).
# LISTA ["A", "B"] significa que requiere A *O* B (OR).
MECHANIC_DEPENDENCIES = {
    # Terror: NECESITA Self-Mill Y Alta densidad de hechizos. No negociable.
    "mechanic_cost_reduction_dynamic": ("self_mill", "high_spell_density"), 
    
    # Delve: Necesita cementerio, pero vale Mill o Loot.
    "mechanic_delve": ["self_mill", "loot"], 
    
    # Mystic: Solo necesita hechizos.
    "trigger_spellslinger": ["high_spell_density"], 
    
    # Affinity: Necesita artefactos.
    "mechanic_affinity": ["high_artifact_count"],
    "mechanic_metalcraft": ["high_artifact_count"],
    
    # Gates: Necesita puertas.
    "mechanic_gates": ["mechanic_gates"]
}

# MECÁNICAS PARASITARIAS / MAZOS LINEALES
# Si el mazo tiene estas mecánicas, se vuelve "Xenófobo": odia cartas que no sean de su tribu.
PARASITIC_MECHANICS = [
    "madness",
    "mechanic_affinity",
    "mechanic_gates",
    "mechanic_bogles" 
]