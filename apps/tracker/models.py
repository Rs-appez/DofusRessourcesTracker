from enum import Enum
from django.db import models
from django.utils import timezone
from datetime import timedelta


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


class ResourceImage(models.Model):
    name = models.CharField(max_length=255, unique=True, null=True, blank=True)
    image = models.ImageField(upload_to="resources/images/")

    def __str__(self):
        return self.name if self.name else f"Image {self.id}"


class ResourceValue(models.Model):
    resource = models.ForeignKey(Resource, on_delete=models.CASCADE)
    value = models.SmallIntegerField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.resource.name} at {self.timestamp}"

    @staticmethod
    def get_average_price(resource: Resource, days=7):
        time_threshold = timezone.now() - timedelta(days=days)
        values = ResourceValue.objects.filter(
            resource_id=resource.id, timestamp__gte=time_threshold
        )
        if values.exists():
            return values.aggregate(models.Avg("value"))["value__avg"]
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
