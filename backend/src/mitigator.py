"""
Mitigation Engine
Suggests safe, reversible actions for detected regime shifts
"""

import numpy as np
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum
import yaml
import json

class SystemType(Enum):
    """Types of systems we can monitor."""
    ML_TRAINING = "ml_training"
    DATA_PIPELINE = "data_pipeline"
    SCIENTIFIC_SIM = "scientific_simulation"
    PRODUCTION_SERVICE = "production_service"
    COMPUTE_CLUSTER = "compute_cluster"

class RiskLevel(Enum):
    """Risk levels for mitigation actions."""
    LOW = "low"      # Safe, always reversible
    MEDIUM = "medium" # Some risk, mostly reversible
    HIGH = "high"    # Higher risk, may have side effects

@dataclass
class MitigationAction:
    """A suggested mitigation action."""
    id: str
    description: str
    command: str
    risk_level: RiskLevel
    confidence: float
    estimated_time: float  # seconds
    reversibility: float   # 0-1, 1 = fully reversible
    prerequisites: List[str]
    validation_checks: List[str]
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for serialization."""
        return {
            'id': self.id,
            'description': self.description,
            'command': self.command,
            'risk_level': self.risk_level.value,
            'confidence': self.confidence,
            'estimated_time': self.estimated_time,
            'reversibility': self.reversibility,
            'prerequisites': self.prerequisites,
            'validation_checks': self.validation_checks
        }

class MitigationEngine:
    """
    Engine that suggests safe mitigation actions for detected issues.
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize mitigation engine.
        
        Args:
            config_path: Path to configuration file
        """
        self.actions_db = self._load_actions_db()
        self.system_profiles = self._load_system_profiles()
        
        if config_path:
            self.config = self._load_config(config_path)
        else:
            self.config = self._default_config()
    
    def _load_actions_db(self) -> Dict[str, MitigationAction]:
        """Load predefined mitigation actions."""
        actions = [
            MitigationAction(
                id="reduce_learning_rate",
                description="Reduce learning rate by 50% to stabilize training",
                command="trainer.set_learning_rate(current_lr * 0.5)",
                risk_level=RiskLevel.LOW,
                confidence=0.8,
                estimated_time=30.0,
                reversibility=1.0,
                prerequisites=["training_in_progress", "has_learning_rate_control"],
                validation_checks=["new_lr > min_lr", "training_not_frozen"]
            ),
            MitigationAction(
                id="pause_training",
                description="Pause training to investigate instability",
                command="trainer.pause()",
                risk_level=RiskLevel.LOW,
                confidence=0.9,
                estimated_time=5.0,
                reversibility=1.0,
                prerequisites=["training_in_progress", "has_pause_capability"],
                validation_checks=["pause_supported", "checkpoint_exists"]
            ),
            MitigationAction(
                id="rollback_checkpoint",
                description="Rollback to last stable checkpoint",
                command="trainer.load_checkpoint('latest_stable.ckpt')",
                risk_level=RiskLevel.MEDIUM,
                confidence=0.7,
                estimated_time=120.0,
                reversibility=0.8,
                prerequisites=["checkpoints_exist", "has_rollback_capability"],
                validation_checks=["checkpoint_valid", "data_compatible"]
            ),
            MitigationAction(
                id="increase_batch_size",
                description="Increase batch size for stability",
                command="trainer.set_batch_size(current_batch * 2)",
                risk_level=RiskLevel.MEDIUM,
                confidence=0.6,
                estimated_time=60.0,
                reversibility=0.7,
                prerequisites=["memory_available", "has_batch_size_control"],
                validation_checks=["new_batch <= max_batch", "memory_sufficient"]
            ),
            MitigationAction(
                id="switch_optimizer",
                description="Switch to more stable optimizer (Adam -> SGD)",
                command="trainer.switch_optimizer('SGD', lr=0.01)",
                risk_level=RiskLevel.HIGH,
                confidence=0.5,
                estimated_time=300.0,
                reversibility=0.5,
                prerequisites=["optimizer_switching_supported"],
                validation_checks=["optimizer_available", "params_compatible"]
            ),
            MitigationAction(
                id="restart_service",
                description="Gracefully restart the service",
                command="systemctl restart service_name",
                risk_level=RiskLevel.MEDIUM,
                confidence=0.8,
                estimated_time=30.0,
                reversibility=0.9,
                prerequisites=["service_managed", "has_restart_permissions"],
                validation_checks=["service_exists", "dependencies_ready"]
            ),
            MitigationAction(
                id="scale_up_resources",
                description="Scale up compute resources",
                command="kubectl scale deployment --replicas=2",
                risk_level=RiskLevel.LOW,
                confidence=0.7,
                estimated_time=180.0,
                reversibility=1.0,
                prerequisites=["orchestration_available", "quota_available"],
                validation_checks=["resources_available", "scaling_supported"]
            ),
            MitigationAction(
                id="enable_safe_mode",
                description="Enable degraded but safe operating mode",
                command="system.enable_safe_mode()",
                risk_level=RiskLevel.LOW,
                confidence=0.9,
                estimated_time=10.0,
                reversibility=1.0,
                prerequisites=["safe_mode_implemented"],
                validation_checks=["safe_mode_available", "transition_safe"]
            )
        ]
        
        return {action.id: action for action in actions}
    
    def _load_system_profiles(self) -> Dict[str, List[str]]:
        """Load system type to action mappings."""
        return {
            SystemType.ML_TRAINING.value: [
                "reduce_learning_rate", "pause_training", "rollback_checkpoint",
                "increase_batch_size", "switch_optimizer"
            ],
            SystemType.DATA_PIPELINE.value: [
                "restart_service", "enable_safe_mode"
            ],
            SystemType.SCIENTIFIC_SIM.value: [
                "pause_training", "enable_safe_mode"
            ],
            SystemType.PRODUCTION_SERVICE.value: [
                "restart_service", "scale_up_resources", "enable_safe_mode"
            ],
            SystemType.COMPUTE_CLUSTER.value: [
                "scale_up_resources", "restart_service"
            ]
        }
    
    def _default_config(self) -> Dict:
        """Default configuration."""
        return {
            "max_actions_per_suggestion": 3,
            "min_confidence": 0.3,
            "risk_tolerance": "medium",  # low, medium, high
            "prefer_reversible": True,
            "require_prerequisites": True
        }
    
    def _load_config(self, config_path: str) -> Dict:
        """Load configuration from file."""
        try:
            with open(config_path, 'r') as f:
                return yaml.safe_load(f)
        except:
            return self._default_config()
    
    def suggest_actions(self, 
                       system_type: str,
                       issue_type: str,
                       severity: float,
                       context: Dict[str, Any],
                       available_actions: Optional[List[str]] = None) -> List[MitigationAction]:
        """
        Suggest mitigation actions for a detected issue.
        
        Args:
            system_type: Type of system (from SystemType)
            issue_type: Type of issue (e.g., "variance_spike", "memory_leak")
            severity: Severity score (0-1)
            context: Additional context about the system
            available_actions: List of action IDs that are available
            
        Returns:
            List of suggested actions, sorted by appropriateness
        """
        if available_actions is None:
            # Get default actions for system type
            if system_type in self.system_profiles:
                available_actions = self.system_profiles[system_type]
            else:
                available_actions = list(self.actions_db.keys())
        
        # Filter available actions
        candidate_actions = []
        for action_id in available_actions:
            if action_id in self.actions_db:
                action = self.actions_db[action_id]
                
                # Check risk tolerance
                risk_allowed = self._check_risk_tolerance(action.risk_level)
                
                # Check prerequisites if required
                prereqs_met = True
                if self.config.get("require_prerequisites", True):
                    prereqs_met = self._check_prerequisites(action, context)
                
                # Check minimum confidence
                confidence_ok = action.confidence >= self.config.get("min_confidence", 0.3)
                
                if risk_allowed and prereqs_met and confidence_ok:
                    # Adjust confidence based on issue type match
                    adjusted_confidence = self._adjust_confidence(
                        action, issue_type, severity, context
                    )
                    
                    if adjusted_confidence > 0:
                        candidate_actions.append((adjusted_confidence, action))
        
        # Sort by confidence and other factors
        candidate_actions.sort(key=lambda x: (
            -x[0],  # Higher confidence first
            x[1].risk_level.value if self.config.get("prefer_reversible", True) else "",
            x[1].estimated_time  # Faster actions preferred
        ))
        
        # Return top N actions
        max_actions = self.config.get("max_actions_per_suggestion", 3)
        return [action for _, action in candidate_actions[:max_actions]]
    
    def _check_risk_tolerance(self, risk_level: RiskLevel) -> bool:
        """Check if action's risk level is within tolerance."""
        tolerance = self.config.get("risk_tolerance", "medium")
        
        risk_values = {
            "low": [RiskLevel.LOW],
            "medium": [RiskLevel.LOW, RiskLevel.MEDIUM],
            "high": [RiskLevel.LOW, RiskLevel.MEDIUM, RiskLevel.HIGH]
        }
        
        return risk_level in risk_values.get(tolerance, [RiskLevel.LOW, RiskLevel.MEDIUM])
    
    def _check_prerequisites(self, action: MitigationAction, context: Dict) -> bool:
        """Check if action prerequisites are met."""
        # Simplified check - in reality would validate each prerequisite
        for prereq in action.prerequisites:
            if prereq not in context.get("capabilities", []):
                return False
        return True
    
    def _adjust_confidence(self, action: MitigationAction, 
                          issue_type: str, severity: float, 
                          context: Dict) -> float:
        """Adjust confidence based on context."""
        base_confidence = action.confidence
        
        # Issue-action matching heuristics
        issue_action_match = {
            "variance_spike": ["reduce_learning_rate", "pause_training"],
            "memory_leak": ["restart_service", "scale_up_resources"],
            "performance_degradation": ["scale_up_resources", "enable_safe_mode"],
            "training_instability": ["reduce_learning_rate", "rollback_checkpoint"],
            "service_unresponsive": ["restart_service", "enable_safe_mode"]
        }
        
        # Boost confidence for good matches
        if issue_type in issue_action_match:
            if action.id in issue_action_match[issue_type]:
                base_confidence *= 1.2
        
        # Adjust for severity
        if severity > 0.7:  # High severity
            # Prefer faster, safer actions
            if action.risk_level == RiskLevel.LOW and action.estimated_time < 60:
                base_confidence *= 1.1
            elif action.risk_level == RiskLevel.HIGH:
                base_confidence *= 0.7
        
        # Adjust for reversibility preference
        if self.config.get("prefer_reversible", True):
            base_confidence *= (0.5 + 0.5 * action.reversibility)
        
        return min(1.0, base_confidence)
    
    def generate_explanation(self, action: MitigationAction, 
                           issue_type: str, severity: float) -> str:
        """Generate human-readable explanation for action."""
        explanations = {
            "reduce_learning_rate": 
                f"High variance detected (severity: {severity:.1%}). Reducing learning rate can stabilize training by taking smaller steps.",
            "pause_training":
                f"Significant regime shift detected. Pausing to allow investigation before continuing.",
            "rollback_checkpoint":
                f"Model appears to have diverged. Rolling back to last known stable checkpoint.",
            "restart_service":
                f"Service showing degradation. Restarting to clear potential memory leaks or stuck states.",
            "scale_up_resources":
                f"Resource constraints detected. Scaling up to provide headroom.",
            "enable_safe_mode":
                f"Multiple warning signals detected. Switching to safe mode to prevent catastrophic failure."
        }
        
        if action.id in explanations:
            return explanations[action.id]
        
        return f"Suggested action '{action.description}' to address {issue_type} issue (severity: {severity:.1%})."
    
    def get_action_by_id(self, action_id: str) -> Optional[MitigationAction]:
        """Get action by ID."""
        return self.actions_db.get(action_id)
    
    def list_all_actions(self) -> List[MitigationAction]:
        """List all available actions."""
        return list(self.actions_db.values())

