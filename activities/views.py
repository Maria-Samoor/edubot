from django.shortcuts import render,redirect,get_object_or_404
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import login_required
from .models import Child, Activity
from .forms import ChildForm
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

@login_required
def select_activity(request):
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
    activities = Activity.objects.all()
    return render(request, 'activities/selectactivity.html' , {'activities': activities})