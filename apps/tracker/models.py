from enum import Enum
from django.db import models


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


class BuyIn(models.Model):
    resource = models.ForeignKey(Resource, on_delete=models.CASCADE)
    price = models.SmallIntegerField()
    quantity = models.SmallIntegerField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"BuyIn of {self.quantity} {self.resource.name} at {self.price} on {self.timestamp}"


class SellOut(models.Model):
    resource = models.ForeignKey(Resource, on_delete=models.CASCADE)
    price = models.SmallIntegerField()
    quantity = models.SmallIntegerField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"SellOut of {self.quantity} {self.resource.name} at {self.price} on {self.timestamp}"
