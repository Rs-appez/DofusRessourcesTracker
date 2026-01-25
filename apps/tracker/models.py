from datetime import timedelta
from enum import Enum

from django.db import models
from django.db.models.functions import TruncDate
from django.utils import timezone


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
        self.current_value = ResourceValue.get_last_value(self)
        self.average_value = ResourceValue.get_average_price(self, days=30)


class ResourceImage(models.Model):
    name = models.CharField(max_length=255, unique=True, null=True, blank=True)
    image = models.ImageField(upload_to="resources/images/")

    def __str__(self):
        return self.name if self.name else f"Image {self.id}"


class ResourceValue(models.Model):
    resource = models.ForeignKey(Resource, on_delete=models.CASCADE)
    price = models.SmallIntegerField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.resource.name} at {self.timestamp}"

    @staticmethod
    def get_average_price(resource: Resource, days=7) -> float | None:
        time_threshold = timezone.now() - timedelta(days=days)
        daily_averages = (
            ResourceValue.objects.filter(
                resource_id=resource.id, timestamp__gte=time_threshold
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
            )
        return None

    @staticmethod
    def get_last_value(resource: Resource):
        return (
            ResourceValue.objects.filter(resource=resource)
            .order_by("-timestamp")
            .values_list("value", flat=True)
            .first()
        )


class BuyIn(models.Model):
    resource = models.ForeignKey(Resource, on_delete=models.CASCADE)
    price = models.SmallIntegerField()
    quantity = models.SmallIntegerField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"BuyIn of {self.quantity} {self.resource.name} at {self.price} on {self.timestamp}"

    @staticmethod
    def get_average_buy_in_price(resource: Resource, days=7):
        time_threshold = timezone.now() - timedelta(days=days)
        buys = BuyIn.objects.filter(
            resource_id=resource.id, timestamp__gte=time_threshold
        )
        if buys.exists():
            return buys.aggregate(models.Avg("price"))["price__avg"]
        return None

    @staticmethod
    def get_last_buy_in_price(resource: Resource):
        return (
            BuyIn.objects.filter(resource=resource)
            .order_by("-timestamp")
            .values_list("price", flat=True)
            .first()
        )


class SellOut(models.Model):
    resource = models.ForeignKey(Resource, on_delete=models.CASCADE)
    price = models.SmallIntegerField()
    quantity = models.SmallIntegerField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"SellOut of {self.quantity} {self.resource.name} at {self.price} on {self.timestamp}"

    @staticmethod
    def get_average_sell_out_price(resource: Resource, days=7):
        time_threshold = timezone.now() - timedelta(days=days)
        sells = SellOut.objects.filter(
            resource_id=resource.id, timestamp__gte=time_threshold
        )
        if sells.exists():
            return sells.aggregate(models.Avg("price"))["price__avg"]
        return None

    @staticmethod
    def get_last_sell_out_price(resource: Resource):
        return (
            SellOut.objects.filter(resource=resource)
            .order_by("-timestamp")
            .values_list("price", flat=True)
            .first()
        )
