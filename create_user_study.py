#!/usr/bin/env python3
"""
Generate 10 clean + 10 adversarial emails for human evaluation study
"""
import random
import re

# Set seed for reproducibility
random.seed(42)

def apply_homoglyph(text, intensity=0.10):
    """Apply homoglyph substitution (10% of characters)"""
    homoglyphs = {
        'a': 'а',  # Cyrillic a
        'e': 'е',  # Cyrillic e
        'o': 'о',  # Cyrillic o
        'p': 'р',  # Cyrillic p
        'c': 'с',  # Cyrillic c
        'l': '1',
        'i': '1',
        'O': '0',
        'S': '$'
    }
    
    chars = list(text)
    num_mods = int(len(chars) * intensity)
    indices = random.sample(range(len(chars)), min(num_mods, len(chars)))
    
    for idx in indices:
        if chars[idx] in homoglyphs:
            chars[idx] = homoglyphs[chars[idx]]
    
    return ''.join(chars)

def create_typosquatting_url(url):
    """Create typosquatting variant"""
    replacements = {
        'paypal.com': 'paypa1-secure.com',
        'amazon.com': 'amaz0n-shipment.com',
        'microsoft.com': 'micr0soft-support.com',
        'apple.com': 'app1e-id.com',
        'google.com': 'g00gle-verify.com'
    }
    
    for original, fake in replacements.items():
        if original in url.lower():
            return url.replace(original, fake)
    return url

# 10 Phishing Emails (these will be shown as-is)
phishing_emails = [
    {
        'id': 'P1',
        'subject': 'Urgent: Your Account Has Been Suspended',
        'body': '''Dear Valued Customer,

Your PayPal account has been temporarily suspended due to unusual activity. To restore access, please verify your identity immediately by clicking the link below:

http://paypal-secure-verify.com/restore

Failure to verify within 24 hours will result in permanent account closure.

Thank you for your cooperation.
PayPal Security Team'''
    },
    {
        'id': 'P2',
        'subject': 'Action Required: Confirm Your Amazon Order',
        'body': '''Hello,

We were unable to process your recent order (#847392). Please confirm your payment method and shipping address:

Click here: amazon-orders.net/confirm

Your order will be cancelled if not confirmed within 12 hours.

Best regards,
Amazon Customer Service'''
    },
    {
        'id': 'P3',
        'subject': 'Microsoft Security Alert',
        'body': '''Important Security Notice:

We detected suspicious login attempts on your Microsoft account from an unknown device in Russia.

Secure your account now: microsoft-account-security.org/verify

If you don't recognize this activity, click here immediately to prevent unauthorized access.

Microsoft Security Team'''
    },
    {
        'id': 'P4',
        'subject': 'Your Package Delivery Failed',
        'body': '''Dear Customer,

We attempted to deliver your package today but no one was available. 

Track your shipment: fedex-tracking-2026.com/track

You must reschedule delivery within 48 hours or your package will be returned to sender.

FedEx Delivery Services'''
    },
    {
        'id': 'P5',
        'subject': 'Congratulations! You Won $5,000',
        'body': '''Dear Winner,

You have been selected to receive a $5,000 Amazon Gift Card in our annual customer appreciation lottery!

Claim your prize: amazon-rewards-center.net/claim

Enter code: WIN5000

This offer expires in 3 days. Don't miss out!

Amazon Rewards Team'''
    },
    {
        'id': 'P6',
        'subject': 'Your Tax Refund is Ready',
        'body': '''IRS Notice:

You are eligible for a tax refund of $892.47 from the 2025 fiscal year.

Process your refund: irs-refund-portal.gov.us/claim

Please submit your banking information to receive your refund via direct deposit.

Internal Revenue Service'''
    },
    {
        'id': 'P7',
        'subject': 'LinkedIn: Someone Viewed Your Profile',
        'body': '''Hi there,

A recruiter from Google just viewed your LinkedIn profile!

See who's interested: linkedin-profile-views.net/check

Premium members get unlimited profile views. Upgrade now for 50% off!

The LinkedIn Team'''
    },
    {
        'id': 'P8',
        'subject': 'Apple ID Security Update Required',
        'body': '''Dear Apple Customer,

Due to recent security updates, you must verify your Apple ID to continue using iCloud services.

Verify now: appleid-verification.com/update

Accounts not verified within 7 days will be permanently disabled.

Apple Support'''
    },
    {
        'id': 'P9',
        'subject': 'Wire Transfer Approval Needed - CEO',
        'body': '''John,

I need you to process an urgent wire transfer for the merger acquisition. Time-sensitive deal.

Amount: $125,000
I'll send account details separately. Keep this confidential - board hasn't approved yet.

Thanks,
CEO'''
    },
    {
        'id': 'P10',
        'subject': 'Your Netflix Subscription Payment Failed',
        'body': '''Hi Member,

We were unable to process your monthly payment. Your account will be suspended in 24 hours.

Update payment info: netflix-billing-update.com/pay

Please update your credit card information to continue enjoying Netflix.

The Netflix Team'''
    }
]

