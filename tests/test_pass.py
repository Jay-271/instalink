import rsa
import pytest
#from Code import main

@pytest.fixture(scope="module")
def test_imports():
    print("Passed imports...")
    assert rsa 

def test_rsa_import(test_imports):
    # This test will implicitly use the fixture
    pass