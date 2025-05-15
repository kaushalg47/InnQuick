# views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from datetime import datetime, timedelta
from .models import Facility, TimeSlot, Booking
from rooms.models import Room
from django.urls import reverse
import json
from django.http import JsonResponse



@login_required
def facilities_dashboard(request):
    """
    All-in-one view for facilities management:
    - List all facilities
    - Add new facility
    - View facility details
    - Add time slots
    """
    facilities = Facility.objects.all()
    selected_facility_id = request.GET.get('facility_id')
    selected_facility = None
    time_slots = []
    rooms = Room.objects.filter(user=request.user)
    
    # Handle form submissions
    if request.method == 'POST':
        form_type = request.POST.get('form_type')
        
        # Add facility form processing
        if form_type == 'add_facility':
            name = request.POST.get('name')
            description = request.POST.get('description')
            price = request.POST.get('price')
            
            if name and description:
                facility = Facility.objects.create(
                    name=name,
                    description=description,
                    price=price if price else None,
                    user=request.user
                )
                messages.success(request, f'Facility "{name}" has been created!')
                # Use redirect with reverse and build the URL correctly
                base_url = reverse('facilities_dashboard')
                return redirect(f'{base_url}?facility_id={facility.id}')
            else:
                messages.error(request, 'Please provide all required information.')
        
        # Add time slot form processing
        elif form_type == 'add_time_slot':
            facility_id = request.POST.get('facility_id')
            facility = get_object_or_404(Facility, id=facility_id)
            
            try:
                start_date = request.POST.get('start_date')
                start_time = request.POST.get('start_time')
                end_time = request.POST.get('end_time')
                
                # Combine date and time
                start_datetime_str = f"{start_date} {start_time}"
                start_datetime = datetime.strptime(start_datetime_str, '%Y-%m-%d %H:%M')
                
                # For end_datetime, use the same date as start
                end_datetime_str = f"{start_date} {end_time}"
                end_datetime = datetime.strptime(end_datetime_str, '%Y-%m-%d %H:%M')
                
                # Create the time slot
                time_slot = TimeSlot.objects.create(
                    facility=facility,
                    start_time=start_datetime,
                    end_time=end_datetime
                )
                
                messages.success(request, 'Time slot added successfully!')
                # Use redirect with reverse and build the URL correctly
                base_url = reverse('facilities_dashboard')
                return redirect(f'{base_url}?facility_id={facility_id}')
            except Exception as e:
                messages.error(request, f'Error creating time slot: {str(e)}')
    
    # Get selected facility details if ID is provided
    if selected_facility_id:
        selected_facility = get_object_or_404(Facility, id=selected_facility_id)
        time_slots = TimeSlot.objects.filter(facility=selected_facility)
    
    return render(request, 'FacilityList.html', {
        'facilities': facilities,
        'selected_facility': selected_facility,
        'time_slots': time_slots,
        'rooms': rooms,
    })

# views.py


@login_required
def mobile_facilities(request):
    """Mobile-friendly view for facilities listing and booking"""
    facilities = Facility.objects.all()
    
    # Handle booking submission
    if request.method == 'POST' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        data = json.loads(request.body)
        slot_id = data.get('slot_id')
        room_id = data.get('room_id')
        
        time_slot = get_object_or_404(TimeSlot, id=slot_id)
        
        # Check if slot is available
        if not time_slot.is_available:
            return JsonResponse({'status': 'error', 'message': 'This time slot is already booked'})
        
        # Get room if provided
        room = None
        if room_id:
            room = get_object_or_404(Room, id=room_id)
        
        # Create booking
        booking = Booking.objects.create(
            time_slot=time_slot,
            user=request.user,
            room=room
        )
        
        return JsonResponse({
            'status': 'success', 
            'message': f'Successfully booked {time_slot.facility.name}',
            'booking_id': booking.id
        })
    
    # Get rooms for the booking form
    rooms = Room.objects.filter(user=request.user)
    
    return render(request, 'FacilityBook.html', {
        'facilities': facilities,
        'rooms': rooms
    })

