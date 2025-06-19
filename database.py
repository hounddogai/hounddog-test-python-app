"""
Database module for managing test user and IP address data using TinyDB.
"""

import os
from typing import Optional, Dict, Any
from tinydb import TinyDB, Query
from tinydb.storages import JSONStorage
from tinydb.middlewares import CachingMiddleware


class TestDatabase:
    """A simple database class for managing test data."""
    
    def __init__(self, db_path: str = "test_data.json"):
        """Initialize the database connection.
        
        Args:
            db_path: Path to the database file
        """
        self.db_path = db_path
        # Use caching middleware for better performance
        self.db = TinyDB(
            db_path, 
            storage=CachingMiddleware(JSONStorage),
            indent=2
        )
        self.users_table = self.db.table('users')
        self.ip_addresses_table = self.db.table('ip_addresses')
    
    def close(self):
        """Close the database connection."""
        self.db.close()
    
    def clear_all_data(self):
        """Clear all data from the database."""
        self.users_table.truncate()
        self.ip_addresses_table.truncate()
    
    # User management methods
    def add_user(self, user_id: int, username: str, email: str = None, active: bool = True) -> int:
        """Add a new user to the database.
        
        Args:
            user_id: Unique user ID
            username: Username
            email: User email (optional)
            active: Whether the user is active
            
        Returns:
            Document ID of the inserted user
        """
        user_data = {
            'user_id': user_id,
            'username': username,
            'email': email,
            'active': active
        }
        return self.users_table.insert(user_data)
    
    def get_user_by_id(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Get a user by their ID.
        
        Args:
            user_id: User ID to search for
            
        Returns:
            User data dictionary or None if not found
        """
        User = Query()
        result = self.users_table.search(User.user_id == user_id)
        return result[0] if result else None
    
    def get_user_by_username(self, username: str) -> Optional[Dict[str, Any]]:
        """Get a user by their username.
        
        Args:
            username: Username to search for
            
        Returns:
            User data dictionary or None if not found
        """
        User = Query()
        result = self.users_table.search(User.username == username)
        return result[0] if result else None
    
    def get_random_user(self) -> Optional[Dict[str, Any]]:
        """Get a random active user from the database.
        
        Returns:
            User data dictionary or None if no users found
        """
        User = Query()
        active_users = self.users_table.search(User.active == True)
        if active_users:
            import random
            return random.choice(active_users)
        return None
    
    def get_all_users(self) -> list:
        """Get all users from the database.
        
        Returns:
            List of user data dictionaries
        """
        return self.users_table.all()
    
    # IP address management methods
    def add_ip_address(self, ip_id: int, ip_address: str, location: str = None, active: bool = True) -> int:
        """Add a new IP address to the database.
        
        Args:
            ip_id: Unique IP ID
            ip_address: IP address string
            location: Location description (optional)
            active: Whether the IP is active
            
        Returns:
            Document ID of the inserted IP address
        """
        ip_data = {
            'ip_id': ip_id,
            'ip_address': ip_address,
            'location': location,
            'active': active
        }
        return self.ip_addresses_table.insert(ip_data)
    
    def get_ip_by_id(self, ip_id: int) -> Optional[Dict[str, Any]]:
        """Get an IP address by its ID.
        
        Args:
            ip_id: IP ID to search for
            
        Returns:
            IP data dictionary or None if not found
        """
        IP = Query()
        result = self.ip_addresses_table.search(IP.ip_id == ip_id)
        return result[0] if result else None
    
    def get_random_ip(self) -> Optional[Dict[str, Any]]:
        """Get a random active IP address from the database.
        
        Returns:
            IP data dictionary or None if no IPs found
        """
        IP = Query()
        active_ips = self.ip_addresses_table.search(IP.active == True)
        if active_ips:
            import random
            return random.choice(active_ips)
        return None
    
    def get_all_ip_addresses(self) -> list:
        """Get all IP addresses from the database.
        
        Returns:
            List of IP data dictionaries
        """
        return self.ip_addresses_table.all()


# Global database instance
_db_instance = None


def get_database() -> TestDatabase:
    """Get the global database instance (singleton pattern).
    
    Returns:
        TestDatabase instance
    """
    global _db_instance
    if _db_instance is None:
        _db_instance = TestDatabase()
    return _db_instance


def close_database():
    """Close the global database instance."""
    global _db_instance
    if _db_instance is not None:
        _db_instance.close()
        _db_instance = None
