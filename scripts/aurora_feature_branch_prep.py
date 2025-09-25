#!/usr/bin/env python3
"""
🌿 Aurora Feature Branch Preparation Tool
📌 Anchor: T1-BRANCH-PREP-2025
🌱 Seed: EOS_SEED_ORION

Interactive tool for creating new feature branches with Aurora CloudBank conventions
"""

import subprocess
import sys
from datetime import datetime
import hashlib


class AuroraFeatureBranchPrep:
    def __init__(self):
        self.branch_types = {
            "feature": "New functionality or enhancement",
            "bugfix": "Bug fixes and corrections", 
            "hotfix": "Critical production fixes",
            "experiment": "Experimental features or proof-of-concepts",
            "refactor": "Code refactoring and optimization",
            "docs": "Documentation updates",
            "security": "Security improvements and fixes",
            "performance": "Performance optimizations",
            "integration": "Third-party integrations",
            "quantum": "Quantum computing enhancements"
        }
        
        self.symbolic_anchors = [
            "T1-FEATURE-2025",
            "T1-ENHANCEMENT-2025", 
            "T1-EXPERIMENT-2025",
            "T1-SECURITY-2025",
            "T1-PERFORMANCE-2025",
            "T1-INTEGRATION-2025",
            "T1-QUANTUM-2025"
        ]

    def get_current_status(self):
        """Check current repository status"""
        print("🔍 Checking current repository status...")
        
        # Check git status
        result = subprocess.run(["git", "status", "--porcelain"], 
                              capture_output=True, text=True)
        
        if result.stdout.strip():
            print("⚠️  Warning: Working directory has uncommitted changes:")
            print(result.stdout)
            return False
        
        # Check current branch
        result = subprocess.run(["git", "branch", "--show-current"], 
                              capture_output=True, text=True)
        current_branch = result.stdout.strip()
        
        # Check if up to date with origin
        result = subprocess.run(["git", "status", "-uno"], 
                              capture_output=True, text=True)
        
        print(f"✅ Current branch: {current_branch}")
        print(f"✅ Working directory: Clean")
        
        if "up to date" in result.stdout:
            print("✅ Branch is up to date with origin")
            return True
        else:
            print("⚠️  Branch may not be up to date with origin")
            return True

    def generate_branch_name(self, branch_type, description):
        """Generate Aurora-standard branch name"""
        # Clean description for branch name
        clean_desc = description.lower().replace(" ", "-").replace("_", "-")
        clean_desc = "".join(c for c in clean_desc if c.isalnum() or c == "-")
        
        # Generate timestamp suffix
        timestamp = datetime.now().strftime("%m%d")
        
        # Create hash for uniqueness
        hash_input = f"{branch_type}-{description}-{datetime.now().isoformat()}"
        branch_hash = hashlib.sha256(hash_input.encode()).hexdigest()[:6]
        
        branch_name = f"{branch_type}/{clean_desc}-{timestamp}-{branch_hash}"
        return branch_name

    def create_symbolic_anchor(self, branch_type, description):
        """Create symbolic anchor for the branch"""
        anchor_map = {
            "feature": "T1-FEATURE-2025",
            "bugfix": "T1-BUGFIX-2025",
            "hotfix": "T1-HOTFIX-2025", 
            "experiment": "T1-EXPERIMENT-2025",
            "refactor": "T1-REFACTOR-2025",
            "docs": "T1-DOCS-2025",
            "security": "T1-SECURITY-2025",
            "performance": "T1-PERFORMANCE-2025",
            "integration": "T1-INTEGRATION-2025",
            "quantum": "T1-QUANTUM-2025"
        }
        
        return anchor_map.get(branch_type, "T1-FEATURE-2025")

    def display_branch_menu(self):
        """Display interactive branch type menu"""
        print("\n🌿 Aurora Feature Branch Types:")
        print("=" * 50)
        
        for i, (key, desc) in enumerate(self.branch_types.items(), 1):
            print(f"{i:2}. {key:12} - {desc}")
        
        print("\n0. Custom branch type")
        
        while True:
            try:
                choice = input("\nSelect branch type (1-10, or 0 for custom): ").strip()
                
                if choice == "0":
                    custom_type = input("Enter custom branch type: ").strip().lower()
                    return custom_type, f"Custom branch type: {custom_type}"
                
                choice_num = int(choice)
                if 1 <= choice_num <= len(self.branch_types):
                    branch_types_list = list(self.branch_types.items())
                    branch_type, description = branch_types_list[choice_num - 1]
                    return branch_type, description
                else:
                    print("❌ Invalid choice. Please select 1-10 or 0.")
                    
            except ValueError:
                print("❌ Please enter a valid number.")

    def get_branch_description(self):
        """Get feature description from user"""
        print("\n📝 Enter feature/branch description:")
        description = input("Description: ").strip()
        
        if not description:
            print("❌ Description cannot be empty")
            return self.get_branch_description()
        
        return description

    def preview_branch_plan(self, branch_type, description, branch_name, anchor):
        """Show branch creation plan"""
        print("\n🎯 Branch Creation Plan:")
        print("=" * 50)
        print(f"Branch Type: {branch_type}")
        print(f"Description: {description}")
        print(f"Branch Name: {branch_name}")
        print(f"Symbolic Anchor: {anchor}")
        print(f"Base Branch: main")
        print(f"EOS Seed: EOS_SEED_ORION (continuity maintained)")
        
        confirm = input("\n✅ Create this branch? (y/N): ").strip().lower()
        return confirm in ['y', 'yes']

    def create_branch(self, branch_name):
        """Create and checkout the new branch"""
        print(f"\n🌿 Creating branch: {branch_name}")
        
        try:
            # Create and checkout new branch
            result = subprocess.run(["git", "checkout", "-b", branch_name], 
                                  capture_output=True, text=True, check=True)
            
            print(f"✅ Successfully created and switched to branch: {branch_name}")
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to create branch: {e.stderr}")
            return False

    def create_branch_readme(self, branch_type, description, branch_name, anchor):
        """Create branch-specific README"""
        readme_content = f"""# 🌿 Feature Branch: {branch_name}

## 📌 Branch Information

**Branch Type**: {branch_type}  
**Description**: {description}  
**Symbolic Anchor**: {anchor}  
**Base Branch**: main  
**Created**: {datetime.now().isoformat()}  

## 🌱 Symbolic Continuity

**EOS Seed**: EOS_SEED_ORION (maintained)  
**Thread Anchor**: {anchor}  
**Entropy State**: Monitored and sealed  

## 🎯 Objectives

- [ ] Complete feature implementation
- [ ] Add comprehensive tests
- [ ] Update documentation
- [ ] Ensure security compliance
- [ ] Maintain symbolic anchor continuity

## 🔧 Development Guidelines

1. **Commit Messages**: Use conventional commits with symbolic anchors
2. **Testing**: Ensure all tests pass before merging
3. **Security**: Run security scans and address issues
4. **Documentation**: Update relevant documentation
5. **Code Quality**: Maintain Aurora CloudBank standards

## 🔄 Merge Checklist

- [ ] All objectives completed
- [ ] Tests passing
- [ ] Security validation complete
- [ ] Documentation updated
- [ ] Code review approved
- [ ] Symbolic anchors sealed

## 🚀 Next Steps

1. Implement feature functionality
2. Add tests and documentation
3. Create pull request when ready
4. Ensure CI/CD pipeline passes

---

**Aurora CloudBank Symbolic System** | **Branch**: {branch_name} | **Anchor**: {anchor}
"""
        
        with open(f"BRANCH_README_{branch_name.replace('/', '_')}.md", "w") as f:
            f.write(readme_content)
        
        print(f"📋 Created branch README: BRANCH_README_{branch_name.replace('/', '_')}.md")

    def run(self):
        """Main execution flow"""
        print("🌿 Aurora Feature Branch Preparation Tool")
        print("📌 Anchor: T1-BRANCH-PREP-2025")
        print("🌱 Seed: EOS_SEED_ORION")
        print("=" * 60)
        
        # Check repository status
        if not self.get_current_status():
            print("❌ Please commit or stash changes before creating a new branch")
            sys.exit(1)
        
        # Get branch type
        branch_type, type_description = self.display_branch_menu()
        
        # Get description
        description = self.get_branch_description()
        
        # Generate branch name and anchor
        branch_name = self.generate_branch_name(branch_type, description)
        anchor = self.create_symbolic_anchor(branch_type, description)
        
        # Preview and confirm
        if not self.preview_branch_plan(branch_type, description, branch_name, anchor):
            print("❌ Branch creation cancelled")
            sys.exit(0)
        
        # Create branch
        if self.create_branch(branch_name):
            # Create branch documentation
            self.create_branch_readme(branch_type, description, branch_name, anchor)
            
            print(f"\n🎉 Feature branch '{branch_name}' ready for development!")
            print(f"📌 Symbolic anchor: {anchor}")
            print(f"🌱 EOS seed continuity: Maintained")
            print(f"\n🔄 Next: Start implementing your feature and commit with symbolic anchors")
        else:
            print("❌ Failed to create branch")
            sys.exit(1)


if __name__ == "__main__":
    prep_tool = AuroraFeatureBranchPrep()
    prep_tool.run()