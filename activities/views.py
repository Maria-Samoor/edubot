from django.shortcuts import render,redirect,get_object_or_404
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import login_required
from .models import Child, Activity, ChildActivity, TouchBodyPartStats, MatchColorStats, FindImageStats
from .forms import ChildForm
from .mqtt_communication import MQTTClient
import time
from django.utils import timezone

@login_required
def home(request):
    """
    View for the home page of the application.
    
    Renders the home page template located at 'activities/home.html'.
    
    Args:
        request: The HTTP request object.
    
    Returns:
        HttpResponse: Rendered home page template.
    """
    return render(request, 'activities/home.html')

@login_required
def select_child(request):

    """
    View to display a list of all children from the database.

    Args:
        request (HttpRequest): The request object.

    Returns:
        HttpResponse: The rendered template with a list of children.
    """
    children = Child.objects.all()  # Retrieve all Child objects from the database
    
    context = {
        'children': children,
    }
    return render(request, 'activities/selectchild.html', context)

@login_required
def delete_child(request, child_id):
    """
    View to delete a child from the database.

    Args:
        request (HttpRequest): The request object.
        child_id (int): The ID of the child to be deleted.

    Returns:
        HttpResponse: Redirects to the list of children after deletion.
    """
    child = get_object_or_404(Child, id=child_id)
    
    if request.method == "POST":
        # Delete the child from the database
        child.delete()
        # Redirect to the child list view or another appropriate view
        return redirect('selectchild')
    
    # If not POST, render a confirmation page (optional)
    return render(request, 'activities/selectchild.html', {'child': child})

@login_required
def add_child(request):
    """
    View to handle adding a child.
    It displays the form, validates the input, and redirects to the 'selectchild' page upon success.
    """
    if request.method == 'POST':
        form = ChildForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('selectchild')  # Adjust the URL name based on your project setup
    else:
        form = ChildForm()
    
    return render(request, 'activities/addchild.html', {'form': form})

@login_required
def select_activity(request, child_id):
    """
    View for the select activity page of the application.
    
    This view retrieves all activities from the database and renders the 
    select activity page template located at 'activities/selectactivity.html'.
    
    Args:
        request: The HTTP request object. This contains metadata about 
                 the request and can be used to access session data, 
                 user information, and other HTTP-related information.
    
    Returns:
        HttpResponse: Rendered select activity page template containing 
                      a list of available activities.
    """
    child = get_object_or_404(Child, id=child_id)
    activities = Activity.objects.all()
    return render(request, 'activities/selectactivity.html' , {'activities': activities, 'child': child})

@login_required
def start_activity(request, child_id, activity_id):
    """
    Start an activity for a specific child by publishing a start command to the MQTT broker.

    This view connects to the MQTT broker, publishes a start command for the selected activity,
    and renders the activity_in_progress.html template, displaying the selected child and activity.

    Args:
        request (HttpRequest): The HTTP request object.
        child_id (int): The ID of the child for whom the activity is being started.
        activity_id (int): The ID of the activity being started.

    Returns:
        HttpResponse: Renders the 'activity_in_progress.html' template with the selected activity and child.
    """
    child = get_object_or_404(Child, id=child_id)
    activity = get_object_or_404(Activity, id=activity_id)
    child_activity, created = ChildActivity.objects.get_or_create(
        child=child,
        activity=activity,
        defaults={'start_activity': timezone.now()}
    )
    if not created:  # If the record already exists, update the start time
        child_activity.start_activity = timezone.now()
        child_activity.save()
    # Initialize MQTT client and connect
    mqtt_client = MQTTClient()
    mqtt_client.connect()

    # Publish start command for the activity
    start_topic = f"activity/start/{activity_id}"
    mqtt_client.publish(start_topic, activity_id)

    return render(request, 'activities/activity_in_progress.html', {'activity': activity, 'child': child})

