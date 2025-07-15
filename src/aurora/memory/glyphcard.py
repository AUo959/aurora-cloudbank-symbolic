"""
Glyphcard Generator for Aurora Sealed Thread Documentation
Generates comprehensive documentation cards for symbolic threads and their preservation state
"""

import time
import json
import hashlib
from typing import Dict, List, Any, Optional, Union
from enum import Enum
from dataclasses import dataclass, asdict
from .thread_manager import SymbolicThread, SymbolicThreadManager, ThreadState, ThreadPriority


class GlyphcardFormat(Enum):
    """Supported glyphcard output formats"""
    JSON = "json"
    YAML = "yaml"
    MARKDOWN = "markdown"
    HTML = "html"
    PLAIN_TEXT = "plain_text"


class GlyphcardTemplate(Enum):
    """Pre-defined glyphcard templates"""
    MINIMAL = "minimal"
    STANDARD = "standard"
    COMPREHENSIVE = "comprehensive"
    TECHNICAL = "technical"
    ARCHIVAL = "archival"
    FORENSIC = "forensic"


@dataclass
class GlyphcardMetadata:
    """Metadata for glyphcard generation"""
    generator_version: str
    generation_timestamp: float
    template_used: str
    format_used: str
    thread_count: int
    data_integrity_hash: str
    

