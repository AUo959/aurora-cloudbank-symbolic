"""
Reliquary Indexer for Aurora Symbolic Thread Discovery
Advanced indexing and discovery system for symbolic threads and computational artifacts
"""

import time
import json
import hashlib
from typing import Dict, List, Any, Optional, Set, Union, Tuple
from enum import Enum
from dataclasses import dataclass, asdict
from .dlp_system import EnhancedDLPSystem, DLPClassification


class IndexType(Enum):
    """Types of reliquary indices"""
    TEMPORAL = "temporal"
    TOPOLOGICAL = "topological"
    SEMANTIC = "semantic"
    LINEAGE = "lineage"
    CLASSIFICATION = "classification"
    CONTENT = "content"
    CROSS_REFERENCE = "cross_reference"


class DiscoveryMode(Enum):
    """Discovery operation modes"""
    FAST = "fast"                # Quick index-based discovery
    COMPREHENSIVE = "comprehensive"  # Deep search with analysis
    SEMANTIC = "semantic"        # Content-based semantic search
    LINEAGE = "lineage"         # Lineage-based discovery
    TEMPORAL = "temporal"       # Time-based discovery
    HYBRID = "hybrid"           # Multi-mode hybrid discovery


@dataclass
class ReliquaryEntry:
    """Entry in the reliquary index"""
    entry_id: str
    item_type: str
    item_id: str
    discovery_metadata: Dict[str, Any]
    index_timestamp: float
    content_signature: str
    classification_level: str
    access_level: str
    lineage_signature: str
    semantic_tags: List[str]
    cross_references: List[str]


@dataclass
class DiscoveryQuery:
    """Query structure for symbolic thread discovery"""
    query_id: str
    query_type: str
    search_terms: List[str]
    filters: Dict[str, Any]
    discovery_mode: DiscoveryMode
    max_results: int
    include_metadata: bool
    include_lineage: bool
    temporal_bounds: Optional[Tuple[float, float]]


@dataclass
class DiscoveryResult:
    """Result from symbolic thread discovery"""
    result_id: str
    query_id: str
    item_id: str
    item_type: str
    relevance_score: float
    discovery_method: str
    metadata: Dict[str, Any]
    lineage_info: Optional[Dict[str, Any]]
    content_excerpt: Optional[str]
    access_verified: bool


