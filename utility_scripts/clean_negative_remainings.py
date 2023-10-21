from rent.models.lease import Payment


Payment.objects.filter(remaining__lt=0).update(remaining=0)
