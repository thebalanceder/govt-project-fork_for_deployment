import re

text = "Contact: student01@university.edu | Phone: 555-123-4567"

# Regex patterns based on your hints
email_pattern = r"\S+@\S+"
phone_pattern = r"\d{3}-\d{3}-\d{4}"  # Specifically matches the 555-123-4567 format

# Extracting the data
email_match = re.search(email_pattern, text)
phone_match = re.search(phone_pattern, text)

# Display results
if email_match:
    print(f"Email: {email_match.group()}")
if phone_match:
    print(f"Phone: {phone_match.group()}")

