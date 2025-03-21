import pytest
from app.analysis.sequence_ordering import SequenceItem
from app.diagrams.sequence_diagram_generator import generate_sequence_diagram_data


class TestSequenceDiagramGenerator:
    """Test cases for sequence diagram data structure generation."""

    def test_basic_sequence_diagram_generation(self):
        """Test generating a basic sequence diagram data structure."""
        # Create a simple sequence
        sequence = [
            SequenceItem("Client", "request", ["data"], 1),
            SequenceItem("Client.request", "validate", [], 2),
            SequenceItem("Client.request", "process", ["validated_data"], 3)
        ]
        
        # Generate diagram data
        diagram_data = generate_sequence_diagram_data(sequence)
        
        # Check diagram structure
        assert "participants" in diagram_data
        assert "messages" in diagram_data
        
        # Check participants
        assert len(diagram_data["participants"]) == 1
        assert diagram_data["participants"][0] == "Client"
        
        # Check messages
        assert len(diagram_data["messages"]) == 3
        
        # Check first message
        assert diagram_data["messages"][0]["from"] == "Client"
        assert diagram_data["messages"][0]["to"] == "Client"
        assert diagram_data["messages"][0]["method"] == "request"
        
        # Check second message
        assert diagram_data["messages"][1]["from"] == "Client"
        assert diagram_data["messages"][1]["to"] == "Client"
        assert diagram_data["messages"][1]["method"] == "validate"
        
        # Check third message
        assert diagram_data["messages"][2]["from"] == "Client"
        assert diagram_data["messages"][2]["to"] == "Client"
        assert diagram_data["messages"][2]["method"] == "process"

    def test_sequence_diagram_with_multiple_participants(self):
        """Test generating a sequence diagram with multiple participants."""
        # Create a sequence with multiple participants
        sequence = [
            SequenceItem("Controller", "processRequest", ["id"], 1),
            SequenceItem("Controller.processRequest", "findData", ["id"], 2),
            SequenceItem("Service", "getData", ["id"], 3),
            SequenceItem("Service.getData", "queryDatabase", ["id"], 4),
            SequenceItem("Database", "executeQuery", ["sql"], 5)
        ]
        
        # Generate diagram data
        diagram_data = generate_sequence_diagram_data(sequence)
        
        # Check participants
        assert len(diagram_data["participants"]) == 3
        assert "Controller" in diagram_data["participants"]
        assert "Service" in diagram_data["participants"]
        assert "Database" in diagram_data["participants"]
        
        # Check messages
        assert len(diagram_data["messages"]) == 5
        
        # Check specific messages between participants
        controller_service_msg = diagram_data["messages"][2]
        assert controller_service_msg["from"] == "Controller"
        assert controller_service_msg["to"] == "Service"
        assert controller_service_msg["method"] == "getData"
        
        service_db_msg = diagram_data["messages"][4]
        assert service_db_msg["from"] == "Service"
        assert service_db_msg["to"] == "Database"
        assert service_db_msg["method"] == "executeQuery"

    def test_sequence_diagram_with_async_calls(self):
        """Test generating a sequence diagram with asynchronous calls."""
        # Create a sequence with async calls
        sequence = [
            SequenceItem("Client", "makeRequest", [], 1),
            SequenceItem("Client.makeRequest", "fetchData", [], 2)
        ]
        
        # Mark second call as async
        sequence[1].is_async = True
        
        # Generate diagram data
        diagram_data = generate_sequence_diagram_data(sequence)
        
        # Check async flag is preserved
        assert len(diagram_data["messages"]) == 2
        assert diagram_data["messages"][1]["is_async"] == True

    def test_sequence_diagram_with_conditional_blocks(self):
        """Test generating a sequence diagram with conditional blocks."""
        # Create a sequence with conditional calls
        sequence = [
            SequenceItem("Controller", "process", ["data"], 1),
            SequenceItem("Controller.process", "validate", ["data"], 2)
        ]
        
        # Mark second call as conditional
        sequence[1].is_conditional = True
        sequence[1].condition = "if data.isValid()"
        
        # Generate diagram data
        diagram_data = generate_sequence_diagram_data(sequence)
        
        # Check conditional info is preserved
        assert len(diagram_data["messages"]) == 2
        assert diagram_data["messages"][1]["is_conditional"] == True
        assert diagram_data["messages"][1]["condition"] == "if data.isValid()"

    def test_sequence_diagram_with_return_messages(self):
        """Test generating a sequence diagram with return messages."""
        # Create a sequence
        sequence = [
            SequenceItem("Client", "requestData", [], 1),
            SequenceItem("Service", "fetchData", [], 2),
            SequenceItem("Database", "query", ["sql"], 3)
        ]
        
        # Generate diagram data with return messages
        diagram_data = generate_sequence_diagram_data(sequence, include_returns=True)
        
        # Should have original messages plus return messages
        assert len(diagram_data["messages"]) == 6  # 3 calls + 3 returns
        
        # Check return messages
        assert diagram_data["messages"][3]["from"] == "Database"
        assert diagram_data["messages"][3]["to"] == "Service"
        assert diagram_data["messages"][3]["is_return"] == True
        
        assert diagram_data["messages"][4]["from"] == "Service"
        assert diagram_data["messages"][4]["to"] == "Client"
        assert diagram_data["messages"][4]["is_return"] == True
        
        assert diagram_data["messages"][5]["from"] == "Client"
        assert diagram_data["messages"][5]["to"] == "Client"  # Self return
        assert diagram_data["messages"][5]["is_return"] == True 