#!/usr/bin/env python3
"""
Email Setup Guide and Test Script for Flask-Mail
"""

import os
import sys

def print_email_setup_guide():
    """Print clear email setup instructions"""
    print("=" * 60)
    print("    EMAIL CONFIGURATION SETUP GUIDE")
    print("=" * 60)
    
    print("\n1. ENABLE 2-FACTOR AUTHENTICATION IN GMAIL:")
    print("   - Go to: https://myaccount.google.com/security")
    print("   - Enable '2-Step Verification'")
    print("   - This is REQUIRED for App Passwords")
    
    print("\n2. CREATE APP PASSWORD:")
    print("   - Go to: https://myaccount.google.com/apppasswords")
    print("   - Select 'Mail' and 'Other (Custom name)'")
    print("   - Name it: 'Reciclagem REEE'")
    print("   - Copy the 16-character password")
    
    print("\n3. UPDATE .env FILE:")
    print("   - Open: .env")
    print("   - Replace: your_email@gmail.com")
    print("   - Replace: your_app_password_here")
    print("   - Save the file")
    
    print("\n4. TEST EMAIL:")
    print("   - Run: python scripts/setup_email.py test")
    print("   - This will send a test email")
    
    print("\n" + "=" * 60)

def test_email_configuration():
    """Test email configuration"""
    try:
        # Add parent directory to path for imports
        sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        
        from app import app, mail
        from flask_mail import Message
        
        with app.app_context():
            # Check configuration
            if not app.config.get("MAIL_USERNAME") or app.config.get("MAIL_USERNAME") == "your_email@gmail.com":
                print("❌ MAIL_USERNAME not configured in .env")
                return False
            
            if not app.config.get("MAIL_PASSWORD") or app.config.get("MAIL_PASSWORD") == "your_app_password_here":
                print("❌ MAIL_PASSWORD not configured in .env")
                return False
            
            print("✅ Email configuration found")
            print(f"   Username: {app.config['MAIL_USERNAME']}")
            print(f"   Server: {app.config['MAIL_SERVER']}:{app.config['MAIL_PORT']}")
            
            # Send test email
            print("\n📧 Sending test email...")
            
            msg = Message(
                'Test Email - Reciclagem REEE',
                sender=app.config["MAIL_DEFAULT_SENDER"],
                recipients=[app.config["MAIL_USERNAME"]]
            )
            
            msg.body = """
This is a test email from Reciclagem REEE application.

If you receive this email, your email configuration is working correctly!

Best regards,
Reciclagem REEE Team
            """
            
            mail.send(msg)
            print("✅ Test email sent successfully!")
            print(f"   Check your inbox: {app.config['MAIL_USERNAME']}")
            
            return True
            
    except Exception as e:
        print(f"❌ Email test failed: {e}")
        return False

def main():
    if len(sys.argv) > 1 and sys.argv[1] == "test":
        test_email_configuration()
    else:
        print_email_setup_guide()

if __name__ == "__main__":
    main()
