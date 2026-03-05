"""
Transformer Predictive Model for Stock Price Prediction

Implements a Transformer encoder for time series forecasting.
"""

import math
import torch
import torch.nn as nn


class PositionalEncoding(nn.Module):
    """
    Positional encoding for Transformer.
    
    Adds positional information to the input embeddings.
    """
    
    def __init__(self, d_model: int, max_len: int = 5000, dropout: float = 0.1):
        super(PositionalEncoding, self).__init__()
        self.dropout = nn.Dropout(p=dropout)
        
        # Create positional encoding matrix
        position = torch.arange(max_len).unsqueeze(1)
        div_term = torch.exp(
            torch.arange(0, d_model, 2) * (-math.log(10000.0) / d_model)
        )
        pe = torch.zeros(max_len, 1, d_model)
        pe[:, 0, 0::2] = torch.sin(position * div_term)
        pe[:, 0, 1::2] = torch.cos(position * div_term)
        self.register_buffer("pe", pe)
    
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """
        Add positional encoding to input.
        
        Args:
            x: Input tensor of shape (seq_len, batch, d_model)
        
        Returns:
            Tensor with positional encoding added
        """
        x = x + self.pe[: x.size(0)]
        return self.dropout(x)


class TransformerPredictor(nn.Module):
    """
    Transformer-based predictor for stock price movement.
    
    Args:
        input_size: Number of input features (default: 25)
        d_model: Model dimension (default: 128)
        nhead: Number of attention heads (default: 8)
        num_layers: Number of transformer layers (default: 4)
        dim_feedforward: Feedforward dimension (default: 512)
        dropout: Dropout rate (default: 0.1)
    """
    
    def __init__(
        self,
        input_size: int = 25,
        d_model: int = 128,
        nhead: int = 8,
        num_layers: int = 4,
        dim_feedforward: int = 512,
        dropout: float = 0.1,
    ):
        super(TransformerPredictor, self).__init__()
        
        self.d_model = d_model
        
        # Input projection
        self.input_projection = nn.Linear(input_size, d_model)
        
        # Positional encoding
        self.pos_encoder = PositionalEncoding(d_model, dropout=dropout)
        
        # Transformer encoder
        encoder_layer = nn.TransformerEncoderLayer(
            d_model=d_model,
            nhead=nhead,
            dim_feedforward=dim_feedforward,
            dropout=dropout,
            batch_first=True,
        )
        self.transformer_encoder = nn.TransformerEncoder(
            encoder_layer, num_layers=num_layers
        )
        
        # Output heads
        self.classifier = nn.Linear(d_model, 2)  # Direction classification
        self.regressor = nn.Linear(d_model, 1)   # Return regression
        self.confidence = nn.Linear(d_model, 1)  # Confidence score
    
    def forward(self, x: torch.Tensor) -> dict:
        """
        Forward pass through the Transformer.
        
        Args:
            x: Input tensor of shape (batch, seq_len, input_size)
        
        Returns:
            Dictionary containing:
                - direction: Classification logits (batch, 2)
                - return: Regression output (batch, 1)
                - confidence: Confidence score (batch, 1)
        """
        # Project input to d_model
        x = self.input_projection(x)
        
        # Add positional encoding (expecting batch_first=True)
        # PositionalEncoding expects (seq_len, batch, d_model), but we have (batch, seq_len, d_model)
        # So we'll skip the positional encoding or adapt it
        x = self.pos_encoder(x.transpose(0, 1)).transpose(0, 1)
        
        # Transformer encoder
        x = self.transformer_encoder(x)
        
        # Use the last time step output
        x = x[:, -1, :]  # (batch, d_model)
        
        return {
            "direction": self.classifier(x),
            "return": self.regressor(x),
            "confidence": torch.sigmoid(self.confidence(x)),
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


def create_transformer_model(
    input_size: int = 25,
    d_model: int = 128,
    nhead: int = 8,
    num_layers: int = 4,
    dim_feedforward: int = 512,
    dropout: float = 0.1,
    pretrained: bool = False,
) -> TransformerPredictor:
    """
    Factory function to create Transformer model.
    
    Args:
        input_size: Number of input features
        d_model: Model dimension
        nhead: Number of attention heads
        num_layers: Number of transformer layers
        dim_feedforward: Feedforward dimension
        dropout: Dropout rate
        pretrained: Whether to load pretrained weights
    
    Returns:
        TransformerPredictor model
    """
    model = TransformerPredictor(
        input_size=input_size,
        d_model=d_model,
        nhead=nhead,
        num_layers=num_layers,
        dim_feedforward=dim_feedforward,
        dropout=dropout,
    )
    
    if pretrained:
        # TODO: Load pretrained weights
        pass
    
    return model
