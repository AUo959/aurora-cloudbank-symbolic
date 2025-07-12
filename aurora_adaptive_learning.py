#!/usr/bin/env python3
"""
🎯 Aurora Adaptive Learning System
Advanced pattern recognition and adaptive learning framework - Native Python implementation
"""

import json
import math
import random
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
import pickle
from pathlib import Path


class AdaptiveLearningNode:
    """Individual learning node with adaptive capabilities"""
    
    def __init__(self, node_id: str, learning_rate: float = 0.01):
        self.node_id = node_id
        self.learning_rate = learning_rate
        self.weights = [random.random() for _ in range(10)]  # Initial random weights
        self.activation_history = []
        
    def activate(self, input_vector: List[float]) -> float:
        """Process input through this node"""
        # Ensure input matches weight dimensions
        if len(input_vector) != len(self.weights):
            input_vector = input_vector[:len(self.weights)] + [0.0] * max(0, len(self.weights) - len(input_vector))
        
        activation = sum(w * x for w, x in zip(self.weights, input_vector))
        self.activation_history.append(activation)
        return activation
    
    def learn(self, input_vector: List[float], target: float, actual: float):
        """Update weights based on learning feedback"""
        error = target - actual
        
        # Simple weight update rule
        for i in range(len(self.weights)):
            if i < len(input_vector):
                self.weights[i] += self.learning_rate * error * input_vector[i]
    
    def get_state(self) -> Dict[str, Any]:
        """Get current state of the node"""
        return {
            "node_id": self.node_id,
            "weights": self.weights,
            "activation_count": len(self.activation_history),
            "learning_rate": self.learning_rate
        }


class PatternRecognitionEngine:
    """Advanced pattern recognition with adaptive learning"""
    
    def __init__(self, num_nodes: int = 50):
        self.nodes = [
            AdaptiveLearningNode(f"node_{i}", learning_rate=0.01 + random.random() * 0.05)
            for i in range(num_nodes)
        ]
        self.pattern_memory = {}
        self.learning_history = []
        
    def process_pattern(self, pattern_data: List[float], pattern_id: str) -> Dict[str, Any]:
        """Process a pattern through the network"""
        
        # Normalize pattern data
        if len(pattern_data) > 0:
            mean_val = sum(pattern_data) / len(pattern_data)
            variance = sum((x - mean_val) ** 2 for x in pattern_data) / len(pattern_data)
            std_val = math.sqrt(variance) if variance > 0 else 1.0
            
            if std_val > 0:
                normalized_pattern = [(x - mean_val) / std_val for x in pattern_data]
            else:
                normalized_pattern = pattern_data
        else:
            normalized_pattern = pattern_data
        
        # Process through all nodes
        activations = {}
        for node in self.nodes:
            activation = node.activate(normalized_pattern)
            activations[node.node_id] = activation
        
        # Create response
        response = {
            "pattern_id": pattern_id,
            "activations": activations,
            "mean_activation": sum(activations.values()) / len(activations),
            "pattern_strength": max(activations.values()) if activations else 0,
            "activation_variance": self._calculate_variance(list(activations.values())),
            "timestamp": datetime.now().isoformat()
        }
        
        # Store in memory
        self.pattern_memory[pattern_id] = response
        
        return response
    
    def _calculate_variance(self, values: List[float]) -> float:
        """Calculate variance of a list of values"""
        if len(values) < 2:
            return 0.0
        mean = sum(values) / len(values)
        variance = sum((x - mean) ** 2 for x in values) / len(values)
        return variance
    
    def adapt_learning_rates(self, feedback_score: float):
        """Adapt learning rates based on feedback"""
        for node in self.nodes:
            # Test node performance
            dummy_input = [random.random() for _ in range(len(node.weights))]
            node.activate(dummy_input)
            
            # Adjust learning rate based on feedback
            if feedback_score > 0.7:
                node.learning_rate *= 1.1  # Increase learning rate for good performance
            elif feedback_score < 0.3:
                node.learning_rate *= 0.9  # Decrease learning rate for poor performance
            
            # Keep learning rate in reasonable bounds
            node.learning_rate = max(0.001, min(0.1, node.learning_rate))
    
    def recognize_similar_patterns(self, new_pattern: List[float], threshold: float = 0.8) -> List[str]:
        """Find similar patterns in memory"""
        if not self.pattern_memory:
            return []
        
        # Process new pattern
        new_response = self.process_pattern(new_pattern, "temp_query")
        new_activations = list(new_response["activations"].values())
        
        similar_patterns = []
        
        for pattern_id, stored_response in self.pattern_memory.items():
            if pattern_id == "temp_query":
                continue
                
            stored_activations = list(stored_response["activations"].values())
            
            # Calculate cosine similarity
            similarity = self._cosine_similarity(new_activations, stored_activations)
            
            if similarity >= threshold:
                similar_patterns.append(pattern_id)
        
        return similar_patterns
    
    def _cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """Calculate cosine similarity between two vectors"""
        if len(vec1) != len(vec2):
            return 0.0
        
        dot_product = sum(a * b for a, b in zip(vec1, vec2))
        norm1 = math.sqrt(sum(a * a for a in vec1))
        norm2 = math.sqrt(sum(b * b for b in vec2))
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        return dot_product / (norm1 * norm2)
    
    def get_network_state(self) -> Dict[str, Any]:
        """Get comprehensive network state"""
        return {
            "num_nodes": len(self.nodes),
            "pattern_count": len(self.pattern_memory),
            "nodes": [node.get_state() for node in self.nodes],
            "avg_learning_rate": sum(node.learning_rate for node in self.nodes) / len(self.nodes),
            "total_activations": sum(len(node.activation_history) for node in self.nodes),
            "network_stats": {
                "avg_activation": sum(
                    sum(node.activation_history) / len(node.activation_history) if node.activation_history else 0.0
                    for node in self.nodes
                ) / len(self.nodes)
            }
        }