@login_required
def pos_facilities(request):
    """Mobile-friendly view for facilities listing and booking"""
    facilities = Facility.objects.all()
    
    # Handle booking submission
    if request.method == 'POST' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        data = json.loads(request.body)
        slot_id = data.get('slot_id')
        room_id = data.get('room_id')
        
        time_slot = get_object_or_404(TimeSlot, id=slot_id)
        
        # Check if slot is available
        if not time_slot.is_available:
            return JsonResponse({'status': 'error', 'message': 'This time slot is already booked'})
        
        # Get room if provided
        room = None
        if room_id:
            room = get_object_or_404(Room, id=room_id)
        
        # Create booking
        booking = Booking.objects.create(
            time_slot=time_slot,
            user=request.user,
            room=room
        )
        
        return JsonResponse({
            'status': 'success', 
            'message': f'Successfully booked {time_slot.facility.name}',
            'booking_id': booking.id
        })
    
    # Get rooms for the booking form
    rooms = Room.objects.filter(user=request.user)
    
    return render(request, 'FacilityBookPos.html', {
        'facilities': facilities,
        'rooms': rooms
    })

@login_required
def get_facility_slots(request, facility_id):
    """API to get time slots for a facility"""
    facility = get_object_or_404(Facility, id=facility_id)
    time_slots = TimeSlot.objects.filter(facility=facility)
    
    # Format time slots for JSON response
    slots_data = []
    for slot in time_slots:
        slots_data.append({
            'id': slot.id,
            'date': slot.start_time.strftime('%Y-%m-%d'),
            'start_time': slot.start_time.strftime('%H:%M'),
            'end_time': slot.end_time.strftime('%H:%M'),
            'is_available': slot.is_available
        })
    
    return JsonResponse({
        'facility': {
            'id': facility.id,
            'name': facility.name,
            'description': facility.description,
            'price': float(facility.price) if facility.price else None
        },
        'time_slots': slots_data
    })




@login_required
def create_booking(request, facility_id):
    """API endpoint to create a booking for a specific facility"""
    if request.method == 'POST' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        try:
            # Parse JSON data from request body
            data = json.loads(request.body)
            slot_id = data.get('slot_id')
            room_id = data.get('room_id')
            
            # Get the time slot
            time_slot = get_object_or_404(TimeSlot, id=slot_id, facility_id=facility_id)
            room = get_object_or_404(Room, id=room_id) if room_id else None
            
            # Check if slot is available
            if not time_slot.is_available:
                return JsonResponse({
                    'status': 'error', 
                    'message': 'This time slot is already booked'
                })
            
            time_slot.is_available = False
            time_slot.save()
            
            # Create booking
            booking = Booking.objects.create(
                time_slot=time_slot,
                user=request.user,
                room=room  # No room selected in this simplified version
            )
            
            return JsonResponse({
                'status': 'success', 
                'message': f'Successfully booked {time_slot.facility.name}',
                'booking_id': booking.id,
                'booking_details': {
                    'facility': time_slot.facility.name,
                    'date': time_slot.start_time.strftime('%Y-%m-%d'),
                    'time': f"{time_slot.start_time.strftime('%H:%M')} - {time_slot.end_time.strftime('%H:%M')}",
                }
            })
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': f'Error creating booking: {str(e)}'
            }, status=400)
    
    # Return error for non-AJAX or non-POST requests
    return JsonResponse({
        'status': 'error',
        'message': 'Invalid request method'
    }, status=405)

@login_required
def view_all_bookings(request):
    """
    View for listing all bookings with filtering options
    """
    # Get all bookings for the current user
    bookings = Booking.objects.filter(user=request.user, settled=False).order_by('-booking_time')
    
    # Optional: Filter by date range if provided in request
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    
    if start_date:
        start_date = datetime.strptime(start_date, '%Y-%m-%d')
        bookings = bookings.filter(time_slot__start_time__gte=start_date)
    
    if end_date:
        end_date = datetime.strptime(end_date, '%Y-%m-%d')
        end_date = end_date + timedelta(days=1)  # Include the end date fully
        bookings = bookings.filter(time_slot__start_time__lt=end_date)
    
    # Optional: Get facilities for the filter dropdown
    facilities = Facility.objects.all()
    
    # Optional: Filter by facility if provided
    facility_id = request.GET.get('facility')
    if facility_id:
        bookings = bookings.filter(time_slot__facility_id=facility_id)
    
    return render(request, 'FacilityBookList.html', {
        'bookings': bookings,
        'facilities': facilities,
        'filters': {
            'start_date': start_date.strftime('%Y-%m-%d') if start_date else '',
            'end_date': (end_date - timedelta(days=1)).strftime('%Y-%m-%d') if end_date else '',
            'facility': facility_id
        }
    })

