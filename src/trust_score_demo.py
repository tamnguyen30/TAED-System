import joblib
import numpy as np
import lime
import lime.lime_text
from sklearn.pipeline import make_pipeline
from attacks.char_attacks import apply_homoglyph_attack 
MODEL_PATH = 'models/random_forest_pipeline.joblib' 
ALPHA = 0.4 
BETA = 0.3  
GAMMA = 0.3 
from phishing_indicators import PHISHING_INDICATORS

def calculate_jaccard_similarity(list1, list2):
