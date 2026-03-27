import json
from datetime import timedelta
from enum import Enum

from django.db import models
from django.db.models import Avg, Count
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
    MISC = 8
    FAMILIAR = 9


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
        self.add_value_stats()
        self.add_sell_stats()

    def add_value_stats(self):
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

        data = [(value, key.strftime("%d-%m")) for key, value in month_values.items()]

        self.days_values, self.days_labels = (
            (list(x) for x in zip(*data)) if data else ([], [])
        )

        self.empty_values = ResourceValue.get_empty_values(
            self, days=list(month_values.keys())
        )

        self.days_sell_values = SellOut.get_dated_data(
            self, days=list(month_values.keys())
        )

        if self.resource_type == ResourceType.WANTED.value:
            self.cards_price = ResourceValue.get_all_cards_price_per_day(
                self, days=list(month_values.keys())
            )

    def add_sell_stats(self):
        self.last_sell_value = SellOut.get_last_price(self)
        self.last_sell_value_formatted = number_format(
            self.last_sell_value, decimal_pos=0, force_grouping=True
        )

        self.average_sell_values = SellOut.get_average_price(self, days=30)
        self.average_sell_values_formatted = number_format(
            self.average_sell_values, decimal_pos=2, force_grouping=True
        )

    def dumps_stats(self):
        self.days_values = json.dumps(self.days_values)
        self.days_labels = json.dumps(self.days_labels)
        self.empty_values = json.dumps(self.empty_values)
        self.days_sell_values = json.dumps(self.days_sell_values)
        if self.resource_type == ResourceType.WANTED.value:
            self.cards_price = json.dumps(self.cards_price)


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
            return transactions.aggregate(Avg("price"))["price__avg"]
        return None

    @classmethod
    def get_last_price(cls, resource: Resource):
        return (
            cls.objects.filter(resource=resource)
            .order_by("-timestamp")
            .values_list("price", flat=True)
            .first()
        )

    @classmethod
    def get_dated_data(
        cls, resource: Resource, days: list[timezone.datetime]
    ) -> list[float | None]:
        transactions = (
            cls.objects.filter(resource_id=resource.id, timestamp__date__in=days)
            .annotate(day=TruncDate("timestamp"))
            .values("day")
            .annotate(avg_per_day=Avg("price"))
        )

        transactions_dict = {t["day"]: t["avg_per_day"] for t in transactions}
        return [transactions_dict.get(day) for day in days]


class ResourceValue(models.Model, TransactionMixin):
    resource = models.ForeignKey(Resource, on_delete=models.CASCADE)
    price = models.IntegerField(null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.resource.name} at {self.timestamp}"

    @classmethod
    def get_average_price(
        cls, resource: Resource, days=7
    ) -> tuple[float | None, list[dict[str, timezone.datetime]]]:
        time_threshold = timezone.now() - timedelta(days=days - 1)
        all_dates = [
            (time_threshold + timedelta(days=day)).date() for day in range(days)
        ]
        results = {date: None for date in all_dates}

        daily_averages = (
            cls.objects.filter(
                resource_id=resource.id,
                timestamp__gte=time_threshold,
                price__isnull=False,
            )
            .annotate(day=TruncDate("timestamp"))
            .values("day")
            .annotate(avg_per_day=Avg("price"))
            .order_by("day")
        )
        if daily_averages.exists():
            for entry in daily_averages:
                results[entry["day"]] = entry["avg_per_day"]

            avgs = [
                d["avg_per_day"] for d in daily_averages if d["avg_per_day"] is not None
            ]
            sorted_avgs = sorted(avgs)
            n = len(sorted_avgs)
            return (
                (sorted_avgs[n // 2])
                if n % 2 == 1
                else (sorted_avgs[n // 2 - 1] + sorted_avgs[n // 2]) / 2
            ), results
        return None, results

    @classmethod
    def get_all_cards_price_per_day(
        cls, resource: Resource, days: list[timezone.datetime]
    ):
        if resource.resource_type != ResourceType.WANTED.value:
            return None

        card_resources = Resource.objects.filter(
            use_in__use_in=resource, resource_type=ResourceType.CARD.value
        )
        nb_cards = card_resources.count()

        card_avg_per_day = (
            cls.objects.filter(
                resource__in=card_resources,
                timestamp__date__in=days,
            )
            .annotate(day=TruncDate("timestamp"))
            .values("day", "resource")
            .annotate(avg_price=Avg("price"))
        )

        dayly_totals = {}
        skip_days = set()
        for entry in card_avg_per_day:
            day = entry["day"]
            avg_price = entry["avg_price"]
            if avg_price is not None and day not in skip_days:
                current = dayly_totals.get(day, (0, 0))
                dayly_totals[day] = (current[0] + avg_price, current[1] + 1)
            else:
                skip_days.add(day)
                dayly_totals[day] = (None, 0)

        return [
            dayly_totals[day][0]
            if dayly_totals.get(day, (0, 0))[1] == nb_cards
            else None
            for day in days
        ]

    @classmethod
    def get_empty_values(
        cls, resource: Resource, days: list[timezone.datetime]
    ) -> list[int | None]:
        empty_values = (
            cls.objects.filter(
                resource_id=resource.id,
                timestamp__date__in=days,
                price__isnull=True,
            )
            .annotate(day=TruncDate("timestamp"))
            .values("day")
            .annotate(count=Count("id"))
        )

        empty_dict = {item["day"]: item["count"] for item in empty_values}
        return [empty_dict.get(day, None) for day in days]


class BuyIn(models.Model, TransactionMixin):
    resource = models.ForeignKey(Resource, on_delete=models.CASCADE)
    price = models.IntegerField()
    quantity = models.SmallIntegerField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"BuyIn of {self.quantity} {self.resource.name} at {self.price} on {self.timestamp}"


class SellOut(models.Model, TransactionMixin):
    resource = models.ForeignKey(Resource, on_delete=models.CASCADE)
    price = models.IntegerField()
    quantity = models.SmallIntegerField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"SellOut of {self.quantity} {self.resource.name} at {self.price} on {self.timestamp}"
