from django.shortcuts import render
from .forms import ImageUploadForm
from backend_poc import extract_img, validate
import os
import tempfile

def index(request):
    path = os.path.dirname(os.path.abspath(__file__))
    if request.method == 'POST':
        form = ImageUploadForm(request.POST, request.FILES)
        if form.is_valid():
            uploaded_image = request.FILES['image']

            # Create a temporary file to provide a file path to extract_img
            with tempfile.NamedTemporaryFile(suffix='.png', delete=True) as tmp:
                for chunk in uploaded_image.chunks():
                    tmp.write(chunk)
                tmp.flush()

                data = extract_img(tmp.name)
                result = validate(os.path.join(path, "model.xz"), data)

            verdict = "Safe" if result == 0 else "Quishing detected !!"
            return render(request, 'scanner/result.html', {'verdict': verdict})
        else:
            return render(request, 'scanner/index.html', {'form': form, 'error': 'Invalid form data'})
    else:
        # GET request, show the form
        return render(request, 'scanner/index.html', {'form': ImageUploadForm()})

