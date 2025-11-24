from django.shortcuts import render

# Create your views here.
def mbti_test(request):
    return render(request, 'mbti_test.html')