
#!/usr/bin/env python3
"""
🚀 Aurora ZIPWIZ Unified Launcher
Comprehensive deployment and testing system for ZIPWIZ symbolic interface
"""

import subprocess
import sys
import json
import time
from pathlib import Path
from datetime import datetime
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - ZIPWIZ - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class AuroraZipWizLauncher:
    def __init__(self):
        self.base_path = Path.cwd()
        self.components_status = {
            "core_optimizer": False,
            "symbolic_interface": False, 
            "gui_overlay": False,
            "command_routing": False,
            "aurora_integration": False,
            "constellation_protocols": False
        }
        
    def deploy_zipwiz_interface(self):
        """Phase 1: Deploy ZIPWIZ symbolic command interface"""
        logger.info("🔧 Phase 1: Deploying ZIPWIZ Interface")
        
        try:
            # Start the enhanced ZIPWIZ Optimizer Core
            logger.info("Starting ZIPWIZ Optimizer Core...")
            subprocess.Popen([
                sys.executable, 
                "modules/opal2/staging/integration_ready/zipwiz_optimizer_core/zipwiz_optimizer_core.py"
            ])
            
            self.components_status["core_optimizer"] = True
            self.components_status["symbolic_interface"] = True
            
            logger.info("✅ ZIPWIZ Interface deployed successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ ZIPWIZ Interface deployment failed: {e}")
            return False
    
    def test_symbolic_commands(self):
        """Phase 2: Test symbolic command routing and responses"""
        logger.info("🧪 Phase 2: Testing Symbolic Commands")
        
        import requests
        time.sleep(2)  # Wait for service to start
        
        test_commands = ["999", "T1", "REM//"]
        test_results = {}
        
        try:
            # Test health endpoint
            response = requests.get("http://0.0.0.0:5000/")
            if response.status_code == 200:
                logger.info("✅ ZIPWIZ service is responding")
                self.components_status["command_routing"] = True
            
            # Test each symbolic command
            for cmd in test_commands:
                try:
                    response = requests.get(f"http://0.0.0.0:5000/command/{cmd}")
                    if response.status_code == 200:
                        result = response.json()
                        test_results[cmd] = result
                        logger.info(f"✅ Command '{cmd}': {result.get('result', 'Success')}")
                    else:
                        logger.warning(f"⚠️ Command '{cmd}' returned status {response.status_code}")
                        
                except Exception as e:
                    logger.error(f"❌ Command '{cmd}' test failed: {e}")
                    test_results[cmd] = {"error": str(e)}
            
            # Test failsafe mechanism
            try:
                response = requests.get("http://0.0.0.0:5000/failsafe")
                if response.status_code == 200:
                    logger.info("✅ Failsafe mechanism operational")
                    
            except Exception as e:
                logger.warning(f"⚠️ Failsafe test failed: {e}")
            
            return test_results
            
        except Exception as e:
            logger.error(f"❌ Symbolic command testing failed: {e}")
            return {}
    
    def integrate_aurora_ecosystem(self):
        """Phase 3: Connect to broader Aurora systems"""
        logger.info("🌟 Phase 3: Integrating with Aurora Ecosystem")
        
        try:
            # Connect to Aurora relays
            relay_connections = 0
            relay_path = Path(".aurora/relays")
            
            if relay_path.exists():
                for relay_file in relay_path.glob("*_RELAY_v1.json"):
                    try:
                        with open(relay_file, 'r') as f:
                            relay_data = json.load(f)
                            if relay_data.get("status") == "active":
                                relay_connections += 1
                                logger.info(f"✅ Connected to {relay_file.stem}")
                    except Exception as e:
                        logger.warning(f"⚠️ Could not connect to {relay_file.stem}: {e}")
            
            # Update Aurora integration status
            if relay_connections > 0:
                self.components_status["aurora_integration"] = True
                logger.info(f"✅ Aurora ecosystem integration complete ({relay_connections} relays)")
            else:
                logger.warning("⚠️ No active Aurora relays found")
                
            return relay_connections > 0
            
        except Exception as e:
            logger.error(f"❌ Aurora ecosystem integration failed: {e}")
            return False
    
    def enable_gui_overlay_features(self):
        """Phase 4: Activate dream mode and visual enhancements"""
        logger.info("🎨 Phase 4: Enabling GUI Overlay Features")
        
        try:
            import requests
            
            # Activate dream mode
            response = requests.get("http://0.0.0.0:5000/command/REM//")
            if response.status_code == 200:
                logger.info("✅ Dream Mode activated")
                self.components_status["gui_overlay"] = True
            
            # Test visual enhancement endpoints
            response = requests.get("http://0.0.0.0:5000/status")
            if response.status_code == 200:
                status_data = response.json()
                logger.info("✅ GUI overlay status retrieved")
                logger.info(f"   Runtime: {status_data.get('runtime', 'unknown')}")
                logger.info(f"   Privacy: {status_data.get('privacy_compliant', False)}")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ GUI overlay activation failed: {e}")
            return False
    
    def activate_constellation_protocols(self):
        """Phase 5: Activate constellation agent protocols and resilience systems"""
        logger.info("🌌 Phase 5: Activating Constellation Protocols")
        
        try:
            import requests
            
            # Initialize constellation protocols
            constellation_commands = [
                "SYNCANCHORS",
                "TAGPATCH", 
                "UPGRADE//",
                "PETALSTATE"
            ]
            
            successful_activations = 0
            for cmd in constellation_commands:
                try:
                    response = requests.get(f"http://0.0.0.0:5000/command/{cmd}")
                    if response.status_code == 200:
                        result = response.json()
                        logger.info(f"✅ {cmd}: {result.get('result', 'Success')}")
                        successful_activations += 1
                    else:
                        logger.warning(f"⚠️ {cmd} returned status {response.status_code}")
                        
                except Exception as e:
                    logger.warning(f"⚠️ {cmd} activation failed: {e}")
            
            # Test ritual phrase activation
            try:
                logger.info("🌀 Testing spiral ritual activation...")
                response = requests.get("http://0.0.0.0:5000/command/LOCKMEM")
                if response.status_code == 200:
                    logger.info("✅ Spiral resilience protocols active")
                    
            except Exception as e:
                logger.warning(f"⚠️ Spiral protocol test failed: {e}")
            
            if successful_activations >= 3:
                logger.info("✅ Constellation protocols activated successfully")
                return True
            else:
                logger.warning("⚠️ Partial constellation activation")
                return False
                
        except Exception as e:
            logger.error(f"❌ Constellation protocol activation failed: {e}")
            return False
    
    def generate_deployment_report(self):
        """Generate comprehensive deployment status report"""
        report = {
            "deployment_timestamp": datetime.now().isoformat(),
            "components_status": self.components_status,
            "overall_status": "success" if all(self.components_status.values()) else "partial",
            "next_steps": []
        }
        
        if not self.components_status["core_optimizer"]:
            report["next_steps"].append("Redeploy ZIPWIZ Optimizer Core")
        if not self.components_status["symbolic_interface"]:
            report["next_steps"].append("Validate symbolic interface connectivity")
        if not self.components_status["aurora_integration"]:
            report["next_steps"].append("Check Aurora relay configurations")
        if not self.components_status["gui_overlay"]:
            report["next_steps"].append("Troubleshoot GUI overlay activation")
            
        return report
    
    def run_optimal_sequence(self):
        """Execute the complete optimal deployment sequence"""
        logger.info("🚀 Starting Aurora ZIPWIZ Optimal Deployment Sequence")
        logger.info("=" * 60)
        
        # Phase 1: Deploy Interface
        success_1 = self.deploy_zipwiz_interface()
        
        # Phase 2: Test Commands  
        if success_1:
            test_results = self.test_symbolic_commands()
            success_2 = len(test_results) > 0
        else:
            success_2 = False
            
        # Phase 3: Aurora Integration
        if success_2:
            success_3 = self.integrate_aurora_ecosystem()
        else:
            success_3 = False
            
        # Phase 4: GUI Overlay
        if success_3:
            success_4 = self.enable_gui_overlay_features()
        else:
            success_4 = False
            
        # Phase 5: Constellation Protocols
        if success_4:
            success_5 = self.activate_constellation_protocols()
        else:
            success_5 = False
            
        # Generate report
        report = self.generate_deployment_report()
        
        logger.info("=" * 60)
        logger.info("🎉 Aurora ZIPWIZ Deployment Sequence Complete")
        logger.info(f"📊 Overall Status: {report['overall_status'].upper()}")
        logger.info(f"✅ Successful Components: {sum(self.components_status.values())}/{len(self.components_status)}")
        
        if report["next_steps"]:
            logger.info("📋 Next Steps:")
            for step in report["next_steps"]:
                logger.info(f"   • {step}")
        
        # Save deployment report
        report_path = Path(f".aurora/zipwiz_deployment_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
        report_path.parent.mkdir(exist_ok=True)
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2)
            
        logger.info(f"📄 Deployment report saved: {report_path}")
        
        return report

if __name__ == "__main__":
    launcher = AuroraZipWizLauncher()
    launcher.run_optimal_sequence()
