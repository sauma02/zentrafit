from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("tienda", "0003_merge_20261105_2312")]

    operations = [
        migrations.AlterField(
            model_name="movimientoinventario",
            name="usuarioId",
            field=models.ForeignKey(
                blank=True,
                db_column="usuarioId",
                null=True,
                on_delete=models.SET_NULL,
                related_name="movimientos_inventario",
                to="tienda.usuario",
            ),
        ),
    ]