class ReliquaryIndexer:
    """Advanced indexing and discovery system for Aurora symbolic artifacts"""
    
    def __init__(self, dlp_system: Optional[EnhancedDLPSystem] = None):
        self.dlp_system = dlp_system or EnhancedDLPSystem()
        
        # Core indices
        self.indices: Dict[IndexType, Dict[str, Any]] = {
            IndexType.TEMPORAL: {},
            IndexType.TOPOLOGICAL: {},
            IndexType.SEMANTIC: {},
            IndexType.LINEAGE: {},
            IndexType.CLASSIFICATION: {},
            IndexType.CONTENT: {},
            IndexType.CROSS_REFERENCE: {}
        }
        
        # Main reliquary registry
        self.reliquary_registry: Dict[str, ReliquaryEntry] = {}
        
        # Discovery and indexing configuration
        self.indexing_config = {
            'auto_indexing_enabled': True,
            'semantic_analysis_enabled': True,
            'lineage_tracking_enabled': True,
            'content_extraction_enabled': True,
            'cross_reference_detection': True,
            'classification_auto_indexing': True
        }
        
        # Search configuration
        self.search_config = {
            'default_max_results': 50,
            'relevance_threshold': 0.1,
            'semantic_similarity_threshold': 0.3,
            'enable_fuzzy_matching': True,
            'enable_wildcard_search': True,
            'cache_search_results': True
        }
        
        # Discovery statistics
        self.discovery_statistics = {
            'total_indexed_items': 0,
            'indices_size': {},
            'discovery_queries_performed': 0,
            'discovery_cache_hits': 0,
            'indexing_operations': 0,
            'last_index_rebuild': 0
        }
        
        # Discovery cache
        self.discovery_cache: Dict[str, Dict[str, Any]] = {}
        self.cache_ttl = 3600  # 1 hour
        
        # Semantic analysis tools
        self.semantic_extractors = {
            'keyword_extractor': self._extract_keywords,
            'concept_extractor': self._extract_concepts,
            'entity_extractor': self._extract_entities,
            'pattern_extractor': self._extract_patterns
        }
    
    def index_item(self, item_id: str, item_data: Dict[str, Any], 
                  item_type: str = "symbolic_artifact") -> str:
        """Index an item in the reliquary"""
        indexing_timestamp = time.time()
        
        # Generate entry ID
        entry_id = self._generate_entry_id(item_id, item_type, indexing_timestamp)
        
        # Extract discovery metadata
        discovery_metadata = self._extract_discovery_metadata(item_data, item_type)
        
        # Calculate content signature
        content_signature = self._calculate_content_signature(item_data)
        
        # Determine classification and access level
        classification_info = self._determine_classification(item_data)
        
        # Calculate lineage signature
        lineage_signature = self._calculate_lineage_signature(item_id, item_data)
        
        # Extract semantic tags
        semantic_tags = self._extract_semantic_tags(item_data) if self.indexing_config['semantic_analysis_enabled'] else []
        
        # Detect cross-references
        cross_references = self._detect_cross_references(item_data) if self.indexing_config['cross_reference_detection'] else []
        
        # Create reliquary entry
        reliquary_entry = ReliquaryEntry(
            entry_id=entry_id,
            item_type=item_type,
            item_id=item_id,
            discovery_metadata=discovery_metadata,
            index_timestamp=indexing_timestamp,
            content_signature=content_signature,
            classification_level=classification_info['classification'],
            access_level=classification_info['access_level'],
            lineage_signature=lineage_signature,
            semantic_tags=semantic_tags,
            cross_references=cross_references
        )
        
        # Add to registry
        self.reliquary_registry[entry_id] = reliquary_entry
        
        # Update indices
        self._update_indices(reliquary_entry, item_data)
        
        # Update statistics
        self.discovery_statistics['total_indexed_items'] += 1
        self.discovery_statistics['indexing_operations'] += 1
        
        return entry_id
    
    def discover_threads(self, query: Union[DiscoveryQuery, Dict[str, Any]]) -> List[DiscoveryResult]:
        """Discover symbolic threads based on query"""
        query_start_time = time.time()
        
        # Convert dict to DiscoveryQuery if needed
        if isinstance(query, dict):
            query = self._dict_to_discovery_query(query)
        
        # Check cache first
        cache_key = self._generate_cache_key(query)
        if self.search_config['cache_search_results'] and cache_key in self.discovery_cache:
            cached_result = self.discovery_cache[cache_key]
            if time.time() - cached_result['timestamp'] < self.cache_ttl:
                self.discovery_statistics['discovery_cache_hits'] += 1
                return cached_result['results']
        
        # Perform discovery based on mode
        if query.discovery_mode == DiscoveryMode.FAST:
            results = self._fast_discovery(query)
        elif query.discovery_mode == DiscoveryMode.COMPREHENSIVE:
            results = self._comprehensive_discovery(query)
        elif query.discovery_mode == DiscoveryMode.SEMANTIC:
            results = self._semantic_discovery(query)
        elif query.discovery_mode == DiscoveryMode.LINEAGE:
            results = self._lineage_discovery(query)
        elif query.discovery_mode == DiscoveryMode.TEMPORAL:
            results = self._temporal_discovery(query)
        elif query.discovery_mode == DiscoveryMode.HYBRID:
            results = self._hybrid_discovery(query)
        else:
            results = self._fast_discovery(query)  # Default fallback
        
        # Apply filters and ranking
        filtered_results = self._apply_filters(results, query.filters)
        ranked_results = self._rank_results(filtered_results, query)
        
        # Limit results
        final_results = ranked_results[:query.max_results]
        
        # Verify access permissions
        accessible_results = self._verify_access_permissions(final_results)
        
        # Cache results
        if self.search_config['cache_search_results']:
            self.discovery_cache[cache_key] = {
                'results': accessible_results,
                'timestamp': time.time(),
                'query_duration': time.time() - query_start_time
            }
        
        # Update statistics
        self.discovery_statistics['discovery_queries_performed'] += 1
        
        return accessible_results
    
    def _extract_discovery_metadata(self, item_data: Dict[str, Any], item_type: str) -> Dict[str, Any]:
        """Extract metadata for discovery indexing"""
        metadata = {
            'item_type': item_type,
            'data_keys': list(item_data.keys()) if isinstance(item_data, dict) else [],
            'data_size': len(str(item_data)),
            'extraction_timestamp': time.time()
        }
        
        # Extract type-specific metadata
        if item_type == 'symbolic_thread':
            metadata.update(self._extract_thread_metadata(item_data))
        elif item_type == 'symbolic_anchor':
            metadata.update(self._extract_anchor_metadata(item_data))
        elif item_type == 'execution_chain':
            metadata.update(self._extract_chain_metadata(item_data))
        elif item_type == 'entropy_state':
            metadata.update(self._extract_entropy_metadata(item_data))
        
        return metadata
    
    def _extract_thread_metadata(self, thread_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract metadata specific to symbolic threads"""
        metadata = {}
        
        # Basic thread information
        if 'thread_id' in thread_data:
            metadata['thread_id'] = thread_data['thread_id']
        
        if 'thread_type' in thread_data:
            metadata['thread_type'] = thread_data['thread_type']
        
        if 'priority' in thread_data:
            metadata['priority'] = thread_data['priority']
        
        if 'state' in thread_data:
            metadata['thread_state'] = thread_data['state']
        
        # Temporal information
        if 'creation_timestamp' in thread_data:
            metadata['creation_time'] = thread_data['creation_timestamp']
        
        if 'last_activity_timestamp' in thread_data:
            metadata['last_activity'] = thread_data['last_activity_timestamp']
        
        # Computation information
        if 'computation_history' in thread_data:
            computation_history = thread_data['computation_history']
            metadata['computation_count'] = len(computation_history) if isinstance(computation_history, list) else 0
            
            if computation_history and isinstance(computation_history, list):
                metadata['first_computation'] = computation_history[0].get('timestamp', 0)
                metadata['last_computation'] = computation_history[-1].get('timestamp', 0)
        
        # Dependency information
        if 'dependencies' in thread_data:
            dependencies = thread_data['dependencies']
            if isinstance(dependencies, (list, set)):
                metadata['dependency_count'] = len(dependencies)
                metadata['has_dependencies'] = len(dependencies) > 0
        
        if 'dependents' in thread_data:
            dependents = thread_data['dependents']
            if isinstance(dependents, (list, set)):
                metadata['dependent_count'] = len(dependents)
                metadata['has_dependents'] = len(dependents) > 0
        
        return metadata
    
    def _extract_anchor_metadata(self, anchor_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract metadata specific to symbolic anchors"""
        metadata = {}
        
        # Anchor type and state
        if 'type' in anchor_data:
            metadata['anchor_type'] = anchor_data['type']
        
        if 'state' in anchor_data:
            metadata['anchor_state'] = anchor_data['state']
        
        if 'resolution' in anchor_data:
            metadata['anchor_resolution'] = anchor_data['resolution']
        
        # Entropy information
        if 'entropy_monitoring' in anchor_data:
            entropy_info = anchor_data['entropy_monitoring']
            metadata['current_entropy'] = entropy_info.get('current_entropy', 0)
            metadata['entropy_tracking'] = True
        
        # Performance information
        if 'performance' in anchor_data:
            performance_info = anchor_data['performance']
            metadata.update({f'perf_{k}': v for k, v in performance_info.items()})
        
        return metadata
    
    def _extract_chain_metadata(self, chain_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract metadata specific to execution chains"""
        metadata = {}
        
        # Chain identification
        if 'chain_id' in chain_data:
            metadata['chain_id'] = chain_data['chain_id']
        
        # Execution information
        if 'results' in chain_data:
            results = chain_data['results']
            if isinstance(results, list):
                metadata['step_count'] = len(results)
                metadata['has_results'] = len(results) > 0
        
        if 'execution_context' in chain_data:
            context = chain_data['execution_context']
            metadata['execution_time'] = context.get('total_execution_time', 0)
            metadata['start_step'] = context.get('start_step', 0)
            metadata['end_step'] = context.get('end_step', 0)
        
        return metadata
    
    def _extract_entropy_metadata(self, entropy_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract metadata specific to entropy states"""
        metadata = {}
        
        # Entropy values
        if 'current_entropy' in entropy_data:
            metadata['entropy_value'] = entropy_data['current_entropy']
        
        if 'analysis' in entropy_data:
            analysis = entropy_data['analysis']
            if 'cross_window' in analysis:
                cross_window = analysis['cross_window']
                metadata['entropy_stability'] = cross_window.get('overall_stability', 0)
                metadata['entropy_trend'] = cross_window.get('overall_trend', 0)
        
        if 'alerts' in entropy_data:
            alerts = entropy_data['alerts']
            if isinstance(alerts, list):
                metadata['alert_count'] = len(alerts)
                metadata['has_alerts'] = len(alerts) > 0
        
        return metadata
    
    def _calculate_content_signature(self, item_data: Dict[str, Any]) -> str:
        """Calculate unique content signature for item"""
        # Create a normalized representation of the content
        content_elements = []
        
        if isinstance(item_data, dict):
            # Extract key structural elements
            for key in sorted(item_data.keys()):
                value = item_data[key]
                if isinstance(value, (str, int, float, bool)):
                    content_elements.append(f"{key}:{value}")
                elif isinstance(value, (list, tuple)):
                    content_elements.append(f"{key}:list_{len(value)}")
                elif isinstance(value, dict):
                    content_elements.append(f"{key}:dict_{len(value)}")
        
        # Create signature from structural elements
        content_string = "|".join(content_elements)
        return hashlib.sha256(content_string.encode()).hexdigest()[:16]
    
    def _determine_classification(self, item_data: Dict[str, Any]) -> Dict[str, Any]:
        """Determine classification and access level for item"""
        # Check if item already has classification
        if 'classification' in item_data:
            classification = item_data['classification']
            access_level = item_data.get('access_level', 'internal')
        elif 'dlp_metadata' in item_data:
            dlp_metadata = item_data['dlp_metadata']
            classification = dlp_metadata.get('classification', 'AURORA_INTERNAL')
            access_level = dlp_metadata.get('sensitivity', 'internal')
        else:
            # Perform automatic classification
            try:
                item_id = item_data.get('id', item_data.get('item_id', 'unknown'))
                classification_result = self.dlp_system.classify_data(item_id, item_data)
                classification = classification_result['classification_result']['classification'].value
                access_level = classification_result['classification_result']['sensitivity'].value
            except Exception:
                # Default classification
                classification = 'AURORA_INTERNAL'
                access_level = 'internal'
        
        return {
            'classification': classification,
            'access_level': access_level
        }
    
    def _calculate_lineage_signature(self, item_id: str, item_data: Dict[str, Any]) -> str:
        """Calculate lineage signature for item"""
        lineage_elements = []
        
        # Extract dependency information
        dependencies = item_data.get('dependencies', [])
        if isinstance(dependencies, (list, set)):
            lineage_elements.extend(sorted(str(dep) for dep in dependencies))
        
        # Extract parent references
        parent_ids = item_data.get('parent_ids', [])
        if isinstance(parent_ids, (list, set)):
            lineage_elements.extend(sorted(str(pid) for pid in parent_ids))
        
        # Extract lineage metadata if available
        if 'lineage_metadata' in item_data:
            lineage_metadata = item_data['lineage_metadata']
            operation = lineage_metadata.get('operation', 'unknown')
            lineage_elements.append(f"op:{operation}")
        
        # Create lineage signature
        if lineage_elements:
            lineage_string = "|".join(lineage_elements)
            return hashlib.sha256(lineage_string.encode()).hexdigest()[:16]
        else:
            return "no_lineage"
    
    def _extract_semantic_tags(self, item_data: Dict[str, Any]) -> List[str]:
        """Extract semantic tags from item data"""
        semantic_tags = set()
        
        # Use all available extractors
        for extractor_name, extractor_func in self.semantic_extractors.items():
            try:
                tags = extractor_func(item_data)
                semantic_tags.update(tags)
            except Exception:
                continue
        
        return list(semantic_tags)
    
    def _extract_keywords(self, item_data: Dict[str, Any]) -> List[str]:
        """Extract keywords from item data"""
        keywords = set()
        
        # Extract from string values
        def extract_from_value(value):
            if isinstance(value, str):
                # Simple keyword extraction (would be enhanced with NLP in production)
                words = value.lower().split()
                # Filter for meaningful words (length > 2, not common words)
                meaningful_words = [word for word in words if len(word) > 2 and word not in ['the', 'and', 'for', 'are', 'with']]
                keywords.update(meaningful_words)
            elif isinstance(value, dict):
                for v in value.values():
                    extract_from_value(v)
            elif isinstance(value, list):
                for item in value:
                    extract_from_value(item)
        
        extract_from_value(item_data)
        return list(keywords)[:20]  # Limit to top 20 keywords
    
    def _extract_concepts(self, item_data: Dict[str, Any]) -> List[str]:
        """Extract conceptual tags from item data"""
        concepts = set()
        
        # Domain-specific concept extraction
        content_str = str(item_data).lower()
        
        # Aurora/symbolic concepts
        aurora_concepts = [
            'quantum', 'symbolic', 'anchor', 'entropy', 'thread', 'chain',
            'preservation', 'rehydration', 'lineage', 'classification',
            'temporal', 'spatial', 'boundary', 'resolution'
        ]
        
        for concept in aurora_concepts:
            if concept in content_str:
                concepts.add(f"concept:{concept}")
        
        # Mathematical/computational concepts
        math_concepts = [
            'matrix', 'vector', 'calculation', 'computation', 'algorithm',
            'optimization', 'analysis', 'processing', 'transformation'
        ]
        
        for concept in math_concepts:
            if concept in content_str:
                concepts.add(f"math:{concept}")
        
        return list(concepts)
    
    def _extract_entities(self, item_data: Dict[str, Any]) -> List[str]:
        """Extract entity references from item data"""
        entities = set()
        
        # Extract IDs and references
        def extract_entities_recursive(obj, prefix=""):
            if isinstance(obj, dict):
                for key, value in obj.items():
                    if 'id' in key.lower():
                        entities.add(f"entity:{value}")
                    elif key.lower() in ['type', 'class', 'category']:
                        entities.add(f"type:{value}")
                    elif isinstance(value, (dict, list)):
                        extract_entities_recursive(value, f"{prefix}.{key}")
            elif isinstance(obj, list):
                for i, item in enumerate(obj):
                    if isinstance(item, (dict, list)):
                        extract_entities_recursive(item, f"{prefix}[{i}]")
        
        extract_entities_recursive(item_data)
        return list(entities)[:10]  # Limit entities
    
    def _extract_patterns(self, item_data: Dict[str, Any]) -> List[str]:
        """Extract structural patterns from item data"""
        patterns = set()
        
        # Analyze data structure patterns
        if isinstance(item_data, dict):
            # Common patterns in Aurora data
            if 'timestamp' in item_data and 'data' in item_data:
                patterns.add("pattern:timestamped_data")
            
            if 'dependencies' in item_data and 'dependents' in item_data:
                patterns.add("pattern:dependency_graph")
            
            if 'entropy' in str(item_data).lower():
                patterns.add("pattern:entropy_tracking")
            
            if 'state' in item_data and 'transition' in str(item_data).lower():
                patterns.add("pattern:state_machine")
            
            # Detect nested structures
            nested_dicts = sum(1 for v in item_data.values() if isinstance(v, dict))
            if nested_dicts > 3:
                patterns.add("pattern:complex_nested")
            
            # Detect array patterns
            arrays = sum(1 for v in item_data.values() if isinstance(v, list))
            if arrays > 2:
                patterns.add("pattern:multi_array")
        
        return list(patterns)
    
    def _detect_cross_references(self, item_data: Dict[str, Any]) -> List[str]:
        """Detect cross-references to other items"""
        cross_references = set()
        
        def find_references(obj):
            if isinstance(obj, dict):
                for key, value in obj.items():
                    if isinstance(value, str):
                        # Look for ID patterns
                        if 'id' in key.lower() and value != obj.get('id', obj.get('item_id')):
                            cross_references.add(value)
                        # Look for reference patterns
                        elif any(ref_keyword in key.lower() for ref_keyword in ['ref', 'link', 'parent', 'child', 'dep']):
                            cross_references.add(value)
                    elif isinstance(value, (dict, list)):
                        find_references(value)
            elif isinstance(obj, list):
                for item in obj:
                    if isinstance(item, (dict, list)):
                        find_references(item)
                    elif isinstance(item, str) and len(item) > 5:  # Potential ID
                        cross_references.add(item)
        
        find_references(item_data)
        return list(cross_references)[:20]  # Limit cross-references
    
    def _update_indices(self, entry: ReliquaryEntry, item_data: Dict[str, Any]):
        """Update all indices with new entry"""
        
        # Temporal index
        self._update_temporal_index(entry)
        
        # Topological index (based on relationships)
        self._update_topological_index(entry)
        
        # Semantic index
        self._update_semantic_index(entry)
        
        # Lineage index
        self._update_lineage_index(entry)
        
        # Classification index
        self._update_classification_index(entry)
        
        # Content index
        self._update_content_index(entry, item_data)
        
        # Cross-reference index
        self._update_cross_reference_index(entry)
        
        # Update index size statistics
        for index_type in IndexType:
            self.discovery_statistics['indices_size'][index_type.value] = len(self.indices[index_type])
    
    def _update_temporal_index(self, entry: ReliquaryEntry):
        """Update temporal index"""
        temporal_index = self.indices[IndexType.TEMPORAL]
        
        # Index by time buckets (day, week, month)
        timestamp = entry.index_timestamp
        
        # Daily bucket
        day_key = int(timestamp // 86400)  # Seconds in a day
        if day_key not in temporal_index:
            temporal_index[day_key] = []
        temporal_index[day_key].append(entry.entry_id)
        
        # Also index by creation time if available
        metadata = entry.discovery_metadata
        if 'creation_time' in metadata:
            creation_day = int(metadata['creation_time'] // 86400)
            creation_key = f"created_{creation_day}"
            if creation_key not in temporal_index:
                temporal_index[creation_key] = []
            temporal_index[creation_key].append(entry.entry_id)
    
    def _update_topological_index(self, entry: ReliquaryEntry):
        """Update topological index based on relationships"""
        topological_index = self.indices[IndexType.TOPOLOGICAL]
        
        # Index by dependency relationships
        metadata = entry.discovery_metadata
        
        # Index items with dependencies
        if metadata.get('has_dependencies', False):
            dep_count = metadata.get('dependency_count', 0)
            dep_key = f"dependencies_{dep_count}"
            if dep_key not in topological_index:
                topological_index[dep_key] = []
            topological_index[dep_key].append(entry.entry_id)
        
        # Index items with dependents
        if metadata.get('has_dependents', False):
            dependent_count = metadata.get('dependent_count', 0)
            dependent_key = f"dependents_{dependent_count}"
            if dependent_key not in topological_index:
                topological_index[dependent_key] = []
            topological_index[dependent_key].append(entry.entry_id)
        
        # Index by connection degree (total connections)
        total_connections = metadata.get('dependency_count', 0) + metadata.get('dependent_count', 0)
        if total_connections > 0:
            connection_key = f"connections_{total_connections}"
            if connection_key not in topological_index:
                topological_index[connection_key] = []
            topological_index[connection_key].append(entry.entry_id)
    
    def _update_semantic_index(self, entry: ReliquaryEntry):
        """Update semantic index"""
        semantic_index = self.indices[IndexType.SEMANTIC]
        
        # Index by semantic tags
        for tag in entry.semantic_tags:
            if tag not in semantic_index:
                semantic_index[tag] = []
            semantic_index[tag].append(entry.entry_id)
    
    def _update_lineage_index(self, entry: ReliquaryEntry):
        """Update lineage index"""
        lineage_index = self.indices[IndexType.LINEAGE]
        
        # Index by lineage signature
        lineage_sig = entry.lineage_signature
        if lineage_sig not in lineage_index:
            lineage_index[lineage_sig] = []
        lineage_index[lineage_sig].append(entry.entry_id)
    
    def _update_classification_index(self, entry: ReliquaryEntry):
        """Update classification index"""
        classification_index = self.indices[IndexType.CLASSIFICATION]
        
        # Index by classification level
        classification = entry.classification_level
        if classification not in classification_index:
            classification_index[classification] = []
        classification_index[classification].append(entry.entry_id)
        
        # Index by access level
        access_level = entry.access_level
        access_key = f"access_{access_level}"
        if access_key not in classification_index:
            classification_index[access_key] = []
        classification_index[access_key].append(entry.entry_id)
    
    def _update_content_index(self, entry: ReliquaryEntry, item_data: Dict[str, Any]):
        """Update content index"""
        content_index = self.indices[IndexType.CONTENT]
        
        # Index by content signature
        content_sig = entry.content_signature
        if content_sig not in content_index:
            content_index[content_sig] = []
        content_index[content_sig].append(entry.entry_id)
        
        # Index by item type
        item_type = entry.item_type
        if item_type not in content_index:
            content_index[item_type] = []
        content_index[item_type].append(entry.entry_id)
    
    def _update_cross_reference_index(self, entry: ReliquaryEntry):
        """Update cross-reference index"""
        cross_ref_index = self.indices[IndexType.CROSS_REFERENCE]
        
        # Index by cross-references
        for ref in entry.cross_references:
            if ref not in cross_ref_index:
                cross_ref_index[ref] = []
            cross_ref_index[ref].append(entry.entry_id)
    
    def _dict_to_discovery_query(self, query_dict: Dict[str, Any]) -> DiscoveryQuery:
        """Convert dictionary to DiscoveryQuery object"""
        return DiscoveryQuery(
            query_id=query_dict.get('query_id', f"query_{int(time.time())}"),
            query_type=query_dict.get('query_type', 'general'),
            search_terms=query_dict.get('search_terms', []),
            filters=query_dict.get('filters', {}),
            discovery_mode=DiscoveryMode(query_dict.get('discovery_mode', 'fast')),
            max_results=query_dict.get('max_results', self.search_config['default_max_results']),
            include_metadata=query_dict.get('include_metadata', True),
            include_lineage=query_dict.get('include_lineage', False),
            temporal_bounds=query_dict.get('temporal_bounds')
        )
    
    def _generate_cache_key(self, query: DiscoveryQuery) -> str:
        """Generate cache key for query"""
        query_elements = [
            query.query_type,
            "|".join(sorted(query.search_terms)),
            str(sorted(query.filters.items())),
            query.discovery_mode.value,
            str(query.max_results)
        ]
        cache_string = "|".join(query_elements)
        return hashlib.sha256(cache_string.encode()).hexdigest()[:16]
    
    def _fast_discovery(self, query: DiscoveryQuery) -> List[DiscoveryResult]:
        """Fast discovery using direct index lookups"""
        results = []
        
        # Search semantic index for terms
        for term in query.search_terms:
            if term in self.indices[IndexType.SEMANTIC]:
                entry_ids = self.indices[IndexType.SEMANTIC][term]
                for entry_id in entry_ids:
                    if entry_id in self.reliquary_registry:
                        entry = self.reliquary_registry[entry_id]
                        result = self._create_discovery_result(entry, query, 'semantic_index', 0.8)
                        results.append(result)
        
        # Search content index for item types
        for term in query.search_terms:
            if term in self.indices[IndexType.CONTENT]:
                entry_ids = self.indices[IndexType.CONTENT][term]
                for entry_id in entry_ids:
                    if entry_id in self.reliquary_registry:
                        entry = self.reliquary_registry[entry_id]
                        result = self._create_discovery_result(entry, query, 'content_index', 0.7)
                        results.append(result)
        
        return results
    
    def _comprehensive_discovery(self, query: DiscoveryQuery) -> List[DiscoveryResult]:
        """Comprehensive discovery across all indices"""
        results = []
        
        # Start with fast discovery
        results.extend(self._fast_discovery(query))
        
        # Search across all indices
        for index_type, index_data in self.indices.items():
            for term in query.search_terms:
                # Fuzzy matching for index keys
                if self.search_config['enable_fuzzy_matching']:
                    matching_keys = [key for key in index_data.keys() if term.lower() in str(key).lower()]
                else:
                    matching_keys = [key for key in index_data.keys() if term == str(key)]
                
                for key in matching_keys:
                    entry_ids = index_data[key]
                    for entry_id in entry_ids:
                        if entry_id in self.reliquary_registry:
                            entry = self.reliquary_registry[entry_id]
                            result = self._create_discovery_result(entry, query, f'{index_type.value}_index', 0.6)
                            results.append(result)
        
        return results
    
    def _semantic_discovery(self, query: DiscoveryQuery) -> List[DiscoveryResult]:
        """Semantic discovery based on content analysis"""
        results = []
        
        # Expand search terms with semantic variations
        expanded_terms = self._expand_search_terms(query.search_terms)
        
        # Search semantic index with expanded terms
        for term in expanded_terms:
            if term in self.indices[IndexType.SEMANTIC]:
                entry_ids = self.indices[IndexType.SEMANTIC][term]
                for entry_id in entry_ids:
                    if entry_id in self.reliquary_registry:
                        entry = self.reliquary_registry[entry_id]
                        # Calculate semantic similarity
                        similarity = self._calculate_semantic_similarity(query.search_terms, entry.semantic_tags)
                        if similarity >= self.search_config['semantic_similarity_threshold']:
                            result = self._create_discovery_result(entry, query, 'semantic_analysis', similarity)
                            results.append(result)
        
        return results
    
    def _lineage_discovery(self, query: DiscoveryQuery) -> List[DiscoveryResult]:
        """Discovery based on lineage relationships"""
        results = []
        
        # Find items by lineage connections
        for term in query.search_terms:
            # Search cross-reference index
            if term in self.indices[IndexType.CROSS_REFERENCE]:
                entry_ids = self.indices[IndexType.CROSS_REFERENCE][term]
                for entry_id in entry_ids:
                    if entry_id in self.reliquary_registry:
                        entry = self.reliquary_registry[entry_id]
                        result = self._create_discovery_result(entry, query, 'lineage_reference', 0.9)
                        results.append(result)
        
        return results
    
    def _temporal_discovery(self, query: DiscoveryQuery) -> List[DiscoveryResult]:
        """Discovery based on temporal relationships"""
        results = []
        
        temporal_index = self.indices[IndexType.TEMPORAL]
        
        # Use temporal bounds if provided
        if query.temporal_bounds:
            start_time, end_time = query.temporal_bounds
            start_day = int(start_time // 86400)
            end_day = int(end_time // 86400)
            
            for day in range(start_day, end_day + 1):
                if day in temporal_index:
                    entry_ids = temporal_index[day]
                    for entry_id in entry_ids:
                        if entry_id in self.reliquary_registry:
                            entry = self.reliquary_registry[entry_id]
                            result = self._create_discovery_result(entry, query, 'temporal_range', 0.8)
                            results.append(result)
        else:
            # Search for recent items
            current_time = time.time()
            recent_days = [int((current_time - i * 86400) // 86400) for i in range(7)]  # Last 7 days
            
            for day in recent_days:
                if day in temporal_index:
                    entry_ids = temporal_index[day]
                    for entry_id in entry_ids:
                        if entry_id in self.reliquary_registry:
                            entry = self.reliquary_registry[entry_id]
                            result = self._create_discovery_result(entry, query, 'temporal_recent', 0.7)
                            results.append(result)
        
        return results
    
    def _hybrid_discovery(self, query: DiscoveryQuery) -> List[DiscoveryResult]:
        """Hybrid discovery using multiple methods"""
        all_results = []
        
        # Combine results from different discovery methods
        all_results.extend(self._fast_discovery(query))
        all_results.extend(self._semantic_discovery(query))
        all_results.extend(self._lineage_discovery(query))
        all_results.extend(self._temporal_discovery(query))
        
        # Remove duplicates and weight by multiple discovery methods
        result_weights = {}
        unique_results = {}
        
        for result in all_results:
            item_id = result.item_id
            if item_id not in unique_results:
                unique_results[item_id] = result
                result_weights[item_id] = result.relevance_score
            else:
                # Increase weight for items found by multiple methods
                result_weights[item_id] += result.relevance_score * 0.5
                # Update relevance score
                unique_results[item_id].relevance_score = result_weights[item_id]
        
        return list(unique_results.values())
    
    def _expand_search_terms(self, search_terms: List[str]) -> List[str]:
        """Expand search terms with semantic variations"""
        expanded_terms = set(search_terms)
        
        # Add semantic variations for Aurora-specific terms
        term_expansions = {
            'thread': ['threads', 'symbolic_thread', 'computation'],
            'anchor': ['anchors', 't1', 'srb', 'temporal', 'spatial'],
            'entropy': ['entropies', 'stability', 'drift', 'stabilization'],
            'chain': ['chains', 'execution', 'sequence', 'steps'],
            'preservation': ['preserved', 'sealed', 'archived'],
            'lineage': ['dependency', 'parent', 'relationship', 'connection']
        }
        
        for term in search_terms:
            term_lower = term.lower()
            if term_lower in term_expansions:
                expanded_terms.update(term_expansions[term_lower])
        
        return list(expanded_terms)
    
    def _calculate_semantic_similarity(self, query_terms: List[str], item_tags: List[str]) -> float:
        """Calculate semantic similarity between query terms and item tags"""
        if not query_terms or not item_tags:
            return 0.0
        
        query_set = set(term.lower() for term in query_terms)
        tag_set = set(tag.lower() for tag in item_tags)
        
        # Calculate Jaccard similarity
        intersection = len(query_set & tag_set)
        union = len(query_set | tag_set)
        
        return intersection / union if union > 0 else 0.0
    
    def _create_discovery_result(self, entry: ReliquaryEntry, query: DiscoveryQuery, 
                               discovery_method: str, relevance_score: float) -> DiscoveryResult:
        """Create a discovery result from a reliquary entry"""
        result_id = f"result_{entry.entry_id}_{query.query_id}"
        
        # Prepare metadata
        metadata = entry.discovery_metadata.copy() if query.include_metadata else {}
        
        # Prepare lineage info
        lineage_info = None
        if query.include_lineage:
            lineage_info = {
                'lineage_signature': entry.lineage_signature,
                'cross_references': entry.cross_references
            }
        
        # Generate content excerpt
        content_excerpt = None
        if entry.semantic_tags:
            # Create excerpt from semantic tags
            content_excerpt = f"Tags: {', '.join(entry.semantic_tags[:5])}"
            if len(entry.semantic_tags) > 5:
                content_excerpt += f" (+{len(entry.semantic_tags) - 5} more)"
        
        return DiscoveryResult(
            result_id=result_id,
            query_id=query.query_id,
            item_id=entry.item_id,
            item_type=entry.item_type,
            relevance_score=relevance_score,
            discovery_method=discovery_method,
            metadata=metadata,
            lineage_info=lineage_info,
            content_excerpt=content_excerpt,
            access_verified=False  # Will be verified later
        )
    
    def _apply_filters(self, results: List[DiscoveryResult], filters: Dict[str, Any]) -> List[DiscoveryResult]:
        """Apply filters to discovery results"""
        filtered_results = []
        
        for result in results:
            # Apply filters
            passes_filters = True
            
            # Item type filter
            if 'item_type' in filters:
                if result.item_type != filters['item_type']:
                    passes_filters = False
            
            # Classification filter
            if 'classification' in filters:
                entry = self.reliquary_registry.get(f"{result.item_type}_{result.item_id}")
                if entry and entry.classification_level != filters['classification']:
                    passes_filters = False
            
            # Relevance threshold filter
            if 'min_relevance' in filters:
                if result.relevance_score < filters['min_relevance']:
                    passes_filters = False
            
            # Temporal filter
            if 'created_after' in filters:
                created_after = filters['created_after']
                creation_time = result.metadata.get('creation_time', 0)
                if creation_time < created_after:
                    passes_filters = False
            
            if passes_filters:
                filtered_results.append(result)
        
        return filtered_results
    
    def _rank_results(self, results: List[DiscoveryResult], query: DiscoveryQuery) -> List[DiscoveryResult]:
        """Rank discovery results by relevance"""
        # Sort by relevance score (descending)
        ranked_results = sorted(results, key=lambda r: r.relevance_score, reverse=True)
        
        # Remove duplicates (keep highest scoring)
        seen_items = set()
        unique_results = []
        
        for result in ranked_results:
            if result.item_id not in seen_items:
                seen_items.add(result.item_id)
                unique_results.append(result)
        
        return unique_results
    
    def _verify_access_permissions(self, results: List[DiscoveryResult]) -> List[DiscoveryResult]:
        """Verify access permissions for discovery results"""
        accessible_results = []
        
        for result in results:
            # Find the reliquary entry for access verification
            entry_id = None
            for eid, entry in self.reliquary_registry.items():
                if entry.item_id == result.item_id:
                    entry_id = eid
                    break
            
            if entry_id:
                entry = self.reliquary_registry[entry_id]
                # Simple access check (would be enhanced with actual access control)
                access_level = entry.access_level
                
                # For now, allow access to all internal and public items
                if access_level in ['public', 'internal']:
                    result.access_verified = True
                    accessible_results.append(result)
                # Additional access checks would go here for restricted items
        
        return accessible_results
    
    def rebuild_indices(self) -> Dict[str, Any]:
        """Rebuild all indices from scratch"""
        rebuild_start_time = time.time()
        
        # Clear existing indices
        for index_type in IndexType:
            self.indices[index_type].clear()
        
        # Rebuild from reliquary registry
        rebuilt_count = 0
        for entry_id, entry in self.reliquary_registry.items():
            try:
                # Reconstruct item data (simplified - would need full data in production)
                item_data = {'metadata': entry.discovery_metadata}
                self._update_indices(entry, item_data)
                rebuilt_count += 1
            except Exception:
                continue
        
        rebuild_duration = time.time() - rebuild_start_time
        self.discovery_statistics['last_index_rebuild'] = rebuild_start_time
        
        return {
            'rebuild_timestamp': rebuild_start_time,
            'rebuild_duration': rebuild_duration,
            'entries_rebuilt': rebuilt_count,
            'indices_rebuilt': len(IndexType),
            'total_registry_entries': len(self.reliquary_registry)
        }
    
    def get_indexer_statistics(self) -> Dict[str, Any]:
        """Get comprehensive indexer statistics"""
        return {
            'discovery_statistics': self.discovery_statistics.copy(),
            'index_sizes': {index_type.value: len(index_data) for index_type, index_data in self.indices.items()},
            'registry_size': len(self.reliquary_registry),
            'cache_size': len(self.discovery_cache),
            'configuration': {
                'indexing_config': self.indexing_config.copy(),
                'search_config': self.search_config.copy()
            },
            'supported_discovery_modes': [mode.value for mode in DiscoveryMode],
            'supported_index_types': [index_type.value for index_type in IndexType]
        }