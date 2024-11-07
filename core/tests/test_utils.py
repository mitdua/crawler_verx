import pytest
from ..crawler import generate_csv
from ..schemas import Resposta

def test_generate_csv_valid_data():
    data = [{"Symbol": "AAPL", "Name": "Apple Inc.", "Price": "150.00"}]
    response = generate_csv(data)
    assert isinstance(response, Resposta)
    assert response.erro is None
    assert response.success.endswith(".csv")

def test_generate_csv_empty_data():
    data = []
    response = generate_csv(data)
    assert response.erro == "(generate_csv) -> The list data is empty"
