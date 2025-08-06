# -*- coding: utf-8 -*-
"""
Tämä moduuli sisältää sovelluksenlaajuiset vakiot ja konfiguraatiot.
Sisältää mm. sovellusversion, käyttöliittymässä käytettävät emojit ja värit,
sekä yleisesti tunnettujen riskielinten (OAR) nimet.
"""

APP_VERSION = "v0.3.0-alpha" # <--- SOVELLUKSEN VERSIO PÄIVITETTY

# --- Emojit ja Värit ---
EMOJI_COPY = "📋"; EMOJI_CROP_IN = "✂️"; EMOJI_CROP_OUT = "✂️"
EMOJI_UNION = "➕"; EMOJI_RING = "💍"; EMOJI_MARGIN = "↔️"
EMOJI_BOOLEAN = "🧩"; EMOJI_CHECK = "👀"; EMOJI_WARNING = "⚠️"
EMOJI_MANUAL = "✍️"; EMOJI_INFO = "ℹ️"; EMOJI_DONE = "✅"
EMOJI_SEARCH = "🔍"

COLOR_COMPLETED_BG = "#e8f5e9"; COLOR_COMPLETED_FG = "#555555"
COLOR_DEFAULT_BG = "white"; COLOR_ALT_BG = "#f8f8f8"; COLOR_BORDER = "#d0d0d0"
COLOR_TITLE = "#003366"; COLOR_INSTRUCTION = "#333333"; COLOR_CODE = "#000080"
COLOR_VALUE = "#005000"; COLOR_PLACEHOLDER = "#444444"; COLOR_TOOL = "#005000"
COLOR_ACTION = "#c00000"; COLOR_NOTE = "#555555"
COLOR_SEARCH_HIGHLIGHT_BG = "#fff3cd" # Background for search highlight (temporary)
COLOR_SEARCH_HIGHLIGHT_BORDER = "#ffc107" # Border for search highlight (temporary)

# Updated list including common OARs and those extracted from the provided text
COMMON_OARS = sorted(list(set([
    "A_Aorta", "A_Carotid_L", "A_Carotid_R", "A_LAD", "A_Pulm",
    "Arytenoid_L", "Arytenoid_R", "Atrium_L", "Atrium_R",
    "Bag_Bowel", "Bladder", "Bone_Mandible", "Bone_Pelvic", "BowelBag", "BowelLarge", "BowelSmall",
    "BrachialPlex_L", "BrachialPlex_R", "BrachialPlexus_L", "BrachialPlexus_R",
    "Brain", "Brainstem", "Breast_L", "Breast_R", "Breast_RTOG_L", "Breast_RTOG_R",
    "Bronchus_Prox", "BrTW_RTOG_L", "BrTW_RTOG_R", "Buccal_Mucosa_L", "Buccal_Mucosa_R",
    "CaudaEquina", "Cavity_Oral", "Chestwall_L", "Chestwall_R", "Cochlea_L", "Cochlea_R",
    "Cricophar_inlet", "Duodenum", "Esophagus", "Esophagus_S",
    "Eye_Ant_L", "Eye_Ant_R", "Eye_L", "Eye_R", "Eye_Post_L", "Eye_Post_R",
    "FemoralHead_L", "FemoralHead_R", "Femur_Head_L", "Femur_Head_R", "Femur_Implant_L", "Femur_Implant_R", "Femur_L", "Femur_R",
    "Fossa_Pituitary", "Glnd_Lacrimal_L", "Glnd_Lacrimal_R", "Glnd_Submand_L", "Glnd_Submand_R", "Glnd_Thyroid",
    "Glottis", "Heart", "Heart+A_Pulm", "Humerus_Head_L", "Humerus_Head_R", "Humerus_L", "Humerus_R",
    "Hippocampus_L", "Hippocampus_R",
    "Kidney_L", "Kidney_R", "Kidneys_Total",
    "L4_VB", "L5_VB", "Larynx", "Larynx_SG", "Lens_L", "Lens_R", "Lips", "Liver",
    "LN_Axilla_RTOG_L", "LN_Axilla_RTOG_R", "LN_Axillary_L", "LN_Axillary_R", # Broad regions
    "LN_Inguinal_L", "LN_Inguinal_R", "LN_NRG", "LN_Pivotal", "LN_RTOG", # General node volumes
    "Lung_L", "Lung_R", "Lungs_Total",
    "Mandible", "Markers", "Musc_Coccygeus_L", "Musc_Coccygeus_R", "Musc_Constrict",
    "Musc_Iliacus_L", "Musc_Iliacus_R", "Musc_Obt_Int_L", "Musc_Obt_Int_R",
    "Musc_Pirifor_L", "Musc_Pirifor_R", "Musc_Psoas_Maj_L", "Musc_Psoas_Maj_R",
    "OpticChiasm", "OpticChiasm_cnv", "OpticNerve_L", "OpticNerve_R", "OpticNrv_L", "OpticNrv_R", "OpticNrv_cnv_L", "OpticNrv_cnv_R",
    "OralCavity", "Pancreas", "Parotid_L", "Parotid_R", "PenileBulb", "PharynxConstrictors",
    "Pituitary", "Prostate", "RectoSigmoid", "Rectum", "Sacrum", "SeminalVes",
    "SpinalCanal", "SpinalCord", "Spleen", "Stomach",
    "Thyroid", "Trachea", "Trachea_Prox",
    "V_Venacava_I", "V_Venacava_S", "Ventricle_L", "Ventricle_R",
    "Vessels_L", "Vessels_Long_L", "Vessels_Long_R", "Vessels_R"
])))