def settle_booking(request, booking_id):
    """
    Update the status of a booking (e.g., mark as settled)
    """
    try:
        booking = get_object_or_404(Booking, id=booking_id)
        time_slot = booking.time_slot
        
        if request.method == 'POST':
            # Mark booking as settled
            time_slot.is_available = True
            time_slot.save()
            booking.settled = True
            booking.save()
            messages.success(request, 'Booking marked as settled.')
        
        return JsonResponse({
                    'status': 'success', 
                    'message': 'Booking settled successfully',
                })
    except Exception as e:
        return JsonResponse({
                    'status': 'error', 
                    'message': f'Error settling booking: {str(e)}'
                }, status=400)
    
# Fixed delete_booking view
@login_required
def delete_booking(request, booking_id):
    """API to delete a booking"""
    import logging
    logger = logging.getLogger(__name__)
    logger.info(f"Delete booking request received for booking_id: {booking_id}")
    
    # First, verify the request method
    if request.method != 'POST':
        logger.warning(f"Invalid method: {request.method} for delete_booking")
        return JsonResponse({
            'status': 'error',
            'message': 'Invalid request method. Please use POST.'
        }, status=400)
    
    try:
        # Log the headers to debug potential issues
        logger.info(f"Request headers: {dict(request.headers)}")
        
        # Get the booking object
        booking = get_object_or_404(Booking, id=booking_id)
        logger.info(f"Booking found: {booking.id} for facility {booking.time_slot.facility.name}")
        
        # Check if the booking belongs to the current user
        if booking.user != request.user:
            logger.warning(f"User {request.user.id} attempted to delete booking {booking_id} belonging to user {booking.user.id}")
            return JsonResponse({
                'status': 'error',
                'message': 'You do not have permission to delete this booking.'
            }, status=403)
        
        # Store references before deleting
        facility_name = booking.time_slot.facility.name
        time_slot = booking.time_slot
        
        # Delete the booking
        logger.info(f"Deleting booking {booking_id}")
        booking.delete()
        
        # Update the time slot
        logger.info(f"Setting time_slot {time_slot.id} availability to True")
        time_slot.is_available = True
        time_slot.save()
        
        success_message = f'Your booking for {facility_name} has been cancelled successfully.'
        logger.info(f"Booking deleted successfully: {success_message}")
        
        # Return JSON response
        return JsonResponse({
            'status': 'success',
            'message': success_message
        })
    
    except Booking.DoesNotExist:
        logger.error(f"Booking with id {booking_id} not found")
        return JsonResponse({
            'status': 'error',
            'message': 'Booking not found.'
        }, status=404)
    except Exception as e:
        # Detailed error logging
        logger.error(f"Error in delete_booking for booking_id {booking_id}: {str(e)}", exc_info=True)
        
        # Return JSON error response
        return JsonResponse({
            'status': 'error',
            'message': 'An error occurred while processing your request. Please try again.'
        }, status=500)
        

@login_required
def get_all_bookings(request):
    """
    API to get all bookings for the logged-in user
    """
    if request.method == 'GET':
        bookings = Booking.objects.filter(user=request.user)

        # Serialize bookings into a list of dictionaries
        bookings_data = []
        for booking in bookings:
            bookings_data.append({
                'id': booking.id,
                'time_slot': {
                    'id': booking.time_slot.id,
                    'facility': booking.time_slot.facility.name,
                    'start_time': booking.time_slot.start_time.strftime('%Y-%m-%d %H:%M'),
                    'end_time': booking.time_slot.end_time.strftime('%Y-%m-%d %H:%M'),
                },
                'settled': booking.settled,
                'booking_time': booking.booking_time.strftime('%Y-%m-%d %H:%M'),
                # Add more fields as needed
            })

        return JsonResponse({'bookings': bookings_data}, status=200)

    return JsonResponse({'error': 'Only GET method allowed'}, status=405)

