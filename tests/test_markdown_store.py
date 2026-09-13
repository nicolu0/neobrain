import pytest
from memory.markdown_store import MarkdownMemoryStore

@pytest.fixture
def store(tmp_path):
    return MarkdownMemoryStore(tmp_path / "memory.md")

def test_facts_empty_store(store):
    assert store.get_facts() == []

def test_append_single_fact(store):
    store.append("User lives in California")
    assert store.get_facts() == ["User lives in California"]

def test_append_multiple_facts(store):
    store.append("User lives in California")
    store.append("User likes pizza")
    store.append("User has a big poodle")
    assert store.get_facts() == ["User lives in California", "User likes pizza", "User has a big poodle"]

def test_append_sanitizes_input(store):
    store.append("  User likes to play soccer\nand basketball    ")
    assert store.get_facts() == ["User likes to play soccer and basketball"]

def test_stats_on_empty_store(store):
    stats = store.stats()
    assert stats == {
        "num_facts": 0,
        "file_size": 0,
        "estimated_tokens": 0
    }

def test_stats_with_single_fact(store):
    store.append("User lives in California")
    stats = store.stats()
    assert stats["num_facts"] == 1
    assert stats["file_size"] > 0
    assert stats["estimated_tokens"] == 6

def test_stats_with_multiple_facts(store):
    store.append("User lives in California")
    store.append("User likes pizza")
    store.append("User has a big poodle")
    stats = store.stats()
    assert stats["num_facts"] == 3
    assert stats["file_size"] > 0
    assert stats["estimated_tokens"] == 15

def test_tokenize(store):
    tokens = store._tokenize("User likes pizza, pasta, and burgers. User doesn't like vegetables.")
    assert tokens == {"likes", "pizza", "pasta", "burgers", "vegetables"}
    
def test_keyword_search_empty_store(store):
    assert store.keyword_search("What does the user like?") == []

def test_keyword_search_only_stopwords(store):
    store.append("User likes to eat pizza")
    assert store.keyword_search("the and or is but") == []

def test_keyword_search_one_non_overlapping_fact(store):
    store.append("User likes to eat pizza")
    assert store.keyword_search("User hates drinking water") == []

def test_keyword_search_one_overlapping_fact(store):
    store.append("User likes to eat pizza")
    assert store.keyword_search("User loves to eat burgers") == ["User likes to eat pizza"]

def test_keyword_search_multiple_overlapping_facts(store):
    store.append("User likes to eat pizza with sausage and pepperoni")
    store.append("User loves to eat pizza with sausage")
    assert store.keyword_search("User likes to put sausage and pepperoni on his pizza") == ["User likes to eat pizza with sausage and pepperoni", "User loves to eat pizza with sausage"]

def test_keyword_search_matching_facts_with_question(store):
    store.append("User loves to eat pizza")
    store.append("User likes to eat salad")
    store.append("User doesn't like to eat ice cream")
    store.append("User is a software engineer")
    assert store.keyword_search("What does the user love to eat?") == ["User loves to eat pizza", "User likes to eat salad", "User doesn't like to eat ice cream"]
