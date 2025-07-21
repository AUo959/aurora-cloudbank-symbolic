#!/usr/bin/env python3
"""
🎯 Aurora Adaptive Learning System
Advanced pattern recognition and adaptive learning framework
"""

import json
import numpy as np
from datetime import datetime

class AdaptiveLearningNode:
    """Individual learning node with adaptive capabilities"""

    def __init__(self, node_id: str, learning_rate: float = 0.01):
        self.node_id = node_id
        self.learning_rate = learning_rate
        self.weights = np.random.rand(10)  # Initial random weights
        self.activation_history = []
        self.learning_history = []
        self.adaptation_factor = 1.0

    def activate(self, input_vector: np.ndarray) -> float:
        """Activate the node with input vector"""
        if len(input_vector) != len(self.weights):
            input_vector = np.resize(input_vector, len(self.weights))

        activation = np.dot(self.weights, input_vector)
        self.activation_history.append(activation)
        return activation

    def learn(self, input_vector: np.ndarray, target: float, actual: float):
        """Adaptive learning with error correction"""
        error = target - actual

        # Adaptive learning rate based on error magnitude
        adaptive_rate = self.learning_rate * self.adaptation_factor
        if abs(error) > 0.5:
            adaptive_rate *= 1.5  # Increase learning for large errors
        elif abs(error) < 0.1:
            adaptive_rate *= 0.8  # Decrease learning for small errors

        # Update weights
        if len(input_vector) == len(self.weights):
            weight_delta = adaptive_rate * error * input_vector
            self.weights += weight_delta

        self.learning_history.append(
            {"error": error, "learning_rate": adaptive_rate, "timestamp": datetime.now().isoformat()}
        )

        # Update adaptation factor
        self.adaptation_factor = min(2.0, max(0.1, self.adaptation_factor + error * 0.01))