# Optional: AI-powered suggestion enhancer
class AISuggestionEnhancer:
    """Enhances suggestions with AI-generated insights."""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key
        self.enabled = api_key is not None
    
    def enhance_suggestion(self, action: MitigationAction, 
                          context: Dict) -> Dict:
        """
        Enhance suggestion with AI-generated insights.
        
        Note: This would typically call an external API.
        For hackathon, we simulate with rule-based responses.
        """
        if not self.enabled:
            return {
                "enhanced": False,
                "reasoning": "AI enhancement disabled",
                "alternative_actions": [],
                "risks": action.risk_level.value,
                "expected_impact": "unknown"
            }
        
        # Simulated AI response
        enhancements = {
            "reduce_learning_rate": {
                "reasoning": "Based on gradient noise analysis, learning rate appears too high for current loss landscape.",
                "alternative_actions": ["add_gradient_clipping", "increase_batch_size"],
                "risks": "Very low - learning rate changes are easily reversible",
                "expected_impact": "Training stability should improve within 100 steps"
            },
            "pause_training": {
                "reasoning": "Multiple early warning signals detected simultaneously.",
                "alternative_actions": ["reduce_learning_rate", "enable_debug_logging"],
                "risks": "Low - pause state is fully reversible",
                "expected_impact": "Allows manual inspection of training state"
            }
        }
        
        if action.id in enhancements:
            return {
                "enhanced": True,
                **enhancements[action.id]
            }
        
        # Default enhancement
        return {
            "enhanced": True,
            "reasoning": f"Action recommended based on {context.get('detection_method', 'statistical analysis')}",
            "alternative_actions": [],
            "risks": action.risk_level.value,
            "expected_impact": f"Should address {context.get('issue_type', 'detected issue')} within {action.estimated_time} seconds"
        }