import os
import csv
from inventory.models import ProductCategory
from inventory.models import Product
from services.models import ServiceCategory
from django.db.models import Model
from gestor.settings import BASE_DIR
from io import BytesIO


# exec(open('upload_images.py').read())


def uploadImages(model: Model, fname: str):
    count = 0
    with open(fname, newline='\n') as csvfile:
        model_files = csv.reader(csvfile)
        for row in model_files:
            id = row[0]
            file_name = row[1].split('/media/')[1]
            print(file_name)
            file_path = os.path.join(BASE_DIR, 'img_bk/', file_name)
            if os.path.exists(file_path):
                with open(file_path, 'rb') as f:
                    # Upload
                    obj = model.objects.get(id=id)
                    file_name = file_name.split('/')[-1]
                    try:
                        obj.icon.save(file_name, BytesIO(f.read()))
                        # print(F"uploading: {file_name}")
                    except AttributeError:
                        try:
                            obj.image.save(file_name, BytesIO(f.read()))
                            # obj.save()
                            # print(F"uploading: {file_name}")
                        except AttributeError:
                            print('file not found!')

                    count += 1

    print(F"Successfully uploaded {count} images!")


# fname = os.path.join(BASE_DIR, "product_categories_img.csv")
# uploadImages(ProductCategory, fname)
# fname = os.path.join(BASE_DIR, "service_categories_img.csv")
# uploadImages(ServiceCategory, fname)
fname = os.path.join(BASE_DIR, "products_img.csv")
uploadImages(Product, fname)
