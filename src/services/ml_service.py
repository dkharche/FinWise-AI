"""Machine Learning service for classification and forecasting."""

import logging
from typing import List, Dict, Any, Optional
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder

logger = logging.getLogger(__name__)


class MLService:
    """Service for traditional ML tasks."""
    
    def __init__(self):
        self.models = {}
        self.encoders = {}
        self.category_keywords = self._init_category_keywords()
    
    def _init_category_keywords(self) -> Dict[str, List[str]]:
        """Initialize keyword mappings for expense categorization."""
        return {
            "Food & Dining": ["grocery", "food", "restaurant", "cafe", "dining", "pizza", "burger"],
            "Transportation": ["gas", "fuel", "transport", "uber", "lyft", "taxi", "parking"],
            "Housing": ["rent", "mortgage", "property", "lease"],
            "Utilities": ["utility", "electric", "water", "gas bill", "internet", "phone"],
            "Healthcare": ["medical", "doctor", "pharmacy", "hospital", "health"],
            "Entertainment": ["movie", "theater", "concert", "game", "netflix", "spotify"],
            "Shopping": ["amazon", "store", "mall", "shop", "retail"],
            "Insurance": ["insurance", "policy", "premium"],
            "Education": ["school", "tuition", "course", "book"],
        }
    
    async def categorize_expenses(self, transactions: List[Dict[str, Any]]) -> List[str]:
        """Categorize financial transactions.
        
        Args:
            transactions: List of transaction dictionaries
        
        Returns:
            List of category labels
        """
        logger.info(f"Categorizing {len(transactions)} transactions")
        
        categories = []
        for transaction in transactions:
            description = transaction.get("description", "").lower()
            category = self._categorize_single(description)
            categories.append(category)
        
        return categories
    
    def _categorize_single(self, description: str) -> str:
        """Categorize a single transaction description."""
        description_lower = description.lower()
        
        for category, keywords in self.category_keywords.items():
            if any(keyword in description_lower for keyword in keywords):
                return category
        
        return "Other"
    
    async def forecast_expenses(
        self,
        historical_data: pd.DataFrame,
        periods: int = 3
    ) -> Dict[str, Any]:
        """Forecast future expenses using simple moving average.
        
        Args:
            historical_data: DataFrame with historical expense data
            periods: Number of periods to forecast
        
        Returns:
            Dictionary with forecast and confidence intervals
        """
        logger.info(f"Forecasting {periods} periods ahead")
        
        if len(historical_data) < 3:
            return {
                "forecast": [],
                "confidence_interval": [],
                "method": "insufficient_data"
            }
        
        # Simple moving average forecast
        if 'amount' in historical_data.columns:
            recent_avg = historical_data['amount'].tail(3).mean()
            recent_std = historical_data['amount'].tail(3).std()
        else:
            recent_avg = historical_data.iloc[:, 0].tail(3).mean()
            recent_std = historical_data.iloc[:, 0].tail(3).std()
        
        forecast = [recent_avg] * periods
        confidence_interval = [
            (f - 1.96 * recent_std, f + 1.96 * recent_std)
            for f in forecast
        ]
        
        return {
            "forecast": forecast,
            "confidence_interval": confidence_interval,
            "method": "moving_average",
            "baseline": recent_avg
        }
    
    async def detect_anomalies(
        self,
        transactions: List[Dict[str, Any]],
        threshold: float = 2.0
    ) -> List[bool]:
        """Detect anomalous transactions using z-score.
        
        Args:
            transactions: List of transaction dictionaries
            threshold: Z-score threshold for anomaly detection
        
        Returns:
            List of boolean flags indicating anomalies
        """
        logger.info(f"Detecting anomalies in {len(transactions)} transactions")
        
        amounts = [abs(t.get("amount", 0)) for t in transactions]
        
        if len(amounts) < 2:
            return [False] * len(amounts)
        
        mean = np.mean(amounts)
        std = np.std(amounts)
        
        if std == 0:
            return [False] * len(amounts)
        
        # Z-score based anomaly detection
        anomalies = [abs(amount - mean) > threshold * std for amount in amounts]
        
        logger.info(f"Found {sum(anomalies)} anomalies")
        return anomalies
    
    async def analyze_spending_patterns(
        self,
        transactions: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Analyze spending patterns.
        
        Args:
            transactions: List of transaction dictionaries
        
        Returns:
            Dictionary with spending analysis
        """
        logger.info("Analyzing spending patterns")
        
        if not transactions:
            return {"error": "No transactions provided"}
        
        # Categorize transactions
        categories = await self.categorize_expenses(transactions)
        
        # Calculate statistics
        df = pd.DataFrame(transactions)
        df['category'] = categories
        
        analysis = {
            "total_transactions": len(transactions),
            "total_amount": df['amount'].sum() if 'amount' in df.columns else 0,
            "average_transaction": df['amount'].mean() if 'amount' in df.columns else 0,
            "by_category": {},
            "top_merchants": []
        }
        
        # Group by category
        if 'amount' in df.columns:
            category_summary = df.groupby('category')['amount'].agg(['sum', 'count', 'mean'])
            analysis['by_category'] = category_summary.to_dict('index')
        
        # Top merchants
        if 'merchant' in df.columns and 'amount' in df.columns:
            top_merchants = df.groupby('merchant')['amount'].sum().nlargest(5)
            analysis['top_merchants'] = top_merchants.to_dict()
        
        return analysis