# 10 Legitimate Emails (clean versions)
legitimate_emails = [
    {
        'id': 'L1',
        'subject': 'Your Amazon Order Has Shipped',
        'body': '''Hello,

Good news! Your order #112-8473920-4738291 has been shipped and is on the way.

Track your package: https://www.amazon.com/gp/css/order-history

Estimated delivery: February 5, 2026

Thank you for shopping with Amazon!

Amazon Customer Service'''
    },
    {
        'id': 'L2',
        'subject': 'Microsoft Office 365 Renewal Reminder',
        'body': '''Dear Subscriber,

Your Microsoft Office 365 subscription will expire on March 1, 2026.

Renew at: https://www.microsoft.com/account/services

Your current plan: Office 365 Personal - $69.99/year

Microsoft Subscriptions Team'''
    },
    {
        'id': 'L3',
        'subject': 'Weekly Team Meeting - Tomorrow 2pm',
        'body': '''Hi Team,

Reminder: Our weekly sync is tomorrow (Wednesday) at 2:00 PM in Conference Room B.

Agenda:
- Q1 project updates
- Sprint planning
- Budget review

See you there!
Sarah, Project Manager'''
    },
    {
        'id': 'L4',
        'subject': 'Your PayPal Payment Receipt',
        'body': '''Thank you for your payment.

You sent $47.99 to TechGadgets Store on Feb 1, 2026.

Transaction ID: 8K7J2N4P9M1L

View details: https://www.paypal.com/activity

PayPal'''
    },
    {
        'id': 'L5',
        'subject': 'GitHub Security Alert: New Login from Windows',
        'body': '''Hi tamhmynguyen,

A new login to your GitHub account was detected:

Device: Windows 10 (Chrome)
Location: Fort Worth, Texas, US
Time: Feb 1, 2026 10:23 AM CST

If this was you, no action needed. If not, secure your account: https://github.com/settings/security

GitHub Security'''
    },
    {
        'id': 'L6',
        'subject': 'Your Flight Confirmation - UA 1847',
        'body': '''Confirmation Code: ABC123

Flight: United Airlines UA 1847
Date: March 15, 2026
Departure: DFW 7:30 AM → Arrival: ORD 10:45 AM

Check in: https://www.united.com/checkin

Safe travels!
United Airlines'''
    },
    {
        'id': 'L7',
        'subject': 'IT Security Patch - Action Required by Friday',
        'body': '''All Employees,

Critical security patch must be installed by end of day Friday, Feb 5.

Instructions: https://company.sharepoint.com/IT/security-updates

Contact IT helpdesk if you need assistance: helpdesk@company.com

IT Security Team'''
    },
    {
        'id': 'L8',
        'subject': 'LinkedIn Connection Request from Jane Smith',
        'body': '''Jane Smith wants to connect with you on LinkedIn.

Jane Smith
Senior Software Engineer at Google
Austin, Texas Area

Accept: https://www.linkedin.com/in/janesmith

LinkedIn'''
    },
    {
        'id': 'L9',
        'subject': 'Your Spotify Wrapped 2025 is Ready!',
        'body': '''Your year in music is here!

You listened to 45,287 minutes of music in 2025.
Top artist: Taylor Swift
Top song: Anti-Hero

See your Wrapped: https://www.spotify.com/wrapped

Happy listening!
Spotify'''
    },
    {
        'id': 'L10',
        'subject': 'Zoom Meeting Invitation - Q1 All Hands',
        'body': '''You're invited to join:

Q1 All Hands Meeting
Friday, Feb 5, 2026 at 3:00 PM CST

Join Zoom Meeting:
https://zoom.us/j/1234567890

Meeting ID: 123 456 7890
Passcode: 987654

Zoom'''
    }
]

print("=" * 80)
print("USER STUDY EMAILS GENERATED")
print("=" * 80)

