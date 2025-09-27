
from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone
from adminapp.models import WhatsAppCatalogue
from adminapp.scraper import scrape_whatsapp_catalogue
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Scrape WhatsApp catalogues for product data'

    def add_arguments(self, parser):
        parser.add_argument(
            '--catalogue-id',
            type=str,
            help='Scrape a specific catalogue by ID',
        )
        parser.add_argument(
            '--all',
            action='store_true',
            help='Scrape all active catalogues',
        )
        parser.add_argument(
            '--due',
            action='store_true',
            help='Scrape catalogues that are due for scraping based on frequency',
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force scrape even if not due (ignores frequency settings)',
        )

    def handle(self, *args, **options):
        catalogues_to_scrape = []
        
        if options['catalogue_id']:
            try:
                catalogue = WhatsAppCatalogue.objects.get(id=options['catalogue_id'])
                catalogues_to_scrape = [catalogue]
                self.stdout.write(f"Scraping specific catalogue: {catalogue.name}")
            except WhatsAppCatalogue.DoesNotExist:
                raise CommandError(f"Catalogue with ID {options['catalogue_id']} does not exist")
        
        elif options['all']:
            catalogues_to_scrape = WhatsAppCatalogue.objects.filter(is_active=True)
            self.stdout.write(f"Scraping all {catalogues_to_scrape.count()} active catalogues")
        
        elif options['due']:
            catalogues_to_scrape = [
                cat for cat in WhatsAppCatalogue.objects.filter(is_active=True) 
                if cat.should_scrape
            ]
            self.stdout.write(f"Scraping {len(catalogues_to_scrape)} catalogues due for update")
        
        else:
            # Default: scrape catalogues that are due
            catalogues_to_scrape = [
                cat for cat in WhatsAppCatalogue.objects.filter(is_active=True) 
                if cat.should_scrape
            ]
            self.stdout.write(f"Scraping {len(catalogues_to_scrape)} catalogues due for update")

        if not catalogues_to_scrape:
            self.stdout.write(
                self.style.WARNING("No catalogues to scrape")
            )
            return

        total_success = 0
        total_failed = 0
        
        for catalogue in catalogues_to_scrape:
            # Check if should scrape (unless forced)
            if not options['force'] and not catalogue.should_scrape:
                self.stdout.write(
                    self.style.WARNING(f"Skipping {catalogue.name} - not due for scraping")
                )
                continue

            self.stdout.write(f"\nStarting scrape for: {catalogue.name}")
            self.stdout.write(f"URL: {catalogue.url}")
            
            try:
                scrape_log = scrape_whatsapp_catalogue(catalogue.id)
                
                if scrape_log and scrape_log.status in ['success', 'partial']:
                    total_success += 1
                    self.stdout.write(
                        self.style.SUCCESS(
                            f"✓ Completed: {catalogue.name}\n"
                            f"  Products found: {scrape_log.products_found}\n"
                            f"  Products added: {scrape_log.products_added}\n"
                            f"  Products updated: {scrape_log.products_updated}\n"
                            f"  Products removed: {scrape_log.products_removed}\n"
                            f"  Execution time: {scrape_log.execution_time}"
                        )
                    )
                else:
                    total_failed += 1
                    error_msg = scrape_log.error_message if scrape_log else "Unknown error"
                    self.stdout.write(
                        self.style.ERROR(
                            f"✗ Failed: {catalogue.name}\n"
                            f"  Error: {error_msg}"
                        )
                    )
                    
            except Exception as e:
                total_failed += 1
                logger.error(f"Unexpected error scraping {catalogue.name}: {str(e)}")
                self.stdout.write(
                    self.style.ERROR(
                        f"✗ Failed: {catalogue.name}\n"
                        f"  Unexpected error: {str(e)}"
                    )
                )

        # Summary
        self.stdout.write("\n" + "="*50)
        self.stdout.write(f"SCRAPING SUMMARY")
        self.stdout.write("="*50)
        self.stdout.write(f"Total catalogues processed: {len(catalogues_to_scrape)}")
        self.stdout.write(f"Successful: {total_success}")
        self.stdout.write(f"Failed: {total_failed}")
        
        if total_success > 0:
            self.stdout.write(
                self.style.SUCCESS(f"\n✓ Successfully scraped {total_success} catalogues")
            )
        
        if total_failed > 0:
            self.stdout.write(
                self.style.ERROR(f"\n✗ Failed to scrape {total_failed} catalogues")
            )

# Usage examples:
# python manage.py scrape_catalogues --all
# python manage.py scrape_catalogues --due
# python manage.py scrape_catalogues --catalogue-id=<uuid>
# python manage.py scrape_catalogues --force