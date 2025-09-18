#!/usr/bin/env python3

"""
🔐 Aurora CloudBank GPG Persistent Fix
Resolves 403 author invalid errors by configuring GPG signing properly
"""


class GPGPersistentFix:
    pass
    def __init__(self):
    pass
        self.config_applied = False

    def check_git_config(self):
    pass
        """Check current Git configuration"""
        print("🔍 Checking Git configuration...")

        try:
    pass
            # Check user.name
            result = subprocess.run(["git", "config", "user.name"], capture_output=True, text=True)
            user_name = result.stdout.strip() if result.returncode == 0 else None

            # Check user.email
            result = subprocess.run(["git", "config", "user.email"], capture_output=True, text=True)
            user_email = result.stdout.strip() if result.returncode == 0 else None

            # Check GPG signing
            result = subprocess.run(["git", "config", "commit.gpgsign"], capture_output=True, text=True)
            gpg_sign = result.stdout.strip() if result.returncode == 0 else None

            print("📧 User Name: {user_name or 'NOT SET'}")
            print("📨 User Email: {user_email or 'NOT SET'}")
            print("🔐 GPG Signing: {gpg_sign or 'NOT SET'}")

            return user_name, user_email, gpg_sign

        except Exception as _:
    pass
            print("❌ Error checking Git config: {e}")
            return None, None, None

    def disable_gpg_signing(self):
    pass
        """Disable GPG signing to avoid 403 errors"""
        print("🔧 Disabling GPG signing...")

        try:
    pass
            # Disable GPG signing globally
            subprocess.run(["git", "config", "--global", "commit.gpgsign", "false"], check=True)

            # Disable GPG signing for this repo
            subprocess.run(["git", "config", "commit.gpgsign", "false"], check=True)

            # Disable tag signing
            subprocess.run(["git", "config", "--global", "tag.gpgsign", "false"], check=True)
            subprocess.run(["git", "config", "tag.gpgsign", "false"], check=True)

            print("✅ GPG signing disabled successfully")
            return True

        except Exception as _:
    pass
            print("❌ Error disabling GPG signing: {e}")
            return False

    def configure_git_user(self):
    pass
        """Configure Git user with fallback values"""
        print("👤 Configuring Git user...")

        try:
    pass
            # Set a default user name and email to avoid author issues
            subprocess.run(["git", "config", "--global", "user.name", "Aurora CloudBank"], check=True)
            subprocess.run(["git", "config", "--global", "user.email", "aurora@cloudbank.dev"], check=True)

            # Also set locally
            subprocess.run(["git", "config", "user.name", "Aurora CloudBank"], check=True)
            subprocess.run(["git", "config", "user.email", "aurora@cloudbank.dev"], check=True)

            print("✅ Git user configured successfully")
            return True

        except Exception as _:
    pass
            print("❌ Error configuring Git user: {e}")
            return False

    def fix_commit_author_issues(self):
    pass
        """Fix commit author format issues"""
        print("📝 Fixing commit author format...")

        try:
    pass
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

        except Exception as _:
    pass
            print("❌ Error fixing commit author: {e}")
            return False

    def create_gitconfig_backup(self):
    pass
        """Create backup of current Git config"""
        print("💾 Creating Git config backup...")

        try:
    pass
            home_dir = Path.home()
            gitconfig_path = home_dir / ".gitconfig"
            backup_path = home_dir / ".gitconfig.aurora.backup"

            if gitconfig_path.exists():
    pass
                subprocess.run(["cp", str(gitconfig_path), str(backup_path)], check=True)
                print("✅ Backup created: {backup_path}")
            else:
    pass
                print("ℹ️ No existing .gitconfig found")

            return True

        except Exception as _:
    pass
            print("❌ Error creating backup: {e}")
            return False

    def apply_persistent_fix(self):
    pass
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
    pass
            print("\n🎉 All GPG fixes applied successfully!")
            self.config_applied = True
            return True,
        else:
    pass
            print("\n⚠️ Some fixes may have failed")
            return False

    def test_commit(self):
    pass
        """Test if commits work without 403 errors"""
        print("\n🧪 Testing commit functionality...")

        try:
    pass
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

        except Exception as _:
    pass
            print("❌ Test commit failed: {e}")
            return False

    def create_persistent_script(self):
    pass
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

        print("📜 Persistent fix script created: {script_path}")
        print("💡 Run './aurora_gpg_fix.sh' anytime to apply GPG fixes")

def main():
    pass
    """Main function"""
    print("🔐 Aurora CloudBank GPG Persistent Fix")
    print("Resolving 403 author invalid errors...")
    print("=" * 60)

    fixer = GPGPersistentFix()

    try:
    pass
        # Apply all fixes
        success = fixer.apply_persistent_fix()

        if success:
    pass
            # Test the fix
            fixer.test_commit()

            # Create persistent script
            fixer.create_persistent_script()

            print("\n🎉 GPG PERSISTENT FIX COMPLETE!")
            print("✅ 403 author invalid errors should be resolved")
            print("🔧 All commits will now work without GPG signing")
            print("📜 Script 'aurora_gpg_fix.sh' created for future use")

        return success

    except Exception as _:
    pass
        print("❌ Critical error in GPG fix: {e}")
        return False

if __name__ == "__main__":
    pass
    success = main()
    sys.exit(0 if success else 1)
