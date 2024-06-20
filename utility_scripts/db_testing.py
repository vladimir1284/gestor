from utils.models import Order

o = Order.objects.all().prefetch_related(
    "producttransaction_set",
    "producttransaction_set__product",
    "producttransaction_set__product__producttransaction_set",
)
for i in o:
    for pt in i.producttransaction_set.all():
        for pt2 in pt.product.producttransaction_set.filter(id=pt.id):
            print(pt.id, pt2.id)
