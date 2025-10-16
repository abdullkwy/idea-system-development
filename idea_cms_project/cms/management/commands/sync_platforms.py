"""
Django management command لمزامنة بيانات المنصات الخارجية
يمكن تشغيله يدوياً أو عبر cron job
"""

from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone
from cms.integrations import IntegrationManager
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Sync data from external platforms (Meta Business, X Twitter)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--platform',
            type=str,
            choices=['meta_business', 'x_twitter', 'all'],
            default='all',
            help='Specify which platform to sync (default: all)'
        )
        
        parser.add_argument(
            '--test-only',
            action='store_true',
            help='Only test connections without syncing data'
        )
        
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force sync even if recent sync exists'
        )

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS(
                f'Starting platform sync at {timezone.now()}'
            )
        )
        
        try:
            integration_manager = IntegrationManager()
            
            if options['test_only']:
                self.test_connections(integration_manager, options['platform'])
            else:
                self.sync_data(integration_manager, options['platform'], options['force'])
                
        except Exception as e:
            logger.error(f"Platform sync failed: {e}")
            raise CommandError(f'Sync failed: {e}')

    def test_connections(self, integration_manager, platform):
        """اختبار الاتصالات فقط"""
        self.stdout.write('Testing platform connections...')
        
        if platform == 'all':
            results = integration_manager.test_all_connections()
        elif platform == 'meta_business':
            results = {'meta_business': integration_manager.meta_business.test_connection()}
        elif platform == 'x_twitter':
            results = {'x_twitter': integration_manager.x_twitter.test_connection()}
        
        for platform_name, result in results.items():
            if result['success']:
                self.stdout.write(
                    self.style.SUCCESS(
                        f'✓ {platform_name}: {result.get("message", "Connected")}'
                    )
                )
            else:
                self.stdout.write(
                    self.style.ERROR(
                        f'✗ {platform_name}: {result.get("error", "Connection failed")}'
                    )
                )

    def sync_data(self, integration_manager, platform, force):
        """مزامنة البيانات"""
        self.stdout.write('Starting data synchronization...')
        
        if platform == 'all':
            results = integration_manager.sync_all_data()
        elif platform == 'meta_business':
            results = {'meta_business': integration_manager.meta_business.sync_campaigns_data()}
        elif platform == 'x_twitter':
            results = {'x_twitter': integration_manager.x_twitter.sync_content_data()}
        
        total_synced = 0
        
        for platform_name, result in results.items():
            if result['success']:
                synced_count = result.get('synced_campaigns', 0) + result.get('synced_content', 0)
                total_synced += synced_count
                
                self.stdout.write(
                    self.style.SUCCESS(
                        f'✓ {platform_name}: {result.get("message", f"Synced {synced_count} items")}'
                    )
                )
            else:
                self.stdout.write(
                    self.style.ERROR(
                        f'✗ {platform_name}: {result.get("error", "Sync failed")}'
                    )
                )
        
        # إنشاء تقرير موحد
        if total_synced > 0:
            self.stdout.write('Generating unified report...')
            report_result = integration_manager.get_unified_report()
            
            if report_result['success']:
                report_data = report_result['data']
                self.stdout.write(
                    self.style.SUCCESS(
                        f'Report generated: {report_data["total_impressions"]} impressions, '
                        f'{report_data["total_clicks"]} clicks, '
                        f'{report_data["total_spend"]:.2f} spend'
                    )
                )
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Sync completed. Total items synced: {total_synced}'
            )
        )

