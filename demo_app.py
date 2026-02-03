import streamlit as st
import time
from hybrid_defense import TAEDSystem

# --- CONFIGURATION: CLEAN & POWERFUL ---
st.set_page_config(
    page_title="Phishing Shield Pro",
    page_icon="🛡️",
    layout="wide"
)

# --- CUSTOM DESIGN: THE "APPLE STYLE" LOOK ---
st.markdown("""
<style>
    .verdict-box {
        padding: 30px; 
        border-radius: 15px; 
        text-align: center; 
        margin-bottom: 25px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .safe-box {
        background-color: #d4edda; 
        border: 2px solid #28a745;
        color: #155724;
    }
    .danger-box {
        background-color: #f8d7da; 
        border: 2px solid #dc3545;
        color: #721c24;
    }
    .big-text { font-size: 32px; font-weight: bold; }
    .sub-text { font-size: 18px; margin-top: 10px; }
    
    .metric-card {
        background-color: white;
        padding: 15px;
        border-radius: 10px;
        border: 1px solid #e6e6e6;
        text-align: center;
    }
    .metric-number { font-size: 24px; font-weight: bold; color: #333; }
    .metric-label { font-size: 14px; color: #666; }
</style>
""", unsafe_allow_html=True)

# --- INITIALIZE THE "STRONG" SYSTEM ---
@st.cache_resource
def load_system():
    return TAEDSystem()

system = load_system()

# --- SIDEBAR: EASY TESTING ---
st.sidebar.header("📂 Test Scenarios")
st.sidebar.info("Click a button to load a real-world attack example.")

if st.sidebar.button("1. The 'Microsoft' Scam"):
    st.session_state['email_input'] = """From: Microsoft Security <alerts@microsoft-support.gq>\nSubject: Unusual Sign-in Activity\n\nWe detected a login from an unrecognized device. To protect your data, your account is locked.\n\nVerify immediately: http://microsoft-verify.tk\nFailure to verify will result in suspension."""

if st.sidebar.button("2. The 'Stanford' Job Scam"):
    st.session_state['email_input'] = """From: Prof. Jure Leskovec <jureleskovec032@gmail.com>\nSubject: RA Position\n\nI am looking for a student for a Remote Research Assistant position. Pay is $400/week.\n\nKindly reply with your Full Name and Phone Number.\n\nBest,\nJure Leskovec\nStanford University"""

if st.sidebar.button("3. The 'PayPal' Trick"):
    st.session_state['email_input'] = """From: Service <service@paypal.com>\nSubject: Wallet Suspended\n\nPlease log in to PаyPаl to confirm your transaction history.\n(Note: The 'a's above are Cyrillic)."""

if st.sidebar.button("4. Safe Email"):
    st.session_state['email_input'] = """From: Sarah Jenkins <sjenkins@tcu.edu>\nSubject: Meeting Update\n\nHi Team,\nI've attached the agenda for Friday's budget review. Let me know if 2 PM works.\nThanks,\nSarah"""

# --- MAIN APP ---
st.title("🛡️ Phishing Shield Pro")
st.markdown("### Advanced Security, Simplified.")

col1, col2 = st.columns([1, 1])

with col1:
    st.markdown("#### 1. Paste Email")
    email_text = st.text_area(
        "", 
        value=st.session_state.get('email_input', ""), 
        height=300,
        placeholder="Paste the suspicious email here..."
    )
    
    if st.button("🔍 Scan for Threats", type="primary", use_container_width=True):
        if email_text:
            with st.spinner("Analyzing Sender, Links, and Tone..."):
                time.sleep(0.5) 
                result = system.analyze_email(email_text)
                
                # --- SIMPLE DISPLAY LOGIC ---
                is_phishing = result['prediction'] == "PHISHING"
                trust = result['trust_score']
                
                # Extract metrics for simple bars
                lure_score = 0.0
                pii_score = 0.0
                for feat in result['metrics']['features']:
                    if "Lure" in feat: lure_score = float(feat.split(": ")[1])
                    if "PII" in feat: pii_score = float(feat.split(": ")[1])
                
                instability = result['metrics']['instability']

            # --- THE RESULTS (RIGHT COLUMN) ---
            with col2:
                st.markdown("#### 2. Analysis Results")
                
                # A. The "Traffic Light" Verdict
                if is_phishing:
                    st.markdown(f"""
                    <div class="verdict-box danger-box">
                        <div class="big-text">🚫 BLOCKED</div>
                        <div class="sub-text">This email is <b>Dangerous</b>. Do not reply.</div>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                    <div class="verdict-box safe-box">
                        <div class="big-text">LOOKS SAFE</div>
                        <div class="sub-text">We found no suspicious patterns.</div>
                    </div>
                    """, unsafe_allow_html=True)

                # B. Simple Explanation (The "Why")
                st.markdown("#####  Why?")
                # Clean up the technical text to be friendly
                reason = result['natural_language'].replace("BLOCKED:", "").strip()
                st.info(f"{reason}")

                # C. The "Power Bar" Metrics (Strong Backend, Simple View)
                st.markdown("#####  Threat Levels")
                
                # Metric 1: Fake Identity
                st.write("**Fake Identity Risk** (Sender Mismatch)")
                st.progress(instability)
                if instability > 0.1: st.caption(" The sender address looks fake or tricky.")

                # Metric 2: Scam Bait
                st.write("**Scam Bait** (Money/Job Offers)")
                st.progress(lure_score)
                if lure_score > 0.4: st.caption("Trying to trick you with money or easy jobs.")

                # Metric 3: Data Theft
                st.write("**Data Theft** (Asking for Info)")
                st.progress(pii_score)
                if pii_score > 0.4: st.caption(" Asking for your private data (Name, Phone, SSN).")

                # D. Technical Proof (Expandable)
                with st.expander("View Technical Proof (For Admins)"):
                    st.json(result)
                    st.write(f"Trust Score: {trust:.4f}")

        else:
            st.warning("Please paste an email to scan.")
