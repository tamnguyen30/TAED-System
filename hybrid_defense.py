import re
import numpy as np
import pandas as pd
import pickle
import hashlib
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.metrics.pairwise import cosine_similarity
from urllib.parse import urlparse
from collections import Counter

class TAEDSystem:
    """
    Trust-Aware Explainable Defense (TAED) Framework - Final Thesis Version
    Research Question: Can we quantify and defend the trustworthiness of 
    explanations under adversarial manipulations?
    """
    
    def __init__(self):
        print(" [TAED] Initializing Trust-Aware Explainable Defense (Ensemble Architecture)...")
        print(" Research Focus: Explanation Trustworthiness Under Adversarial Attack")
        
        # Trust Score weights (tuned for research)
        self.alpha = 0.35   # Confidence
        self.beta = 0.40    # Fidelity
        self.gamma = 0.25   # Instability
        
        # Thresholds
        self.TS_HIGH_TRUST = 0.80    # Accept
        self.TS_MEDIUM_TRUST = 0.50  # Flag
        
        # Knowledge Base
        self.phishing_evidence = {
            'spoofing': ['similar domain', 'typo', 'misspell', 'look-alike', 'impersonat'],
            'urgency': ['urgent', 'immediately', 'asap', 'limited time', 'expires', 'act now'],
            'threats': ['suspend', 'lock', 'frozen', 'terminate', 'close', 'restricted'],
            'verification': ['verify', 'confirm', 'validate', 'authenticate', 'update'],
            'financial': ['payment', 'refund', 'wire', 'bitcoin', 'gift card', 'transfer'],
            'credentials': ['password', 'username', 'login', 'credential', 'ssn'],
            'rewards': ['winner', 'prize', 'reward', 'claim', 'congratulations'],
            'authority': ['irs', 'fbi', 'bank', 'paypal', 'amazon', 'microsoft']
        }
        
        # Reference vector for Fidelity
        self.reference_phishing_features = [
            'verify', 'urgent', 'suspend', 'click', 'password', 'account', 
            'update', 'confirm', 'security', 'unusual', 'locked', 'expires'
        ]
        
        self.suspicious_tlds = ['.gq', '.tk', '.cf', '.ml', '.ga', '.top', '.xyz', '.work', '.club', '.online']
        
        # Adversarial Homoglyph Map
        self.homoglyphs = {
            '@': 'a', '1': 'i', '0': 'o', '3': 'e', '$': 's', '!': 'i', 
            '5': 's', '7': 't', '4': 'a', 'а': 'a', 'е': 'e', 'о': 'o', 
            'р': 'p', 'с': 'c', 'у': 'y', 'х': 'x'
        }
        
        self.trusted_domains = ['google.com', 'microsoft.com', 'apple.com', 'amazon.com', 'github.com', 'linkedin.com']
        self.brand_targets = ['paypal', 'amazon', 'netflix', 'microsoft', 'apple', 'google', 'facebook', 'chase']
        
        self.feedback_history = []
        self._load_or_train_models()

    def _load_or_train_models(self):
        """Load ensemble classifiers"""
        try:
            with open('taed_rf_model.pkl', 'rb') as f:
                self.rf_model = pickle.load(f)
            with open('taed_gb_model.pkl', 'rb') as f:
                self.gb_model = pickle.load(f)
            print(" > Loaded ensemble models (RF + GB)")
        except FileNotFoundError:
            self._train_new_models()

    def _train_new_models(self):
        """Train adversarially-aware NLP ensemble"""
        try:
            csv_file = 'data/balanced_phishing_dataset.csv'
            print(f" > Training ensemble on {csv_file}...")
            df = pd.read_csv(csv_file, on_bad_lines='skip')
            
            text_col = next((c for c in df.columns if c.lower() in ['text', 'email', 'body', 'content']), df.columns[0])
            label_col = next((c for c in df.columns if c.lower() in ['label', 'class', 'phishing', 'status']), df.columns[1])
            
            # Limit to 12k for speed
            df = df.dropna(subset=[text_col, label_col]).sample(n=min(len(df), 12000), random_state=42)
            
            X = np.array([self._extract_features(str(t), training=True) for t in df[text_col]])
            y = df[label_col].values
            
            print(" > Training Random Forest...")
            self.rf_model = RandomForestClassifier(n_estimators=100, max_depth=20, n_jobs=-1, random_state=42)
            self.rf_model.fit(X, y)
            
            print(" > Training Gradient Boosting...")
            self.gb_model = GradientBoostingClassifier(n_estimators=100, learning_rate=0.1, max_depth=5, random_state=42)
            self.gb_model.fit(X, y)
            
            with open('taed_rf_model.pkl', 'wb') as f: pickle.dump(self.rf_model, f)
            with open('taed_gb_model.pkl', 'wb') as f: pickle.dump(self.gb_model, f)
            print(" > Ensemble models saved.")
        except Exception as e:
            print(f" > Training failed: {e}. Using fallback.")
            self.rf_model = RandomForestClassifier()
            self.gb_model = GradientBoostingClassifier()
            self.rf_model.fit([[0]*15, [1]*15], [0, 1])
            self.gb_model.fit([[0]*15, [1]*15], [0, 1])

    def _normalize_text(self, text):
        text = text.lower()
        for char, replacement in self.homoglyphs.items():
            text = text.replace(char, replacement)
        return re.sub(r'\s+', ' ', text).strip()

    def _extract_urls(self, text):
        url_pattern = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
        urls = re.findall(url_pattern, text)
        urls.extend(re.findall(r'www\.[a-zA-Z0-9-]+\.[a-zA-Z]{2,}', text))
        return urls

    def _check_typosquatting(self, domain):
        domain_lower = domain.lower()
        for brand in self.brand_targets:
            if brand in domain_lower:
                if not any(trusted in domain_lower for trusted in self.trusted_domains):
                    return True
        return False

    def _analyze_urls(self, urls, text):
        if not urls:
            return {'has_url': 0.0, 'url_risk': 0.0, 'shortened_ratio': 0.0, 'typosquat_detected': False, 'ip_domain': False, 'suspicious_tld': False}
        
        suspicious_count = 0
        shortened_count = 0
        typosquat_detected = False
        ip_domain = False
        suspicious_tld = False
        
        for url in urls:
            if any(short in url.lower() for short in ['bit.ly', 'tinyurl', 'goo.gl', 'ow.ly']):
                shortened_count += 1
                suspicious_count += 1
            try:
                parsed = urlparse(url if url.startswith('http') else f'http://{url}')
                domain = parsed.netloc or parsed.path.split('/')[0]
                
                if any(domain.endswith(tld) for tld in self.suspicious_tlds):
                    suspicious_count += 1
                    suspicious_tld = True
                
                if self._check_typosquatting(domain):
                    typosquat_detected = True
                    suspicious_count += 1
                
                if re.match(r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}', domain):
                    suspicious_count += 1
                    ip_domain = True
            except:
                suspicious_count += 1
        
        return {
            'has_url': 1.0,
            'url_risk': min(suspicious_count / max(len(urls), 1), 1.0),
            'shortened_ratio': shortened_count / max(len(urls), 1),
            'typosquat_detected': typosquat_detected,
            'ip_domain': ip_domain,
            'suspicious_tld': suspicious_tld
        }

    def _calculate_semantic_density(self, text):
        normalized = self._normalize_text(text)
        total_words = len(normalized.split())
        if total_words == 0: return 0.0, {}
        
        densities = {}
        for category, keywords in self.phishing_evidence.items():
            hits = sum(1 for kw in keywords if kw in normalized)
            densities[category] = hits / total_words
        
        weighted_density = (
            densities.get('spoofing', 0) * 2.0 +
            densities.get('urgency', 0) * 1.5 +
            densities.get('threats', 0) * 1.8 +
            densities.get('verification', 0) * 1.3 +
            densities.get('financial', 0) * 1.6 +
            densities.get('credentials', 0) * 2.0 +
            densities.get('rewards', 0) * 1.4 +
            densities.get('authority', 0) * 1.2
        ) / 12.0
        return min(weighted_density, 1.0), densities

    def _extract_features(self, text, training=False):
        normalized = self._normalize_text(text)
        urls = self._extract_urls(text)
        url_analysis = self._analyze_urls(urls, text)
        overall_density, category_densities = self._calculate_semantic_density(text)
        
        words = normalized.split()
        vocab_richness = len(set(words)) / max(len(words), 1) if words else 0.5
        caps_ratio = sum(1 for c in text if c.isupper()) / max(len(text), 1)
        caps_abnormal = 1.0 if caps_ratio > 0.5 or caps_ratio < 0.01 else 0.0
        special_chars = sum(1 for c in text if c in '!@#$%^&*()_+={}[]|\\:;"<>?,./~`')
        special_density = min(special_chars / max(len(text), 1), 1.0)
        numbers = sum(1 for c in text if c.isdigit())
        number_density = min(numbers / max(len(text), 1), 1.0)
        
        feature_vector = np.array([
            overall_density,
            category_densities.get('urgency', 0),
            category_densities.get('threats', 0),
            category_densities.get('verification', 0),
            category_densities.get('financial', 0),
            category_densities.get('credentials', 0),
            category_densities.get('authority', 0),
            url_analysis['has_url'],
            url_analysis['url_risk'],
            url_analysis['shortened_ratio'],
            1.0 if url_analysis['typosquat_detected'] else 0.0,
            vocab_richness,
            caps_abnormal,
            special_density,
            number_density
        ])
        
        if training: return feature_vector
        return feature_vector.reshape(1, -1)

    def _generate_adversarial_perturbations(self, text):
        variants = []
        # 1. Homoglyphs
        v1 = text
        for char, replacement in self.homoglyphs.items():
            if replacement in v1: v1 = v1.replace(replacement, char)
        variants.append(v1)
        # 2. Reordering
        words = text.split()
        if len(words) > 2:
            v2_words = words.copy()
            v2_words[0], v2_words[1] = v2_words[1], v2_words[0]
            variants.append(' '.join(v2_words))
        # 3. Char swap
        chars = list(text)
        if len(chars) > 5:
             chars[2], chars[3] = chars[3], chars[2]
        variants.append("".join(chars))
        return variants

    def _classify_phishing_risk(self, features):
        rf_probs = self.rf_model.predict_proba(features)[0]
        gb_probs = self.gb_model.predict_proba(features)[0]
        ensemble_probs = (rf_probs * 0.6) + (gb_probs * 0.4)
        return {
            'confidence': ensemble_probs[1],
            'ensemble_agreement': abs(rf_probs[1] - gb_probs[1])
        }

    def _generate_explanation(self, text, features, url_analysis, category_densities, classification_result):
        components = []
        evidence = []
        
        if url_analysis['typosquat_detected']:
            components.append("Domain impersonation detected (typosquatting)")
            evidence.extend(['domain', 'typo', 'spoofing'])
        if url_analysis['url_risk'] >= 0.5:
            components.append(f"High-risk URL patterns (Risk: {url_analysis['url_risk']:.2f})")
            evidence.extend(['url', 'link'])
        if url_analysis['ip_domain']:
            components.append("IP address used as domain")
            evidence.extend(['ip'])
        if url_analysis['suspicious_tld']:
            components.append("Suspicious TLD detected")
            evidence.extend(['domain'])
            
        for cat, density in category_densities.items():
            if density > 0.05:
                components.append(f"{cat.title()} language detected")
                evidence.append(cat)
                
        if features[0][12] == 1.0:
            components.append("Abnormal capitalization")
            evidence.append('formatting')
            
        if not components: components.append("No significant indicators found.")
        
        return {
            'components': components,
            'evidence_tokens': list(set(evidence)),
            'natural_language': " | ".join(components)
        }

    def _verify_explanation_consistency(self, text, features, explanation, classification_result, url_analysis):
        score = 1.0
        issues = []
        normalized = self._normalize_text(text)
        
        # Check 1: Do evidence tokens exist?
        found = sum(1 for t in explanation['evidence_tokens'] if t in normalized)
        consistency = found / max(len(explanation['evidence_tokens']), 1)
        if consistency < 0.5:
            score -= 0.2
            issues.append("Evidence weak in text")
            
        # Check 2: Confidence vs Evidence
        conf = classification_result['confidence']
        if conf > 0.8 and len(explanation['components']) < 2:
            score -= 0.2
            issues.append("High confidence/Low evidence")
            
        # Check 3: Ensemble Disagreement
        if classification_result['ensemble_agreement'] > 0.3:
            score -= 0.15
            issues.append("Models disagree")
            
        return {
            'verification_score': max(0.0, score),
            'consistency_issues': issues,
            'is_consistent': score >= 0.7
        }

    def analyze_email(self, text, user_feedback=None):
        features = self._extract_features(text)
        urls = self._extract_urls(text)
        url_analysis = self._analyze_urls(urls, text)
        _, category_densities = self._calculate_semantic_density(text)
        
        # 1. Classify
        cls_result = self._classify_phishing_risk(features)
        
        # 2. Explain
        explanation = self._generate_explanation(text, features, url_analysis, category_densities, cls_result)
        
        # 3. Verify
        ver_result = self._verify_explanation_consistency(text, features, explanation, cls_result, url_analysis)
        
        # 4. Trust Score
        confidence = cls_result['confidence']
        prediction = "PHISHING" if confidence >= 0.50 else "SAFE"
        
        C = confidence if prediction == "PHISHING" else (1.0 - confidence)
        
        # Fidelity
        evidence_tokens = set(explanation['evidence_tokens'])
        ref_tokens = set(self.reference_phishing_features)
        if not evidence_tokens: jaccard = 0.0
        else: jaccard = len(evidence_tokens.intersection(ref_tokens)) / len(evidence_tokens.union(ref_tokens))
        fidelity = (jaccard * 0.6) + (ver_result['verification_score'] * 0.4)
        if prediction == "SAFE": fidelity = 1.0 - fidelity
        
        # Instability
        perturbations = self._generate_adversarial_perturbations(text)
        var_scores = []
        for p in perturbations:
            p_feat = self._extract_features(p)
            p_conf = self._classify_phishing_risk(p_feat)['confidence']
            var_scores.append(abs(confidence - p_conf))
        instability = np.mean(var_scores) if var_scores else 0.0
        
        ts = (self.alpha * C) + (self.beta * fidelity) - (self.gamma * instability)
        ts = max(0.0, min(1.0, ts))
        
        # Final Packaging
        full_explanation = explanation['natural_language']
        if not ver_result['is_consistent']:
            full_explanation += f" (⚠️ Inconsistent: {', '.join(ver_result['consistency_issues'])})"
        
        if ts < 0.5 and prediction == "PHISHING":
            full_explanation += " [⛔ LOW TRUST: Escalate]"

        return {
            'prediction': prediction,
            'trust_score': float(ts),
            'natural_language': full_explanation, # Mapped for UI
            'metrics': {
                'C (Confidence)': round(C, 2),
                'F (Fidelity)': round(fidelity, 2),
                'I (Instability)': round(instability, 2),
                'raw_features': features.tolist()[0]
            }
        }
