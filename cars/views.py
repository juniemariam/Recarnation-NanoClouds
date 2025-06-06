from django.shortcuts import render, redirect, get_object_or_404
from .models import Car
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.contrib.admin.views.decorators import staff_member_required

# Function to display a list of cars
def cars(request):
    """
    Displays a paginated list of approved cars.
    - Fetches cars with the 'Approved' status, sorted by creation date.
    - Uses a paginator to limit the number of cars displayed per page.
    - Provides search filters for model, city, year, and body style for use in the UI.
    - Renders the 'cars.html' template with the filtered data.
    """
    cars = Car.objects.filter(status='Approved').order_by('-created_date')
    paginator = Paginator(cars, 4)
    page = request.GET.get('page')
    paged_cars = paginator.get_page(page)

    model_search = Car.objects.filter(status='Approved').values_list('model', flat=True).distinct()
    city_search = Car.objects.filter(status='Approved').values_list('city', flat=True).distinct()
    year_search = Car.objects.filter(status='Approved').values_list('year', flat=True).distinct()
    body_style_search = Car.objects.filter(status='Approved').values_list('body_style', flat=True).distinct()

    data = {
        'cars': paged_cars,
        'model_search': model_search,
        'city_search': city_search,
        'year_search': year_search,
        'body_style_search': body_style_search,
    }
    return render(request, 'cars/cars.html', data)

# Function to display details of a single car
def car_detail(request, id):
    """
    Displays the details of a single car.
    - Fetches the car object using its primary key (id).
    - Returns a 404 error if the car does not exist.
    - Renders the 'car_detail.html' template with the car's details.
    """

    single_car = get_object_or_404(Car, pk=id)

    data = {
        'single_car': single_car,
    }
    return render(request, 'cars/car_detail.html', data)

# Function to handle car search
def search(request):
    """
    Handles car search functionality.
    - Allows users to search for cars based on keywords, model, city, year, body style, and price range.
    - Retrieves all cars initially and filters them based on query parameters provided in the request.
    - Provides distinct values for search filters like model, city, year, body style, and transmission.
    - Renders the 'search.html' template with the filtered results.
    """
    cars = Car.objects.order_by('-created_date')

    model_search = Car.objects.values_list('model', flat=True).distinct()
    city_search = Car.objects.values_list('city', flat=True).distinct()
    year_search = Car.objects.values_list('year', flat=True).distinct()
    body_style_search = Car.objects.values_list('body_style', flat=True).distinct()
    transmission_search = Car.objects.values_list('transmission', flat=True).distinct()

    if 'keyword' in request.GET:
        keyword = request.GET['keyword']
        if keyword:
            cars = cars.filter(description__icontains=keyword)

    if 'model' in request.GET:
        model = request.GET['model']
        if model:
            cars = cars.filter(model__iexact=model)

    if 'city' in request.GET:
        city = request.GET['city']
        if city:
            cars = cars.filter(city__iexact=city)

    if 'year' in request.GET:
        year = request.GET['year']
        if year:
            cars = cars.filter(year__iexact=year)

    if 'body_style' in request.GET:
        body_style = request.GET['body_style']
        if body_style:
            cars = cars.filter(body_style__iexact=body_style)

    if 'min_price' in request.GET:
        min_price = request.GET['min_price']
        max_price = request.GET['max_price']
        if max_price:
            cars = cars.filter(price__gte=min_price, price__lte=max_price)

    data = {
        'cars': cars,
        'model_search': model_search,
        'city_search': city_search,
        'year_search': year_search,
        'body_style_search': body_style_search,
        'transmission_search': transmission_search,
    }
    return render(request, 'cars/search.html', data)

# Function to approve or reject cars (Admin only)
@staff_member_required
def approve_cars(request):
    """
    Allows staff members to approve or reject cars.
    - Fetches all cars with the 'Pending' status.
    - Handles POST requests to update the status of a car ('Approved' or 'Rejected').
    - Redirects back to the same page after processing the action.
    - Renders the 'approve_cars.html' template with the list of pending cars.
    """
    pending_cars = Car.objects.filter(status='Pending')
    if request.method == 'POST':
        car_id = request.POST.get('car_id')
        action = request.POST.get('action')  # 'approve' or 'reject'
        car = Car.objects.get(id=car_id)
        if action == 'approve':
            car.status = 'Approved'
        elif action == 'reject':
            car.status = 'Rejected'
        car.save()
        return redirect('approve_cars')
    return render(request, 'approve_cars.html', {'pending_cars': pending_cars})


