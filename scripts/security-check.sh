#!/bin/bash

# Script to check for potentially sensitive files before committing

echo "🔍 Checking for potentially sensitive files..."

# Check for image files that might be personal documents
echo "Checking for personal document images..."
find . -type f \( -name "*passport*" -o -name "*license*" -o -name "*id_card*" \) \( -name "*.jpg" -o -name "*.jpeg" -o -name "*.png" \) | grep -v "test-data" | grep -v "sample-data"

# Check for files with potentially real personal data patterns
echo "Checking for files with potential real personal data..."
grep -r --include="*.txt" --include="*.md" --include="*.json" -l '\b[A-Z][a-z]+ [A-Z][a-z]+\b.*\b(19|20)[0-9][0-9]' . 2>/dev/null | while read file; do
    # Skip test and sample files
    if [[ "$file" != *"test"* ]] && [[ "$file" != *"sample"* ]] && [[ "$file" != *".git"* ]]; then
        echo "⚠️  Potential personal data found in: $file"
        echo "   Please review this file to ensure it contains only fictional test data"
    fi
done

# Check for large image files that might be real documents
echo "Checking for large image files..."
find . -type f \( -name "*.jpg" -o -name "*.jpeg" -o -name "*.png" \) -size +500k | grep -v "test-data" | grep -v "sample-data" | while read file; do
    echo "⚠️  Large image file found: $file ($(du -h "$file" | cut -f1))"
    echo "   Please verify this is not a real personal document"
done

echo "✅ Security check complete. Review any warnings above before committing."
