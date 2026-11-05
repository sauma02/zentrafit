from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("tienda", "0001_initial")]

    operations = [
        migrations.AlterField(
            model_name="carrito",
            name="sesionId",
            field=models.CharField(
                blank=True, max_length=50, null=True
            ),
        ),
    ]
