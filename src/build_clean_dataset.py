import pandas as pd
from sklearn.model_selection import train_test_split

print("Building clean high-quality dataset for CCS submission...")

# ── LOAD ALL SOURCES ──────────────────────────────────────────────

# Real phishing
itasec_phishing = pd.read_csv('/home/tamhmynguyen/phishing_detection_project/data/itasec_phishing.csv')
nazario = pd.read_csv('/home/tamhmynguyen/phishing_detection_project/data/Nazario.csv')

# Real legitimate
itasec_legit = pd.read_csv('/home/tamhmynguyen/phishing_detection_project/data/itasec_legit.csv')
spamassassin = pd.read_csv('/home/tamhmynguyen/phishing_detection_project/data/SpamAssasin.csv')

# Synthetic dataset
synthetic = pd.read_csv('/home/tamhmynguyen/phishing_detection_project/data/phishing_legit_dataset_KD_10000.csv')

# ── FILTER NAZARIO ───────────────────────────────────────────────
phishing_keywords = ['verify', 'account', 'suspend', 'login', 'confirm',
                     'password', 'click', 'credential', 'urgent', 'security',
                     'update', 'expire', 'bank', 'paypal', 'microsoft', 'apple']

garbage_keywords = ['internal format', 'mail folder', 'mail system software',
                    'unsubscribe', 'mailing list', 'listinfo', 'no flow',
                    'forwarded by', 'sitara', 'teco tap']

nazario_good = nazario[
    (nazario['body'].str.len() > 100) &
    (nazario['body'].str.len() < 3000) &
    (nazario['body'].str.lower().apply(
        lambda x: any(kw in str(x) for kw in phishing_keywords)
    )) &
    (~nazario['body'].str.lower().apply(
        lambda x: any(kw in str(x) for kw in garbage_keywords)
    ))
].copy()
nazario_good['label'] = 1

# ── FILTER SPAMASSASSIN LEGIT ────────────────────────────────────
legit_spam = spamassassin[spamassassin['label'] == 0].copy()
garbage_legit = ['unsubscribe', 'mailing list', 'listinfo',
                 'majordomo', 'yahoo groups', 'digest', 'subscribe']

legit_spam_good = legit_spam[
    (legit_spam['body'].str.len() > 80) &
    (legit_spam['body'].str.len() < 2000) &
    (~legit_spam['body'].str.lower().apply(
        lambda x: any(kw in str(x) for kw in garbage_legit)
    ))
].copy()

# ── CLEAN SYNTHETIC DATASET ──────────────────────────────────────
# Remove the Keywords: artifact from LLM generation
synthetic['text'] = synthetic['text'].str.replace(
    r'\nKeywords:.*', '', regex=True
).str.strip()

synthetic_phishing = synthetic[synthetic['label'] == 1].copy()
synthetic_legit = synthetic[synthetic['label'] == 0].copy()

# ── STANDARDIZE ALL TO text + label ──────────────────────────────
def standardize(df, label, text_col='body'):
    if 'body' in df.columns and 'subject' in df.columns:
        df['text'] = df['subject'].fillna('') + ' ' + df['body'].fillna('')
    elif 'body' in df.columns:
        df['text'] = df['body'].fillna('')
    elif 'text' in df.columns:
        df['text'] = df['text'].fillna('')
    df['label'] = label
    return df[['text', 'label']]

itasec_p = standardize(itasec_phishing.copy(), 1)
nazario_p = standardize(nazario_good, 1)
itasec_l = standardize(itasec_legit.copy(), 0)
spam_l = standardize(legit_spam_good, 0)
syn_p = standardize(synthetic_phishing, 1)
syn_l = standardize(synthetic_legit, 0)

# ── COMBINE ──────────────────────────────────────────────────────
phishing_all = pd.concat([itasec_p, nazario_p, syn_p]).drop_duplicates(subset=['text'])
legit_all = pd.concat([itasec_l, spam_l, syn_l]).drop_duplicates(subset=['text'])

print(f"Total phishing: {len(phishing_all)}")
print(f"Total legitimate: {len(legit_all)}")

# Balance
min_size = min(len(phishing_all), len(legit_all))
phishing_final = phishing_all.sample(n=min_size, random_state=42)
legit_final = legit_all.sample(n=min_size, random_state=42)

df_final = pd.concat([phishing_final, legit_final])
df_final = df_final.sample(frac=1, random_state=42).reset_index(drop=True)

print(f"\nFinal dataset: {len(df_final)} samples")
print(f"Labels: {df_final['label'].value_counts().to_dict()}")

# ── SAVE ─────────────────────────────────────────────────────────
output = '/home/tamhmynguyen/phishing_detection_project/data/ccs_clean_dataset.csv'
df_final.to_csv(output, index=False)
print(f"\n✅ Saved to {output}")

# ── SPLIT ────────────────────────────────────────────────────────
X = df_final['text']
y = df_final['label']

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

X_train.to_csv('/home/tamhmynguyen/TAED-System/data/splits/X_train_ccs.csv', index=False)
X_test.to_csv('/home/tamhmynguyen/TAED-System/data/splits/X_test_ccs.csv', index=False)
y_train.to_csv('/home/tamhmynguyen/TAED-System/data/splits/y_train_ccs.csv', index=False)
y_test.to_csv('/home/tamhmynguyen/TAED-System/data/splits/y_test_ccs.csv', index=False)

print(f"Train: {len(X_train)}, Test: {len(X_test)}")
print("✅ Done! Ready to generate adversarial dataset.")