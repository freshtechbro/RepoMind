import pytest
import ast
from app.analysis.async_pattern_detector import detect_async_patterns, AsyncPatternDetector

def test_detect_basic_async_await_syntax():
    """Test detection of basic async/await patterns."""
    code = """
    async def fetch_data():
        response = await api.get_data()
        return response
    
    result = await fetch_data()
    """
    
    patterns = detect_async_patterns(code)
    
    assert len(patterns) == 2
    assert patterns[0]['type'] == 'async_function'
    assert patterns[0]['name'] == 'fetch_data'
    assert patterns[1]['type'] == 'await_expression'
    assert patterns[1]['function'] == 'fetch_data'

def test_detect_promise_then_catch():
    """Test detection of promise-like patterns in Python."""
    code = """
    def process_data():
        promise = client.fetch_data()
        promise.then(lambda data: print(data))
        promise.catch(lambda error: print(error))
    """
    
    patterns = detect_async_patterns(code)
    
    assert len(patterns) == 2
    assert patterns[0]['type'] == 'promise_then'
    assert patterns[0]['caller'] == 'promise'
    assert patterns[1]['type'] == 'promise_catch'
    assert patterns[1]['caller'] == 'promise'

def test_detect_callback_patterns():
    """Test detection of callback patterns."""
    code = """
    def fetch_data(callback):
        # Simulate async operation
        result = api.get_data()
        callback(result)
    
    fetch_data(lambda data: process_data(data))
    """
    
    patterns = detect_async_patterns(code)
    
    assert len(patterns) == 1
    assert patterns[0]['type'] == 'callback_pattern'
    assert patterns[0]['function'] == 'fetch_data'

def test_detect_threading_patterns():
    """Test detection of Python threading patterns."""
    code = """
    import threading
    
    def background_task():
        # Do some work
        pass
    
    thread = threading.Thread(target=background_task)
    thread.start()
    # Do other work
    thread.join()
    """
    
    patterns = detect_async_patterns(code)
    
    assert len(patterns) == 1
    assert patterns[0]['type'] == 'threading'
    assert patterns[0]['target'] == 'background_task'

def test_async_class_methods():
    """Test detection of async class methods."""
    code = """
    class DataService:
        async def fetch_data(self):
            return await api.get_data()
        
        def process(self):
            data = asyncio.run(self.fetch_data())
            return data
    """
    
    patterns = detect_async_patterns(code)
    
    assert len(patterns) == 2
    assert patterns[0]['type'] == 'async_method'
    assert patterns[0]['class'] == 'DataService'
    assert patterns[0]['method'] == 'fetch_data'
    assert patterns[1]['type'] == 'asyncio_run'

def test_asyncio_patterns():
    """Test detection of asyncio specific patterns."""
    code = """
    import asyncio
    
    async def main():
        task1 = asyncio.create_task(fetch_data())
        task2 = asyncio.create_task(process_data())
        await asyncio.gather(task1, task2)
    
    asyncio.run(main())
    """
    
    patterns = detect_async_patterns(code)
    
    assert len(patterns) >= 3
    assert any(p['type'] == 'create_task' for p in patterns)
    assert any(p['type'] == 'asyncio_gather' for p in patterns)
    assert any(p['type'] == 'asyncio_run' for p in patterns) 