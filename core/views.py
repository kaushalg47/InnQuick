from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import UserSettings, ServiceType
from django.views.decorators.csrf import csrf_exempt
from decimal import Decimal, InvalidOperation
from django.http import JsonResponse
from django.shortcuts import get_object_or_404



@login_required
def user_settings_view(request):
    settings, created = UserSettings.objects.get_or_create(user=request.user)
    services = ServiceType.objects.filter(user=request.user)
    return render(request, 'settings.html', {
        'settings': settings,
        'services': services
    })


@login_required
def update_settings(request):
    if request.method == 'POST':
        settings = request.user.settings
        settings.tax_percentage = request.POST.get('tax_percentage') or 0.0
        settings.additional_charge = request.POST.get('additional_charge') or 0.0
        settings.is_menu_available = 'is_menu_available' in request.POST
        settings.is_service_available = 'is_service_available' in request.POST
        settings.save()
        return redirect('user_settings_view')
    

@login_required
def service_type_list(request):
    services = ServiceType.objects.filter(user=request.user)
    return render(request, 'core/service_types.html', {'services': services})

@csrf_exempt
@login_required
def add_service_type(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        price = request.POST.get('price')

        if not name:
            return JsonResponse({'error': 'Name is required.'}, status=400)

        final_price = None  # Default if price is not provided

        if price:
            try:
                final_price = Decimal(price)
            except InvalidOperation:
                return JsonResponse({'error': 'Invalid price format.'}, status=400)

        service, created = ServiceType.objects.get_or_create(
            user=request.user,
            name=name.strip().lower(),
            defaults={'price': final_price}
        )

        if not created:
            return JsonResponse({'error': 'Service already exists.'}, status=409)

        return JsonResponse({
            "message": "Service added successfully.",
            "item": {
                "id": service.id,
                "name": service.name,
                "price": float(service.price) if service.price is not None else None
            }
        }, status=201)

    return JsonResponse({'error': 'Only POST method allowed.'}, status=405)


@csrf_exempt
@login_required
def delete_service_type(request, service_id):
    if request.method == 'POST':
        service = get_object_or_404(ServiceType, id=service_id, user=request.user)
        service.delete()
    return JsonResponse({
            "message": f"Deleted successfully.",
        }, status=201)
