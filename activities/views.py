from django.shortcuts import render,redirect,get_object_or_404
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import login_required
from .models import Child, Activity, ChildActivity
from .forms import ChildForm
from .socket_communication import SocketCommunication

# Create your views here.
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
    Starts an activity for a specific child by sending the activity ID to 
    Choregraphe via socket communication.

    Args:
        request (HttpRequest): The request object.
        child_id (int): The ID of the child.
        activity_id (int): The ID of the activity to start.

    Returns:
        HttpResponse: Renders the activity started page with the selected 
                       activity and child details.
    """
    child = get_object_or_404(Child, id=child_id)
    activity = get_object_or_404(Activity, id=activity_id)

    socket_communication = SocketCommunication()
    socket_communication.bind_server()

    socket_communication.send_int(int(activity_id))
    socket_communication.connect_client()

    return render(request, 'activities/activity_in_progress.html', {'activity': activity, 'child': child})

@login_required
def stop_activity(request, child_id, activity_id):
    """
    Stops an ongoing activity for a specific child by sending a stop signal 
    to Choregraphe via socket communication, and receives performance data 
    to update or create a ChildActivity record.

    Args:
        request (HttpRequest): The request object.
        child_id (int): The ID of the child.
        activity_id (int): The ID of the activity to stop.

    Returns:
        HttpResponse: Redirects to the activity report for the selected child.
    """
    # Create a SocketCommunication instance
    socket_communication = SocketCommunication()
    socket_communication.connect_client()

    # Send stop signal (0)
    socket_communication.send_int(0)

    # Receive performance data
    wrong_answers = socket_communication.receive_int()
    right_answers = socket_communication.receive_int()
    avg_time =0.0
    if wrong_answers is not None and right_answers is not None:
    # Update or create ChildActivity record
        child_activity, created = ChildActivity.objects.update_or_create(
        child_id=child_id,
        activity_id=activity_id,
        defaults={
            'correct_answers': right_answers,
            'incorrect_answers': wrong_answers,
            'average_time': avg_time if avg_time is not None else 0,
        },
        )

    socket_communication.disconnect()  # Close the socket connection

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
    performance_records = ChildActivity.objects.filter(child=child).select_related('activity')

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