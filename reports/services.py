from django.db import connection, models

from .models import Order, OrderStatus


def get_orders_by_priority():
    return Order.objects.annotate(
        priority= models.Case(
            models.When(
                status=OrderStatus.IN_PROGRESS,
                then=0
            ),
            models.When(
                status=OrderStatus.PAID,
                then=1
            ),
            models.When(
                status=OrderStatus.SHIPPED,
                then=2
            ),
            models.When(
                status=OrderStatus.DELIVERED,
                then=3
            ),
        )
    ).order_by("priority")


def get_order_leaderboard():
    class OrderTotals(models.Model):
        category = models.CharField(primary_key=True)
        total = models.IntegerField()

    totals = OrderTotals.objects.raw(
        """\
            select Coalesce(product, 'Total') as category, count(*) as total from reports_order
            group by Rollup(product)
            order by total desc
            limit 6;
        """
    )

    return [{"category": o.category, "total": o.total} for o in totals]


def get_order_leaderboard_with_other():
    class OrderTotals(models.Model):
        category = models.CharField(primary_key=True)
        total = models.IntegerField()

    totals = OrderTotals.objects.raw(
        """\
            with (select Coalesce(product, 'Total') as category, count(*) as total from reports_order
            group by Rollup(product)
            order by total desc
            ) as a
            Union
            (
            select Coalesce(product, 'Total') as category, count(*) as total from reports_order
            group by Rollup(product)
            order by total asc
            limit 6
            )
        """
    )

    return [{"category": o.category, "total": o.total} for o in totals]


def get_order_leaderboard_by_store():
    class OrderTotals(models.Model):
        category = models.CharField(primary_key=True)
        total = models.IntegerField()

    totals = OrderTotals.objects.raw(
        """\
        select 'Total' as category, 0 as total
        """
    )

    return [{"category": o.category, "total": o.total} for o in totals]


def get_set_from_db(query):
    with connection.cursor() as cursor:
        cursor.execute(query)
        return [row[0] for row in cursor.fetchall()]


def series_1_to_10():
    return get_set_from_db("select generate_series(1,10)")


def series_even_numbers_to_20():
    return get_set_from_db("select generate_series(2,20, 2)")


def series_date_range_jan_2025():
    return get_set_from_db("select generate_series('2025-01-01'::timestamptz, '2025-01-31'::timestamptz, '1 day'::interval)")


def sales_report():
    class Sales(models.Model):
        # doesn't matter about uniqueness, just need to set a primary_key to stop Django from complaining
        date = models.DateField(primary_key=True)
        store = models.CharField()
        total = models.IntegerField()

    qs = Sales.objects.raw(
        """\
        select '2025-01-01'::date as date,
               '???' as store,
               0 as total
        """
    )

    return [
        {"date": s.date.strftime("%Y-%m-%d"), "store": s.store, "total": s.total}
        for s in qs
    ]


def sales_report_by_fortnight():
    class Sales(models.Model):
        # doesn't matter about uniqueness, just need to set a primary_key to stop Django from complaining
        date = models.DateField(primary_key=True)
        store = models.CharField()
        total = models.IntegerField()

    qs = Sales.objects.raw(
        """\
        select '2025-01-01'::date as date,
               '???' as store,
               0 as total
        """
    )

    return [
        {"date": s.date.strftime("%Y-%m-%d"), "store": s.store, "total": s.total}
        for s in qs
    ]


def sporadic_sales_report():
    class Sales(models.Model):
        start_date = models.DateField(primary_key=True)
        end_date = models.DateField()
        total = models.IntegerField()

    qs = Sales.objects.raw(
        """\
        select '2025-01-01'::date as start_date,
               '2025-01-01'::date as end_date,
               0 as total
        """
    )

    return [
        {
            "date_range": s.start_date.strftime("%Y-%m-%d")
            + " -> "
            + s.end_date.strftime("%Y-%m-%d"),
            "total": s.total,
        }
        for s in qs
    ]


def series_1_to_10_recursive():
    return get_set_from_db("select limit 0")


def show_reporting_chain():
    return get_set_from_db("select limit 0")
