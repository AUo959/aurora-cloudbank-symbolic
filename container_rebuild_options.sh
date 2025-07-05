#!/bin/bash

# 🔧 AURORA CLOUDBANK - CONTAINER REBUILD OPTIONS
# Multiple rebuild strategies for different scenarios

echo "🔧 AURORA CLOUDBANK - CONTAINER REBUILD OPTIONS"
echo "==============================================="

# Function to print status
print_status() {
    if [ $1 -eq 0 ]; then
        echo "✅ $2"
    else
        echo "❌ $2 (Exit code: $1)"
    fi
}

echo ""
echo "📋 Available Rebuild Options:"
echo "============================="
echo ""
echo "1. 🔄 SOFT REBUILD (Recommended)"
echo "   - Reinstall dependencies"
echo "   - Refresh environment"
echo "   - Preserve all data"
echo "   - Quick and safe"
echo ""
echo "2. 🔥 HARD REBUILD"
echo "   - Full container recreation"
echo "   - Clean environment"
echo "   - Requires VS Code restart"
echo "   - Use if soft rebuild fails"
echo ""
echo "3. 📦 DEPENDENCY REFRESH"
echo "   - Only update packages"
echo "   - Fastest option"
echo "   - Good for package issues"
echo ""
echo "4. 🔧 CUSTOM REBUILD"
echo "   - Manual step-by-step"
echo "   - For specific issues"
echo "   - Full control"
echo ""

read -p "Choose rebuild option (1-4): " REBUILD_OPTION

case $REBUILD_OPTION in
    1)
        echo ""
        echo "🔄 SOFT REBUILD SELECTED"
        echo "========================"
        echo "This will:"
        echo "• Reinstall npm packages"
        echo "• Reinstall Python packages"
        echo "• Refresh environment variables"
        echo "• Preserve all your work"
        echo ""
        read -p "Continue with soft rebuild? (y/n): " CONFIRM
        if [ "$CONFIRM" = "y" ]; then
            echo "🔄 Starting soft rebuild..."
            
            # Clean npm cache and reinstall
            echo "📦 Cleaning npm cache..."
            npm cache clean --force
            print_status $? "npm cache cleaned"
            
            echo "📦 Reinstalling npm packages..."
            rm -rf node_modules package-lock.json
            npm install
            print_status $? "npm packages reinstalled"
            
            # Reinstall Python packages
            echo "🐍 Reinstalling Python packages..."
            pip install --upgrade pip
            pip install -r requirements.txt --upgrade --force-reinstall
            print_status $? "Python packages reinstalled"
            
            # Refresh environment
            echo "🔄 Refreshing environment..."
            source ~/.bashrc 2>/dev/null || true
            export GPG_TTY=$(tty)
            print_status $? "Environment refreshed"
            
            echo "✅ Soft rebuild complete!"
        else
            echo "❌ Soft rebuild cancelled"
        fi
        ;;
    2)
        echo ""
        echo "🔥 HARD REBUILD SELECTED"
        echo "========================"
        echo "⚠️  WARNING: This will recreate the entire container!"
        echo "• All running processes will be stopped"
        echo "• VS Code will need to be restarted"
        echo "• Your workspace files will be preserved"
        echo "• Container will be rebuilt from scratch"
        echo ""
        read -p "Are you sure you want to hard rebuild? (y/n): " CONFIRM
        if [ "$CONFIRM" = "y" ]; then
            echo "🔥 Hard rebuild requires VS Code restart..."
            echo ""
            echo "📋 Hard Rebuild Instructions:"
            echo "1. Save all your work"
            echo "2. Close VS Code"
            echo "3. Reopen VS Code"
            echo "4. Select 'Rebuild Container' when prompted"
            echo "5. Or use Command Palette: 'Dev Containers: Rebuild Container'"
            echo ""
            echo "💡 VS Code Command Palette shortcuts:"
            echo "• Ctrl+Shift+P (Windows/Linux) or Cmd+Shift+P (Mac)"
            echo "• Type: 'Dev Containers: Rebuild Container'"
            echo "• Select 'Rebuild Without Cache' for complete rebuild"
        else
            echo "❌ Hard rebuild cancelled"
        fi
        ;;
    3)
        echo ""
        echo "📦 DEPENDENCY REFRESH SELECTED"
        echo "=============================="
        echo "This will only update packages without changing the container"
        echo ""
        read -p "Continue with dependency refresh? (y/n): " CONFIRM
        if [ "$CONFIRM" = "y" ]; then
            echo "📦 Refreshing dependencies..."
            
            # Update npm packages
            if [ -f "package.json" ]; then
                echo "📦 Updating npm packages..."
                npm update
                print_status $? "npm packages updated"
            fi
            
            # Update Python packages
            if [ -f "requirements.txt" ]; then
                echo "🐍 Updating Python packages..."
                pip install -r requirements.txt --upgrade
                print_status $? "Python packages updated"
            fi
            
            echo "✅ Dependency refresh complete!"
        else
            echo "❌ Dependency refresh cancelled"
        fi
        ;;
    4)
        echo ""
        echo "🔧 CUSTOM REBUILD SELECTED"
        echo "=========================="
        echo "Available custom options:"
        echo ""
        echo "a) Clean node_modules only"
        echo "b) Reset Python environment"
        echo "c) Reset Git configuration"
        echo "d) Clean all caches"
        echo "e) Reinstall specific package"
        echo "f) Run diagnostics only"
        echo ""
        read -p "Choose custom option (a-f): " CUSTOM_OPTION
        
        case $CUSTOM_OPTION in
            a)
                echo "🧹 Cleaning node_modules..."
                rm -rf node_modules package-lock.json
                npm install
                print_status $? "node_modules cleaned and reinstalled"
                ;;
            b)
                echo "🐍 Resetting Python environment..."
                pip install --upgrade pip
                pip install -r requirements.txt --force-reinstall
                print_status $? "Python environment reset"
                ;;
            c)
                echo "🔧 Git configuration reset available"
                echo "Run './setup_gpg_signing.sh' to reconfigure Git/GPG"
                ;;
            d)
                echo "🧹 Cleaning all caches..."
                npm cache clean --force
                pip cache purge
                print_status $? "All caches cleaned"
                ;;
            e)
                read -p "Enter package name to reinstall: " PACKAGE_NAME
                if [ -n "$PACKAGE_NAME" ]; then
                    npm install "$PACKAGE_NAME" --force
                    print_status $? "Package $PACKAGE_NAME reinstalled"
                fi
                ;;
            f)
                echo "🔍 Running diagnostics..."
                ./container_rebuild_analysis.sh
                ;;
            *)
                echo "❌ Invalid custom option"
                ;;
        esac
        ;;
    *)
        echo "❌ Invalid option selected"
        ;;
esac

echo ""
echo "🎯 REBUILD OPERATION SUMMARY"
echo "============================"
echo "📅 Completed: $(date)"
echo "🔧 Option used: $REBUILD_OPTION"
echo ""
echo "💡 Next steps:"
echo "• Test your Aurora CloudBank applications"
echo "• Run: git status (to check repository state)"
echo "• Run: ./container_rebuild_analysis.sh (for full diagnostics)"
echo ""
echo "🚀 Aurora CloudBank container rebuild process complete!"
