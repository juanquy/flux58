#!/usr/bin/env python3
import psycopg2
from psycopg2.extras import RealDictCursor
import json
import os
import sys

# Database connection parameters
DB_PARAMS = {
    'host': 'localhost',
    'port': 5432,
    'database': 'flux58',
    'user': 'flux58_user',
    'password': 'flux58_password'
}

def fix_landing_page_settings():
    """Fix landing page settings by ensuring all settings are properly stored"""
    
    # Default landing page settings
    default_settings = {
        # Navbar settings
        "navbar_brand_text": "FLUX58 AI MEDIA LABS",
        "navbar_logo": "img/flux58-logo.png",
        "navbar_bg_color": "#212529",
        "navbar_text_color": "#ffffff",
        "navbar_menu_items": "[]",
        
        # Hero section
        "landing_page_title": "FLUX58 AI MEDIA LABS",
        "landing_page_subtitle": "Powerful AI-Enhanced Video Editing",
        "landing_page_description": "Create professional videos with our cloud-based video editor, powered by AI",
        "landing_page_hero_image": "img/custom/openshot-banner.jpg",
        "hero_bg_color": "#343a40",
        "hero_text_color": "#ffffff",
        "hero_bg_image": "",
        "hero_bg_image_overlay": "False",
        
        # Page settings
        "page_bg_color": "#ffffff",
        "content_bg_color": "#ffffff",
        "content_text_color": "#212529",
        "page_bg_image": "",
        
        # Features section
        "features_title": "Features",
        "features_accent_color": "#007bff",
        "feature1_icon": "bi-camera-video",
        "feature1_title": "Video Editing",
        "feature1_text": "Edit video with our powerful cloud-based editor",
        "feature2_icon": "bi-robot", 
        "feature2_title": "AI Enhancement",
        "feature2_text": "Leverage AI to enhance your videos automatically",
        "feature3_icon": "bi-cloud-upload",
        "feature3_title": "Cloud Storage",
        "feature3_text": "Store your projects securely in the cloud",
        
        # CTA section
        "cta_title": "Ready to get started?",
        "cta_subtitle": "Sign up today and create amazing videos.",
        "cta_button_text": "Get Started",
        "cta_button_color": "#007bff"
    }
    
    try:
        # Connect to PostgreSQL
        conn = psycopg2.connect(**DB_PARAMS)
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        # Get current settings
        cursor.execute("SELECT key, value FROM system_settings")
        current_settings = {row['key']: row['value'] for row in cursor.fetchall()}
        
        # Print current settings (truncated to first 30 chars)
        print("Current settings in database:")
        for key, value in current_settings.items():
            print(f"  {key} = {value[:30]}{'...' if len(value) > 30 else ''}")
        
        # Check for missing settings
        missing_settings = []
        for key, value in default_settings.items():
            if key not in current_settings:
                missing_settings.append((key, value))
        
        print(f"\nFound {len(missing_settings)} missing settings")
        
        # Add missing settings
        if missing_settings:
            for key, value in missing_settings:
                try:
                    print(f"Adding missing setting: {key} = {value}")
                    cursor.execute(
                        "INSERT INTO system_settings (key, value, updated_at) VALUES (%s, %s, NOW())",
                        (key, value)
                    )
                    conn.commit()
                except Exception as e:
                    conn.rollback()
                    print(f"Error adding setting {key}: {str(e)}")
        
        # Verify setting save/retrieval works with a test setting
        test_value = "test_value_from_fix_script"
        cursor.execute(
            "UPDATE system_settings SET value = %s, updated_at = NOW() WHERE key = %s",
            (test_value, "test_fix_script")
        )
        if cursor.rowcount == 0:
            cursor.execute(
                "INSERT INTO system_settings (key, value, updated_at) VALUES (%s, %s, NOW())",
                ("test_fix_script", test_value)
            )
        conn.commit()
        
        cursor.execute("SELECT value FROM system_settings WHERE key = %s", ("test_fix_script",))
        result = cursor.fetchone()
        if result and result['value'] == test_value:
            print("\nSetting save/retrieve is working properly")
        else:
            print("\nWARNING: Setting save/retrieve not working properly!")
        
        print("\nLanding page settings have been fixed.")
        return True
    except Exception as e:
        print(f"Error: {str(e)}")
        return False
    finally:
        cursor.close()
        conn.close()

def verify_database_connectivity():
    """Make sure we can connect to the PostgreSQL database"""
    try:
        # Connect to PostgreSQL
        conn = psycopg2.connect(**DB_PARAMS)
        cursor = conn.cursor()
        
        cursor.execute("SELECT version()")
        version = cursor.fetchone()[0]
        print(f"Connected to PostgreSQL: {version}")
        
        return True
    except Exception as e:
        print(f"Error connecting to database: {str(e)}")
        return False
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    print("Running landing page settings fix")
    
    # Verify database connectivity
    if not verify_database_connectivity():
        print("Cannot connect to database, exiting")
        sys.exit(1)
    
    # Fix settings
    fix_landing_page_settings()