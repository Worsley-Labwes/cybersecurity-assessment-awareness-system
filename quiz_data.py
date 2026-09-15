"""
quiz_data.py
------------
Question bank for the Cybersecurity Awareness Training Module
(Prototype 3). Topics match Section 4.3 of the methodology:
password security, phishing, malware, social engineering,
safe browsing, email security, mobile security, data protection.

Each question: {"q": ..., "options": [...], "answer": index, "tip": ...}
"tip" is shown as immediate feedback after answering.
"""

QUIZZES = {
    "password-security": {
        "title": "Password Security",
        "article": "Strong, unique passwords are your first line of defence. Use a password "
        "manager, enable MFA wherever possible, and never reuse passwords across accounts.",
        "questions": [
            {
                "q": "Which of these is the strongest password?",
                "options": ["password123", "Kx9!vT2#mQ7z", "companyname2024", "12345678"],
                "answer": 1,
                "tip": "Long, random passwords with mixed character types resist brute-force attacks best.",
            },
            {
                "q": "How often should you reuse the same password across different accounts?",
                "options": ["Always", "Sometimes", "Never", "Only for unimportant accounts"],
                "answer": 2,
                "tip": "Reusing passwords means one breach can compromise every account using it.",
            },
            {
                "q": "What extra step significantly improves account security beyond a password?",
                "options": ["Writing it on a sticky note", "Multi-factor authentication (MFA)", "Using a shorter password", "Sharing it with a colleague"],
                "answer": 1,
                "tip": "MFA requires a second proof of identity, blocking most credential-based attacks.",
            },
        ],
    },
    "phishing": {
        "title": "Phishing Awareness",
        "article": "Phishing emails impersonate trusted senders to trick you into clicking links, "
        "opening attachments, or revealing credentials. Always verify sender addresses and links.",
        "questions": [
            {
                "q": "You get an urgent email asking you to click a link to 'verify your account'. What should you do first?",
                "options": ["Click immediately", "Check the sender's real email address and hover over the link", "Reply with your password", "Forward it to a friend"],
                "answer": 1,
                "tip": "Verifying sender details and link destinations exposes most phishing attempts.",
            },
            {
                "q": "Which is a common sign of a phishing email?",
                "options": ["Perfect grammar and branding", "A sense of urgency and threats", "Coming from a known colleague with no odd requests", "No links or attachments"],
                "answer": 1,
                "tip": "Urgency and fear (\"act now or your account will be closed\") are classic phishing tactics.",
            },
        ],
    },
    "malware": {
        "title": "Malware",
        "article": "Malware includes viruses, ransomware, and spyware that can damage systems or "
        "steal data. Keep software updated and avoid downloading from untrusted sources.",
        "questions": [
            {
                "q": "What is ransomware?",
                "options": ["Software that speeds up your PC", "Malware that encrypts files and demands payment", "A type of firewall", "A password manager"],
                "answer": 1,
                "tip": "Ransomware locks your files until a ransom is paid - regular backups are the best defence.",
            },
            {
                "q": "What is the best defence against malware infections?",
                "options": ["Disabling antivirus to speed up the PC", "Keeping software/OS updated and using antivirus", "Only using email", "Ignoring software updates"],
                "answer": 1,
                "tip": "Updates patch known vulnerabilities that malware exploits.",
            },
        ],
    },
    "social-engineering": {
        "title": "Social Engineering",
        "article": "Social engineering manipulates people, not systems, into giving up confidential "
        "information - e.g. someone impersonating IT support over the phone.",
        "questions": [
            {
                "q": "A caller claims to be from 'IT Support' and asks for your password to 'fix an issue'. What do you do?",
                "options": ["Give it to them", "Refuse and verify through official channels", "Give a fake password", "Hang up without reporting it"],
                "answer": 1,
                "tip": "Legitimate IT staff never need your actual password. Always verify through a known channel.",
            }
        ],
    },
    "safe-browsing": {
        "title": "Safe Browsing",
        "article": "Look for HTTPS, avoid suspicious pop-ups, and don't download software from "
        "unofficial sites.",
        "questions": [
            {
                "q": "What does the padlock icon in a browser address bar indicate?",
                "options": ["The site is guaranteed safe", "The connection is encrypted (HTTPS)", "The site has no ads", "The site is government-run"],
                "answer": 1,
                "tip": "HTTPS encrypts traffic but doesn't guarantee the site itself is trustworthy - stay alert.",
            }
        ],
    },
    "email-security": {
        "title": "Email Security",
        "article": "Be cautious with attachments and links, even from known contacts, since accounts "
        "can be compromised or spoofed.",
        "questions": [
            {
                "q": "You receive an unexpected invoice attachment from a known supplier. Best action?",
                "options": ["Open it immediately", "Confirm with the supplier via a separate channel before opening", "Forward to the whole company", "Delete without checking"],
                "answer": 1,
                "tip": "Confirming out-of-band prevents opening malicious attachments from spoofed/compromised accounts.",
            }
        ],
    },
    "mobile-security": {
        "title": "Mobile Security",
        "article": "Mobile devices holding work data need lock screens, updates, and care with app "
        "permissions and public Wi-Fi.",
        "questions": [
            {
                "q": "What is a key risk of using public Wi-Fi for work tasks without a VPN?",
                "options": ["Faster internet", "Traffic can be intercepted by attackers on the same network", "Better battery life", "No risk at all"],
                "answer": 1,
                "tip": "Unencrypted public Wi-Fi lets attackers on the same network intercept traffic.",
            }
        ],
    },
    "data-protection": {
        "title": "Data Protection",
        "article": "Sensitive company and customer data should be encrypted, backed up, and shared "
        "only on a need-to-know basis.",
        "questions": [
            {
                "q": "What is the purpose of regular data backups?",
                "options": ["To slow down the system", "To recover data after loss, ransomware, or hardware failure", "To increase storage costs only", "They serve no security purpose"],
                "answer": 1,
                "tip": "Backups are the most reliable recovery path after ransomware or hardware failure.",
            }
        ],
    },
}
