import pytest
from app.analysis.typescript_async_detector import detect_async_patterns

def test_detect_async_await_syntax():
    """Test detection of async/await patterns in TypeScript."""
    code = """
    async function fetchData() {
        const response = await api.getData();
        return response;
    }
    
    const result = await fetchData();
    """
    
    patterns = detect_async_patterns(code)
    
    assert len(patterns) == 2
    assert patterns[0]['type'] == 'async_function'
    assert patterns[0]['name'] == 'fetchData'
    assert patterns[1]['type'] == 'await_expression'
    assert patterns[1]['function'] == 'fetchData'

def test_detect_promise_then_catch():
    """Test detection of Promise.then/catch patterns."""
    code = """
    function processData() {
        const promise = client.fetchData();
        promise.then(data => console.log(data))
               .catch(error => console.error(error));
    }
    """
    
    patterns = detect_async_patterns(code)
    
    assert len(patterns) == 2
    assert patterns[0]['type'] == 'promise_then'
    assert patterns[0]['caller'] == 'promise'
    assert patterns[1]['type'] == 'promise_catch'
    assert patterns[1]['caller'] == 'promise'

def test_detect_promise_creation():
    """Test detection of Promise creation."""
    code = """
    function fetchData() {
        return new Promise((resolve, reject) => {
            // Simulate async operation
            setTimeout(() => {
                if (data) {
                    resolve(data);
                } else {
                    reject(new Error('No data'));
                }
            }, 1000);
        });
    }
    """
    
    patterns = detect_async_patterns(code)
    
    assert len(patterns) == 1
    assert patterns[0]['type'] == 'promise_constructor'
    assert patterns[0]['function'] == 'fetchData'

def test_detect_promise_all_race():
    """Test detection of Promise.all and Promise.race."""
    code = """
    async function fetchMultiple() {
        const promises = [fetchData1(), fetchData2(), fetchData3()];
        const results = await Promise.all(promises);
        
        const fastResult = await Promise.race([fetchFast1(), fetchFast2()]);
        return { results, fastResult };
    }
    """
    
    patterns = detect_async_patterns(code)
    
    assert len(patterns) >= 3
    assert any(p['type'] == 'promise_all' for p in patterns)
    assert any(p['type'] == 'promise_race' for p in patterns)
    assert any(p['type'] == 'async_function' for p in patterns)

def test_detect_async_arrow_functions():
    """Test detection of async arrow functions."""
    code = """
    const fetchData = async () => {
        const response = await api.getData();
        return response;
    };
    
    const processItems = async (items) => {
        return await Promise.all(items.map(async item => {
            return await processItem(item);
        }));
    };
    """
    
    patterns = detect_async_patterns(code)
    
    assert len(patterns) >= 3
    assert any(p['type'] == 'async_arrow_function' and p['name'] == 'fetchData' for p in patterns)
    assert any(p['type'] == 'async_arrow_function' and p['name'] == 'processItems' for p in patterns)
    assert any(p['type'] == 'promise_all' for p in patterns)

def test_detect_async_methods():
    """Test detection of async class methods."""
    code = """
    class DataService {
        async fetchData() {
            return await api.getData();
        }
        
        process() {
            return this.fetchData().then(data => this.transformData(data));
        }
        
        async transformData(data) {
            return await worker.process(data);
        }
    }
    """
    
    patterns = detect_async_patterns(code)
    
    assert len(patterns) >= 3
    assert any(p['type'] == 'async_method' and p['method'] == 'fetchData' for p in patterns)
    assert any(p['type'] == 'async_method' and p['method'] == 'transformData' for p in patterns)
    assert any(p['type'] == 'promise_then' for p in patterns) 