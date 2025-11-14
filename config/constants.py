"""
Aurora CloudBank Configuration Constants
Centralized configuration values extracted from codebase

Created: 2025-11-10
Part of: Issue #320 Phase 1 Code Quality Sprint
Purpose: Eliminate magic numbers and improve maintainability
"""

# ==============================================================================
# SECURITY CONFIGURATION
# ==============================================================================

# CSRF Token Configuration
CSRF_TOKEN_MIN_LENGTH = 10  # Minimum token length for basic validation
CSRF_TOKEN_EXPIRY_SECONDS = 300  # 5 minutes
CSRF_CLOCK_SKEW_GRACE_SECONDS = 30  # Allow 30s clock skew between client/server

# Session Configuration
SESSION_TIMEOUT_SECONDS = 3600  # 1 hour default session timeout
SESSION_TOKEN_LENGTH = 32  # Bytes for session token generation

# Rate Limiting Defaults (per minute unless specified)
RATE_LIMIT_DEFAULT_PER_MINUTE = 60
RATE_LIMIT_DEFAULT_PER_HOUR = 1000
RATE_LIMIT_DEFAULT_PER_DAY = 10000

# API-Specific Rate Limits
RATE_LIMIT_GEOMETRIC_OPERATIONS = 60  # Computational operations
RATE_LIMIT_STATE_CHANGES = 10  # State-changing operations (enable/disable)
RATE_LIMIT_HEALTH_CHECK = 120  # Health check endpoint
RATE_LIMIT_AGENT_EXECUTION = 20  # Agent tool execution
RATE_LIMIT_WEBSOCKET_MESSAGES = 100  # WebSocket messages per minute

# ==============================================================================
# QUANTUM SIMULATOR CONFIGURATION
# ==============================================================================

# Supply Chain Cost Factors
SUPPLY_CHAIN_HOLDING_COST_PER_UNIT = 10.0
SUPPLY_CHAIN_ORDERING_COST_MULTIPLIER = 100.0
SUPPLY_CHAIN_ORDERING_COST_EPSILON = 0.01  # Prevent division by zero
SUPPLY_CHAIN_STOCKOUT_COST_PER_UNIT = 50.0

# Energy Grid Cost Factors (per unit)
ENERGY_SOLAR_COST = 0.05
ENERGY_WIND_COST = 0.06
ENERGY_NATURAL_GAS_COST = 0.15
ENERGY_BATTERY_COST = 0.10
ENERGY_CARBON_PENALTY_MULTIPLIER = 2.0

# Risk Analysis Thresholds
RISK_HIGH_THRESHOLD = 0.7  # Above this is high risk
RISK_MEDIUM_THRESHOLD = 0.4  # Between this and high is medium
RISK_LOW_THRESHOLD = 0.2  # Below this is low risk

# ==============================================================================
# VECTOR SYMBOLIC ARCHITECTURE (VSA)
# ==============================================================================

# Default VSA Dimensions
VSA_DEFAULT_DIMENSION = 512
VSA_MIN_DIMENSION = 128
VSA_MAX_DIMENSION = 4096

# Similarity Thresholds
VSA_SIMILARITY_HIGH = 0.8  # Above this considered highly similar
VSA_SIMILARITY_MEDIUM = 0.5  # Between this and high is moderately similar
VSA_SIMILARITY_LOW = 0.3  # Below this considered dissimilar

# ==============================================================================
# MEMORY MANAGEMENT
# ==============================================================================

# AuMemManager Capacity
MEMORY_MANAGER_DEFAULT_CAPACITY = 56000
MEMORY_MANAGER_WARNING_THRESHOLD = 0.8  # Warn at 80% capacity
MEMORY_MANAGER_CRITICAL_THRESHOLD = 0.95  # Critical at 95% capacity

# Memory Seal Configuration
MEMORY_SEAL_HASH_ALGORITHM = "sha256"
MEMORY_SEAL_EXPIRY_HOURS = 24

# ==============================================================================
# API CONFIGURATION
# ==============================================================================

