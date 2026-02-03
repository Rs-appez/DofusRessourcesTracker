from datetime import timedelta
from enum import Enum

from django.db import models
from django.db.models.functions import TruncDate
from django.utils import timezone
from django.utils.formats import number_format


class ResourceType(Enum):
    ITEM = 0
    CRAFT = 1
    HARVEST = 2
    BOSS = 3
    MONSTER = 4
    WANTED = 5
    CARD = 6
    QUEST = 7


class Resource(models.Model):
    name = models.CharField(max_length=255)
    image = models.ForeignKey(
        "ResourceImage", on_delete=models.SET_NULL, null=True, blank=True
    )
    resource_type = models.IntegerField(
        choices=[(tag.value, tag.name) for tag in ResourceType]
    )
    use_in = models.ManyToManyField(
        "self", symmetrical=False, related_name="used_for", blank=True
    )

    def __str__(self):
        return self.name

    def add_stats(self):
        self.current_value = ResourceValue.get_last_price(self)
        self.current_value_formatted = number_format(
            self.current_value, decimal_pos=0, force_grouping=True
        )

        self.average_value, month_values = ResourceValue.get_average_price(
            self, days=30
        )
        self.average_value_formatted = number_format(
            self.average_value, decimal_pos=2, force_grouping=True
        )

        data = [
            (value["avg_per_day"], value["day"].strftime("%d-%m"))
            for value in month_values
        ]

        self.days_values, self.days_labels = (
            (list(x) for x in zip(*data)) if data else ([], [])
        )

        if self.resource_type == ResourceType.WANTED.value:
            self.last_sell_value = SellOut.get_last_price(self)
            self.last_sell_value_formatted = number_format(
                self.last_sell_value, decimal_pos=0, force_grouping=True
            )

            self.average_sell_values = SellOut.get_average_price(self, days=30)
            self.average_sell_values_formatted = number_format(
                self.average_sell_values, decimal_pos=2, force_grouping=True
            )


class ResourceImage(models.Model):
    name = models.CharField(max_length=255, unique=True, null=True, blank=True)
    image = models.ImageField(upload_to="resources/images/")

    def __str__(self):
        return self.name if self.name else f"Image {self.id}"


class TransactionMixin:
    @classmethod
    def get_average_price(cls, resource: Resource, days=7):
        time_threshold = timezone.now() - timedelta(days=days)
        transactions = cls.objects.filter(
            resource_id=resource.id, timestamp__gte=time_threshold
        )
        if transactions.exists():
            return transactions.aggregate(models.Avg("price"))["price__avg"]
        return None

    @classmethod
    def get_last_price(cls, resource: Resource):
        return (
            cls.objects.filter(resource=resource)
            .order_by("-timestamp")
            .values_list("price", flat=True)
            .first()
        )


class ResourceValue(models.Model, TransactionMixin):
    resource = models.ForeignKey(Resource, on_delete=models.CASCADE)
    price = models.SmallIntegerField(null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.resource.name} at {self.timestamp}"

    @classmethod
    def get_average_price(
        cls, resource: Resource, days=7
    ) -> tuple[float, list[dict[str, timezone.datetime]]] | None:
        time_threshold = timezone.now() - timedelta(days=days)

        daily_averages = (
            cls.objects.filter(
                resource_id=resource.id,
                timestamp__gte=time_threshold,
                price__isnull=False,
            )
            .annotate(day=TruncDate("timestamp"))
            .values("day")
            .annotate(avg_per_day=models.Avg("price"))
        )
        if daily_averages.exists():
            avgs = [
                d["avg_per_day"] for d in daily_averages if d["avg_per_day"] is not None
            ]
            sorted_avgs = sorted(avgs)
            n = len(sorted_avgs)
            return (
                (sorted_avgs[n // 2])
                if n % 2 == 1
                else (sorted_avgs[n // 2 - 1] + sorted_avgs[n // 2]) / 2
            ), daily_averages
        return None


class BuyIn(models.Model, TransactionMixin):
    resource = models.ForeignKey(Resource, on_delete=models.CASCADE)
    price = models.SmallIntegerField()
    quantity = models.SmallIntegerField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"BuyIn of {self.quantity} {self.resource.name} at {self.price} on {self.timestamp}"


class SellOut(models.Model, TransactionMixin):
    resource = models.ForeignKey(Resource, on_delete=models.CASCADE)
    price = models.SmallIntegerField()
    quantity = models.SmallIntegerField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"SellOut of {self.quantity} {self.resource.name} at {self.price} on {self.timestamp}"
