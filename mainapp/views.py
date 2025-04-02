from django.shortcuts import render
from mainapp.models import DeliveryLocation
from django.http import JsonResponse


def home(request):
    return render(request, "front-end/index-2.html")

def gelLocationList(request):
    
    delivery_locations  = DeliveryLocation.objects.all().values('location', 'deliveries')

    return JsonResponse({'deliveryLocations': list(delivery_locations)}, safe=False)
    