# Timeout Values (seconds)
API_DEFAULT_TIMEOUT = 30
API_LONG_OPERATION_TIMEOUT = 120
API_WEBSOCKET_TIMEOUT = 300

# Response Limits
API_MAX_RESPONSE_SIZE_MB = 10
API_MAX_LIST_ITEMS = 1000
API_DEFAULT_PAGE_SIZE = 100

# Error Message Truncation
ERROR_MESSAGE_MAX_LENGTH = 200
STACK_TRACE_MAX_LINES = 10

# ==============================================================================
# THREAD TRANSFER / CONSENSUS
# ==============================================================================

# Raft Consensus Configuration
RAFT_ELECTION_TIMEOUT_MIN_MS = 150
RAFT_ELECTION_TIMEOUT_MAX_MS = 300
RAFT_HEARTBEAT_INTERVAL_MS = 50
RAFT_LOG_COMPACTION_THRESHOLD = 1000

# Thread Transfer Limits
THREAD_TRANSFER_MAX_PAYLOAD_MB = 5
THREAD_TRANSFER_MAX_HOPS = 10
THREAD_TRANSFER_TIMEOUT_SECONDS = 60

# ==============================================================================
# TESTING CONFIGURATION
# ==============================================================================

# Test Timeouts
TEST_SHORT_TIMEOUT = 5  # For unit tests
TEST_MEDIUM_TIMEOUT = 30  # For integration tests
TEST_LONG_TIMEOUT = 120  # For system tests

# Test Data Sizes
TEST_SMALL_DATASET_SIZE = 100
TEST_MEDIUM_DATASET_SIZE = 1000
TEST_LARGE_DATASET_SIZE = 10000

# ==============================================================================
# LOGGING CONFIGURATION
# ==============================================================================

# Log Levels
LOG_LEVEL_DEVELOPMENT = "DEBUG"
LOG_LEVEL_STAGING = "INFO"
LOG_LEVEL_PRODUCTION = "WARNING"

# Log Rotation
LOG_MAX_BYTES = 10 * 1024 * 1024  # 10MB
LOG_BACKUP_COUNT = 5
LOG_MAX_AGE_DAYS = 30

# ==============================================================================
# PERFORMANCE TUNING
# ==============================================================================

# Cache Configuration
CACHE_DEFAULT_TTL_SECONDS = 300  # 5 minutes
CACHE_MAX_SIZE_MB = 100
CACHE_EVICTION_POLICY = "LRU"  # Least Recently Used

# Worker Pool Configuration
WORKER_POOL_DEFAULT_SIZE = 4
WORKER_POOL_MAX_SIZE = 16
WORKER_QUEUE_MAX_SIZE = 1000

# ==============================================================================
# VALIDATION LIMITS
# ==============================================================================

# Input Validation
INPUT_MAX_LENGTH_DEFAULT = 1000
INPUT_MAX_LENGTH_LARGE = 10000
USERNAME_MIN_LENGTH = 3
USERNAME_MAX_LENGTH = 50
PASSWORD_MIN_LENGTH = 8
PASSWORD_MAX_LENGTH = 128

# Expression Evaluation
EXPRESSION_MAX_LENGTH = 1000
EXPRESSION_MAX_DEPTH = 10  # AST recursion depth

# ==============================================================================
# DEPLOYMENT CONFIGURATION
# ==============================================================================

# Environment Detection
ENV_DEVELOPMENT = "development"
ENV_STAGING = "staging"
ENV_PRODUCTION = "production"

# Feature Flags
FEATURE_QUANTUM_SIMULATION_ENABLED = True
FEATURE_GEOMETRIC_ALGEBRA_ENABLED = True
FEATURE_SONNET4_INTEGRATION_ENABLED = True
FEATURE_AUMEMMANAGER_ENABLED = True

# ==============================================================================
# MIGRATION TRACKING
# ==============================================================================

# This file was created as part of Issue #320 Phase 1 Sprint
# Migration from: Hardcoded values throughout codebase
# Migration to: Centralized configuration
# Date: 2025-11-10
# Author: Commander Thorne / CTO Webb
# Reviewed by: Senior Officer Review Protocol Team
