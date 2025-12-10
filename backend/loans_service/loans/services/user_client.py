import requests
import logging
import os
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)


class UserServiceClient:
    """
    Client HTTP pour communiquer avec le User Service
    """
    
    def __init__(self):
        self.base_url = os.getenv('USER_SERVICE_URL', 'http://localhost:8001')
        self.timeout = 10  # secondes
    
    def get_user(self, user_id: int) -> Optional[Dict[str, Any]]:
        """
        Récupérer les informations d'un utilisateur
        
        Args:
            user_id: ID de l'utilisateur
            
        Returns:
            Dict avec les infos de l'utilisateur ou None si erreur
        """
        url = f"{self.base_url}/users/{user_id}/"
        
        try:
            response = requests.get(url, timeout=self.timeout)
            
            if response.status_code == 200:
                user_data = response.json()
                logger.info(f"✅ User {user_id} trouvé: {user_data.get('username')}")
                return user_data
            elif response.status_code == 404:
                logger.warning(f"❌ User {user_id} non trouvé")
                return None
            else:
                logger.error(f"❌ Erreur User Service: {response.status_code} - {response.text}")
                return None
                
        except requests.exceptions.Timeout:
            logger.error(f"⏱️ Timeout lors de l'appel User Service pour user {user_id}")
            return None
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ Erreur de connexion User Service: {e}")
            return None
    
    def is_user_active(self, user_id: int) -> bool:
        """
        Vérifier si un utilisateur est actif
        
        Args:
            user_id: ID de l'utilisateur
            
        Returns:
            True si actif, False sinon
        """
        user_data = self.get_user(user_id)
        if not user_data:
            return False
        
        return user_data.get('is_active', False)
    
    def get_user_email(self, user_id: int) -> Optional[str]:
        """
        Récupérer l'email d'un utilisateur
        
        Args:
            user_id: ID de l'utilisateur
            
        Returns:
            Email ou None
        """
        user_data = self.get_user(user_id)
        if not user_data:
            return None
        
        return user_data.get('email')
