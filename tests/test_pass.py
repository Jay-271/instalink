import rsa
import pytest
from Code import main

@pytest.fixture(scope="module")
def test_imports():
    print("Passed imports...")
    assert rsa 
    assert main