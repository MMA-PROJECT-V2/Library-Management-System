import requests
import logging
import os
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)


class BookServiceClient:
    """
    Client HTTP pour communiquer avec le Books Service
    """
    
    def __init__(self):
        self.base_url = os.getenv('BOOKS_SERVICE_URL', 'http://localhost:8002')
        self.timeout = 10  # secondes
    
    def get_book(self, book_id: int) -> Optional[Dict[str, Any]]:
        """
        Récupérer les informations d'un livre
        
        Args:
            book_id: ID du livre
            
        Returns:
            Dict avec les infos du livre ou None si erreur
        """
        url = f"{self.base_url}/books/{book_id}/"
        
        try:
            response = requests.get(url, timeout=self.timeout)
            
            if response.status_code == 200:
                book_data = response.json()
                logger.info(f"✅ Book {book_id} trouvé: {book_data.get('title')}")
                return book_data
            elif response.status_code == 404:
                logger.warning(f"❌ Book {book_id} non trouvé")
                return None
            else:
                logger.error(f"❌ Erreur Books Service: {response.status_code} - {response.text}")
                return None
                
        except requests.exceptions.Timeout:
            logger.error(f"⏱️ Timeout lors de l'appel Books Service pour book {book_id}")
            return None
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ Erreur de connexion Books Service: {e}")
            return None
    
    def check_availability(self, book_id: int) -> bool:
        """
        Vérifier si un livre est disponible
        
        Args:
            book_id: ID du livre
            
        Returns:
            True si disponible (available_copies > 0), False sinon
        """
        book_data = self.get_book(book_id)
        if not book_data:
            return False
        
        available_copies = book_data.get('available_copies', 0)
        return available_copies > 0
    
    def get_available_copies(self, book_id: int) -> int:
        """
        Récupérer le nombre d'exemplaires disponibles
        
        Args:
            book_id: ID du livre
            
        Returns:
            Nombre d'exemplaires disponibles
        """
        book_data = self.get_book(book_id)
        if not book_data:
            return 0
        
        return book_data.get('available_copies', 0)
    
    def decrement_stock(self, book_id: int) -> bool:
        """
        Décrémenter le stock d'un livre (lors d'un emprunt)
        
        Args:
            book_id: ID du livre
            
        Returns:
            True si succès, False sinon
        """
        url = f"{self.base_url}/books/{book_id}/stock/"
        payload = {
            'action': 'decrement',
            'quantity': 1
        }
        
        try:
            response = requests.put(url, json=payload, timeout=self.timeout)
            
            if response.status_code == 200:
                logger.info(f"✅ Stock décrémenté pour book {book_id}")
                return True
            else:
                logger.error(f"❌ Erreur décrémentation stock: {response.status_code} - {response.text}")
                return False
                
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ Erreur lors de la décrémentation du stock: {e}")
            return False
    
    def increment_stock(self, book_id: int) -> bool:
        """
        Incrémenter le stock d'un livre (lors d'un retour)
        
        Args:
            book_id: ID du livre
            
        Returns:
            True si succès, False sinon
        """
        url = f"{self.base_url}/books/{book_id}/stock/"
        payload = {
            'action': 'increment',
            'quantity': 1
        }
        
        try:
            response = requests.put(url, json=payload, timeout=self.timeout)
            
            if response.status_code == 200:
                logger.info(f"✅ Stock incrémenté pour book {book_id}")
                return True
            else:
                logger.error(f"❌ Erreur incrémentation stock: {response.status_code} - {response.text}")
                return False
                
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ Erreur lors de l'incrémentation du stock: {e}")
            return False