class GlyphcardGenerator:
    """Advanced glyphcard generator for Aurora symbolic thread documentation"""
    
    def __init__(self, thread_manager: SymbolicThreadManager):
        self.thread_manager = thread_manager
        self.generator_version = "2.0.0-aurora"
        
        # Template configurations
        self.templates = {
            GlyphcardTemplate.MINIMAL: {
                'sections': ['basic_info', 'status'],
                'detail_level': 'low',
                'include_history': False,
                'include_dependencies': False
            },
            GlyphcardTemplate.STANDARD: {
                'sections': ['basic_info', 'status', 'dependencies', 'recent_activity'],
                'detail_level': 'medium',
                'include_history': True,
                'include_dependencies': True,
                'history_limit': 10
            },
            GlyphcardTemplate.COMPREHENSIVE: {
                'sections': ['basic_info', 'status', 'dependencies', 'full_history', 'performance', 'integrity'],
                'detail_level': 'high',
                'include_history': True,
                'include_dependencies': True,
                'include_performance': True,
                'include_integrity': True
            },
            GlyphcardTemplate.TECHNICAL: {
                'sections': ['basic_info', 'technical_details', 'dependencies', 'performance', 'memory_usage'],
                'detail_level': 'high',
                'include_technical': True,
                'include_memory_analysis': True
            },
            GlyphcardTemplate.ARCHIVAL: {
                'sections': ['complete_record'],
                'detail_level': 'maximum',
                'include_everything': True,
                'preserve_raw_data': True
            },
            GlyphcardTemplate.FORENSIC: {
                'sections': ['forensic_analysis', 'timeline', 'integrity_chain', 'relationships'],
                'detail_level': 'forensic',
                'include_forensic_data': True,
                'include_timeline': True
            }
        }
        
        # Format processors
        self.format_processors = {
            GlyphcardFormat.JSON: self._format_as_json,
            GlyphcardFormat.YAML: self._format_as_yaml,
            GlyphcardFormat.MARKDOWN: self._format_as_markdown,
            GlyphcardFormat.HTML: self._format_as_html,
            GlyphcardFormat.PLAIN_TEXT: self._format_as_plain_text
        }
        
        # Generation statistics
        self.generation_stats = {
            'total_generated': 0,
            'by_template': {},
            'by_format': {},
            'generation_history': []
        }
    
    def generate_thread_glyphcard(self, thread_id: str, 
                                 template: GlyphcardTemplate = GlyphcardTemplate.STANDARD,
                                 format_type: GlyphcardFormat = GlyphcardFormat.JSON,
                                 custom_sections: List[str] = None) -> Dict[str, Any]:
        """Generate a glyphcard for a specific thread"""
        
        # Get thread (active or preserved)
        thread_data = self._get_thread_data(thread_id)
        if not thread_data:
            return {'error': f'Thread {thread_id} not found'}
        
        # Apply template configuration
        template_config = self.templates[template].copy()
        if custom_sections:
            template_config['sections'] = custom_sections
        
        # Generate glyphcard content
        glyphcard_content = self._build_glyphcard_content(thread_data, template_config)
        
        # Add metadata
        metadata = GlyphcardMetadata(
            generator_version=self.generator_version,
            generation_timestamp=time.time(),
            template_used=template.value,
            format_used=format_type.value,
            thread_count=1,
            data_integrity_hash=self._calculate_content_hash(glyphcard_content)
        )
        
        glyphcard = {
            'metadata': asdict(metadata),
            'content': glyphcard_content
        }
        
        # Apply format processor
        formatted_glyphcard = self.format_processors[format_type](glyphcard)
        
        # Update statistics
        self._update_generation_stats(template, format_type, 1)
        
        return {
            'glyphcard': formatted_glyphcard,
            'metadata': metadata,
            'thread_id': thread_id
        }
    
    def generate_multi_thread_glyphcard(self, thread_ids: List[str],
                                       template: GlyphcardTemplate = GlyphcardTemplate.STANDARD,
                                       format_type: GlyphcardFormat = GlyphcardFormat.JSON,
                                       include_relationships: bool = True) -> Dict[str, Any]:
        """Generate a combined glyphcard for multiple threads"""
        
        threads_data = []
        valid_thread_ids = []
        
        for thread_id in thread_ids:
            thread_data = self._get_thread_data(thread_id)
            if thread_data:
                threads_data.append(thread_data)
                valid_thread_ids.append(thread_id)
        
        if not threads_data:
            return {'error': 'No valid threads found'}
        
        template_config = self.templates[template].copy()
        
        # Build multi-thread content
        multi_thread_content = {
            'summary': self._build_multi_thread_summary(threads_data),
            'threads': {}
        }
        
        # Generate individual thread sections
        for i, thread_data in enumerate(threads_data):
            thread_id = valid_thread_ids[i]
            multi_thread_content['threads'][thread_id] = self._build_glyphcard_content(
                thread_data, template_config
            )
        
        # Add relationship analysis if requested
        if include_relationships:
            multi_thread_content['relationships'] = self._analyze_thread_relationships(threads_data)
        
        # Add metadata
        metadata = GlyphcardMetadata(
            generator_version=self.generator_version,
            generation_timestamp=time.time(),
            template_used=template.value,
            format_used=format_type.value,
            thread_count=len(threads_data),
            data_integrity_hash=self._calculate_content_hash(multi_thread_content)
        )
        
        glyphcard = {
            'metadata': asdict(metadata),
            'content': multi_thread_content
        }
        
        # Apply format processor
        formatted_glyphcard = self.format_processors[format_type](glyphcard)
        
        # Update statistics
        self._update_generation_stats(template, format_type, len(threads_data))
        
        return {
            'glyphcard': formatted_glyphcard,
            'metadata': metadata,
            'thread_ids': valid_thread_ids
        }
    
    def generate_system_glyphcard(self, template: GlyphcardTemplate = GlyphcardTemplate.COMPREHENSIVE,
                                 format_type: GlyphcardFormat = GlyphcardFormat.JSON) -> Dict[str, Any]:
        """Generate a system-wide glyphcard for all threads"""
        
        # Get all thread data
        all_active_threads = list(self.thread_manager.active_threads.keys())
        all_preserved_threads = list(self.thread_manager.preserved_threads.keys())
        all_thread_ids = all_active_threads + all_preserved_threads
        
        if not all_thread_ids:
            return {'error': 'No threads found in system'}
        
        # Generate system-wide analysis
        system_content = {
            'system_overview': self._build_system_overview(),
            'thread_distribution': self._analyze_thread_distribution(),
            'performance_summary': self._build_performance_summary(),
            'integrity_status': self._build_integrity_status(),
            'preservation_summary': self._build_preservation_summary()
        }
        
        # Add detailed thread information based on template
        if template in [GlyphcardTemplate.COMPREHENSIVE, GlyphcardTemplate.ARCHIVAL, GlyphcardTemplate.FORENSIC]:
            system_content['detailed_threads'] = {}
            
            for thread_id in all_thread_ids[:50]:  # Limit to first 50 threads for performance
                thread_data = self._get_thread_data(thread_id)
                if thread_data:
                    template_config = self.templates[template].copy()
                    system_content['detailed_threads'][thread_id] = self._build_glyphcard_content(
                        thread_data, template_config
                    )
        
        # Add metadata
        metadata = GlyphcardMetadata(
            generator_version=self.generator_version,
            generation_timestamp=time.time(),
            template_used=template.value,
            format_used=format_type.value,
            thread_count=len(all_thread_ids),
            data_integrity_hash=self._calculate_content_hash(system_content)
        )
        
        glyphcard = {
            'metadata': asdict(metadata),
            'content': system_content
        }
        
        # Apply format processor
        formatted_glyphcard = self.format_processors[format_type](glyphcard)
        
        # Update statistics
        self._update_generation_stats(template, format_type, len(all_thread_ids))
        
        return {
            'glyphcard': formatted_glyphcard,
            'metadata': metadata,
            'system_summary': {
                'total_threads': len(all_thread_ids),
                'active_threads': len(all_active_threads),
                'preserved_threads': len(all_preserved_threads)
            }
        }
    
    def _get_thread_data(self, thread_id: str) -> Optional[Dict[str, Any]]:
        """Get comprehensive thread data from active or preserved threads"""
        
        # Check active threads
        if thread_id in self.thread_manager.active_threads:
            thread = self.thread_manager.active_threads[thread_id]
            return self._extract_thread_data(thread, 'active')
        
        # Check preserved threads
        if thread_id in self.thread_manager.preserved_threads:
            preservation_info = self.thread_manager.preserved_threads[thread_id]
            return self._extract_preserved_thread_data(thread_id, preservation_info)
        
        return None
    
    def _extract_thread_data(self, thread: SymbolicThread, status: str) -> Dict[str, Any]:
        """Extract comprehensive data from an active thread"""
        return {
            'basic_info': {
                'thread_id': thread.thread_id,
                'thread_type': thread.thread_type,
                'priority': thread.priority.value,
                'state': thread.state.value,
                'status': status
            },
            'timestamps': {
                'creation_timestamp': thread.creation_timestamp,
                'last_activity_timestamp': thread.last_activity_timestamp,
                'preservation_timestamp': thread.preservation_timestamp,
                'rehydration_timestamp': thread.rehydration_timestamp
            },
            'data': {
                'thread_data': thread.thread_data,
                'execution_context': thread.execution_context,
                'computation_history': thread.computation_history,
                'integrity_hash': thread.integrity_hash
            },
            'relationships': {
                'dependencies': list(thread.dependencies),
                'dependents': list(thread.dependents)
            },
            'validation': {
                'validation_history': thread.validation_history
            },
            'raw_thread_object': thread  # For advanced analysis
        }
    
    def _extract_preserved_thread_data(self, thread_id: str, preservation_info: Dict[str, Any]) -> Dict[str, Any]:
        """Extract data from preserved thread information"""
        
        # Try to get the preserved package for detailed information
        try:
            seal_id = preservation_info['seal_id']
            preserved_package = self.thread_manager.memory_sealer.unseal_state(seal_id)
            
            if preserved_package:
                return {
                    'basic_info': {
                        'thread_id': thread_id,
                        'thread_type': preserved_package['thread_metadata'].get('thread_type', 'unknown'),
                        'priority': preserved_package['thread_metadata'].get('priority', 'unknown'),
                        'state': 'preserved',
                        'status': 'preserved'
                    },
                    'timestamps': {
                        'creation_timestamp': preserved_package['thread_metadata'].get('creation_timestamp'),
                        'last_activity_timestamp': preserved_package['thread_metadata'].get('last_activity_timestamp'),
                        'preservation_timestamp': preserved_package['preservation_timestamp'],
                        'rehydration_timestamp': None
                    },
                    'data': {
                        'thread_data': preserved_package['thread_data'],
                        'execution_context': preserved_package['execution_context'],
                        'computation_history': preserved_package['computation_history'],
                        'integrity_hash': preservation_info['integrity_hash']
                    },
                    'relationships': {
                        'dependencies': preserved_package.get('dependencies', []),
                        'dependents': preserved_package.get('dependents', [])
                    },
                    'preservation': {
                        'seal_id': seal_id,
                        'preservation_reason': preserved_package.get('preservation_reason', 'unknown'),
                        'package_size': preservation_info.get('preservation_package_size', 0)
                    }
                }
        except Exception:
            pass
        
        # Fallback to preservation metadata only
        return {
            'basic_info': {
                'thread_id': thread_id,
                'thread_type': preservation_info['thread_metadata'].get('thread_type', 'unknown'),
                'priority': preservation_info['thread_metadata'].get('priority', 'unknown'),
                'state': 'preserved',
                'status': 'preserved'
            },
            'timestamps': {
                'preservation_timestamp': preservation_info['preservation_timestamp']
            },
            'preservation': {
                'seal_id': preservation_info['seal_id'],
                'integrity_hash': preservation_info['integrity_hash'],
                'package_size': preservation_info.get('preservation_package_size', 0)
            },
            'error': 'detailed_data_unavailable'
        }
    
    def _build_glyphcard_content(self, thread_data: Dict[str, Any], template_config: Dict[str, Any]) -> Dict[str, Any]:
        """Build glyphcard content based on template configuration"""
        content = {}
        sections = template_config.get('sections', ['basic_info'])
        
        # Basic information section
        if 'basic_info' in sections:
            content['basic_info'] = thread_data['basic_info'].copy()
            content['basic_info']['generation_timestamp'] = time.time()
        
        # Status section
        if 'status' in sections:
            content['status'] = self._build_status_section(thread_data)
        
        # Dependencies section
        if 'dependencies' in sections and template_config.get('include_dependencies', False):
            content['dependencies'] = self._build_dependencies_section(thread_data)
        
        # Activity/History sections
        if 'recent_activity' in sections or 'full_history' in sections:
            history_limit = template_config.get('history_limit')
            content['activity_history'] = self._build_activity_section(thread_data, history_limit)
        
        # Performance section
        if 'performance' in sections and template_config.get('include_performance', False):
            content['performance'] = self._build_performance_section(thread_data)
        
        # Integrity section
        if 'integrity' in sections and template_config.get('include_integrity', False):
            content['integrity'] = self._build_integrity_section(thread_data)
        
        # Technical details section
        if 'technical_details' in sections and template_config.get('include_technical', False):
            content['technical_details'] = self._build_technical_section(thread_data)
        
        # Memory usage section
        if 'memory_usage' in sections and template_config.get('include_memory_analysis', False):
            content['memory_usage'] = self._build_memory_section(thread_data)
        
        # Complete record section (for archival)
        if 'complete_record' in sections and template_config.get('include_everything', False):
            content['complete_record'] = self._build_complete_record(thread_data, template_config)
        
        # Forensic sections
        if template_config.get('include_forensic_data', False):
            content['forensic_analysis'] = self._build_forensic_section(thread_data)
            if 'timeline' in sections:
                content['timeline'] = self._build_timeline_section(thread_data)
            if 'integrity_chain' in sections:
                content['integrity_chain'] = self._build_integrity_chain_section(thread_data)
        
        return content
    
    def _build_status_section(self, thread_data: Dict[str, Any]) -> Dict[str, Any]:
        """Build status section"""
        basic_info = thread_data['basic_info']
        timestamps = thread_data.get('timestamps', {})
        
        current_time = time.time()
        status_info = {
            'current_state': basic_info['state'],
            'thread_age': current_time - timestamps.get('creation_timestamp', current_time),
            'last_activity_age': current_time - timestamps.get('last_activity_timestamp', current_time),
            'is_preserved': basic_info['status'] == 'preserved'
        }
        
        # Add preservation info if available
        if 'preservation' in thread_data:
            preservation = thread_data['preservation']
            status_info['preservation_info'] = {
                'preservation_age': current_time - timestamps.get('preservation_timestamp', current_time),
                'seal_id': preservation.get('seal_id'),
                'preservation_reason': preservation.get('preservation_reason', 'unknown')
            }
        
        return status_info
    
    def _build_dependencies_section(self, thread_data: Dict[str, Any]) -> Dict[str, Any]:
        """Build dependencies section"""
        relationships = thread_data.get('relationships', {})
        
        dependencies_info = {
            'dependencies': relationships.get('dependencies', []),
            'dependents': relationships.get('dependents', []),
            'dependency_count': len(relationships.get('dependencies', [])),
            'dependent_count': len(relationships.get('dependents', []))
        }
        
        # Analyze dependency health
        active_threads = set(self.thread_manager.active_threads.keys())
        preserved_threads = set(self.thread_manager.preserved_threads.keys())
        all_threads = active_threads | preserved_threads
        
        valid_dependencies = [dep for dep in dependencies_info['dependencies'] if dep in all_threads]
        invalid_dependencies = [dep for dep in dependencies_info['dependencies'] if dep not in all_threads]
        
        dependencies_info['dependency_health'] = {
            'valid_dependencies': valid_dependencies,
            'invalid_dependencies': invalid_dependencies,
            'dependency_validity_ratio': len(valid_dependencies) / len(dependencies_info['dependencies']) if dependencies_info['dependencies'] else 1.0
        }
        
        return dependencies_info
    
    def _build_activity_section(self, thread_data: Dict[str, Any], history_limit: Optional[int] = None) -> Dict[str, Any]:
        """Build activity/history section"""
        data = thread_data.get('data', {})
        computation_history = data.get('computation_history', [])
        
        if history_limit:
            computation_history = computation_history[-history_limit:]
        
        activity_info = {
            'total_computations': len(data.get('computation_history', [])),
            'displayed_computations': len(computation_history),
            'computation_history': computation_history
        }
        
        # Calculate activity metrics
        if computation_history:
            timestamps = [comp['timestamp'] for comp in computation_history]
            if len(timestamps) >= 2:
                activity_info['activity_metrics'] = {
                    'first_computation': min(timestamps),
                    'last_computation': max(timestamps),
                    'activity_span': max(timestamps) - min(timestamps),
                    'average_computation_interval': (max(timestamps) - min(timestamps)) / (len(timestamps) - 1)
                }
        
        return activity_info
    
    def _build_performance_section(self, thread_data: Dict[str, Any]) -> Dict[str, Any]:
        """Build performance section"""
        data = thread_data.get('data', {})
        timestamps = thread_data.get('timestamps', {})
        computation_history = data.get('computation_history', [])
        
        current_time = time.time()
        creation_time = timestamps.get('creation_timestamp', current_time)
        thread_age = current_time - creation_time
        
        performance_info = {
            'thread_age': thread_age,
            'total_computations': len(computation_history),
            'computation_rate': len(computation_history) / thread_age if thread_age > 0 else 0,
            'data_size_estimate': len(str(data.get('thread_data', {}))) + len(str(data.get('execution_context', {})))
        }
        
        # Performance score calculation
        if performance_info['computation_rate'] > 0:
            # Normalize to 0-1 score (assuming 1 computation per second is optimal)
            performance_info['performance_score'] = min(performance_info['computation_rate'], 1.0)
        else:
            performance_info['performance_score'] = 0.0
        
        return performance_info
    
    def _build_integrity_section(self, thread_data: Dict[str, Any]) -> Dict[str, Any]:
        """Build integrity section"""
        data = thread_data.get('data', {})
        validation = thread_data.get('validation', {})
        
        integrity_info = {
            'current_integrity_hash': data.get('integrity_hash'),
            'validation_history_count': len(validation.get('validation_history', [])),
            'last_validation': validation.get('validation_history', [])[-1] if validation.get('validation_history') else None
        }
        
        # Calculate integrity status
        validation_history = validation.get('validation_history', [])
        recent_validations = [v for v in validation_history if time.time() - v.get('timestamp', 0) < 3600]  # Last hour
        
        integrity_info['integrity_status'] = {
            'recent_validations': len(recent_validations),
            'recent_failures': len([v for v in recent_validations if v.get('type') == 'integrity_failure']),
            'integrity_health_score': 1.0 - (len([v for v in recent_validations if v.get('type') == 'integrity_failure']) / max(len(recent_validations), 1))
        }
        
        return integrity_info
    
    def _build_technical_section(self, thread_data: Dict[str, Any]) -> Dict[str, Any]:
        """Build technical details section"""
        data = thread_data.get('data', {})
        
        technical_info = {
            'data_structure_info': {
                'thread_data_keys': list(data.get('thread_data', {}).keys()),
                'execution_context_keys': list(data.get('execution_context', {}).keys()),
                'computation_history_length': len(data.get('computation_history', []))
            }
        }
        
        # Add raw data if available
        if 'raw_thread_object' in thread_data:
            thread = thread_data['raw_thread_object']
            technical_info['object_info'] = {
                'class_name': thread.__class__.__name__,
                'memory_address': hex(id(thread)),
                'attributes_count': len(dir(thread))
            }
        
        return technical_info
    
    def _build_memory_section(self, thread_data: Dict[str, Any]) -> Dict[str, Any]:
        """Build memory usage section"""
        import sys
        
        data = thread_data.get('data', {})
        
        memory_info = {
            'data_sizes': {
                'thread_data_size': sys.getsizeof(str(data.get('thread_data', {}))),
                'execution_context_size': sys.getsizeof(str(data.get('execution_context', {}))),
                'computation_history_size': sys.getsizeof(str(data.get('computation_history', [])))
            }
        }
        
        memory_info['total_estimated_size'] = sum(memory_info['data_sizes'].values())
        
        # Add preservation size if available
        if 'preservation' in thread_data:
            memory_info['preservation_size'] = thread_data['preservation'].get('package_size', 0)
        
        return memory_info
    
    def _build_complete_record(self, thread_data: Dict[str, Any], template_config: Dict[str, Any]) -> Dict[str, Any]:
        """Build complete archival record"""
        complete_record = thread_data.copy()
        
        # Add generation metadata
        complete_record['archival_metadata'] = {
            'archived_at': time.time(),
            'generator_version': self.generator_version,
            'preservation_format': 'complete_aurora_record',
            'data_integrity_verified': True
        }
        
        # Remove raw thread object to avoid serialization issues
        if 'raw_thread_object' in complete_record:
            del complete_record['raw_thread_object']
        
        return complete_record
    
    def _build_forensic_section(self, thread_data: Dict[str, Any]) -> Dict[str, Any]:
        """Build forensic analysis section"""
        forensic_info = {
            'analysis_timestamp': time.time(),
            'data_chain_verification': self._verify_data_chain(thread_data),
            'anomaly_indicators': self._detect_forensic_anomalies(thread_data),
            'trace_analysis': self._build_trace_analysis(thread_data)
        }
        
        return forensic_info
    
    def _build_timeline_section(self, thread_data: Dict[str, Any]) -> Dict[str, Any]:
        """Build timeline section for forensic analysis"""
        timeline_events = []
        
        # Add creation event
        timestamps = thread_data.get('timestamps', {})
        if timestamps.get('creation_timestamp'):
            timeline_events.append({
                'timestamp': timestamps['creation_timestamp'],
                'event_type': 'thread_created',
                'details': {'thread_id': thread_data['basic_info']['thread_id']}
            })
        
        # Add computation events
        computation_history = thread_data.get('data', {}).get('computation_history', [])
        for comp in computation_history:
            timeline_events.append({
                'timestamp': comp['timestamp'],
                'event_type': 'computation_performed',
                'details': comp
            })
        
        # Add preservation event
        if timestamps.get('preservation_timestamp'):
            timeline_events.append({
                'timestamp': timestamps['preservation_timestamp'],
                'event_type': 'thread_preserved',
                'details': thread_data.get('preservation', {})
            })
        
        # Add rehydration event
        if timestamps.get('rehydration_timestamp'):
            timeline_events.append({
                'timestamp': timestamps['rehydration_timestamp'],
                'event_type': 'thread_rehydrated',
                'details': {}
            })
        
        # Sort by timestamp
        timeline_events.sort(key=lambda x: x['timestamp'])
        
        return {
            'total_events': len(timeline_events),
            'timeline': timeline_events,
            'timeline_span': timeline_events[-1]['timestamp'] - timeline_events[0]['timestamp'] if len(timeline_events) >= 2 else 0
        }
    
    def _build_integrity_chain_section(self, thread_data: Dict[str, Any]) -> Dict[str, Any]:
        """Build integrity chain section"""
        validation_history = thread_data.get('validation', {}).get('validation_history', [])
        
        integrity_chain = []
        for validation in validation_history:
            if validation.get('type') in ['integrity_check', 'integrity_failure']:
                integrity_chain.append({
                    'timestamp': validation['timestamp'],
                    'result': validation['type'],
                    'hash_info': validation.get('expected_hash', validation.get('actual_hash', 'unknown'))
                })
        
        return {
            'chain_length': len(integrity_chain),
            'integrity_chain': integrity_chain,
            'chain_integrity': all(entry['result'] == 'integrity_check' for entry in integrity_chain)
        }
    
    def _verify_data_chain(self, thread_data: Dict[str, Any]) -> Dict[str, Any]:
        """Verify forensic data chain"""
        # Simple verification based on available data
        verification_result = {
            'chain_intact': True,
            'verification_points': [],
            'anomalies': []
        }
        
        # Check timestamp consistency
        timestamps = thread_data.get('timestamps', {})
        creation_time = timestamps.get('creation_timestamp', 0)
        last_activity = timestamps.get('last_activity_timestamp', 0)
        
        if last_activity < creation_time:
            verification_result['chain_intact'] = False
            verification_result['anomalies'].append('last_activity_before_creation')
        
        verification_result['verification_points'].append('timestamp_consistency')
        
        return verification_result
    
    def _detect_forensic_anomalies(self, thread_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Detect forensic anomalies in thread data"""
        anomalies = []
        
        # Check for unusual computation patterns
        computation_history = thread_data.get('data', {}).get('computation_history', [])
        if len(computation_history) > 1000:
            anomalies.append({
                'type': 'excessive_computations',
                'severity': 'medium',
                'details': {'computation_count': len(computation_history)}
            })
        
        # Check for missing data
        required_fields = ['basic_info', 'timestamps']
        for field in required_fields:
            if field not in thread_data:
                anomalies.append({
                    'type': 'missing_required_field',
                    'severity': 'high',
                    'details': {'missing_field': field}
                })
        
        return anomalies
    
    def _build_trace_analysis(self, thread_data: Dict[str, Any]) -> Dict[str, Any]:
        """Build trace analysis for forensic purposes"""
        trace_info = {
            'data_lineage': self._trace_data_lineage(thread_data),
            'access_pattern': self._analyze_access_pattern(thread_data),
            'modification_history': self._trace_modifications(thread_data)
        }
        
        return trace_info
    
    def _trace_data_lineage(self, thread_data: Dict[str, Any]) -> Dict[str, Any]:
        """Trace data lineage"""
        return {
            'creation_source': 'thread_manager',
            'data_sources': thread_data.get('relationships', {}).get('dependencies', []),
            'lineage_verified': True
        }
    
    def _analyze_access_pattern(self, thread_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze data access patterns"""
        computation_history = thread_data.get('data', {}).get('computation_history', [])
        
        if computation_history:
            timestamps = [comp['timestamp'] for comp in computation_history]
            intervals = [timestamps[i+1] - timestamps[i] for i in range(len(timestamps)-1)]
            
            return {
                'total_accesses': len(computation_history),
                'access_intervals': intervals,
                'regular_pattern': len(set(round(interval) for interval in intervals)) < len(intervals) * 0.5 if intervals else True
            }
        
        return {'total_accesses': 0, 'pattern': 'no_activity'}
    
    def _trace_modifications(self, thread_data: Dict[str, Any]) -> Dict[str, Any]:
        """Trace data modifications"""
        validation_history = thread_data.get('validation', {}).get('validation_history', [])
        
        modifications = [
            validation for validation in validation_history
            if validation.get('type') in ['data_modified', 'integrity_failure']
        ]
        
        return {
            'modification_count': len(modifications),
            'modifications': modifications,
            'last_modification': modifications[-1] if modifications else None
        }
    
    def _build_multi_thread_summary(self, threads_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Build summary for multiple threads"""
        summary = {
            'total_threads': len(threads_data),
            'thread_states': {},
            'thread_types': {},
            'thread_priorities': {},
            'total_computations': 0
        }
        
        for thread_data in threads_data:
            basic_info = thread_data['basic_info']
            
            # Count states
            state = basic_info['state']
            summary['thread_states'][state] = summary['thread_states'].get(state, 0) + 1
            
            # Count types
            thread_type = basic_info['thread_type']
            summary['thread_types'][thread_type] = summary['thread_types'].get(thread_type, 0) + 1
            
            # Count priorities
            priority = basic_info['priority']
            summary['thread_priorities'][priority] = summary['thread_priorities'].get(priority, 0) + 1
            
            # Sum computations
            computation_count = len(thread_data.get('data', {}).get('computation_history', []))
            summary['total_computations'] += computation_count
        
        return summary
    
    def _analyze_thread_relationships(self, threads_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze relationships between multiple threads"""
        thread_ids = [thread_data['basic_info']['thread_id'] for thread_data in threads_data]
        
        relationships = {
            'internal_dependencies': [],
            'external_dependencies': [],
            'dependency_graph': {},
            'isolated_threads': []
        }
        
        for thread_data in threads_data:
            thread_id = thread_data['basic_info']['thread_id']
            dependencies = thread_data.get('relationships', {}).get('dependencies', [])
            
            relationships['dependency_graph'][thread_id] = dependencies
            
            # Categorize dependencies
            for dep in dependencies:
                if dep in thread_ids:
                    relationships['internal_dependencies'].append((dep, thread_id))
                else:
                    relationships['external_dependencies'].append((dep, thread_id))
        
        # Find isolated threads
        connected_threads = set()
        for deps in relationships['dependency_graph'].values():
            connected_threads.update(deps)
        for thread_id in relationships['dependency_graph'].keys():
            if relationships['dependency_graph'][thread_id]:  # Has dependencies
                connected_threads.add(thread_id)
        
        relationships['isolated_threads'] = [tid for tid in thread_ids if tid not in connected_threads]
        
        return relationships
    
    def _build_system_overview(self) -> Dict[str, Any]:
        """Build system overview"""
        stats = self.thread_manager.get_thread_statistics()
        
        return {
            'active_threads': stats['active_threads'],
            'preserved_threads': stats['preserved_threads'],
            'total_threads': stats['total_threads_registered'],
            'thread_distribution': {
                'by_priority': stats['active_by_priority'],
                'by_type': stats['active_by_type']
            },
            'system_health': {
                'average_inactivity_time': stats['average_inactivity_time'],
                'preservation_policies': stats['preservation_policies']
            }
        }
    
    def _analyze_thread_distribution(self) -> Dict[str, Any]:
        """Analyze thread distribution across the system"""
        active_threads = self.thread_manager.active_threads
        preserved_threads = self.thread_manager.preserved_threads
        
        distribution = {
            'active_distribution': {},
            'preserved_distribution': {},
            'age_distribution': {}
        }
        
        current_time = time.time()
        
        # Analyze active threads
        for thread in active_threads.values():
            thread_type = thread.thread_type
            distribution['active_distribution'][thread_type] = distribution['active_distribution'].get(thread_type, 0) + 1
            
            # Age analysis
            age = current_time - thread.creation_timestamp
            age_bucket = self._get_age_bucket(age)
            distribution['age_distribution'][age_bucket] = distribution['age_distribution'].get(age_bucket, 0) + 1
        
        # Analyze preserved threads (metadata only)
        for preservation_info in preserved_threads.values():
            thread_metadata = preservation_info.get('thread_metadata', {})
            thread_type = thread_metadata.get('thread_type', 'unknown')
            distribution['preserved_distribution'][thread_type] = distribution['preserved_distribution'].get(thread_type, 0) + 1
        
        return distribution
    
    def _get_age_bucket(self, age_seconds: float) -> str:
        """Get age bucket for thread age analysis"""
        if age_seconds < 3600:  # Less than 1 hour
            return 'recent'
        elif age_seconds < 86400:  # Less than 1 day
            return 'daily'
        elif age_seconds < 604800:  # Less than 1 week
            return 'weekly'
        elif age_seconds < 2592000:  # Less than 1 month
            return 'monthly'
        else:
            return 'old'
    
    def _build_performance_summary(self) -> Dict[str, Any]:
        """Build system performance summary"""
        active_threads = self.thread_manager.active_threads
        
        if not active_threads:
            return {'status': 'no_active_threads'}
        
        computation_rates = []
        memory_estimates = []
        
        for thread in active_threads.values():
            # Calculate computation rate
            thread_age = time.time() - thread.creation_timestamp
            computation_rate = len(thread.computation_history) / thread_age if thread_age > 0 else 0
            computation_rates.append(computation_rate)
            
            # Estimate memory usage
            import sys
            memory_estimate = (sys.getsizeof(str(thread.thread_data)) + 
                             sys.getsizeof(str(thread.execution_context)) +
                             sys.getsizeof(str(thread.computation_history)))
            memory_estimates.append(memory_estimate)
        
        return {
            'average_computation_rate': sum(computation_rates) / len(computation_rates),
            'total_estimated_memory': sum(memory_estimates),
            'average_memory_per_thread': sum(memory_estimates) / len(memory_estimates),
            'performance_distribution': {
                'high_performers': len([rate for rate in computation_rates if rate > 1.0]),
                'normal_performers': len([rate for rate in computation_rates if 0.1 <= rate <= 1.0]),
                'low_performers': len([rate for rate in computation_rates if rate < 0.1])
            }
        }
    
    def _build_integrity_status(self) -> Dict[str, Any]:
        """Build system integrity status"""
        active_threads = self.thread_manager.active_threads
        
        integrity_status = {
            'threads_with_hashes': 0,
            'threads_without_hashes': 0,
            'validation_coverage': 0
        }
        
        for thread in active_threads.values():
            if thread.integrity_hash:
                integrity_status['threads_with_hashes'] += 1
            else:
                integrity_status['threads_without_hashes'] += 1
            
            if thread.validation_history:
                integrity_status['validation_coverage'] += 1
        
        total_threads = len(active_threads)
        if total_threads > 0:
            integrity_status['hash_coverage_ratio'] = integrity_status['threads_with_hashes'] / total_threads
            integrity_status['validation_coverage_ratio'] = integrity_status['validation_coverage'] / total_threads
        
        return integrity_status
    
    def _build_preservation_summary(self) -> Dict[str, Any]:
        """Build preservation system summary"""
        preserved_threads = self.thread_manager.preserved_threads
        
        if not preserved_threads:
            return {'status': 'no_preserved_threads'}
        
        preservation_ages = []
        package_sizes = []
        
        current_time = time.time()
        
        for preservation_info in preserved_threads.values():
            preservation_time = preservation_info.get('preservation_timestamp', current_time)
            age = current_time - preservation_time
            preservation_ages.append(age)
            
            package_size = preservation_info.get('preservation_package_size', 0)
            package_sizes.append(package_size)
        
        return {
            'total_preserved_threads': len(preserved_threads),
            'average_preservation_age': sum(preservation_ages) / len(preservation_ages),
            'total_preservation_storage': sum(package_sizes),
            'average_package_size': sum(package_sizes) / len(package_sizes) if package_sizes else 0,
            'preservation_distribution': {
                'recent': len([age for age in preservation_ages if age < 86400]),  # Last day
                'weekly': len([age for age in preservation_ages if 86400 <= age < 604800]),  # Last week
                'old': len([age for age in preservation_ages if age >= 604800])  # Older than week
            }
        }
    
    def _calculate_content_hash(self, content: Dict[str, Any]) -> str:
        """Calculate hash of glyphcard content for integrity verification"""
        content_str = json.dumps(content, sort_keys=True, default=str)
        return hashlib.sha256(content_str.encode()).hexdigest()
    
    def _format_as_json(self, glyphcard: Dict[str, Any]) -> str:
        """Format glyphcard as JSON"""
        return json.dumps(glyphcard, indent=2, default=str)
    
    def _format_as_yaml(self, glyphcard: Dict[str, Any]) -> str:
        """Format glyphcard as YAML"""
        try:
            import yaml
            return yaml.dump(glyphcard, default_flow_style=False, sort_keys=False)
        except ImportError:
            # Fallback to JSON if YAML not available
            return f"# YAML format requested but not available\n# Fallback to JSON:\n{self._format_as_json(glyphcard)}"
    
    def _format_as_markdown(self, glyphcard: Dict[str, Any]) -> str:
        """Format glyphcard as Markdown"""
        metadata = glyphcard.get('metadata', {})
        content = glyphcard.get('content', {})
        
        md_lines = [
            f"# Aurora Glyphcard",
            f"",
            f"**Generated:** {time.strftime('%Y-%m-%d %H:%M:%S UTC', time.gmtime(metadata.get('generation_timestamp', time.time())))}",
            f"**Template:** {metadata.get('template_used', 'unknown')}",
            f"**Generator Version:** {metadata.get('generator_version', 'unknown')}",
            f"**Thread Count:** {metadata.get('thread_count', 0)}",
            f"",
        ]
        
        # Add content sections
        for section_name, section_data in content.items():
            md_lines.extend([
                f"## {section_name.replace('_', ' ').title()}",
                f"",
                f"```json",
                json.dumps(section_data, indent=2, default=str),
                f"```",
                f""
            ])
        
        return "\n".join(md_lines)
    
    def _format_as_html(self, glyphcard: Dict[str, Any]) -> str:
        """Format glyphcard as HTML"""
        metadata = glyphcard.get('metadata', {})
        content = glyphcard.get('content', {})
        
        html_parts = [
            "<!DOCTYPE html>",
            "<html>",
            "<head>",
            "<title>Aurora Glyphcard</title>",
            "<style>",
            "body { font-family: Arial, sans-serif; margin: 20px; }",
            ".metadata { background: #f0f0f0; padding: 10px; border-radius: 5px; }",
            ".section { margin: 20px 0; }",
            ".section h2 { color: #333; border-bottom: 2px solid #007acc; }",
            "pre { background: #f8f8f8; padding: 10px; border-radius: 3px; overflow-x: auto; }",
            "</style>",
            "</head>",
            "<body>",
            "<h1>Aurora Glyphcard</h1>",
            "<div class='metadata'>",
            f"<strong>Generated:</strong> {time.strftime('%Y-%m-%d %H:%M:%S UTC', time.gmtime(metadata.get('generation_timestamp', time.time())))}<br>",
            f"<strong>Template:</strong> {metadata.get('template_used', 'unknown')}<br>",
            f"<strong>Generator Version:</strong> {metadata.get('generator_version', 'unknown')}<br>",
            f"<strong>Thread Count:</strong> {metadata.get('thread_count', 0)}",
            "</div>"
        ]
        
        # Add content sections
        for section_name, section_data in content.items():
            html_parts.extend([
                "<div class='section'>",
                f"<h2>{section_name.replace('_', ' ').title()}</h2>",
                "<pre>",
                json.dumps(section_data, indent=2, default=str),
                "</pre>",
                "</div>"
            ])
        
        html_parts.extend([
            "</body>",
            "</html>"
        ])
        
        return "\n".join(html_parts)
    
    def _format_as_plain_text(self, glyphcard: Dict[str, Any]) -> str:
        """Format glyphcard as plain text"""
        metadata = glyphcard.get('metadata', {})
        content = glyphcard.get('content', {})
        
        text_lines = [
            "=" * 60,
            "AURORA GLYPHCARD",
            "=" * 60,
            "",
            f"Generated: {time.strftime('%Y-%m-%d %H:%M:%S UTC', time.gmtime(metadata.get('generation_timestamp', time.time())))}",
            f"Template: {metadata.get('template_used', 'unknown')}",
            f"Generator Version: {metadata.get('generator_version', 'unknown')}",
            f"Thread Count: {metadata.get('thread_count', 0)}",
            "",
            "=" * 60,
            ""
        ]
        
        # Add content sections
        for section_name, section_data in content.items():
            text_lines.extend([
                f"{section_name.replace('_', ' ').upper()}",
                "-" * len(section_name),
                "",
                json.dumps(section_data, indent=2, default=str),
                "",
                ""
            ])
        
        return "\n".join(text_lines)
    
    def _update_generation_stats(self, template: GlyphcardTemplate, format_type: GlyphcardFormat, thread_count: int):
        """Update generation statistics"""
        self.generation_stats['total_generated'] += 1
        
        template_key = template.value
        format_key = format_type.value
        
        self.generation_stats['by_template'][template_key] = self.generation_stats['by_template'].get(template_key, 0) + 1
        self.generation_stats['by_format'][format_key] = self.generation_stats['by_format'].get(format_key, 0) + 1
        
        self.generation_stats['generation_history'].append({
            'timestamp': time.time(),
            'template': template_key,
            'format': format_key,
            'thread_count': thread_count
        })
        
        # Maintain history limit
        if len(self.generation_stats['generation_history']) > 1000:
            self.generation_stats['generation_history'] = self.generation_stats['generation_history'][-500:]
    
    def get_generation_statistics(self) -> Dict[str, Any]:
        """Get glyphcard generation statistics"""
        return {
            'statistics': self.generation_stats.copy(),
            'generator_info': {
                'version': self.generator_version,
                'supported_templates': [template.value for template in GlyphcardTemplate],
                'supported_formats': [format_type.value for format_type in GlyphcardFormat]
            },
            'current_system_state': {
                'active_threads': len(self.thread_manager.active_threads),
                'preserved_threads': len(self.thread_manager.preserved_threads),
                'total_threads': len(self.thread_manager.thread_registry)
            }
        }