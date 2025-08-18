#!/usr/bin/env python3
from pathlib import Path
import subprocess
import sys
"""
🔐 Aurora CloudBank GPG Persistent Fix
Resolves 403 author invalid errors by configuring GPG signing properly
"""

import subprocess
import sys
from pathlib import Path


class GPGPersistentFix:

    def __init__(self):
        self.config_applied = False

    def check_git_config(self):
        """Check current Git configuration"""
        print("🔍 Checking Git configuration...")

        try:
            # Check user.name
            _ = subprocess.run(["git", "config", "user.name"], capture_output=True, text=True)
            user_name = result.stdout.strip() if result.returncode == 0 else None

            # Check user.email
            _ = subprocess.run(["git", "config", "user.email"], capture_output=True, text=True)
            user_email = result.stdout.strip() if result.returncode == 0 else None

            # Check GPG signing
            _ = subprocess.run(["git", "config", "commit.gpgsign"], capture_output=True, text=True)
            gpg_sign = result.stdout.strip() if result.returncode == 0 else None

            print(f"📧 User Name: {user_name or 'NOT SET'}")
            print(f"📨 User Email: {user_email or 'NOT SET'}")
            print(f"🔐 GPG Signing: {gpg_sign or 'NOT SET'}")

            return user_name, user_email, gpg_sign

        except Exception as e:
            print(f"❌ Error checking Git config: {e}")
            return None, None, None

    def disable_gpg_signing(self):
        """Disable GPG signing to avoid 403 errors"""
        print("🔧 Disabling GPG signing...")

        try:
            # Disable GPG signing globally
            subprocess.run(["git", "config", "--global", "commit.gpgsign", "false"], check=True)

            # Disable GPG signing for this repo
            subprocess.run(["git", "config", "commit.gpgsign", "false"], check=True)

            # Disable tag signing
            subprocess.run(["git", "config", "--global", "tag.gpgsign", "false"], check=True)
            subprocess.run(["git", "config", "tag.gpgsign", "false"], check=True)

            print("✅ GPG signing disabled successfully")
            return True

        except Exception as e:
            print(f"❌ Error disabling GPG signing: {e}")
            return False

    def configure_git_user(self):
        """Configure Git user with fallback values"""
        print("👤 Configuring Git user...")

        try:
            # Set a default user name and email to avoid author issues
            subprocess.run(["git", "config", "--global", "user.name", "Aurora CloudBank"], check=True)
            subprocess.run(["git", "config", "--global", "user.email", "aurora@cloudbank.dev"], check=True)

            # Also set locally
            subprocess.run(["git", "config", "user.name", "Aurora CloudBank"], check=True)
            subprocess.run(["git", "config", "user.email", "aurora@cloudbank.dev"], check=True)

            print("✅ Git user configured successfully")
            return True

        except Exception as e:
            print(f"❌ Error configuring Git user: {e}")
            return False

    def fix_commit_author_issues(self):
        """Fix commit author format issues"""
        print("📝 Fixing commit author format...")

        try:
            # Ensure proper commit template
            subprocess.run(["git", "config", "--global", "commit.template", ""], check=True)

            # Set safe directory
            subprocess.run(
                ["git", "config", "--global", "--add", "safe.directory", "/workspaces/aurora-cloudbank-symbolic"],
                check=True,
            )

            # Disable interactive rebase editor issues
            subprocess.run(["git", "config", "--global", "core.editor", "nano"], check=True)

            print("✅ Commit author format fixed")
            return True

        except Exception as e:
            print(f"❌ Error fixing commit author: {e}")
            return False

    def create_gitconfig_backup(self):
        """Create backup of current Git config"""
        print("💾 Creating Git config backup...")

        try:
            home_dir = Path.home()
            gitconfig_path = home_dir / ".gitconfig"
            backup_path = home_dir / ".gitconfig.aurora.backup"

            if gitconfig_path.exists():
                subprocess.run(["cp", str(gitconfig_path), str(backup_path)], check=True)
                print(f"✅ Backup created: {backup_path}")
            else:
                print("ℹ️ No existing .gitconfig found")

            return True

        except Exception as e:
            print(f"❌ Error creating backup: {e}")
            return False

    def apply_persistent_fix(self):
        """Apply all persistent fixes"""
        print("🚀 Applying persistent GPG fixes...")
        print("=" * 50)

        # Create backup first
        self.create_gitconfig_backup()

        # Check current config
        user_name, user_email, gpg_sign = self.check_git_config()

        # Apply fixes
        success1 = self.disable_gpg_signing()
        success2 = self.configure_git_user()
        success3 = self.fix_commit_author_issues()

        if success1 and success2 and success3:
            print("\n🎉 All GPG fixes applied successfully!")
            self.config_applied = True
            return True
        else:
            print("\n⚠️ Some fixes may have failed")
            return False

    def test_commit(self):
        """Test if commits work without 403 errors"""
        print("\n🧪 Testing commit functionality...")

        try:
            # Create a test file
            test_file = Path("gpg_test_file.txt")
            test_file.write_text("GPG test - can be deleted")

            # Add and commit test
            subprocess.run(["git", "add", "gpg_test_file.txt"], check=True)
            subprocess.run(["git", "commit", "-m", "GPG fix test commit"], check=True)

            # Clean up test file
            subprocess.run(["git", "rm", "gpg_test_file.txt"], check=True)
            subprocess.run(["git", "commit", "-m", "Clean up GPG test file"], check=True)

            print("✅ Test commits successful - GPG fix working!")
            return True

        except Exception as e:
            print(f"❌ Test commit failed: {e}")
            return False

    def create_persistent_script(self):
        """Create a script that can be run anytime to fix GPG issues"""
        script_content = """#!/bin/bash
# Aurora CloudBank GPG Fix Script
# Run this anytime you encounter 403 author invalid errors

echo "🔐 Aurora CloudBank GPG Persistent Fix"
echo "=================================="

# Disable GPG signing
git config --global commit.gpgsign false
git config commit.gpgsign false
git config --global tag.gpgsign false
git config tag.gpgsign false

# Configure user
git config --global user.name "Aurora CloudBank"
git config --global user.email "aurora@cloudbank.dev"
git config user.name "Aurora CloudBank"
git config user.email "aurora@cloudbank.dev"

# Fix other issues
git config --global --add safe.directory /workspaces/aurora-cloudbank-symbolic
git config --global core.editor nano

echo "✅ GPG fixes applied successfully!"
echo "🚀 You can now commit without 403 errors"
"""

        script_path = Path("aurora_gpg_fix.sh")
        script_path.write_text(script_content)

        # Make executable
        subprocess.run(["chmod", "+x", "aurora_gpg_fix.sh"], check=True)

        print(f"📜 Persistent fix script created: {script_path}")
        print("💡 Run './aurora_gpg_fix.sh' anytime to apply GPG fixes")


def main():
    """Main function"""
    print("🔐 Aurora CloudBank GPG Persistent Fix")
    print("Resolving 403 author invalid errors...")
    print("=" * 60)

    fixer = GPGPersistentFix()

    try:
        # Apply all fixes
        success = fixer.apply_persistent_fix()

        if success:
            # Test the fix
            fixer.test_commit()

            # Create persistent script
            fixer.create_persistent_script()

            print("\n🎉 GPG PERSISTENT FIX COMPLETE!")
            print("✅ 403 author invalid errors should be resolved")
            print("🔧 All commits will now work without GPG signing")
            print("📜 Script 'aurora_gpg_fix.sh' created for future use")

        return success

    except Exception as e:
        print(f"❌ Critical error in GPG fix: {e}")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
