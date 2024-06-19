from django.apps import apps

models = apps.get_models()

for m in models:
    postgres = m.objects.count()
    sqlite = m.objects.using("old_db").count()

    if sqlite != postgres:
        print(m)
        print(f"sqlite and postgres don't match: {sqlite} != {postgres}")
