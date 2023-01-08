from users.models import User, Company, Associated
from equipment.models import Vehicle, Trailer
from datetime import date
from gestor.tests import BaseModelTests


class ServiceOrderTests(BaseModelTests):

    def setUp(self):
        super(ServiceOrderTests, self).setUp()

        # Create some clients
        self.clien1 = Associated.objects.create(
            name='Jane Doe',
            language='Spanish',
            state='Florida',
            type='Client',
            license='ABC456'
        )
        self.clien2 = Associated.objects.create(
            name='John Smith',
            language='English',
            state='Texas',
            type='Client',
            license='XYZ123'
        )

        # Create some companies
        self.company1 = Company.objects.create(
            name='Dispatcher',
            language='Spanish',
        )
        self.company2 = Company.objects.create(
            name='Rental example',
            language='English',
            vehicles='2-5'
        )

        # Create some equipment
        self.trailer = Trailer.objects.create(
            type='flatbed',
            cdl=False,
            manufacturer='bigtex',
            axis_number=2,
            load=10,
            year=2000,
            vin='23456',

        )
        self.vehicle = Vehicle.objects.create(
            model='3500',
            manufacturer='chevrolet',
            year=2010,
            vin='7u803',
        )