@login_required
def stop_activity(request, child_id, activity_id):
    """
    Stop an activity for a specific child and retrieve performance data from the MQTT broker.

    This view connects to the MQTT broker, subscribes to the performance topic for the selected activity,
    publishes a stop signal, and waits for performance data (correct/incorrect answers and average time).
    If performance data is received within the timeout period, it updates or creates a record for the 
    child's activity performance.

    Args:
        request (HttpRequest): The HTTP request object.
        child_id (int): The ID of the child whose activity is being stopped.
        activity_id (int): The ID of the activity being stopped.

    Returns:
        HttpResponse: Redirects to the 'activity_report' view with the updated child activity data.
    """
    mqtt_client = MQTTClient()
    mqtt_client.connect()

    # Publish stop signal to specific activity's stop topic
    stop_topic = f"activity/stop/{activity_id}"
    performance_topic = f"activity/performance/{activity_id}"
    mqtt_client.subscribe(performance_topic)
    mqtt_client.publish(stop_topic, "0")  # Sending "0" to indicate stop

    # Wait for performance data
    timeout = time.time() + 10  # 10-second timeout
    performance_data = None

    while time.time() < timeout:
        if mqtt_client.performance_data_received:
            performance_data = mqtt_client.performance_data
            break
        time.sleep(0.1)

    if not performance_data:
        print(f"No performance data received for activity {activity_id}.")
        return redirect('activity_report', child_id=child_id)
    
    # Retrieve or create the ChildActivity object
    child_activity, created = ChildActivity.objects.get_or_create(
        child_id=child_id,
        activity_id=activity_id,
    )
    child_activity.stop_activity = timezone.now()
    child_activity.total_right_answers = sum(performance_data['right_answers'].values())
    child_activity.total_wrong_answers = sum(performance_data['wrong_answers'].values())
    child_activity.save()

    # Update or create TouchBodyPartStats records for each body part
    if activity_id == 1:
        # Handle Touch Body Part activity
        for body_part, right_answers in performance_data['right_answers'].items():
            wrong_answers = performance_data['wrong_answers'].get(body_part, 0)
            TouchBodyPartStats.objects.update_or_create(
                child_activity=child_activity,
                body_part=body_part,
                defaults={
                    'right_answers': right_answers,
                    'wrong_answers': wrong_answers,
                },
            )
    elif activity_id == 2:
        # Handle Match Color activity
        for color, right_answers in performance_data['right_answers'].items():
            wrong_answers = performance_data['wrong_answers'].get(color, 0)
            MatchColorStats.objects.update_or_create(
                child_activity=child_activity,
                color=color,
                defaults={
                    'right_answers': right_answers,
                    'wrong_answers': wrong_answers,
                },
            )
    elif activity_id == 4: 
        for image_type, right_answers in performance_data['right_answers'].items():
            wrong_answers = performance_data['wrong_answers'].get(image_type, 0)
            FindImageStats.objects.update_or_create(
                child_activity=child_activity,
                image_type=image_type,
                defaults={
                    'right_answers': right_answers,
                    'wrong_answers': wrong_answers,
                },
            )

        # Reset performance data and unsubscribe from topic
    mqtt_client.reset_performance_data()
    mqtt_client.unsubscribe(performance_topic)

    return redirect('activity_report', child_id=child_id)

@login_required
def activity_report(request, child_id):
    """
    Displays the activity report for a specific child, showing performance data
    such as correct answers, incorrect answers, and average time taken.

    Args:
        request (HttpRequest): The request object.
        child_id (int): The ID of the child.

    Returns:
        HttpResponse: Renders the activity report page with performance data.
    """
    child = get_object_or_404(Child, id=child_id)
    print("child: ", child)
    performance_records = ChildActivity.objects.filter(child=child).select_related('activity')
    print("performance_records: ", performance_records)
    return render(request, 'activities/activity_report.html', {
        'child': child,
        'performance_records': performance_records,
    })

@login_required
def logout_view(request):
    """
    View for the login  page of the application.
    
    Renders the login page template located at 'selectchild/home.html'.
    
    Args:
        request: The HTTP request object.
    
    Returns:
        HttpResponse: Rendered add child page template.
    """
    logout(request)
    return redirect('login')