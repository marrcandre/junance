from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("imports", "0001_initial"),
        ("ledger", "0003_expense_is_void_income_is_void_transfer_is_void"),
    ]

    operations = [
        migrations.AddField(
            model_name="importbatch",
            name="account",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="import_batches",
                to="ledger.account",
            ),
        ),
    ]