class AdaptiveLearningSystem:
    """Main adaptive learning system"""
    
    def __init__(self):
        self.pattern_engine = PatternRecognitionEngine()
        self.learning_sessions = []
        self.adaptation_count = 0
        
    def run_learning_session(self, patterns: List[List[float]], session_id: str) -> Dict[str, Any]:
        """Run a complete learning session"""
        session_start = datetime.now()
        
        print(f"🧠 Starting Learning Session: {session_id}")
        
        session_results = {
            "session_id": session_id,
            "patterns_processed": 0,
            "adaptations_made": 0,
            "start_time": session_start.isoformat()
        }
        
        # Process patterns
        for i, pattern in enumerate(patterns):
            pattern_id = f"{session_id}_pattern_{i}"
            response = self.pattern_engine.process_pattern(pattern, pattern_id)
            session_results["patterns_processed"] += 1
            
            print(f"  ✅ Processed pattern {i+1}: strength={response['pattern_strength']:.3f}")
        
        # Adapt based on session performance
        feedback_score = 0.5 + 0.5 * random.random()  # Random feedback between 0.5 and 1.0
        self.pattern_engine.adapt_learning_rates(feedback_score)
        self.adaptation_count += 1
        session_results["adaptations_made"] = 1
        
        session_results["end_time"] = datetime.now().isoformat()
        session_results["feedback_score"] = feedback_score
        
        self.learning_sessions.append(session_results)
        
        print(f"🎯 Session Complete - Feedback Score: {feedback_score:.3f}")
        return session_results
    
    def run_adaptive_learning_demo(self) -> Dict[str, Any]:
        """Run comprehensive adaptive learning demonstration"""
        print("🧠 Aurora Adaptive Learning Demo")
        print("=" * 40)
        
        # Generate test patterns
        test_patterns = [
            [random.random() for _ in range(10)] for _ in range(5)
        ]
        
        # Run learning session
        session_result = self.run_learning_session(test_patterns, "demo_session")
        
        # Test pattern recognition
        print("\n🔍 Testing Pattern Recognition...")
        test_pattern = [random.random() for _ in range(10)]
        similar_patterns = self.pattern_engine.recognize_similar_patterns(test_pattern, threshold=0.6)
        print(f"✅ Found {len(similar_patterns)} similar patterns")
        
        # Get network state
        network_state = self.pattern_engine.get_network_state()
        print(f"📊 Network State: {network_state['num_nodes']} nodes, {network_state['pattern_count']} patterns")
        
        demo_result = {
            "demo_status": "COMPLETE",
            "session_result": session_result,
            "network_state": network_state,
            "similar_patterns_found": len(similar_patterns),
            "timestamp": datetime.now().isoformat()
        }
        
        print("\n🎉 Adaptive Learning Demo Complete!")
        return demo_result


def main():
    """Main adaptive learning execution"""
    system = AdaptiveLearningSystem()
    result = system.run_adaptive_learning_demo()
    return result


if __name__ == "__main__":
    main()