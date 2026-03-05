"""
LSTM Predictive Model for Stock Price Prediction

Implements a multi-layer LSTM network for time series forecasting.
"""

import torch
import torch.nn as nn


class LSTMPredictor(nn.Module):
    """
    LSTM-based predictor for stock price movement.
    
    Args:
        input_size: Number of input features (default: 25)
        hidden_size: Number of hidden units (default: 128)
        num_layers: Number of LSTM layers (default: 2)
        dropout: Dropout rate (default: 0.2)
        bidirectional: Whether to use bidirectional LSTM (default: False)
    """
    
    def __init__(
        self,
        input_size: int = 25,
        hidden_size: int = 128,
        num_layers: int = 2,
        dropout: float = 0.2,
        bidirectional: bool = False,
    ):
        super(LSTMPredictor, self).__init__()
        
        self.hidden_size = hidden_size
        self.num_layers = num_layers
        self.bidirectional = bidirectional
        self.num_directions = 2 if bidirectional else 1
        
        self.lstm = nn.LSTM(
            input_size=input_size,
            hidden_size=hidden_size,
            num_layers=num_layers,
            batch_first=True,
            dropout=dropout if num_layers > 1 else 0,
            bidirectional=bidirectional,
        )
        
        self.dropout = nn.Dropout(dropout)
        
        # Output layer for direction classification (up/down)
        self.classifier = nn.Linear(
            hidden_size * self.num_directions, 2
        )
        
        # Output layer for return prediction (regression)
        self.regressor = nn.Linear(
            hidden_size * self.num_directions, 1
        )
        
        # Confidence head
        self.confidence = nn.Linear(
            hidden_size * self.num_directions, 1
        )
    
    def forward(self, x: torch.Tensor) -> dict:
        """
        Forward pass through the LSTM.
        
        Args:
            x: Input tensor of shape (batch, seq_len, input_size)
        
        Returns:
            Dictionary containing:
                - direction: Classification logits (batch, 2)
                - return: Regression output (batch, 1)
                - confidence: Confidence score (batch, 1)
        """
        # LSTM forward
        lstm_out, (h_n, c_n) = self.lstm(x)
        
        # Use the last hidden state
        if self.bidirectional:
            # Concatenate forward and backward hidden states
            hidden = torch.cat((h_n[-2, :, :], h_n[-1, :, :]), dim=1)
        else:
            hidden = h_n[-1, :, :]
        
        hidden = self.dropout(hidden)
        
        return {
            "direction": self.classifier(hidden),
            "return": self.regressor(hidden),
            "confidence": torch.sigmoid(self.confidence(hidden)),
        }
    
    def predict_direction(self, x: torch.Tensor) -> torch.Tensor:
        """
        Predict price direction (up/down).
        
        Args:
            x: Input tensor of shape (batch, seq_len, input_size)
        
        Returns:
            Predicted class (0 or 1)
        """
        outputs = self.forward(x)
        return torch.argmax(outputs["direction"], dim=1)
    
    def predict_return(self, x: torch.Tensor) -> torch.Tensor:
        """
        Predict price return.
        
        Args:
            x: Input tensor of shape (batch, seq_len, input_size)
        
        Returns:
            Predicted return value
        """
        outputs = self.forward(x)
        return outputs["return"].squeeze(-1)


def create_lstm_model(
    input_size: int = 25,
    hidden_size: int = 128,
    num_layers: int = 2,
    dropout: float = 0.2,
    pretrained: bool = False,
) -> LSTMPredictor:
    """
    Factory function to create LSTM model.
    
    Args:
        input_size: Number of input features
        hidden_size: Number of hidden units
        num_layers: Number of LSTM layers
        dropout: Dropout rate
        pretrained: Whether to load pretrained weights
    
    Returns:
        LSTMPredictor model
    """
    model = LSTMPredictor(
        input_size=input_size,
        hidden_size=hidden_size,
        num_layers=num_layers,
        dropout=dropout,
    )
    
    if pretrained:
        # TODO: Load pretrained weights
        pass
    
    return model
