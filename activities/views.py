from django.shortcuts import render,redirect,get_object_or_404
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import login_required
from .models import Child, Activity, ChildActivity, TouchBodyPartStats, MatchColorStats, FindImageStats, FindNumberStats, LearnWithButtonsStats
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
    
    child.delete()
    # Redirect to the child list view or another appropriate view
    return redirect('selectchild')
    

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
    It ensures that the MQTT client connects and publishes to the topic only
    when the selected child ID changes or isn't consecutive.

    Args:
        request: The HTTP request object. This contains metadata about 
                 the request and can be used to access session data, 
                 user information, and other HTTP-related information.
        child_id: The ID of the selected child.

    Returns:
        HttpResponse: Rendered select activity page template containing 
                      a list of available activities and child details.
    """
    child = get_object_or_404(Child, id=child_id)
    activities = Activity.objects.all()

    # Retrieve the last selected child ID from the session
    last_child_id = request.session.get('last_selected_child_id')

    # Check if the selected child ID is different from the last stored ID
    if last_child_id != child_id:
        mqtt_client = MQTTClient()
        mqtt_client.connect()

        start_topic = f"activity/start/6"
        mqtt_client.publish(start_topic, "6")
        
        time.sleep(3)
        first_name = child.name.split()[0]
        mqtt_client.publish("child/name", first_name)

        request.session['last_selected_child_id'] = child_id

    return render(request, 'activities/selectactivity.html', {'activities': activities, 'child': child})


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
        return redirect('activity_report', child_id=child_id, activity_id=activity_id)
    
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
        for body_part, right_answers in performance_data['right_answers'].items():
            wrong_answers = performance_data['wrong_answers'].get(body_part, 0)
            TouchBodyPartStats.objects.create(
                child_activity=child_activity,
                body_part=body_part,
                right_answers=right_answers,
                wrong_answers=wrong_answers,
            )
    elif activity_id == 2:
        for color, right_answers in performance_data['right_answers'].items():
            wrong_answers = performance_data['wrong_answers'].get(color, 0)
            MatchColorStats.objects.create(
                child_activity=child_activity,
                color=color,
                right_answers=right_answers,
                wrong_answers=wrong_answers,
            )
    elif activity_id == 3: 
        for number, right_answers in performance_data['right_answers'].items():
            wrong_answers = performance_data['wrong_answers'].get(number, 0)
            FindNumberStats.objects.create(
                child_activity=child_activity,
                number=number,
                right_answers=right_answers,
                wrong_answers=wrong_answers,
        )
            
    elif activity_id == 4: 
        for image_type, right_answers in performance_data['right_answers'].items():
            wrong_answers = performance_data['wrong_answers'].get(image_type, 0)
            FindImageStats.objects.create(
                child_activity=child_activity,
                image_type=image_type,
                right_answers=right_answers,
                wrong_answers=wrong_answers,
            )
    elif activity_id == 5: 
        for button, right_answers in performance_data['right_answers'].items():
            wrong_answers = performance_data['wrong_answers'].get(button, 0)
            LearnWithButtonsStats.objects.create(
                child_activity=child_activity,
                button=button,
                right_answers=right_answers,
                wrong_answers=wrong_answers,
            )

    # Reset performance data and unsubscribe from topic
    mqtt_client.reset_performance_data()
    mqtt_client.unsubscribe(performance_topic)

    return redirect('activity_report', child_id=child_id, activity_id=activity_id)

@login_required
def child_report(request, child_id):
    """
    Displays the report for a specific child, showing performance data
    such as correct answers, incorrect answers, and time taken.

    Args:
        request (HttpRequest): The request object.
        child_id (int): The ID of the child.

    Returns:
        HttpResponse: Renders the report page with performance data.
    """
    child = get_object_or_404(Child, id=child_id)
    print("child: ", child)
    performance_records = ChildActivity.objects.filter(child=child).select_related('activity')
    print("performance_records: ", performance_records)
    return render(request, 'activities/child_report.html', {
        'child': child,
        'performance_records': performance_records,
    })

@login_required
def activity_report(request, child_id,activity_id):
    """
    Displays the activity report for a specific child and activity, showing all attempts
    ordered from newest to oldest.
    """
    # Retrieve the child and activity objects
    child = get_object_or_404(Child, id=child_id)
    activity = get_object_or_404(Activity, id=activity_id)

    # Retrieve the ChildActivity instance for this child and activity
    child_activity = get_object_or_404(ChildActivity, child=child, activity=activity)

    # Determine the related stats based on the activity type
    stats_model_mapping = {
        "Touch Correct Body Part": TouchBodyPartStats,
        "Match the Color": MatchColorStats,
        "Finger Counting Game": FindNumberStats,
        "Find the Different Image": FindImageStats,
        "Learning with Buttons": LearnWithButtonsStats,
    }

    stats_model = stats_model_mapping.get(child_activity.activity.activity_name)
    # if not stats_model:
    #     return render(request, "error.html", {"message": "Invalid activity type"})

    # Fetch all related stats for the activity
    stats = stats_model.objects.filter(child_activity=child_activity)

    # Extract unique choices (e.g., body parts, colors, etc.)
    choices_field = {
        TouchBodyPartStats: "body_part",
        MatchColorStats: "color",
        FindNumberStats: "number",
        FindImageStats: "image_type",
        LearnWithButtonsStats: "button",
    }.get(stats_model)

    # Prepare a dictionary for storing display names
    display_name_mapping = {
        "color": dict(MatchColorStats.COLOR_CHOICES),
        "body_part": dict(TouchBodyPartStats.BODY_PART_CHOICES),
        "number": dict(FindNumberStats.NUMBER_CHOICES),
        "image_type": dict(FindImageStats.IMAGE_CHOICES),
        "button": dict(LearnWithButtonsStats.BUTTON_CHOICES),

    }
    
    # Retrieve distinct choices and map to display names
    raw_choices = stats.values_list(choices_field, flat=True).distinct()
    sorted_choices = sorted(raw_choices, key=lambda x: int(x) if x.isdigit() else x)
    choices = [
        display_name_mapping[choices_field].get(choice, choice)
        for choice in sorted_choices
    ]

    # Group attempts by choice with display names
    grouped_attempts = {}
    for raw_choice in sorted_choices:
        display_choice = display_name_mapping[choices_field].get(raw_choice, raw_choice)
        grouped_attempts[display_choice] = stats.filter(**{choices_field: raw_choice}).order_by("attempt")

    # Prepare context for the template
    context = {
        "child_id": child_activity.child.id,
        "child_name": child_activity.child.name,
        "activity_name": child_activity.activity.activity_name,
        "activity_id": child_activity.activity.id,
        "choices": choices,
        "attempts_by_choice": grouped_attempts,
    }

    return render(request, "activities/activity_report.html", context)

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