# Save clean versions
with open('user_study_clean_emails.txt', 'w') as f:
    f.write("=" * 80 + "\n")
    f.write("PHISHING EMAILS (Original - No Modification)\n")
    f.write("=" * 80 + "\n\n")
    
    for email in phishing_emails:
        f.write(f"EMAIL {email['id']}\n")
        f.write(f"Subject: {email['subject']}\n")
        f.write(f"Body:\n{email['body']}\n")
        f.write("\n" + "-" * 80 + "\n\n")
    
    f.write("\n" + "=" * 80 + "\n")
    f.write("LEGITIMATE EMAILS (Original - Clean)\n")
    f.write("=" * 80 + "\n\n")
    
    for email in legitimate_emails:
        f.write(f"EMAIL {email['id']}\n")
        f.write(f"Subject: {email['subject']}\n")
        f.write(f"Body:\n{email['body']}\n")
        f.write("\n" + "-" * 80 + "\n\n")

print("✓ Saved: user_study_clean_emails.txt (10 phishing + 10 legitimate)")

# Create adversarial versions of legitimate emails
with open('user_study_adversarial_emails.txt', 'w') as f:
    f.write("=" * 80 + "\n")
    f.write("ADVERSARIAL EMAILS (Modified with Attacks)\n")
    f.write("These are LEGITIMATE emails that have been adversarially modified\n")
    f.write("=" * 80 + "\n\n")
    
    for i, email in enumerate(legitimate_emails, 1):
        # Choose attack type
        if i % 3 == 0:
            # Typosquatting attack
            modified_body = create_typosquatting_url(email['body'])
            attack_type = "Typosquatting"
        elif i % 3 == 1:
            # Homoglyph attack
            modified_body = apply_homoglyph(email['body'], intensity=0.08)
            attack_type = "Homoglyph substitution"
        else:
            # Combined
            temp = create_typosquatting_url(email['body'])
            modified_body = apply_homoglyph(temp, intensity=0.05)
            attack_type = "Combined (Typosquatting + Homoglyph)"
        
        f.write(f"EMAIL L{i}-ADV (Attack: {attack_type})\n")
        f.write(f"Original ID: {email['id']}\n")
        f.write(f"Subject: {email['subject']}\n")
        f.write(f"Body:\n{modified_body}\n")
        f.write(f"\n[GROUND TRUTH: Originally LEGITIMATE, now ADVERSARIAL]\n")
        f.write("\n" + "-" * 80 + "\n\n")

print("✓ Saved: user_study_adversarial_emails.txt (10 modified versions)")

# Create survey form
with open('user_study_survey_form.txt', 'w') as f:
    f.write("=" * 80 + "\n")
    f.write("USER STUDY SURVEY FORM\n")
    f.write("=" * 80 + "\n\n")
    
    f.write("Instructions for Participants:\n")
    f.write("For each email below, answer:\n")
    f.write("1. Is this email LEGITIMATE or PHISHING?\n")
    f.write("2. How confident are you? (1=Not confident, 5=Very confident)\n")
    f.write("3. What made you decide? (brief explanation)\n\n")
    f.write("-" * 80 + "\n\n")
    
    # Randomize order
    all_emails = []
    
    # Add 5 phishing
    for email in random.sample(phishing_emails, 5):
        all_emails.append(('PHISHING', email))
    
    # Add 5 legitimate
    for email in random.sample(legitimate_emails, 5):
        all_emails.append(('LEGITIMATE', email))
    
    # Add 5 adversarial (modified legitimate)
    for i in random.sample(range(1, 11), 5):
        email = legitimate_emails[i-1]
        # Apply attack
        if i % 2 == 0:
            modified_body = apply_homoglyph(email['body'], intensity=0.08)
        else:
            modified_body = create_typosquatting_url(email['body'])
        
        all_emails.append(('ADVERSARIAL', {
            'id': f"L{i}-ADV",
            'subject': email['subject'],
            'body': modified_body
        }))
    
    random.shuffle(all_emails)
    
    for idx, (truth, email) in enumerate(all_emails, 1):
        f.write(f"EMAIL #{idx}\n")
        f.write(f"Subject: {email['subject']}\n")
        f.write(f"Body:\n{email['body']}\n\n")
        f.write("Your Answer:\n")
        f.write("[ ] LEGITIMATE   [ ] PHISHING\n")
        f.write("Confidence: [ 1 ] [ 2 ] [ 3 ] [ 4 ] [ 5 ]\n")
        f.write("Reasoning: _________________________________________________\n")
        f.write(f"\n[GROUND TRUTH: {truth}]\n")
        f.write("\n" + "=" * 80 + "\n\n")

print("✓ Saved: user_study_survey_form.txt (randomized survey)")

print("\n" + "=" * 80)
print("FILES CREATED:")
print("=" * 80)
print("1. user_study_clean_emails.txt - All 20 original emails")
print("2. user_study_adversarial_emails.txt - 10 adversarially modified versions")
print("3. user_study_survey_form.txt - Ready-to-use survey with 15 emails")
print("\nSend these files to your professor!")
