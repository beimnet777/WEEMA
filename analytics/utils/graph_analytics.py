from django.db.models import Sum, Max, Avg, DecimalField, F
from django.db.models.functions import Coalesce
from cluster_management.models import SelfHelpGroup, Member
from data_collection.models import AnnualData, SixMonthData, AnnualSelfHelpGroupData, AnnualSelfHelpGroupData
from django.utils.dateparse import parse_datetime
from django.db.models.functions import Cast
from django.utils.timezone import now
from dateutil.relativedelta import relativedelta
from datetime import timedelta

def get_location_level_graph_data(start_date=None, end_date=None, cluster=None, region= None, zone = None, woreda = None):
    
    # Prepare a dictionary for optional date filtering
    date_filters = {}
    if start_date and end_date:
        date_filters['created_at__range'] = [start_date, end_date]

    # If a cluster filter is provided, further restrict the groups.
    groups_qs = SelfHelpGroup.objects.all()
    group_field = 'region'
    if cluster:
        groups_qs = groups_qs.filter(cluster=cluster)
    
    if region:
        group_field = 'Zone'
        groups_qs = groups_qs.filter(region=region)
    
    if zone:
        group_field = 'woreda'
        groups_qs = groups_qs.filter(Zone=zone)
    # decide which field to group by
    if woreda:
        group_field = 'woreda'
        groups_qs = groups_qs.filter(woreda=woreda)
        
    
    # Get distinct, non-empty location values from SelfHelpGroup.
    locations = (
        groups_qs
        .exclude(**{f"{group_field}__isnull": True})
        .exclude(**{f"{group_field}__exact": ""})
        .values_list(group_field, flat=True)
        .distinct()
    )

    results = {}

    for loc in locations:
        # For each location, get all groups at that location
        groups = groups_qs.filter(**{group_field: loc})
        total_groups = groups.count()

        # Get all members that belong to these groups
        members = Member.objects.filter(group__in=groups)
        total_members = members.count()

        # Aggregate savings from AnnualData for these members (with date filtering if provided)
        total_savings = AnnualData.objects.filter(member__in=members, **date_filters).aggregate(
            total=Sum('total_savings')
        )['total']
        if not total_savings: total_savings = 0
        # Aggregate capital and loan data from SixMonthData
        total_capital = SixMonthData.objects.filter(member__in=members, **date_filters).aggregate(
            total=Sum('iga_capital')
        )['total']
        
        if not total_capital: total_capital = 0

        total_loan_circulated = SixMonthData.objects.filter(member__in=members, **date_filters).aggregate(
            total=Sum('loan_amount_received_shg')
        )['total']
        
        if not total_loan_circulated: total_loan_circulated = 0

        max_loan_taken = SixMonthData.objects.filter(member__in=members, **date_filters).aggregate(
            maximum=Max('loan_amount_received_shg')
        )['maximum']
        
        if not max_loan_taken : max_loan_taken = 0

        total_loan_other_sources = SixMonthData.objects.filter(member__in=members, **date_filters).aggregate(
            total=Sum('loan_amount_from_other_sources')
        )['total']
        
        if not total_loan_other_sources : total_loan_other_sources = 0

        # Build the dictionary for the current location
        results[loc] = {
            "total_groups": total_groups,
            "total_members": total_members,
            "total_savings": total_savings,
            "total_capital": total_capital,
            "total_loan_circulated": total_loan_circulated,
            "max_loan_taken": max_loan_taken,
            "total_loan_other_sources": total_loan_other_sources,
        }

    return results



def get_group_level_financial_metrics(start_date=None, end_date=None, cluster=None, group_age=None):
    # Build date filters if provided
    filters = {}
    if start_date and end_date:
        # Expecting start_date and end_date to be strings in "YYYY-MM-DD" format
        start_date = parse_datetime(start_date)
        end_date = parse_datetime(end_date)
        filters['created_at__range'] = [start_date, end_date]
    
    # Get the SelfHelpGroup queryset; if a cluster is provided, filter by cluster.
    groups_qs = SelfHelpGroup.objects.all()
    if cluster:
        groups_qs = groups_qs.filter(cluster=cluster)
    
    if group_age is not None:
        # Get the approximate date range for the given age
        group_age = int(group_age)
        today = now().date()
        min_date = today - relativedelta(years=group_age + 1) + timedelta(days=1)  # Just past the previous year
        max_date = today - relativedelta(years=group_age)  # Up to the exact year
        
        groups_qs = groups_qs.filter(created_at__range=(min_date, max_date))
    
    
    
    results = {}
    
    # Loop over each group in the queryset.
    for group in groups_qs:
        print(group.group_name)
        # Get all members in this group
        members = Member.objects.filter(group=group)
        # if not members.exists():
        #     continue  # Skip groups with no members
        
        # Aggregate monthly savings from AnnualData for these members.
        total_monthly_savings = AnnualData.objects.filter(member__in=members, **filters).aggregate(
            total=Sum('total_savings')
        )['total']
        if not total_monthly_savings: total_monthly_savings = 0
        # Convert monthly savings to weekly saving
        weekly_saving = total_monthly_savings 
        
        # Total Capital from SixMonthData: sum of iga_capital
        total_capital = SixMonthData.objects.filter(member__in=members, **filters).aggregate(
            total=Sum('iga_capital')
        )['total']
        
        if not total_capital: total_capital = 0
        
        # # # Total Expenditure from AnnualData: sum of total_expenditure
        total_expenditure = AnnualSelfHelpGroupData.objects.filter(group=group, **filters).aggregate(
            total=Sum('expenditure_social_savings')
        )['total']
        
        if not total_expenditure: total_expenditure = 0
        
        # IGA Capital: average of iga_capital
        avg_iga_capital = SixMonthData.objects.filter(member__in=members, **filters).aggregate(
            avg=Avg('iga_capital')
        )['avg']
        
        if not avg_iga_capital: avg_iga_capital = 0
        
        # Approximate Monthly Income: average of approx_monthly_personal_income
        avg_monthly_income = SixMonthData.objects.filter(member__in=members, **filters).aggregate(
            avg=Avg('approx_monthly_personal_income')
        )['avg']
        
        if not avg_monthly_income: avg_monthly_income = 0
        
        # Build the metrics dictionary for this group.
        results[group.group_name] = {
            "weekly_saving": round(weekly_saving, 2),
            "total_capital": round(total_capital, 2),
            "total_expenditure": round(total_expenditure, 2),
            "iga_capital": round(avg_iga_capital, 2),
            "approx_monthly_income": round(avg_monthly_income, 2)
        }
    
    return results
