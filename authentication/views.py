from django.shortcuts import redirect, render

# Create your views here.
def home(request):
    if not request.user.is_authenticated: 
        return render(request, 'home.html')
    if request.user.is_superuser:
        return redirect('admin:index')

    if request.user.is_creator:
        pass

    # if not request.user.is_authenticated: 
    #     return redirect('schools:districts')
    
    # if not request.user.is_staff:
    #     # please class teacher or principal to activate
    #     return render(request,'home.html')
    # if request.user.is_teacher:
    #     return redirect('classroom:attendance')
        
    # elif request.user.is_student:
    #     return redirect('dashboard:attendance')
    # # some other users, eg: principal,admin
    # return redirect('admin:index')
    return render(request, 'home.html')