#!/usr/bin/env python3
"""
Test the corrected entropy calculation to ensure we're computing 
Shannon entropy correctly for individual items rather than using 
global probabilities.
"""

import math
import sys


def correct_entropy_calculation(tags):
    """
    Calculate Shannon entropy for tags within a single item.
    
    Shannon entropy: H(X) = -∑ p(x) * log2(p(x))
    where p(x) is the probability of tag x within this specific item.
    """
    if not tags:
        return 0.0
    
    # Count occurrences of each tag within this item
    tag_counts = {}
    for tag in tags:
        tag_counts[tag] = tag_counts.get(tag, 0) + 1
    
    # Calculate probabilities within this item
    total_tags = len(tags)
    entropy = 0.0
    
    for count in tag_counts.values():
        p = count / total_tags
        if p > 0:
            entropy -= p * math.log2(p)
    
    return entropy


def incorrect_global_entropy_calculation(items, item_tags):
    """
    This demonstrates the INCORRECT approach that was being used:
    calculating entropy using global tag probabilities across all items.
    """
    # Build global tag counts (this is wrong for individual item entropy)
    global_tag_counts = {}
    total_global_tags = 0
    
    for item in items:
        for tag in item.get('tags', []):
            global_tag_counts[tag] = global_tag_counts.get(tag, 0) + 1
            total_global_tags += 1
    
    # Calculate global probabilities 
    global_tag_probs = {}
    for tag, count in global_tag_counts.items():
        global_tag_probs[tag] = count / total_global_tags
    
    # Calculate "entropy" using global probabilities (this is wrong!)
    entropy = 0.0
    unique_tags = set(item_tags)
    for tag in unique_tags:
        if tag in global_tag_probs:
            p = global_tag_probs[tag]
            entropy -= p * math.log2(p)
    
    return entropy


def test_entropy_calculation_fix():
    """Test that demonstrates the fix for the entropy calculation."""
    print("Testing entropy calculation fix")
    print("=" * 50)
    
    # Example dataset that shows the difference between local and global entropy
    items = [
        {'title': 'Item 1', 'tags': ['rare1', 'rare2']},           # 2 rare tags, uniform locally
        {'title': 'Item 2', 'tags': ['common', 'common']},         # repeated common tag  
        {'title': 'Item 3', 'tags': ['common', 'common', 'common']}, # more repeated common
        {'title': 'Item 4', 'tags': ['rare1', 'rare3', 'rare4']}, # 3 rare tags, uniform locally
    ]
    
    print("Test data:")
    for item in items:
        print(f"  {item['title']}: {item['tags']}")
    print()
    
    # Calculate local entropy (correct approach)
    print("LOCAL ENTROPY (Correct approach - per item):")
    for item in items:
        local_entropy = correct_entropy_calculation(item['tags'])
        print(f"  {item['title']}: entropy = {local_entropy:.3f}")
    print()
    
    # Calculate global entropy (incorrect approach - what was happening before)
    print("GLOBAL ENTROPY (Incorrect approach - was being used before):")
    for item in items:
        global_entropy = incorrect_global_entropy_calculation(items, item['tags'])
        print(f"  {item['title']}: entropy = {global_entropy:.3f}")
    print()
    
    # Show the mathematical correctness of specific cases
    print("Mathematical verification:")
    
    # Case 1: Uniform distribution
    uniform_tags = ['a', 'b', 'c']
    uniform_entropy = correct_entropy_calculation(uniform_tags)
    expected_uniform = math.log2(3)  # For uniform distribution of n items: log2(n)
    print(f"  Uniform tags {uniform_tags}: {uniform_entropy:.6f} (expected: {expected_uniform:.6f})")
    assert abs(uniform_entropy - expected_uniform) < 1e-10, "Uniform entropy calculation error"
    
    # Case 2: Single repeated tag
    single_tags = ['a']
    single_entropy = correct_entropy_calculation(single_tags)
    print(f"  Single tag {single_tags}: {single_entropy:.6f} (expected: 0.000000)")
    assert single_entropy == 0.0, "Single tag entropy should be 0"
    
    # Case 3: Binary distribution 
    binary_tags = ['a', 'b']
    binary_entropy = correct_entropy_calculation(binary_tags)
    expected_binary = 1.0  # -0.5*log2(0.5) - 0.5*log2(0.5) = 1.0
    print(f"  Binary tags {binary_tags}: {binary_entropy:.6f} (expected: {expected_binary:.6f})")
    assert abs(binary_entropy - expected_binary) < 1e-10, "Binary entropy calculation error"
    
    # Case 4: Repeated tags (lower entropy)
    repeated_tags = ['a', 'a', 'b']
    repeated_entropy = correct_entropy_calculation(repeated_tags)
    # p(a) = 2/3, p(b) = 1/3
    # H = -(2/3)*log2(2/3) - (1/3)*log2(1/3) ≈ 0.918
    expected_repeated = -(2/3) * math.log2(2/3) - (1/3) * math.log2(1/3)
    print(f"  Repeated tags {repeated_tags}: {repeated_entropy:.6f} (expected: {expected_repeated:.6f})")
    assert abs(repeated_entropy - expected_repeated) < 1e-10, "Repeated tags entropy calculation error"
    
    print("\n✅ All mathematical verifications passed!")
    print("\nThe fix ensures that entropy is calculated based on tag frequency")
    print("within each individual item, providing proper information content")
    print("measurement for ranking purposes.")


def demonstrate_ranking_difference():
    """Demonstrate how the fix changes ranking behavior."""
    print("\nRanking behavior comparison:")
    print("=" * 30)
    
    # Items that show the ranking difference
    test_items = [
        {'title': 'Locally uniform, globally rare', 'tags': ['rare1', 'rare2']},
        {'title': 'Locally repeated, globally common', 'tags': ['common', 'common']},
        {'title': 'Mixed distribution', 'tags': ['rare1', 'common']},
    ]
    
    dataset = [
        {'tags': ['common'] * 10},  # Make 'common' very frequent globally
        {'tags': ['rare1', 'rare2']},  # Keep rare tags infrequent 
    ] + test_items
    
    print("With correct LOCAL entropy calculation:")
    for item in test_items:
        local_entropy = correct_entropy_calculation(item['tags'])
        score = len(item['tags']) * (1 + local_entropy)
        print(f"  {item['title']}: score = {score:.3f}")
    
    print("\nWith incorrect GLOBAL entropy calculation:")
    for item in test_items:
        global_entropy = incorrect_global_entropy_calculation(dataset, item['tags'])
        score = len(item['tags']) * (1 + global_entropy)
        print(f"  {item['title']}: score = {score:.3f}")
    
    print("\nThe local entropy approach correctly prioritizes items with")
    print("diverse tag distributions within the item itself, rather than")
    print("being biased by global tag frequency.")


if __name__ == "__main__":
    try:
        test_entropy_calculation_fix()
        demonstrate_ranking_difference()
        print("\n🎉 Entropy calculation fix validation completed successfully!")
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        sys.exit(1)