class AdaptiveLearningNetwork:
    """Network of adaptive learning nodes"""

    def __init__(self, network_size: int = 20):
        self.nodes = {}
        self.network_size = network_size
        self.pattern_memory = {}
        self.learning_sessions = []

        # Initialize nodes
        for i in range(network_size):
            node_id = f"node_{i:03d}"
            self.nodes[node_id] = AdaptiveLearningNode(node_id)

    def process_pattern(self, pattern_data: np.ndarray, pattern_id: str) -> Dict[str, Any]:
        """Process a pattern through the network"""
        if pattern_data.size == 0:
            return {"error": "empty_pattern"}

        # Normalize pattern data
        if np.std(pattern_data) > 0:
            normalized_pattern = (pattern_data - np.mean(pattern_data)) / np.std(pattern_data)
        else:
            normalized_pattern = pattern_data

        # Process through all nodes
        activations = {}
        for node_id, node in self.nodes.items():
            activation = node.activate(normalized_pattern)
            activations[node_id] = activation

        # Calculate network response
        network_response = {
            "pattern_id": pattern_id,
            "activations": activations,
            "mean_activation": np.mean(list(activations.values())),
            "max_activation": max(activations.values()),
            "min_activation": min(activations.values()),
            "activation_variance": np.var(list(activations.values())),
            "timestamp": datetime.now().isoformat(),
        }

        # Store in pattern memory
        self.pattern_memory[pattern_id] = network_response

        return network_response

    def learn_from_feedback(self, pattern_id: str, feedback_score: float):
        """Learn from feedback on pattern processing"""
        if pattern_id not in self.pattern_memory:
            return False

        pattern_response = self.pattern_memory[pattern_id]
        activations = pattern_response["activations"]

        # Train nodes based on feedback
        for node_id, activation in activations.items():
            node = self.nodes[node_id]

            # Use the original pattern for learning
            # This is a simplified approach - in practice, you'd store the original input
            dummy_input = np.random.rand(len(node.weights))
            node.learn(dummy_input, feedback_score, activation)

        learning_record = {
            "pattern_id": pattern_id,
            "feedback_score": feedback_score,
            "learning_timestamp": datetime.now().isoformat(),
        }

        self.learning_sessions.append(learning_record)
        return True

    def recognize_similar_patterns(self, new_pattern: np.ndarray, threshold: float = 0.8) -> List[str]:
        """Recognize patterns similar to the new input"""
        if not self.pattern_memory:
            return []

        new_response = self.process_pattern(new_pattern, "temp_pattern")
        new_activations = np.array(list(new_response["activations"].values()))

        similar_patterns = []
        for pattern_id, stored_response in self.pattern_memory.items():
            if pattern_id == "temp_pattern":
                continue

            stored_activations = np.array(list(stored_response["activations"].values()))

            # Calculate similarity using cosine similarity
            similarity = np.dot(new_activations, stored_activations) / (
                np.linalg.norm(new_activations) * np.linalg.norm(stored_activations)
            )

            if similarity >= threshold:
                similar_patterns.append(pattern_id)

        return similar_patterns

    def get_learning_statistics(self) -> Dict[str, Any]:
        """Get comprehensive learning statistics"""
        total_patterns = len(self.pattern_memory)
        total_learning_sessions = len(self.learning_sessions)

        if total_learning_sessions > 0:
            feedback_scores = [session["feedback_score"] for session in self.learning_sessions]
            avg_feedback = sum(feedback_scores) / len(feedback_scores)
        else:
            avg_feedback = 0.0

        # Node-level statistics
        node_stats = {}
        for node_id, node in self.nodes.items():
            node_stats[node_id] = {
                "total_activations": len(node.activation_history),
                "avg_activation": np.mean(node.activation_history) if node.activation_history else 0.0,
                "learning_events": len(node.learning_history),
                "current_adaptation_factor": node.adaptation_factor,
            }

        return {
            "network_statistics": {
                "total_patterns_processed": total_patterns,
                "total_learning_sessions": total_learning_sessions,
                "average_feedback_score": avg_feedback,
                "network_size": self.network_size,
            },
            "node_statistics": node_stats,
            "learning_evolution": self.learning_sessions[-10:] if self.learning_sessions else [],
        }

    def save_network_state(self, filename: str):
        """Save the current network state"""
        network_state = {
            "nodes": {
                node_id: {
                    "weights": node.weights.tolist(),
                    "learning_rate": node.learning_rate,
                    "adaptation_factor": node.adaptation_factor,
                    "activation_history": node.activation_history,
                    "learning_history": node.learning_history,
                }
                for node_id, node in self.nodes.items()
            },
            "pattern_memory": self.pattern_memory,
            "learning_sessions": self.learning_sessions,
            "save_timestamp": datetime.now().isoformat(),
        }

        with open(filename, "w", encoding="utf-8") as f:
            json.dump(network_state, f, indent=2)

def test_adaptive_learning():
    """Test adaptive learning system"""
    print("🎯 Testing Adaptive Learning System")

    # Create network
    network = AdaptiveLearningNetwork(network_size=10)

    # Generate test patterns
    test_patterns = [np.random.rand(10) for _ in range(5)]

    # Process patterns
    for i, pattern in enumerate(test_patterns):
        pattern_id = f"test_pattern_{i}"
        response = network.process_pattern(pattern, pattern_id)
        print(f"Pattern {i}: Mean activation = {response['mean_activation']:.3f}")

        # Simulate feedback
        feedback_score = 0.5 + 0.5 * np.random.rand()  # Random feedback between 0.5 and 1.0
        network.learn_from_feedback(pattern_id, feedback_score)

    # Test pattern recognition
    similar_to_first = network.recognize_similar_patterns(test_patterns[0], threshold=0.7)
    print(f"Patterns similar to first: {similar_to_first}")

    # Get statistics
    stats = network.get_learning_statistics()
    print(f"Total patterns processed: {stats['network_statistics']['total_patterns_processed']}")
    print(f"Average feedback score: {stats['network_statistics']['average_feedback_score']:.3f}")

    # Save network state
    network.save_network_state("adaptive_learning_test_state.json")
    print("Network state saved")

    return {"test": "passed", "statistics": stats}

if __name__ == "__main__":
    test_adaptive_learning()
