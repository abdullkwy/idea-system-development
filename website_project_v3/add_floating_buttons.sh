#!/bin/bash

# قائمة الصفحات التي تحتاج إلى أزرار عائمة
pages=(
    "about.html"
    "blog-post-1.html"
    "blog.html"
    "clients.html"
    "consultancy.html"
    "contact.html"
    "creative-solutions.html"
    "featured-works.html"
    "logo-design.html"
    "marketing-solutions.html"
    "partners.html"
    "portfolio.html"
    "team.html"
    "technical-solutions.html"
)

# الكود المراد إضافته
floating_buttons='    <!-- أزرار الدعوة للعمل العائمة -->
    <div class="cta-floating">
        <a href="consultancy.html" class="cta-floating-btn">
            <i class="fas fa-headset"></i>
            <span class="cta-floating-tooltip">طلب استشارة مجانية</span>
        </a>
        <a href="services-request.html" class="cta-floating-btn">
            <i class="fas fa-shopping-cart"></i>
            <span class="cta-floating-tooltip">طلب الحلول</span>
        </a>
    </div>'

# إضافة الأزرار لكل صفحة
for page in "${pages[@]}"; do
    if [ -f "$page" ]; then
        echo "إضافة الأزرار العائمة إلى: $page"
        # البحث عن زر scroll-top وإضافة الأزرار العائمة بعده
        if grep -q "scroll-top" "$page"; then
            # إضافة الأزرار بعد زر scroll-top
            sed -i '/scroll-top/,/<\/a>/{
                /<\/a>/a\
\
'"$floating_buttons"'
            }' "$page"
        else
            # إضافة الأزرار قبل إغلاق body
            sed -i '/<\/body>/i\
\
'"$floating_buttons"'
' "$page"
        fi
    fi
done

echo "تم الانتهاء من إضافة الأزرار العائمة"
