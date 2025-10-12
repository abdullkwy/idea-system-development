#!/bin/bash

# قائمة الملفات المراد تحديثها
files=(
    "blog-post-1.html"
    "blog.html"
    "clients.html"
    "consultancy.html"
    "contact.html"
    "creative-solutions.html"
    "featured-works.html"
    "index.html"
    "logo-design.html"
    "marketing-solutions.html"
    "partners.html"
    "portfolio.html"
    "team.html"
    "technical-solutions.html"
)

# التحديثات المطلوبة
declare -A replacements=(
    ["خدماتنا"]="حلولنا"
    ["خدماتكم"]="حلولكم"
    ["خدمات تسويقية"]="حلول تسويقية"
    ["خدمات إبداعية"]="حلول إبداعية"
    ["خدمات تقنية"]="حلول تقنية"
    ["خدمات متكاملة"]="حلول متكاملة"
    ["خدمات متابعة"]="حلول متابعة"
    ["خدمات الدعم"]="حلول الدعم"
    ["خدمة متخصصة"]="حل متخصص"
    ["خدمة العملاء"]="خدمة العملاء"  # هذه تبقى كما هي
    ["الخدمات التسويقية"]="الحلول التسويقية"
    ["الخدمات الإبداعية"]="الحلول الإبداعية"
    ["الخدمات التقنية"]="الحلول التقنية"
)

# تطبيق التحديثات على كل ملف
for file in "${files[@]}"; do
    if [ -f "$file" ]; then
        echo "تحديث الملف: $file"
        for old in "${!replacements[@]}"; do
            new="${replacements[$old]}"
            sed -i "s/$old/$new/g" "$file"
        done
    fi
done

echo "تم الانتهاء من التحديثات"
