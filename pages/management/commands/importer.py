import pandas as pd 
from django.core.management.base import BaseCommand, CommandParser
from pages.models import Provider

class Command(BaseCommand):
    help = 'Imports the Provider dataset'

    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument(
            '--all',
            action="store_true",
            help = 'Delete all datafiles from the provider dataset'
        )

    def handle(self, *args, **options):
        if options['all']:
            files = 50
        else:
            files = 1

        for i in range(files):

            df = pd.read_csv('pages/data/data-' + str(i) + '.csv', low_memory=False, dtype=str)
            df = df.fillna('')

            row_iter = df.iterrows()

            providers = [
                Provider(
                    provider_id = row['NPI'],
                    firstName = row['Provider First Name'],
                    lastName = row['Provider Last Name'],
                    gender = row['gndr'],
                    phone_number = str(row['Telephone Number'])[0:10],
                    specialization = row['pri_spec'],
                    address = row['adr_ln_1'],
                    city = row['City/Town'],
                    state = row['State'],
                    zip_code = row['ZIP Code'],
                    facility_name = row['Facility Name'],
                )
                for index, row in row_iter
            ]
            Provider.objects.bulk_create(providers)

            # Release the dataframe so we don't run out of memory
            del(df)

            self.stdout.write(
                self.style.SUCCESS('Successfully imported provider data %s of 50' % str(i + 1))
            )
        
        self.stdout.write(
            self.style.SUCCESS('Import complete')
        )
