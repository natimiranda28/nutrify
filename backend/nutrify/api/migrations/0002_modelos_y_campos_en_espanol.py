from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("api", "0001_initial"),
    ]

    operations = [
        migrations.RenameModel(
            old_name="DietaryRestriction",
            new_name="RestriccionDieta",
        ),
        migrations.RenameField(
            model_name="restricciondieta",
            old_name="name",
            new_name="nombre",
        ),
        migrations.RenameField(
            model_name="restricciondieta",
            old_name="description",
            new_name="descripcion",
        ),
        migrations.RenameField(
            model_name="product",
            old_name="description",
            new_name="descripcion",
        ),
        migrations.RenameField(
            model_name="product",
            old_name="ingredients",
            new_name="ingredientes",
        ),
        migrations.RenameField(
            model_name="product",
            old_name="allergens",
            new_name="alergias",
        ),
        migrations.RenameField(
            model_name="product",
            old_name="cross_contamination_info",
            new_name="contaminacion_cruzada_info",
        ),
        migrations.AlterModelOptions(
            name="restricciondieta",
            options={"ordering": ["nombre"]},
        ),
    ]
