from django.http import JsonResponse

def your_view(request):
    if request.method == 'POST':
        # Your logic to save or process the content

        # Return a JSON response
        return JsonResponse({'status': 'success', 'message': 'Data saved successfully'})
    else:
        return JsonResponse({'status': 'error', 'message': 'Invalid request method'})
