from django.db import models


class Customer(models.Model):
    cif = models.PositiveIntegerField()
    name = models.CharField(max_length=255)
    birth_date = models.PositiveIntegerField()
    account_no = models.BigIntegerField(unique=True)
    card_no = models.CharField(max_length=60)

    def __str__(self):
        return str(self.account_no)


class Channel(models.Model):
    name = models.CharField(max_length=255)

    class Meta:
        app_label = 'kmeans'
        verbose_name = 'Channel'
        verbose_name_plural = 'Channels'

    def __str__(self):
        return self.name


class TransactionType(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class Transaction(models.Model):

    account_no = models.ForeignKey(Customer, to_field="account_no", on_delete=models.CASCADE)
    channel = models.ForeignKey(Channel, on_delete=models.CASCADE)
    transaction_type = models.ForeignKey(TransactionType, on_delete=models.CASCADE)
    transaction_date = models.PositiveIntegerField()
    amount = models.BigIntegerField()

    def __str__(self):
        return str(self.transaction_date)


class TransactionSummary(Transaction):

    class Meta:
        proxy = True
        verbose_name = 'Transaction Summary'
        verbose_name_plural = 'Transactions Summary'


