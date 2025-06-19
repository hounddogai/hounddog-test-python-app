"""
Script to populate the test database with sample user and IP address data.
"""

from database import get_database, close_database


def setup_test_data():
    """Populate the database with test data."""
    db = get_database()
    
    # Clear existing data
    print("Clearing existing test data...")
    db.clear_all_data()
    
    # Add test users
    print("Adding test users...")
    test_users = [
        (1, "johnsmith", "john.smith@example.com", True),
        (2, "janedoe", "jane.doe@example.com", True),
        (3, "bobwilson", "bob.wilson@example.com", True),
        (4, "alicejohnson", "alice.johnson@example.com", True),
        (5, "mikebrown", "mike.brown@example.com", True),
        (6, "sarahlee", "sarah.lee@example.com", True),
        (7, "davidchen", "david.chen@example.com", True),
        (8, "emilydavis", "emily.davis@example.com", True),
        (9, "testuser", "test@example.com", False),  # Inactive user
        (10, "adminuser", "admin@example.com", True),
    ]
    
    for user_id, username, email, active in test_users:
        db.add_user(user_id, username, email, active)
        print(f"  Added user: {username} ({email})")
    
    # Add test IP addresses
    print("\nAdding test IP addresses...")
    test_ips = [
        (1, "192.168.1.1", "Local Network - Router", True),
        (2, "192.168.1.100", "Local Network - Workstation", True),
        (3, "10.0.0.1", "Private Network - Gateway", True),
        (4, "172.16.0.1", "Corporate Network", True),
        (5, "203.0.113.1", "Test Network - Public", True),
        (6, "198.51.100.1", "Example Network", True),
        (7, "8.8.8.8", "Google DNS", True),
        (8, "1.1.1.1", "Cloudflare DNS", True),
        (9, "127.0.0.1", "Localhost", True),
        (10, "0.0.0.0", "Invalid IP", False),  # Inactive IP
    ]
    
    for ip_id, ip_address, location, active in test_ips:
        db.add_ip_address(ip_id, ip_address, location, active)
        print(f"  Added IP: {ip_address} ({location})")
    
    print(f"\nTest data setup complete!")
    print(f"Total users: {len(db.get_all_users())}")
    print(f"Total IP addresses: {len(db.get_all_ip_addresses())}")


def display_test_data():
    """Display all test data in the database."""
    db = get_database()
    
    print("\n=== Current Test Data ===")
    
    print("\nUsers:")
    users = db.get_all_users()
    if users:
        for user in users:
            status = "Active" if user['active'] else "Inactive"
            print(f"  ID: {user['user_id']}, Username: {user['username']}, "
                  f"Email: {user['email']}, Status: {status}")
    else:
        print("  No users found")
    
    print("\nIP Addresses:")
    ips = db.get_all_ip_addresses()
    if ips:
        for ip in ips:
            status = "Active" if ip['active'] else "Inactive"
            print(f"  ID: {ip['ip_id']}, IP: {ip['ip_address']}, "
                  f"Location: {ip['location']}, Status: {status}")
    else:
        print("  No IP addresses found")


def test_random_selection():
    """Test the random selection functionality."""
    db = get_database()
    
    print("\n=== Testing Random Selection ===")
    
    # Test random user selection
    print("\nRandom user selections:")
    for i in range(3):
        user = db.get_random_user()
        if user:
            print(f"  {i+1}. {user['username']} ({user['email']})")
        else:
            print(f"  {i+1}. No user found")
    
    # Test random IP selection
    print("\nRandom IP selections:")
    for i in range(3):
        ip = db.get_random_ip()
        if ip:
            print(f"  {i+1}. {ip['ip_address']} ({ip['location']})")
        else:
            print(f"  {i+1}. No IP found")


if __name__ == "__main__":
    try:
        setup_test_data()
        display_test_data()
        test_random_selection()
    finally:
        close_database()
